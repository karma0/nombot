"""Contexts for component integrations"""

from marshmallow import fields

from bors.generics.context import ApiContextSchema, StrategyContextSchema

from nombot.generics.config import ApiServiceConfSchema, ApiCredConfSchema


class NomApiContextSchema(ApiContextSchema):
    """Used for sharing information about a single API between instances"""
    conf = fields.Nested(ApiServiceConfSchema())  # API's config
    credentials = fields.List(fields.Nested(ApiCredConfSchema()))
    currencies = fields.List(fields.Str())  # List of currencies to monitor


class NomStrategyContextSchema(StrategyContextSchema):
    """Context to share information among strategies"""
    api_context = fields.Nested(NomApiContextSchema())  # API's context
