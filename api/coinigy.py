"""Coinigy API Facade
"""

import numpy as np
import pandas as pd
import requests


class Coinigy:
    """
        This class implements coinigy's REST api as documented in the
        documentation available at:
        https://github.com/coinigy/api
    """
    name = "coinigy"

    paths = {
        "accounts": "data"
    }

    def __init__(self, acct):
        """Launched by Api when we're ready to connect"""
        self.api = acct.api
        self.secret = acct.secret
        self.endpoint = acct.endpoint
        self.req = requests.Session()

    def call(self, method, query=None, json=True, **args):
        """
        Generic interface to REST api
        :param method:  query name
        :param query:   dictionary of inputs
        :param json:    if True return the raw results in json format
        :param args:    keyword arguments added to the payload
        :return:
        """
        url = '{endpoint}/{method}'.format(
            endpoint=self.endpoint, method=method)

        payload = {'X-API-KEY': self.api, 'X-API-SECRET': self.secret}
        payload.update(**args)

        if query is not None:
            payload.update(query)

        res = self.req.post(url, data=payload)

        if res.status_code > 299:
            print(f"URL: {url}")
            print(f"Payload: {payload}")
            print(f"STATUS: {res.status_code}")
            print(f"RESPONSE: {res.text}")
            return
        elif 'error' in res.json().keys():
            print(res.json()['error'])
            return

        if json:
            return res.json()
        return pd.DataFrame(res.json()['data'])


    def data(self, exchange, market, data_type):
        """
        Common wrapper for data related queries
        :param exchange:
        :param market:
        :param data_type:
            currently supported are 'history', 'bids', 'asks', 'orders'
        :return:
        """
        data = self.call('data',
                         exchange_code=exchange,
                         exchange_market=market,
                         type=data_type)['data']
        res = dict()

        for key in ['history', 'bids', 'asks']:
            if key in data.keys():
                dat = pd.DataFrame.from_records(data[key])
                if 'price' in dat.columns:
                    dat.price = dat.price.astype(np.float)
                if 'quantity' in dat.columns:
                    dat.quantity = dat.quantity.astype(np.float)
                if 'total' in dat.columns:
                    dat.total = dat.total.astype(np.float)
                if 'time_local' in dat.columns:
                    dat.time_local = pd.to_datetime(dat.time_local)
                    dat.set_index('time_local', inplace=True)
                if 'type' in dat.columns:
                    dat.type = dat.type.astype(str)
                if not dat.empty:
                    dat['base_ccy'] = data['primary_curr_code']
                    dat['counter_ccy'] = data['secondary_curr_code']

                res[key] = dat

        return res

    # Custom methods

    def push_notifications(self):
        """List any unshown alerts or trade notifications"""
        return self.api.call('pushNotifications')

    def alerts(self):
        """List all allerts"""
        all_alerts = self.api.call('alerts')
        open_alerts = pd.DataFrame(all_alerts['open_alerts'])
        alert_history = pd.DataFrame(all_alerts['alert_history'])
        return {"open_alerts": open_alerts, "alert_history": alert_history}

    def markets(self, exchange):
        """List markets supported by exchange"""
        return self.api.call('markets', exchange_code=exchange)

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

    def allorders(self, exchange, market):
        """Orders"""
        return self.api.data(exchange=exchange, market=market,
                             data_type='orders')

    def news_feed(self):
        """Retrieve news feed"""
        dat = self.api.call('newsFeed')
        dat.timestamp = pd.to_datetime(dat.timestamp)
        dat.set_index('timestamp', inplace=True)
        return dat

    def order_types(self):
        """List supported order types"""
        dat = self.api.call('orderTypes')['data']
        return dict(order_types=pd.DataFrame.from_records(dat['order_types']),
                    price_types=pd.DataFrame.from_records(dat['price_types']))

    def refresh_balance(self):
        """Refreshes the balance backend"""
        return self.api.call('refreshBalance')

    def add_alert(self, exchange, market, price, note):
        """Add an alert"""
        return self.api.call('addAlert',
                             exch_code=exchange,
                             market_name=market,
                             alert_price=price,
                             alert_note=note)['notifications']

    def delete_alert(self, alert_id):
        """Delete an alert"""
        return self.api.call('deleteAlert',
                             alert_id=alert_id)['notifications']

    def add_order(self, auth_id, exch_id, mkt_id, order_type_id,
                  price_type_id, limit_price, stop_price, order_quantity):
        """Add an order
        ****UNTESTED!****
        """
        return self.api.call('addOrder',
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
        return self.api.call('cancelOrder', internal_order_id=order_id)

    def balance_history(self, date):
        """
        NB: the timestamp columns is the time when the account was last
            snapshot, not the time the balances were effectively refreshed
        :param date:    date str in format YYYY-MM-DD
        :return:        a view of the acccount balances as of the date provided
        """
        balhist = pd.DataFrame.from_records(
            self.api.call('balanceHistory',
                          date=date)['data']['balance_history'])
        if balhist.empty:
            return balhist
        acct = self.call('accounts')[['auth_id', 'exch_name']]
        return pd.merge(balhist, acct, on='auth_id', how='left')
