"""Configuration definition"""

from marshmallow import Schema, fields


class ApiEndpointConfSchema(Schema):
    rest = fields.Str()
    websocket = fields.Str()


class ApiCredsConfSchema(Schema):
    apikey = fields.Str()
    secret = fields.Str()


class ApiServiceConfSchema(Schema):
    name = fields.Str(required=True)
    credentials = fields.Nested(ApiCredsConfSchema())
    subscriptions = fields.List()
    exchanges = fields.List()
    endpoints = fields.Nested(ApiEndpointConfSchema())


class ApiConfSchema(Schema):
    calls = fields.List()
    services = fields.Nested(ApiServiceConfSchema(), many=True)


class LogConfSchema(Schema):
    level = fields.Str(required=True)
    modules = fields.Nested('self',
                            many=True,
                            exclude=('modules',),
                            default=None)


class ConfSchema(Schema):
    """Root configuration schema"""
    currencies = fields.List()
    logger = fields.Nested(LogConfSchema())
