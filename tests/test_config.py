#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Test the `bors` configuration overrides"""


import unittest
from copy import deepcopy

from nombot.app.config import NomAppConf
from nombot.generics.config import NomConfSchema


DEFAULT_TEST_CONFIG = {
    "currencies": ["BTC", "USD", "USDT"],
    "api": {
        "ratelimit": 1,
        "services": [
            {
                "name": "test_service",
                "currencies": ["BTC", "ETH", "XRP"],
                "credentials": [
                    {
                        "name": "test_api_name",
                        "apiKey": "test_key",
                        "secret": "test_secret",
                    },
                ],
                "subscriptions": {"TICKER_X": "ticker"},
                "exchanges": ["bittrex", "coinbase"],
                "endpoints": {
                    "rest": "rest_url",
                    "websocket": "sock_url",
                },
            },
        ],
        "calls": {"test_call1": {"AAA": 123}},
    },
    "log_level": "INFO",
}


class TestConfig(unittest.TestCase):
    """Tests for nombot configuration parser"""

    def setUp(self):
        """Set up test fixtures, if any"""
        self.config = deepcopy(DEFAULT_TEST_CONFIG)

    def test_schema(self):
        """Test the schema definition"""
        l_config = deepcopy(self.config)
        del l_config["api"]["ratelimit"]  # bors field unused by nombot
        config = NomConfSchema().load(l_config).data["conf"]
        self.assertDictEqual(config, l_config)

    def test_config_load(self):
        """Test the load of a configuration"""
        config = NomAppConf(self.config).raw_conf
        self.assertDictEqual(config, self.config)


class TestCurrencies(unittest.TestCase):
    """Tests for nombot currency parser"""

    def setUp(self):
        """Set up test fixtures, if any"""
        self.config = deepcopy(DEFAULT_TEST_CONFIG)

    def test_get_currencies(self):
        """Test the schema definition"""
        config = NomAppConf(self.config)
        self.assertListEqual(config.get_currencies(),
                             self.config["currencies"])

    def test_get_service_currencies(self):
        """Test the schema definition"""
        config = NomAppConf(self.config)

        expected_curr = self.config["api"]["services"][0]["currencies"] + \
            self.config["currencies"]
        result_curr = config.get_currencies("test_service")

        self.assertListEqual(expected_curr, result_curr)

    def test_global_without_service(self):
        """If no service currencies, return only global"""
        l_config = deepcopy(self.config)
        del l_config["api"]["services"][0]["currencies"]
        config = NomAppConf(l_config)

        expected_curr = self.config["currencies"]
        result_curr = config.get_currencies("test_service")

        self.assertListEqual(expected_curr, result_curr)

    def test_global_with_only_service(self):
        """If no global currencies, return only service"""
        l_config = deepcopy(self.config)
        del l_config["currencies"]
        config = NomAppConf(l_config)

        expected_curr = self.config["api"]["services"][0]["currencies"]
        result_curr = config.get_currencies("test_service")

        self.assertListEqual(expected_curr, result_curr)

    def test_no_currencies(self):
        """If no currencies, return empty list"""
        l_config = deepcopy(self.config)
        del l_config["currencies"]
        del l_config["api"]["services"][0]["currencies"]
        config = NomAppConf(l_config)

        expected_curr = []  # type: list
        result_curr = config.get_currencies("test_service")

        self.assertListEqual(expected_curr, result_curr)
