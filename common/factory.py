"""
Define an interface for creating an object, but let subclasses decide
which class to instantiate. Factory Method lets a class defer
instantiation to subclasses.
"""

import abc


class Creator(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods
    """
    Declare the factory method, which returns an object of type Product.
    Creator may also define a default implementation of the factory
    method that returns a default ConcreteProduct object.
    Call the factory method to create a Product object.
    """
    def __init__(self, *args, **kwargs):
        self.product = self._factory_method(*args, **kwargs)

    @abc.abstractmethod
    def _factory_method(self, *args, **kwargs):
        pass


class Product(metaclass=abc.ABCMeta):  # pylint: disable=too-few-public-methods
    """Define the interface of objects the factory method creates."""
    @abc.abstractmethod
    def interface(self):
        """Implement the interface for the object"""
        pass


class BasicFactory(Creator):
    """Generator of adapters"""
    def __init__(self, adapter, *args, **kwargs):
        self.adapter = adapter
        super().__init__(self, *args, **kwargs)

    def _factory_method(self, *args, **kwargs):
        return self.adapter()
