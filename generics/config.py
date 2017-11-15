"""Configuration definition"""

from marshmallow import Schema, fields, post_load


class Conf:
    """Loads a sane configuration"""
    def __init__(self, **config):
        self.conf = config

    def get(self, *args, **kwargs):
        """Get something"""
        return self.conf.get(*args, **kwargs)


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
    credentials = fields.Nested(ApiCredsConfSchema())
    subscriptions = fields.Dict()
    exchanges = fields.List(fields.Str())
    endpoints = fields.Nested(ApiEndpointConfSchema())


class ApiConfSchema(Schema):
    """Log configuration object"""
    calls = fields.Dict()
    services = fields.List(fields.Nested(ApiServiceConfSchema()))


class LogConfSchema(Schema):
    """Log configuration object"""
    level = fields.Str(required=True)
    modules = fields.Dict(
        fields.Nested('self',
                      many=True,
                      exclude=('modules',),
                      default=None)
        )


class ConfSchema(Schema):
    """Root configuration schema"""
    currencies = fields.List(fields.Str())
    logger = fields.Nested(LogConfSchema())
    api = fields.Nested(ApiConfSchema())

    @post_load
    def make_conf(self, data):  # pylint: disable=R0201
        """Generate a configuration object"""
        return Conf(**data)

    class Meta:
        """Make sure that we bail if we can't parse"""
        strict = True
