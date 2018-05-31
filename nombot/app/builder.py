"""
Build the context and pipeline; manage the API
"""
from bors.app.builder import AppBuilder

from nombot.generics.context import NomApiContextSchema
from nombot.generics.context import NomStrategyContextSchema


class NomAppBuilder(AppBuilder):
    """Class that assembles and runs the application"""
    api_context_schema = NomApiContextSchema
    strategy_context_schema = NomStrategyContextSchema

    def create_api_context(self, cls):
        """Create and return an API context"""
        return self.api_context_schema().load({
            "name": cls.name,
            "conf": self.conf.get_api_service(cls.name),
            "calls": self.conf.get_api_calls(),
            "currencies": self.conf.get_currencies(cls.name),
            "credentials": self.conf.get_api_credentials(cls.name),
            "log_level": self.conf.get_log_level(),
            "cls": cls,
            "shared": {},
            "inst": [],
            "callback": self.receive,
        })
