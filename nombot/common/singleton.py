"""A library for implementing a Singleton metaclass"""


class Singleton(type):
    """
    Define an instance operation that lets clients access its unique instance
    """
    def __init__(cls, name, bases, attrs, **kwargs):  # pylint: disable=unused-argument
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance
