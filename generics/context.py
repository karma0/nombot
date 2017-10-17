"""Contexts for component integrations"""

from marshmallow import Schema, fields

from generics.config import ApiServiceConfSchema


class ApiContext(Schema):
    """Used for sharing information about a single API between instances"""
    conf = fields.Nested(ApiServiceConfSchema())

    class Meta:
        """ApiContext metaparameters"""
        strict = True


class ResultSchema(Schema):
    """Generic API result (inherit to use a schema for result creation)"""
    pass


class StrategyContextSchema(Schema):
    """Context to share information among Strategies"""
    api_contexts = fields.List(
        fields.Nested(ApiContext(exclude="credentials")))
    result = fields.Nested(ResultSchema())
