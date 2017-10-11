"""
Generic API Adapter
"""

from collections import namedtuple
import abc
import pandas as pd


Alerts = namedtuple('Alerts', ('open_alerts', 'alert_history'))


class ApiAdapter:
    """Adapter for all IApi implementations"""
    def __init__(self, creds, Api):
        self.api = Api(creds)

    def accounts(self):
        """Returns a list of accounts"""
        return self.api.request('accounts')

    def activity(self):
        """Returns activity history"""
        return self.api.request('activity')

    def balances(self):
        """Returns balances on accounts"""
        return self.api.request('balances')

    def push_notifications(self):
        """List any unshown alerts or trade notifications"""
        return self.api.request('pushNotifications')

    def orders(self):
        """List open orders"""
        return self.api.request('orders')

    def alerts(self):
        """List all allerts"""
        all_alerts = self.api.request('alerts')
        open_alerts = pd.DataFrame(all_alerts['open_alerts'])
        alert_history = pd.DataFrame(all_alerts['alert_history'])
        return Alerts(open_alerts=open_alerts, alert_history=alert_history)

    def exchanges(self):
        """Show accepted exchanges"""
        return self.api.request('exchanges')

    def markets(self, exchange):
        """List markets supported by exchange"""
        return self.api.request('markets', exchange_code=exchange)

    def history(self, exchange, market):
        """Market history"""
        return self.api.data(exchange=exchange, market=market,
                             data_type='history')

    def asks(self, exchange, market):
        """Asks"""
        return self.api.data(exchange=exchange, market=market,
                             data_type='asks')

    def bids(self, exchange, market):
        """Bids"""
        return self.api.data(exchange=exchange, market=market,
                             data_type='bids')

    def orders(self, exchange, market):
        """Orders"""
        return self.api.data(exchange=exchange, market=market,
                             data_type='orders')

    def news_feed(self):
        """Retrieve news feed"""
        dat = self.api.request('newsFeed')
        dat.timestamp = pd.to_datetime(dat.timestamp)
        dat.set_index('timestamp', inplace=True)
        return dat

    def order_types(self):
        """List supported order types"""
        dat = self.api.request('orderTypes')['data']
        return dict(order_types=pd.DataFrame.from_records(dat['order_types']),
                    price_types=pd.DataFrame.from_records(dat['price_types']))

    def refresh_balance(self):
        """Refreshes the balance backend"""
        return self.api.request('refreshBalance')

    def add_alert(self, exchange, market, price, note):
        """Add an alert"""
        return self.api.request('addAlert',
                                exch_code=exchange,
                                market_name=market,
                                alert_price=price,
                                alert_note=note)['notifications']

    def delete_alert(self, alert_id):
        """Delete an alert"""
        return self.api.request('deleteAlert',
                                alert_id=alert_id)['notifications']

    def add_order(self, auth_id, exch_id, mkt_id, order_type_id,
                  price_type_id, limit_price, stop_price, order_quantity):
        """Add an order
        ****UNTESTED!****
        """
        return self.api.request('addOrder',
                                auth_id=auth_id,
                                exch_id=exch_id,
                                mkt_id=mkt_id,
                                order_type_id=order_type_id,
                                price_type_id=price_type_id,
                                limit_price=limit_price,
                                stop_price=stop_price,
                                order_quantity=order_quantity)

    def cancel_order(self, order_id):
        """Cancel an order"""
        return self.api.request('cancelOrder', internal_order_id=order_id)

    def balance_history(self, date):
        """
        NB: the timestamp columns is the time when the account was last
            snapshot, not the time the balances were effectively refreshed
        :param date:    date str in format YYYY-MM-DD
        :return:        a view of the acccount balances as of the date provided
        """
        balhist = pd.DataFrame.from_records(
            self.api.request('balanceHistory',
                             date=date)['data']['balance_history'])
        if balhist.empty:
            return balhist
        acct = self.accounts()[['auth_id', 'exch_name']]
        return pd.merge(balhist, acct, on='auth_id', how='left')


class IApi:
    """Interface to an Api implementation"""
    def __init__(self, acct):
        self.api = acct.api
        self.secret = acct.secret
        self.endpoint = acct.endpoint

    @abc.abstractmethod
    def request(self, call, query=None, **args):
        """
        Generic interface to REST api
        :param method:  query name
        :param query:   dictionary of inputs
        :param json:    if True return the raw results in json format
        :param args:    keyword arguments added to the payload
        :return:
        """
        pass

    @abc.abstractmethod
    def data(self, exchange, market, data_type):
        """
        Common wrapper for data related queries
        :param exchange:
        :param market:
        :param data_type:
            currently supported are 'history', 'bids', 'asks', 'orders'
        :return:
        """
        pass
