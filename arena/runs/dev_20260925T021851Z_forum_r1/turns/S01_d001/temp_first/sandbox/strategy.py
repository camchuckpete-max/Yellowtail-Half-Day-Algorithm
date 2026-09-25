from arena.api.ctx import Strategy, Book, CommitPTO

LONG = ("overnight", "day_1_5", "multi_day")


def _num(x, default=None):
    try:
        return float(x)
    except Exception:
        return default


class Strategy(Strategy):
    name = "warm water first"

    def describe(self):
        return ("Warm water first. Gate: 7-day mean Scripps Pier temperature must be at least 59 F "
                "(colder water has shown almost no yellowtail). Signal: yellowtail per angler on "
                "overnight/1.5-day/multi-day boats over the last 7 days. At the 16:00 tick, book an "
                "OVERNIGHT or 1.5-DAY trip when the signal is hot enough: 0.5 in the fall window "
                "(day of year 255-310), 1.0 otherwise, and outside fall only while keeping $1200 "
                "in reserve. Choose 1.5-day only when its recent rate beats overnight by 30%. Prefer "
                "weekend trips that cost no PTO. Commit PTO 14 days ahead on alternate weekdays "
                "inside the fall peak window (day 270-305), keeping it for weekday overnights. "
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

    def decide(self, ctx):
        acts = []
        doy = ctx.today.doy
        # PTO: commit ahead in the fall peak window
        if ctx.now.hour == 16 and ctx.pto_left >= 1:
            tgt = ctx.today.plus(14)
            if (not tgt.is_weekend and not tgt.is_holiday
                    and 270 <= tgt.doy <= 305 and tgt.doy % 2 == 0):
                acts.append(CommitPTO(tgt, "fall peak window: reserve a weekday for an overnight"))
        if ctx.now.hour != 16:
            return acts
        rate, temp = self._signal(ctx)
        if temp is None or temp < 59:
            return acts
        fall = 255 <= doy <= 310
        need = 0.5 if fall else 1.0
        if rate["all"] < need:
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
            if o.cls == "DAY_1_5":
                if rate["day_1_5"] < 1.3 * max(rate["overnight"], 0.01) or ctx.budget_left < 1100:
                    continue
                score = rate["day_1_5"] * 1.2
            else:
                score = rate["overnight"] + 0.01
            score -= 0.2 * npto
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
        reason = "pier %.1fF, long-range yt/angler %.2f last week" % (temp, rate["all"])
        if boat:
            acts.append(Book(o.id, reason, boat=boat))
        else:
            acts.append(Book(o.id, reason))
        return acts
