"""Context(s) for APIs to use"""

from marshmallow import Schema


class ApiContext(Schema):
    """Used for sharing information about a single API between instances"""
    class Meta:
        additional = (
            "test",
            "secret"
        )
