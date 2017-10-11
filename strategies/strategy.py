"""
Define a family of algorithms, encapsulate each one, and make them
interchangeable. Strategy lets the algorithm vary independently from
clients that use it.
"""

import abc


class Strategy:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self):
        self._strategies = []  # type: list

    def add_strategy(self, strategy):
        """Add strategy to the list of middlewares"""
        self._strategies.append(strategy)

    def execute(self, context):
        """
        Execute the strategies on the given context
        """
        for strat in self._strategies:
            context = strat.bind(context)
        return context


class IStrategy(metaclass=abc.ABCMeta):
    """
    Declare an interface common to all supported algorithms. Context
    uses this interface to call the algorithm defined by a
    ConcreteStrategy.
    """
    @abc.abstractmethod
    def bind(self, context):
        """Bind to the context"""
        pass

    @abc.abstractmethod
    def shutdown(self):
        """Use this to tie up any loose ends"""
        pass
