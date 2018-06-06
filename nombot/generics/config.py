"""Configuration definition"""

from marshmallow import Schema, fields, post_load

from bors.generics.config import ConfSchema


class ApiEndpointConfSchema(Schema):
    """API endpoint configuration object"""
    rest = fields.Str()
    websocket = fields.Str()


class ApiCredConfSchema(Schema):
    """API credential configuration object"""
    name = fields.Str()
    apiKey = fields.Str()
    secret = fields.Str()


class ApiServiceConfSchema(Schema):
    """API service configuration object"""
    name = fields.Str(required=True)
    currencies = fields.List(fields.Str())
    credentials = fields.List(fields.Nested(ApiCredConfSchema))
    subscriptions = fields.Dict()
    exchanges = fields.List(fields.Str())
    endpoints = fields.Nested(ApiEndpointConfSchema())


class ApiConfSchema(Schema):
    """API configuration object"""
    calls = fields.Dict()
    services = fields.List(fields.Nested(ApiServiceConfSchema()))


class NomConfSchema(ConfSchema):
    """Root configuration schema"""
    currencies = fields.List(fields.Str())
    api = fields.Nested(ApiConfSchema())
