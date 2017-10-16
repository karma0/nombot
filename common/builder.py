"""
Build the context and pipeline; manage the API
"""
from api.base import ApiMetaAdapter
from common.context import build_context


class AppBuilder:
    """Class that assembles and runs the application"""
    def __init__(self, api_classes, strategy):
        self.api = ApiMetaAdapter(api_classes)
        self.strat = strategy

    def run(self):
        """Run the queries and middleware pipeline"""
        # call run with receive callback function
        self.api.run(self.receive)

    def receive(self, topic, results):
        """Pass an API result down the pipeline"""
        print(f"topic: {topic}; results: {results}")
        data = {}
        data[topic] = results
        self.strat.execute(build_context(data))

    def shutdown(self):
        """Shut it down"""
        self.api.shutdown()
        self.strat.shutdown()
