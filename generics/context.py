"""Contexts for component integrations"""

from multiprocessing import Lock

from marshmallow import Schema, fields

from generics.config import ApiServiceConfSchema
from generics.exchange import ResultSchema


class ApiContextSchema(Schema):
    """Used for sharing information about a single API between instances"""
    name = fields.Str(required=True)
    conf = fields.Nested(ApiServiceConfSchema())
    calls = fields.List(fields.Str())
    currencies = fields.List(fields.Str())
    shared = fields.Dict()
    callback = fields.Function()
    lock = Lock()

    class Meta:
        """ApiContext metaparameters"""
        strict = True
        additional = ("cls", "inst")


class StrategyContextSchema(Schema):
    """Context to share information among Strategies"""
    api_contexts = fields.Dict()
    api_context = fields.Nested(ApiContextSchema())
    result = fields.Nested(ResultSchema())
