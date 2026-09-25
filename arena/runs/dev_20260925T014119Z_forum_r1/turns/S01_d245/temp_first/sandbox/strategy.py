"""Warm water first: fall offshore window, confirmed by pier temperature and recent offshore counts."""
from arena.api.ctx import Strategy, Book, CommitPTO
import numpy as np
import pandas as pd

FALL_LO, FALL_HI = 250, 318      # doy window where history shows the big offshore yellowtail bite
PTO_LO, PTO_HI = 262, 345        # window for committing Fri/Mon PTO
FALL_PEAK_LO, FALL_PEAK_HI = 268, 300  # historical peak: Friday PTO even if water stays cold
RESERVE_FOR_FALL = 1100.0
TQ_RESERVE = 800.0               # keep this much for offshore trips when booking 3/4-day trips (before late season)


def _df(x):
    if isinstance(x, pd.DataFrame):
        return x
    try:
        return pd.DataFrame(x)
    except Exception:
        return pd.DataFrame()


def _late(doy):
    return doy > FALL_HI or doy < 90


def _boat(ctx, cls, o, fallback_day):
    """Schedule is keyed by the fishing date, not the departure date."""
    try:
        fd = o.fishing_dates[0]
    except Exception:
        fd = fallback_day
    boat = None
    try:
        boat = ctx.pick_boat(cls, fd)
    except Exception:
        boat = None
    if not boat:
        try:
            sb = ctx.scheduled_boats(cls, fd)
            if sb:
                boat = list(sb)[0]
        except Exception:
            boat = None
    return boat


class Strategy(Strategy):
    name = "warm water first"

    def describe(self):
        return ("Follows the water. Signals: Scripps Pier water temp (7-day mean and 3-day trend) and the "
                "offshore bite (yellowtail per angler on overnight and 1.5-day boats, last 6 days). In the "
                "fall window (day-of-year 250-318) it books a 1.5-day or overnight when the bite is >=0.8 "
                "and the water is warm, or the bite is >=2, or >=1.2 over 3+ boat-days. Before the window "
                "it needs warm water AND a bite >=2 and keeps $1100 for fall. After the window (late "
                "season) it spends freely: offshore at bite >=0.8, three-quarter days on weekends/holidays "
                "at a 5-day bite >=0.3, no reserve. PTO: commits Fridays and Mondays 14 days ahead "
                "(doy 262-345) while water >=63F or the offshore bite >=0.8. Boat: the default scheduled "
                "boat for the fishing date.")

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
        late = _late(today.doy)
        wk, trend = self._pier(ctx, now_t)
        wk_ok = wk is not None and np.isfinite(wk)
        warm = wk_ok and (wk >= 65.0 or (wk >= 63.0 and trend >= 0.5))
        bite, n = self._bite(ctx, now_t)
        confirmed = n >= 2 and bite >= 0.8
        strong = n >= 2 and bite >= 2.0

        # PTO commitments 14 days ahead (Fridays and Mondays)
        if hour == 16 and ctx.pto_left > 0:
            d = None
            try:
                d = today.plus(14)
                weekday_ok = (not d.is_weekend) and (not d.is_holiday)
                fri = d.plus(1).is_weekend
                mon = d.plus(-1).is_weekend
                signal = (wk_ok and wk >= 63.0) or confirmed
                ok = (signal and (fri or mon) and PTO_LO <= d.doy <= PTO_HI) or \
                     (fri and FALL_PEAK_LO <= d.doy <= FALL_PEAK_HI and ctx.pto_left > 4)
                if not (weekday_ok and ok):
                    d = None
            except Exception:
                d = None
            if d is not None:
                try:
                    acts.append(CommitPTO(d, "offshore window: warm water or live bite"))
                except Exception:
                    try:
                        acts.append(CommitPTO(day=d, reason="offshore window: warm water or live bite"))
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
                need = 0.3 if late else 0.4
                reserve = 0.0 if late else TQ_RESERVE
                if wk_ok and wk >= 63.0 and free and len(tq) >= 3 and tbite >= need:
                    o = ctx.offer("THREE_QUARTER")
                    budget = float(ctx.budget_left)
                    if o is not None and o.bookable and float(o.cost) <= budget - reserve:
                        boat = _boat(ctx, "THREE_QUARTER", o, d1)
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
        elif late:
            go = confirmed
        else:
            go = warm and strong
        if not go:
            return acts

        budget = float(ctx.budget_left)
        prefs = ["DAY_1_5", "OVERNIGHT"] if (strong and budget >= 1100) else ["OVERNIGHT", "DAY_1_5"]
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
            if not in_fall and not late and budget - cost < RESERVE_FOR_FALL:
                continue
            boat = _boat(ctx, cls, o, today.plus(1))
            if not boat:
                continue
            reason = "pier %.1fF (trend %+.1f), offshore bite %.2f/angler over %d boat-days" % (
                wk if wk_ok else float("nan"), trend or 0.0, bite, n)
            acts.append(Book(o.id, reason, boat=boat))
            break
        return acts
