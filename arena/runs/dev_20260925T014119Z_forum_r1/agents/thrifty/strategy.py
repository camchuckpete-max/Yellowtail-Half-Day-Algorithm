"""Thrifty: Spring bite active now (doy 140-220), book high-value three-quarter trips."""
from arena.api.ctx import Strategy, Book, CommitPTO
from collections import defaultdict


class Strategy(Strategy):
    name = "Spring Bite Active"

    def describe(self) -> str:
        return (
            "Data shows strong yellowtail catch at doy 140-153 with water at 19.9°C. "
            "Books three-quarter trips ($150) on proven boats (San Diego, Malihini, Mission Belle) "
            "averaging 15-27 fish per trip. Prioritizes weekends to avoid PTO, with 2 PTO days reserved "
            "for Friday-departing trips that wrap weekend fishing. Observes fleet catch over last 5 days "
            "by class; books three-quarter when bite is hot (>5 fish/trip average). "
            "With $480 budget expects 3-4 trips for 45-108 fish this season."
        )

    def on_turn(self, ctx) -> None:
        pass

    def decide(self, ctx) -> list:
        actions = []

        # Need minimum budget for a trip
        if ctx.budget_left < 150:
            return actions

        try:
            # Observe recent catch by class
            trips = ctx.observe("trips")
            
            # Calculate bite quality: yt per trip in last 5 days of fishing
            recent_doy = ctx.today.doy - 5
            recent_trips = trips[
                (trips["fish_date_doy"] >= recent_doy) 
                & (trips["fish_date_doy"] <= ctx.today.doy)
            ]
            
            # Check three-quarter bite
            three_q_trips = recent_trips[recent_trips["cls"] == "three_quarter"]
            if len(three_q_trips) > 0:
                three_q_avg = three_q_trips["yt"].sum() / len(three_q_trips)
            else:
                three_q_avg = 0
            
            # Book if bite is hot (>5 fish/trip) and we have budget
            if three_q_avg > 5 and ctx.budget_left >= 150:
                # Get tomorrow's offer
                three_q_offer = ctx.offer("THREE_QUARTER")
                
                if three_q_offer is not None and three_q_offer.bookable:
                    # Use default boat (best in last 60 days)
                    boat = ctx.pick_boat("THREE_QUARTER", ctx.tomorrow)
                    actions.append(
                        Book(
                            three_q_offer.id,
                            reason=f"three_q bite hot ({three_q_avg:.1f} fish/trip)",
                            boat=boat,
                        )
                    )
            
            # Commit PTO for future weekends if we have days left
            # Look 14 days ahead for Friday departures (Fri = 5, wraps to Monday = 1)
            if ctx.pto_left >= 1:
                future_day = ctx.today.plus(14)
                if future_day.weekday == 5:  # Friday
                    # Commit for Friday and Monday
                    actions.append(CommitPTO(future_day.doy, reason="Friday fishing wrap"))
                    if ctx.pto_left >= 2:
                        actions.append(
                            CommitPTO(future_day.plus(3).doy, reason="Monday return")
                        )

        except Exception:
            pass

        return actions
