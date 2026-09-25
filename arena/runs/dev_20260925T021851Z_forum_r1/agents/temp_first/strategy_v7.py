from arena.api.ctx import Strategy, Book, CommitPTO

LONG = ("overnight", "day_1_5", "multi_day")


class Strategy(Strategy):
    name = "warm water first"

    def describe(self):
        return ("Warm water first. Gate: 7-day mean Scripps Pier temperature must be at least 59 F "
                "(colder water has shown almost no yellowtail). Signal: yellowtail per angler on "
                "overnight and 1.5-day boats, each class separately, over the last 7 days. At the 16:00 "
                "tick, book an OVERNIGHT or 1.5-DAY trip whose own class rate is hot enough: 1.5 in "
                "the fall window (day of year 255-310), 1.0 otherwise, and outside fall only while "
                "keeping $1200 in reserve. Among qualifying offers pick the best rate per dollar. Prefer "
                "weekend trips that cost no PTO. Commit PTO 14 days ahead on alternate weekdays "
                "inside the fall peak window (day 270-305), keeping it for weekday overnights. "
                "3/4-day add-on: at 21:00, book a bookable no-PTO 3/4-day trip when the 7-day "
                "3/4-day rate is at least 0.5 per angler (best fish per dollar at $150), with no "
                "budget reserve. "
                "Boat = scheduled boat that ran that class most recently (pick_boat).")

    def _signal(self, ctx):
        t_now = ctx.now.t
        rate = {"overnight": 0.0, "day_1_5": 0.0, "all": 0.0}
        try:
            tr = ctx.observe("trips")
            tr = tr[(tr.fish_date_t > t_now - 8) & tr.cls.isin(LONG)]
            for k in ("overnight", "day_1_5"):
                d = tr[tr.cls == k]
                if d.anglers.sum() > 0:
                    rate[k] = float(d.yt.sum()) / float(d.anglers.sum())
            if tr.anglers.sum() > 0:
                rate["all"] = float(tr.yt.sum()) / float(tr.anglers.sum())
        except Exception:
            pass
        temp = None
        try:
            p = ctx.observe("pier")
            p = p[p.ts_t > t_now - 7]
            if len(p):
                temp = float(p.wtmp_c.mean()) * 9 / 5 + 32
        except Exception:
            pass
        return rate, temp

    def _three_quarter(self, ctx):
        # Book tomorrow's no-PTO 3/4-day trip when the 7-day 3/4-day rate is >= 0.5/angler.
        rate, temp = self._signal(ctx)
        if temp is None or temp < 59:
            return []
        tq = 0.0
        try:
            tr = ctx.observe("trips")
            d = tr[(tr.fish_date_t > ctx.now.t - 8) & (tr.cls == "three_quarter")]
            if d.anglers.sum() > 0:
                tq = float(d.yt.sum()) / float(d.anglers.sum())
        except Exception:
            return []
        if tq < 0.5:
            return []
        # season 1: hot 3/4 boats (doy 240-275) beat 1.5-day trips on fish per
        # dollar, and the 1.5-day reserve never got spent, so no reserve
        reserve = 0
        cands = []
        for o in ctx.offers:
            if str(o.cls).lower() != "three_quarter" or not o.bookable:
                continue
            if len(o.pto_dates or []) > 0 or ctx.budget_left - o.cost < reserve:
                continue
            cands.append(o)
        if not cands:
            return []
        o = cands[0]
        boat = None
        for day in (o.departure, (o.fishing_dates or [None])[0]):
            if day is None:
                continue
            try:
                boat = ctx.pick_boat(o.cls, day)
            except Exception:
                boat = None
            if boat:
                break
        reason = "pier %.1fF, 3/4-day yt/angler %.2f last week" % (temp, tq)
        return [Book(o.id, reason, boat=boat) if boat else Book(o.id, reason)]

    def decide(self, ctx):
        acts = []
        doy = ctx.today.doy
        # PTO: commit ahead in the fall peak window
        if ctx.now.hour == 16 and ctx.pto_left >= 1:
            tgt = ctx.today.plus(14)
            if (not tgt.is_weekend and not tgt.is_holiday
                    and 270 <= tgt.doy <= 305 and tgt.doy % 2 == 0):
                acts.append(CommitPTO(tgt, "fall peak window: reserve a weekday for an overnight"))
        if ctx.now.hour == 21:
            return acts + self._three_quarter(ctx)
        if ctx.now.hour != 16:
            return acts
        rate, temp = self._signal(ctx)
        if temp is None or temp < 59:
            return acts
        fall = 255 <= doy <= 310
        # fall peak weeks run 2-4 yt/angler; early-fall 0.1-0.5 weeks are traps
        need = 1.5 if fall else 1.0
        if max(rate["overnight"], rate["day_1_5"]) < need:
            return acts
        cands = []
        for o in ctx.offers:
            if o.cls not in ("OVERNIGHT", "DAY_1_5") or not o.bookable:
                continue
            if o.cost > ctx.budget_left:
                continue
            if not fall and ctx.budget_left - o.cost < 1200:
                continue
            npto = len(o.pto_dates or [])
            if npto > 0 and not fall:
                continue
            # each class must clear the bar on its own rate (a hot 1.5-day week
            # once triggered a dead overnight); rank by fish per dollar
            r = rate["day_1_5"] if o.cls == "DAY_1_5" else rate["overnight"]
            if r < need:
                continue
            score = r / max(float(o.cost), 1.0) - 0.0002 * npto
            cands.append((score, o))
        if not cands:
            return acts
        cands.sort(key=lambda x: -x[0])
        o = cands[0][1]
        boat = None
        for day in (o.departure, (o.fishing_dates or [None])[0]):
            if day is None:
                continue
            try:
                boat = ctx.pick_boat(o.cls, day)
            except Exception:
                boat = None
            if boat:
                break
        r = rate["day_1_5"] if o.cls == "DAY_1_5" else rate["overnight"]
        reason = "pier %.1fF, %s yt/angler %.2f last week" % (temp, o.cls.lower(), r)
        if boat:
            acts.append(Book(o.id, reason, boat=boat))
        else:
            acts.append(Book(o.id, reason))
        return acts
