"""
Generic response types
"""

from marshmallow import fields, Schema, post_load
from api.response import Result, RESPONSE_MAP


class DefaultSchema(Schema):
    """Default schema parser"""
    MessageType = fields.Str(required=True)

    @post_load
    def generate_obj(self, data):  # pylint: disable=no-self-use
        """Generate new schema based on message type"""
        return RESPONSE_MAP[data["MessageType"]].dump(data["Data"])

    class Meta:
        """Data field is dyanamic type"""
        additional = ("Data",)


RESPONSE_MAP["default"] = DefaultSchema()


class CommonResponseSchema(Schema):
    """Common response schema"""
    errors = fields.Dict()

    def get_result(self, data):  # pylint: disable=no-self-use
        """
        Retrieve the result from the parsed object
          ~~ Override this to match your API. ~~
        """
        return data.get("result", "")


class ResponseSchema(CommonResponseSchema):
    """Schema defining the data structure the API will respond with"""
    @post_load
    def populate_data(self, data):
        """Parse the incoming schema"""
        print(f"""\n\nAPI RESP DATA!{self.context["callname"]}!{data}""")
        if "errors" in data:
            return Result(errors=data["errors"])
        callname = self.context.get("callname")
        result = {
            "callname": callname,
            "result": RESPONSE_MAP[callname]  # type: ignore
                      .dump(self.get_result(data))  # NOQA
        }
        return Result(**result)

    class Meta:
        """Stricty"""
        strict = True
        additional = ("result",)


class WSResponseSchema(CommonResponseSchema):
    """
    Schema defining the data structure from published messages on the websock
    """
    @post_load
    def populate_data(self, data):
        """Parse the incoming schema"""
        if "errors" in data:
            return Result(errors=data["errors"])

        # pylint: disable=E1101
        channel = self.context.get("channel")
        print(f"""\n\nRESP DATA!{channel}!{data}""")
        try:
            sch = RESPONSE_MAP[channel]
        except KeyError:
            sch = RESPONSE_MAP["default"]
        sch.dump(self.get_result(data))
        result = {
            "channel": channel,
            "result": sch.dump(self.get_result(data))  # NOQA
        }
        return Result(**result)
