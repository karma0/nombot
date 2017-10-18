"""Contexts for component integrations"""

from marshmallow import Schema, fields

from generics.config import ApiServiceConfSchema
from generics.exchange import ApiFacadeSchema, ResultSchema


class ApiContextSchema(Schema):
    """Used for sharing information about a single API between instances"""
    name = fields.Str(required=True)
    cls = fields.Nested(ApiFacadeSchema())
    conf = fields.Nested(ApiServiceConfSchema())
    calls = fields.List(fields.Str())
    currencies = fields.List(fields.Str())
    shared = fields.Dict()
    callback = fields.Function()

    class Meta:
        """ApiContext metaparameters"""
        strict = True


class StrategyContextSchema(Schema):
    """Context to share information among Strategies"""
    api_contexts = fields.List(
        fields.Nested(ApiContextSchema(exclude="credentials")))
    result = fields.Nested(ResultSchema())
