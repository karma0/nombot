"""
Build the context and pipeline; manage the API
"""
from core.config import Conf
from api.base import ApiMetaAdapter
from generics.context import ApiContextSchema, StrategyContextSchema


class AppBuilder:
    """Class that assembles and runs the application"""
    def __init__(self, api_classes, strategy):
        self.conf = Conf()
        self.api_contexts = {}  # type: dict

        for api in self.conf.services_by_name.keys():
            for api_cls in api_classes:
                if api_cls.name == api:
                    self.api_contexts[api] = \
                        self.create_api_context(api_cls)

        self.api = ApiMetaAdapter(self.api_contexts)
        self.strat = strategy

    def create_api_context(self, cls):
        """Create and return an API context"""
        sch = ApiContextSchema()
        return sch.load({
            "name": cls.name,
            "cls": cls,
            "conf": self.conf.get_api(cls.name),
            "calls": self.conf.get_api_calls(),
            "currencies": self.conf.get_currencies(),
            "scratch": {},  # Used per-API to monitor state
            "callback": self.receive
            })

    def run(self):
        """Run the queries and middleware pipeline"""
        # call run with receive callback function
        self.api.run()

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
