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
    def __init__(self, acct):
        self.api = acct.api
        self.secret = acct.secret
        self.endpoint = acct.endpoint
        self.req = requests.Session()

    def request(self, method, query=None, json=False, **args):
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
        data = self.request('data',
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
