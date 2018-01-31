"""Trading strategies"""
import pandas as pd

from nombot.app.strategy import IStrategy


class OHLCV:
    """Implementation of OHLCV data (open, high, low, close, volume)"""
    history = pd.DataFrame()

    def __init__(self, hist_size):
        self.hist_size = hist_size

    def update(self, data):
        """Update the data using the latest information"""
        pass

    def dump(self):
        """Dump the data for the strategy pipeline"""
        pass


class OHLCVStrategy(IStrategy):
    """Strategy to supplement/act upon incoming data"""
    name = "ohlc_strategy"

    def __init__(self, hist_size=100):
        self._data = OHLCV(hist_size)
        self.hist_size = hist_size
        self.create_logger()

    def bind(self, context):
        """Bind actions to the strategy context for a given result"""
        self._data.update(context)

        # initialze supplemented data
        context["strategy"].update({
            "ohlc_hist_size": self.hist_size,
            "ohlc": self._data.dump(),
            })

        return context
