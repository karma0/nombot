"""
Build the context and pipeline; manage the API
"""
from api.base import ApisAdapter
from common.context import build_context


class AppBuilder:
    """Class that assembles and runs the application"""
    def __init__(self, api_classes, strategy):
        self.api = ApisAdapter(api_classes)
        self.strat = strategy

    def run(self):
        """Run the queries and middleware pipeline"""
        # call run with receive callback function
        self.api.run(self.receive)

    def receive(self, results):
        """Pass an API result down the pipeline"""
        self.strat.execute(build_context(results))

    def shutdown(self):
        """Shut it down"""
        self.api.shutdown()
        self.strat.shutdown()
