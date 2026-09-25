"""Warm water first: fall offshore window, confirmed by pier temperature and recent offshore counts."""
from arena.api.ctx import Strategy, Book, CommitPTO
import numpy as np
import pandas as pd

FALL_LO, FALL_HI = 250, 318      # doy window where history shows the big offshore yellowtail bite
PTO_LO, PTO_HI = 262, 308        # window for committing Fri/Mon PTO
RESERVE_FOR_FALL = 1100.0


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
        return ("Follows the water. Signals: Scripps Pier water temp (7-day mean, and last 3 days vs the "
                "prior week) and the recent offshore bite (yellowtail per angler on overnight and 1.5-day "
                "boats over the last 6 days). Main window is early fall (roughly day-of-year 250-318), "
                "where past seasons show the offshore bite. In that window it books a 1.5-day (or an "
                "overnight if money is short or the bite is only moderate) when the bite is confirmed (>=0.8 "
                "fish/angler) and the water is warm (>=65F or warming), or the bite is very strong (>=2). "
                "Outside the window it books only when the water is warm AND the bite is strong, keeping "
                "$1100 in reserve for fall. Hot counts on cold water are ignored. PTO: commits Fridays and "
                "Mondays in the fall window 14 days ahead once the water is >=63F, so trips can wrap "
                "weekends. Boat: the default scheduled boat for the class.")

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
        if hour == 16 and ctx.pto_left > 0 and wk is not None and np.isfinite(wk) and wk >= 63.0:
            try:
                d = today.plus(14)
                weekday_ok = (not d.is_weekend) and (not d.is_holiday)
                fri = d.plus(1).is_weekend
                mon = d.plus(-1).is_weekend
                if weekday_ok and (fri or mon) and PTO_LO <= d.doy <= PTO_HI:
                    acts.append(CommitPTO(d, "warm water building into the fall offshore window"))
            except Exception:
                pass

        # Bookings: offshore trips are booked at the 16:00 tick
        if hour != 16:
            return acts
        in_fall = FALL_LO <= today.doy <= FALL_HI
        if in_fall:
            go = (confirmed and warm) or strong
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
