"""Trend-chasing strategy: react to what the fleet is actually catching."""
from arena.api.ctx import Strategy, Book, CommitPTO

SHORT_WINDOW = 5.0
LONG_WINDOW = 20.0
MIN_SAMPLE = 25.0
PTO_LOOKAHEAD = 14

# offer class -> (trips.cls values that count, bar to book PTO-free, bar to
# spend PTO on it, worth pre-committing PTO for)
VALUE_CLASSES = {
    "THREE_QUARTER": {"trip_cls": ["three_quarter"], "book_bar": 0.10, "pto_bar": float("inf")},
    "OVERNIGHT": {"trip_cls": ["overnight"], "book_bar": 0.20, "pto_bar": 0.35},
    "DAY_1_5": {"trip_cls": ["day_1_5"], "book_bar": 0.10, "pto_bar": 0.35},
}


def _window_rate(trips, cls_list, t_now, window):
    try:
        df = trips[
            (trips["cls"].isin(cls_list))
            & (trips["fish_date_t"] < t_now)
            & (trips["fish_date_t"] >= t_now - window)
        ]
        anglers = df["anglers"].sum()
        if anglers < MIN_SAMPLE:
            return None
        return float(df["yt"].sum()) / float(anglers)
    except Exception:
        return None


def _trend_rate(trips, cls_list, t_now):
    if trips is None:
        return 0.0
    r = _window_rate(trips, cls_list, t_now, SHORT_WINDOW)
    if r is not None:
        return r
    r = _window_rate(trips, cls_list, t_now, LONG_WINDOW)
    if r is not None:
        return r
    return 0.0


def _best_boat(ctx, trips, cls_key, cls_list, fishing_day, t_now):
    scheduled = None
    try:
        scheduled = ctx.scheduled_boats(cls_key, fishing_day)
    except Exception:
        scheduled = None
    if not scheduled:
        try:
            return ctx.pick_boat(cls_key, fishing_day)
        except Exception:
            return None
    best_boat, best_rate = None, -1.0
    try:
        window_df = trips[
            (trips["cls"].isin(cls_list))
            & (trips["fish_date_t"] < t_now)
            & (trips["fish_date_t"] >= t_now - LONG_WINDOW)
        ]
        for boat in scheduled:
            bdf = window_df[window_df["boat"] == boat]
            anglers = bdf["anglers"].sum()
            if anglers > 0:
                rate = float(bdf["yt"].sum()) / float(anglers)
                if rate > best_rate:
                    best_rate, best_boat = rate, boat
    except Exception:
        best_boat = None
    if best_boat is not None:
        return best_boat
    try:
        return ctx.pick_boat(cls_key, fishing_day)
    except Exception:
        return scheduled[0]


class Strategy(Strategy):
    name = "trend chaser"

    def describe(self):
        return (
            "For three-quarter, overnight and 1.5-day trips I compute the "
            "fleet's yellowtail-per-angler rate over the last 5 days, "
            "falling back to 20 days when too few anglers were sampled. "
            "Half-day and twilight trips are skipped: historically they "
            "almost never produce yellowtail. If a class's rate clears its "
            "bar, I book the next open offer of that class on whichever "
            "scheduled boat had the best recent rate. Booking a date that "
            "needs paid time off requires a much higher bar (three-quarter "
            "trips never spend PTO at all), since PTO is scarce and never "
            "refunded. When overnight or 1.5-day rates clear that higher "
            "bar, I also pre-commit PTO for the weekday 14 days out, since "
            "PTO must be locked in that far ahead, betting the run is still "
            "going by then. I stop booking a class, and stop pre-committing "
            "PTO for it, as soon as its recent rate falls back near zero, "
            "without trying to predict when a run will start or end."
        )

    def decide(self, ctx):
        if not hasattr(self, "_committed"):
            self._committed = set()
        actions = []
        try:
            trips = ctx.observe("trips")
        except Exception:
            trips = None
        t_now = ctx.now.t

        for cls_key, info in VALUE_CLASSES.items():
            try:
                offer = ctx.offer(cls_key)
            except Exception:
                offer = None
            if offer is None or not getattr(offer, "bookable", False):
                continue
            rate = _trend_rate(trips, info["trip_cls"], t_now)
            pto_dates = getattr(offer, "pto_dates", None) or []
            needs_pto = len(pto_dates) > 0
            bar = info["pto_bar"] if needs_pto else info["book_bar"]
            if rate < bar:
                continue
            cost = getattr(offer, "cost", 0)
            if cost > ctx.budget_left:
                continue
            if needs_pto and len(pto_dates) > ctx.pto_left:
                continue
            fishing_dates = getattr(offer, "fishing_dates", None)
            fishing_day = fishing_dates[0] if fishing_dates else getattr(offer, "departure", ctx.today)
            boat = _best_boat(ctx, trips, cls_key, info["trip_cls"], fishing_day, t_now)
            if boat is None:
                continue
            reason = "%s trailing yt/angler=%.2f over recent fleet trips" % (cls_key, rate)
            actions.append(Book(offer.id, reason, boat=boat))

        try:
            target_day = ctx.today.plus(PTO_LOOKAHEAD)
        except Exception:
            target_day = None
        if target_day is not None and ctx.pto_left > 0:
            is_free = bool(getattr(target_day, "is_weekend", False) or getattr(target_day, "is_holiday", False))
            key = (getattr(target_day, "season", None), getattr(target_day, "doy", None))
            if not is_free and key not in self._committed:
                for cls_key, info in VALUE_CLASSES.items():
                    if info["pto_bar"] == float("inf"):
                        continue
                    rate = _trend_rate(trips, info["trip_cls"], t_now)
                    if rate >= info["pto_bar"]:
                        reason = (
                            "%s trailing yt/angler=%.2f is strong; pre-committing PTO "
                            "%d days out before the window closes" % (cls_key, rate, PTO_LOOKAHEAD)
                        )
                        actions.append(CommitPTO(target_day, reason))
                        self._committed.add(key)
                        break

        return actions
