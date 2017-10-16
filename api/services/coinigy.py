"""Coinigy API Facade
"""

import json
import numpy as np  # pylint: disable=import-error
import pandas as pd  # pylint: disable=import-error

from collections import namedtuple

from common.log import LoggerMixin
from api.requestor import Req
from api.base import IApi, ApiErrorMixin
from api.websock import SockMixin, SockChannel


class Coinigy(IApi, ApiErrorMixin, LoggerMixin, SockMixin):
    """
        This class implements coinigy's REST api as documented in the
        documentation available at:
        https://github.com/coinigy/api
    """
    name = "coinigy"
    endpoint = "https://api.coinigy.com/api/v1"
    wsendpoint = "wss://sc-02.coinigy.com/socketcluster/"

    # A list of paths to the data for parsing
    paths = {
        "default": "data"
    }

    result_types = {
        "accountMessage": namedtuple("accountMessage", (
            "Data",
            "MessageType"
            )),
        "Notification": namedtuple("Notification", (
            "message",
            "message_vars",
            "notification_id",
            "pinned",
            "sound",
            "sound_id",
            "sound_override",
            "style",
            "time",
            "title",
            "title_vars",
            "type"
            ))
    }

    def __init__(self, context, exchange=None, market=None):
        """Launched by Api when we're ready to connect"""
        self.creds = { # used by the webservice API
            "apiKey": context.creds.api,
            "apiSecret": context.creds.secret
        }
        # Used by the REST API
        self.secret = context.creds.secret
        self.api = context.creds.api

        self.context = context
        self.req = Req().get_req_obj()

        self.exchange = exchange
        self.market = market
        self.create_logger()

    def call(self, method, query=None, **args):
        """
        Generic interface to REST api
        :param method:  query name
        :param query:   dictionary of inputs
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
            self.log.error(f"URL: {url}")
            self.log.error(f"Payload: {payload}")
            self.log.error(f"STATUS: {res.status_code}")
            self.log.error(f"RESPONSE: {res.text}")
            return
        elif 'error' in res.json().keys():
            self.log.error(res.json()['error'])
            return

        return res.json()

    def data(self, data_type):
        """
        Common wrapper for data related queries
        :param data_type:
            currently supported are 'history', 'bids', 'asks', 'orders'
        :return:
        """
        self.check_missing_parameter(data_type, "exchange")
        self.check_missing_parameter(data_type, "market")

        data = self.call('data', type=data_type)['data']
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

    def on_ws_connect(self):
        """
        Called by the websocket mixin
        """
        self.sock.emitack("channels", None, self.get_channels)

    def get_channels(self, eventname, error, data):
        """
        Dynamically generate the websocket channels based on exchange and
        currency configurations and what the server reports available.
        """
        if error:
            raise Exception(error)
        #try:
        #    data = json.dumps(jsondata)
        #except:
        #    self.log.critical("Could not parse json from websocket")

        self.all_chans = {}
        for chan in data[0]:
            self.all_chans[chan["channel"]] = False

        for exch in self.context["conf"]["exchanges"]:
            for curr1 in self.context["conf"]["currencies"]:
                for curr2 in self.context["conf"]["currencies"]:
                    for ortra in ["order", "trade"]:
                        for chan in [
                            f"{ortra}-{exch}--{curr1}--{curr2}".upper(),
                            f"{ortra}-{exch}--{curr2}--{curr1}".upper()
                        ]:
                            if chan in self.all_chans:
                                self.all_chans[chan] = True
        self.subscribed_chans = [k for k, v in self.all_chans.items() if v]

        for chan in self.subscribed_chans:
            if chan.startswith("ORDER"):
                restype = "order"
            elif chan.startswith("TRADE"):
                restype = "tradeMessage"
            self.channels.append(
                    SockChannel(chan, restype, self.context.callback))

        self.connect_channels()


    # Custom methods

    def alerts(self):
        """List all allerts"""
        all_alerts = self.api.call('alerts')
        open_alerts = pd.DataFrame(all_alerts['open_alerts'])
        alert_history = pd.DataFrame(all_alerts['alert_history'])
        return {"open_alerts": open_alerts, "alert_history": alert_history}

    def markets(self):
        """List markets supported by exchange"""
        self.check_missing_parameter("markets", "exchange")
        return self.call('markets', exchange_code=self.exchange)

    def history(self):
        """Market history"""
        return self.data(data_type='history')

    def asks(self):
        """Asks"""
        return self.api.data(data_type='asks')

    def bids(self):
        """Bids"""
        return self.api.data(data_type='bids')

    def allorders(self):
        """Orders"""
        return self.api.data(data_type='orders')

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

    def add_alert(self, price, note):
        """Add an alert"""
        self.check_missing_parameter("add_alert", "exchange")
        self.check_missing_parameter("add_alert", "market")

        return self.api.call('addAlert',
                             exch_code=self.exchange,
                             market_name=self.market,
                             alert_price=price,
                             alert_note=note)['notifications']

    def delete_alert(self, alert_id):
        """Delete an alert"""
        return self.api.call('deleteAlert',
                             alert_id=alert_id)['notifications']

    def add_order(self, auth_id, order_type_id, price_type_id,
                  limit_price, stop_price, order_quantity):
        """Add an order
        ****UNTESTED!****
        """
        self.check_missing_parameter("add_order", "exchange")
        self.check_missing_parameter("add_order", "market")

        return self.api.call('addOrder',
                             auth_id=auth_id,
                             exch_id=self.exchange,
                             mkt_id=self.market,
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
