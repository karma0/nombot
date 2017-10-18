"""
Build the context and pipeline; manage the API
"""
from core.config import Conf
from api.base import ApiMetaAdapter
from generics.context import ApiConfContextSchema, StrategyContextSchema


class AppBuilder:
    """Class that assembles and runs the application"""
    def __init__(self, api_classes, strategy):
        self.api = ApiMetaAdapter(api_classes)
        self.strat = strategy
        self.api_contexts = {}  # type: dict

        self.conf = Conf()
        for api in self.conf.services_by_name.keys():
            self.api_contexts[api] = self.create_api_context(api)

    def create_api_context(self, name):
        """Create and return an API context"""
        sch = ApiConfContextSchema()
        return sch.load({
            "conf": self.conf.get_api(name),
            "calls": self.conf.get_api_calls(),
            "currencies": self.conf.get_currencies()
            })

    def run(self):
        """Run the queries and middleware pipeline"""
        # call run with receive callback function
        self.api.run(self.receive)

    def receive(self, topic, results):
        """Pass an API result down the pipeline"""
        print(f"topic: {topic}; results: {results}")
        data = {
            "result": results,
            "api_contexts": self.api_contexts
        }
        self.strat.execute(StrategyContextSchema.load(data))

    def shutdown(self):
        """Shut it down"""
        self.api.shutdown()
        self.strat.shutdown()
