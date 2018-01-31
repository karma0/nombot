"""Contexts for component integrations"""

from multiprocessing import Lock

from marshmallow import Schema, fields

from nombot.generics.config import ApiServiceConfSchema


class ApiContextSchema(Schema):
    """Used for sharing information about a single API between instances"""
    name = fields.Str(required=True)  # Name of the API
    conf = fields.Nested(ApiServiceConfSchema())  # API's config
    calls = fields.Dict()  # API calls list
    currencies = fields.List(fields.Str())  # List of currencies to monitor
    shared = fields.Dict()  # API-level shared information
    callback = fields.Function()  # Callback to drop a result on the pipeline
    lock = Lock()

    class Meta:
        """ApiContext metaparameters"""
        strict = True
        additional = ("cls", "inst")


class StrategyContextSchema(Schema):
    """Context to share information among Strategies"""
    api_contexts = fields.Dict()
    api_context = fields.Nested(ApiContextSchema())

    class Meta:
        """Strategy Context metaparameters"""
        # Where the meat of strategy data is stored
        additional = ("strategy", "result")
        strict = True
