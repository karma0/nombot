"""Coinigy API Facade
"""

from marshmallow import fields, pre_load

import numpy as np  # pylint: disable=import-error
import pandas as pd  # pylint: disable=import-error

from app.log import LoggerMixin
from api.requestor import Req
from api.base import IApi, ApiErrorMixin
from api.schema import ResponseSchema
from api.websock import SockMixin, SockChannel

from generics.exchange import NotificationSchema


class CoinigyResponseSchema(ResponseSchema):
    """Schema defining how the API will respond"""
    notifications = fields.List(fields.Nested(NotificationSchema()))
    err_num = fields.Str()
    err_msg = fields.Str()

    @pre_load
    def combine_errors(self, in_data):
        """Convert the error to the expected output"""
        if "err_num" in in_data:
            in_data["errors"] = dict()
            in_data["errors"][in_data["err_num"]] = in_data["err_msg"]

    def get_result(self, data):
        """Return the actual result data"""
        return data.get("data", "")

    class Meta:
        """Add 'data' field"""
        strict = True
        additional = ("data",)


class Coinigy(IApi, ApiErrorMixin, LoggerMixin, SockMixin):
    """
        This class implements coinigy's REST api as documented in the
        documentation available at:
        https://github.com/coinigy/api
    """
    name = "coinigy"

    def __init__(self, context):
        """Launched by Api when we're ready to connect"""
        self.result_schema = CoinigyResponseSchema

        # ApiContext
        self.context = context
        self.payload = {
            'X-API-KEY': self.context["conf"]["credentials"]["apikey"],
            'X-API-SECRET': self.context["conf"]["credentials"]["secret"],
        }

        # Web request pool
        self.req = Req().get_req_obj()

        self.create_logger()
        self.log.debug(f"Starting API Facade {self.name}")

        self.subscribed_chans = None

    def call(self, method, query=None, **args):
        """
        Generic interface to REST api
        :param method:  query name
        :param query:   dictionary of inputs
        :param args:    keyword arguments added to the payload
        :return:
        """
        url = '{endpoint}/{method}'.format(
            endpoint=self.context["conf"]["endpoints"]["rest"],
            method=method)

        payload = self.payload.copy()
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
        self.sock.emitack("accounts", None, self.get_accounts)

    def get_accounts(self, eventname, error, data):
        self.context["scratch"]["accounts"] = data["data"]

    def get_channels(self, eventname, error, data):
        """
        Dynamically generate the websocket channels based on exchange and
        currency configurations and what the server reports available.
        """
        if error:
            raise Exception(error)

        self.context["scratch"]["all_channels"] = {}
        for chan in data[0]:
            self.context["scratch"]["all_channels"][chan["channel"]] = False

        for exch in self.context["conf"]["exchanges"]:
            for curr1 in self.context["currencies"]:
                for curr2 in self.context["currencies"]:
                    for ortra in ["order", "trade"]:
                        for chan in [
                                f"{ortra}-{exch}--{curr1}--{curr2}".upper(),
                                f"{ortra}-{exch}--{curr2}--{curr1}".upper()
                        ]:
                            if chan in self.context.all_channels:
                                self.context.all_channels[chan] = True
        self.subscribed_chans = \
            [k for k, v in self.context.all_channels.items() if v]

        for chan in self.subscribed_chans:
            if chan.startswith("ORDER"):
                restype = "order"
            elif chan.startswith("TRADE"):
                restype = "tradeMessage"
            self.channels.append(
                SockChannel(chan, restype, self.context.callback))

        # SockMixin
        self.connect_channels()

    # Custom methods

    def alerts(self):
        """List all allerts"""
        all_alerts = self.call('alerts')
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
        return self.data(data_type='asks')

    def bids(self):
        """Bids"""
        return self.data(data_type='bids')

    def allorders(self):
        """Orders"""
        return self.data(data_type='orders')

    def news_feed(self):
        """Retrieve news feed"""
        dat = self.call('newsFeed')
        dat.timestamp = pd.to_datetime(dat.timestamp)
        dat.set_index('timestamp', inplace=True)
        return dat

    def order_types(self):
        """List supported order types"""
        dat = self.call('orderTypes')['data']
        return dict(order_types=pd.DataFrame.from_records(dat['order_types']),
                    price_types=pd.DataFrame.from_records(dat['price_types']))

    def refresh_balance(self):
        """Refreshes the balance backend"""
        return self.call('refreshBalance')

    def add_alert(self, price, note):
        """Add an alert"""
        self.check_missing_parameter("add_alert", "exchange")
        self.check_missing_parameter("add_alert", "market")

        return self.call('addAlert',
                         exch_code=self.exchange,
                         market_name=self.market,
                         alert_price=price,
                         alert_note=note)['notifications']

    def delete_alert(self, alert_id):
        """Delete an alert"""
        return self.call('deleteAlert',
                         alert_id=alert_id)['notifications']

    def add_order(self, auth_id, order_type_id, price_type_id,
                  limit_price, stop_price, order_quantity):
        """Add an order
        ****UNTESTED!****
        """
        self.check_missing_parameter("add_order", "exchange")
        self.check_missing_parameter("add_order", "market")

        return self.call('addOrder',
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
        return self.call('cancelOrder', internal_order_id=order_id)

    def balance_history(self, date):
        """
        NB: the timestamp columns is the time when the account was last
            snapshot, not the time the balances were effectively refreshed
        :param date:    date str in format YYYY-MM-DD
        :return:        a view of the acccount balances as of the date provided
        """
        balhist = pd.DataFrame.from_records(
            self.call('balanceHistory',
                      date=date)['data']['balance_history'])
        if balhist.empty:
            return balhist
        acct = self.call('accounts')[['auth_id', 'exch_name']]
        return pd.merge(balhist, acct, on='auth_id', how='left')
