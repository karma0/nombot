"""Configuration definition"""

from marshmallow import Schema, fields, post_load

from bors.generics.config import Conf, ConfSchema


class ApiEndpointConfSchema(Schema):
    """API endpoint configuration object"""
    rest = fields.Str()
    websocket = fields.Str()


class ApiCredsConfSchema(Schema):
    """API credentials configuration object"""
    apikey = fields.Str()
    secret = fields.Str()


class ApiServiceConfSchema(Schema):
    """API service configuration object"""
    name = fields.Str(required=True)
    currencies = fields.List(fields.Str())
    credentials = fields.Nested(ApiCredsConfSchema())
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
