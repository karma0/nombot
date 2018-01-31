"""
Generic API Interface, mixin, and request maps/types
"""

from marshmallow import fields, Schema, post_load
from nombot.api.request import Request, REQUEST_MAP


class RequestSchema(Schema):
    """Schema defining the data structure the API can be called with"""
    callname = fields.Str(required=True)
    payload = fields.Dict()

    @post_load
    def make_request(self, data):
        """Parse the outgoing schema"""
        callname = self.context.get("callname")
        try:
            payload = REQUEST_MAP[callname].dump(data)  # type: ignore
        except AttributeError:
            payload = None

        request = {
            "callname": callname,
            "payload": payload
        }
        return Request(**request)

    class Meta:
        """Stricty"""
        strict = True
