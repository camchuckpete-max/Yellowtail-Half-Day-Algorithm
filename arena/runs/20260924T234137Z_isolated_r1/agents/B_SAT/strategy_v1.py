"""Scripted baselines (SPEC §5.5), always in the field. Deterministic, ctx-only, no LLM.

They follow the same contract as any strategy and run in the same sandbox. Weekday trips need
PTO committed 14 days ahead (§3.2); the baselines below are literal and do not commit PTO, so
B_SAT / B_PERSIST / B_TEMP fish weekends and holidays only, and B_BIG's Friday-evening 1.5-day
departures (fish Saturday, back Sunday 06:00) cost no PTO.
"""
from __future__ import annotations

from arena.api.ctx import Book, Strategy

JUL_1, OCT_31, AUG_1, SEP_30 = 182, 304, 213, 273   # day-of-year bounds (non-leap; +-1 day in leap years is fine)
HD_CLASSES = ("hd_am", "hd_pm", "hd_unspecified", "hd_twilight")


def _book_if(ctx, cls: str, reason: str):
    o = ctx.offer(cls)
    if o is not None and o.bookable:
        return [Book(o.id, reason)]
    return []


class B_SAT(Strategy):
    name = "B_SAT"

    def describe(self):
        return "Every Saturday from July to October, book the PM half day."

    def decide(self, ctx):
        if ctx.now.hour != 21:
            return []
        d = ctx.tomorrow
        if d.weekday == 5 and JUL_1 <= d.doy <= OCT_31:
            return _book_if(ctx, "HD_PM", "Saturday in July–October")
        return []


class B_PERSIST(Strategy):
    name = "B_PERSIST"

    def describe(self):
        return "Book tomorrow's PM half day if today's pooled half-day yellowtail count (visible at 21:00) is > 0."

    def decide(self, ctx):
        if ctx.now.hour != 21:
            return []
        t = ctx.observe("trips")
        today = t[(t["fish_date_t"] == float(ctx.today.n)) & t["cls"].isin(HD_CLASSES)]
        if len(today) and today["yt"].sum() > 0:
            return _book_if(ctx, "HD_PM", f"pooled half-day yt today = {int(today['yt'].sum())}")
        return []


class B_TEMP(Strategy):
    name = "B_TEMP"

    def describe(self):
        return "July–October, when the latest Scripps Pier water temperature is ≥ 68 °F and ONI > 0, book the PM half day."

    def decide(self, ctx):
        if ctx.now.hour != 21 or not (JUL_1 <= ctx.tomorrow.doy <= OCT_31):
            return []
        pier = ctx.observe("pier")
        recent = pier[pier["ts_t"] >= ctx.now.t - 1.0]["wtmp_c"].dropna()
        if recent.empty:
            return []
        temp_f = float(recent.mean()) * 9 / 5 + 32
        cl = ctx.observe("climate")
        oni = cl[cl["index_id"].str.lower() == "oni"]["value"].dropna()
        if temp_f >= 68.0 and len(oni) and float(oni.iloc[-1]) > 0:
            return _book_if(ctx, "HD_PM", f"pier {temp_f:.1f} °F, ONI {float(oni.iloc[-1]):+.1f}")
        return []


class B_BIG(Strategy):
    name = "B_BIG"

    def describe(self):
        return "Spend the whole budget on 1.5-day trips departing Friday evenings in August–September."

    def decide(self, ctx):
        if ctx.now.hour != 16 or ctx.today.weekday != 4 or not (AUG_1 <= ctx.today.doy <= SEP_30):
            return []
        return _book_if(ctx, "DAY_1_5", "Friday in August–September")


BASELINES = {"B_SAT": B_SAT, "B_PERSIST": B_PERSIST, "B_TEMP": B_TEMP, "B_BIG": B_BIG}
