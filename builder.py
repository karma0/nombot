"""
Build the context and pipeline; manage the API
"""
from api.base import ApiAdapter
from context import build_context


class AppBuider:
    def __init__(self, conf, Api, strategy):
        self.conf = conf
        self.api = ApiAdapter(self.conf.get_credentials(), Api,
                              strategy.calls)
        self.mw = Middleware(strategy)

    def run(self):
        """Run the queries and middleware pipeline"""
        self.api.run(self.mw.receive)


class Middleware:
    def __init__(self, strat):
        self.strat = strat

    def receive(self, results):
        self.strategy.execute(build_context())
