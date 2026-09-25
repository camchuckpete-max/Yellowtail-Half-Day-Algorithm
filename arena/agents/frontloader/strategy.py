"""Initial strategy: do nothing until you write one. Replace this whole file via submit_strategy."""
from arena.api.ctx import Strategy, Book, CommitPTO


class Strategy(Strategy):
    name = "no strategy yet"

    def describe(self):
        return "No strategy yet: books nothing."

    def decide(self, ctx):
        return []
