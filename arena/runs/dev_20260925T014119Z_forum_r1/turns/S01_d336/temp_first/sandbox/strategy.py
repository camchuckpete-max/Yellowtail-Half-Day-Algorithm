"""Warm water first: fall offshore window, confirmed by pier temperature and recent offshore counts."""
from arena.api.ctx import Strategy, Book, CommitPTO
import numpy as np
import pandas as pd

FALL_LO, FALL_HI = 250, 318      # doy window where history shows the big offshore yellowtail bite
PTO_LO, PTO_HI = 262, 308        # window for committing Fri/Mon PTO
FALL_PEAK_LO, FALL_PEAK_HI = 268, 300  # historical peak: Friday PTO even if water stays cold
RESERVE_FOR_FALL = 1100.0
TQ_RESERVE = 800.0               # keep this much for offshore trips when booking 3/4-day trips


def _df(x):
    if isinstance(x, pd.DataFrame):
        return x
    try:
        return pd.DataFrame(x)
    except Exception:
        return pd.DataFrame()


class Strategy(Strategy):
    name = "warm water first"

    def describe(self):
        return ("Follows the water. Signals: Scripps Pier water temp (7-day mean and 3-day trend) and the "
                "offshore bite (yellowtail per angler on overnight and 1.5-day boats, last 6 days). In the "
                "fall window (day-of-year 250-318) it books a 1.5-day or overnight when the bite is >=0.8 "
                "and the water is warm (>=65F or warming), or the bite is >=2, or >=1.2 over 3+ boat-days. "
                "Outside the window it books only with warm water AND a bite >=2, keeping $1100 for fall. "
                "PTO: commits fall-window Fridays and Mondays 14 days ahead once the water is >=63F; in a "
                "cold year it still commits a few Fridays at the historical peak (doy 268-300). "
                "Also books a three-quarter-day trip for weekend/holiday dates (no PTO) when water >=63F "
                "and its 5-day bite is >=0.4/angler, keeping $800 for offshore. "
                "Boat: the default scheduled boat for the class.")

    def _pier(self, ctx, now_t):
        p = _df(ctx.observe("pier"))
        if p.empty or "ts_t" not in p:
            return None, None
        p = p[p["ts_t"] > now_t - 11]
        if p.empty:
            return None, None
        f = p["wtmp_c"].astype(float) * 9 / 5 + 32
        wk = f[p["ts_t"] > now_t - 7].mean()
        last3 = f[p["ts_t"] > now_t - 3].mean()
        prior = f[(p["ts_t"] <= now_t - 3) & (p["ts_t"] > now_t - 10)].mean()
        trend = (last3 - prior) if (np.isfinite(last3) and np.isfinite(prior)) else 0.0
        return wk, trend

    def _bite(self, ctx, now_t):
        t = _df(ctx.observe("trips"))
        if t.empty or "fish_date_t" not in t:
            return 0.0, 0
        t = t[(t["fish_date_t"] > now_t - 6) & t["cls"].isin(["overnight", "day_1_5"])]
        a = float(t["anglers"].sum()) if len(t) else 0.0
        if a <= 0:
            return 0.0, 0
        return float(t["yt"].sum()) / a, len(t)

    def decide(self, ctx):
        acts = []
        now_t = float(ctx.now.t)
        hour = int(ctx.now.hour)
        today = ctx.today
        wk, trend = self._pier(ctx, now_t)
        warm = wk is not None and np.isfinite(wk) and (wk >= 65.0 or (wk >= 63.0 and trend >= 0.5))
        bite, n = self._bite(ctx, now_t)
        confirmed = n >= 2 and bite >= 0.8
        strong = n >= 2 and bite >= 2.0

        # PTO commitments 14 days ahead (Fridays and Mondays in the fall window)
        wk_ok = wk is not None and np.isfinite(wk)
        if hour == 16 and ctx.pto_left > 0 and wk_ok:
            try:
                d = today.plus(14)
                weekday_ok = (not d.is_weekend) and (not d.is_holiday)
                fri = d.plus(1).is_weekend
                mon = d.plus(-1).is_weekend
                # fallback: cold year -> still commit Fridays at the historical fall peak
                ok = (wk >= 63.0 and (fri or mon) and PTO_LO <= d.doy <= PTO_HI) or \
                     (fri and FALL_PEAK_LO <= d.doy <= FALL_PEAK_HI and ctx.pto_left > 4)
                if weekday_ok and ok:
                    acts.append(CommitPTO(d, "fall offshore window (warm water or historical peak)"))
            except Exception:
                pass

        # Three-quarter day trips: booked 21:00 the day before, only for free (weekend/holiday) days
        if hour == 21:
            try:
                tq = _df(ctx.observe("trips"))
                tq = tq[(tq["fish_date_t"] > now_t - 5) & (tq["cls"] == "three_quarter")]
                ta = float(tq["anglers"].sum()) if len(tq) else 0.0
                tbite = float(tq["yt"].sum()) / ta if ta > 0 else 0.0
                d1 = today.plus(1)
                free = d1.is_weekend or d1.is_holiday
                if wk_ok and wk >= 63.0 and free and len(tq) >= 3 and tbite >= 0.4:
                    o = ctx.offer("THREE_QUARTER")
                    budget = float(ctx.budget_left)
                    if o is not None and o.bookable and float(o.cost) <= budget - TQ_RESERVE:
                        boat = ctx.pick_boat("THREE_QUARTER", d1)
                        if boat:
                            acts.append(Book(o.id, "3/4 bite %.2f/angler over %d boat-days, pier %.1fF" % (
                                tbite, len(tq), wk), boat=boat))
            except Exception:
                pass
            return acts

        # Bookings: offshore trips are booked at the 16:00 tick
        if hour != 16:
            return acts
        in_fall = FALL_LO <= today.doy <= FALL_HI
        if in_fall:
            go = (confirmed and warm) or strong or (n >= 3 and bite >= 1.2)
        else:
            go = warm and strong
        if not go:
            return acts

        budget = float(ctx.budget_left)
        prefs = ["DAY_1_5", "OVERNIGHT"] if (strong or budget >= 1100) else ["OVERNIGHT", "DAY_1_5"]
        for cls in prefs:
            try:
                o = ctx.offer(cls)
            except Exception:
                o = None
            if o is None or not o.bookable:
                continue
            cost = float(o.cost)
            if cost > budget:
                continue
            if not in_fall and budget - cost < RESERVE_FOR_FALL:
                continue
            try:
                boat = ctx.pick_boat(cls, today)
            except Exception:
                boat = None
            if not boat:
                continue
            reason = "pier %.1fF (trend %+.1f), offshore bite %.2f/angler over %d boat-days" % (
                wk if wk is not None else float("nan"), trend or 0.0, bite, n)
            acts.append(Book(o.id, reason, boat=boat))
            break
        return acts
