import json
import urllib
import os
import time

from unittest import TestCase
from mock import Mock, patch
from radarrelay import radarrelay
from ccxt.base.errors import BaseError, InvalidOrder

class TestRadarRelayPersonalCCXT(TestCase):

    def setUp(self):
        self.exchange = radarrelay()
        with open(os.getcwd() +'/orderbook_data.json') as order_data:
            self.exchange.order_bk = json.load(order_data)

        self.exchange.markets = {'req/eth':{'symbol':'req/eth',
            'quoteTokenAddress':"0x2956356cd2a2bf3202f771f50d3d14a367b48070",
            'baseTokenAddress': "0x8f8221afbb33998d8584a2b05749ba73c37a938a",
            'precision': {
                'amountBase': 10**18,
                'amountQuote': 10**18
            }
        }}

    def test_set_wallet(self):
        self.fail("create set_wallet function.")

    def test_fetch_balance_no_wallet(self):
        with self.assertRaises(AttributeError):
            self.exchange.fetch_balance()

class TestRadarRelayCCXTOrderMath(TestCase):

    def setUp(self):
        self.exchange = radarrelay()

        self.fees = {
          "feeRecipient": "0xa258b39954cef5cb142fd567a46cddb31a670124",
          "makerFee": "100000000000000",
          "takerFee": "200000000000000"
        }

        self.order = {
          "exchangeContractAddress": "0x12459c951127e0c374ff9105dda097662a027093",
          "maker": "0x9e56625509c2f60af937f23b7b532600390e8c8b",
          "taker": "0x0000000000000000000000000000000000000000",
          "makerTokenAddress": "0x2956356cd2a2bf3202f771f50d3d14a367b48070",
          "takerTokenAddress": "0x8f8221afbb33998d8584a2b05749ba73c37a938a",
          "feeRecipient": "0xa258b39954cef5cb142fd567a46cddb31a670124",
          "makerTokenAmount": "375000000000000000",
          "takerTokenAmount": "2500000000000000000000",
          "makerFee": "100000000000000",
          "takerFee": "200000000000000",
          "expirationUnixTimestampSec": "42",
          "salt": "67006738228878699843088602623665307406148487219438534730168799356281242528500",
          "ecSignature": {
              "v": 27,
              "r": "0x61a3ed31b43c8780e905a260a35faefcc527be7516aa11c0256729b5b351bc33",
              "s": "0x40349190569279751135161d22529dc25add4f6069af05be04cacbda2ace2254"
          }
        }

        self.markets = {'req/eth':{'symbol':'req/eth',
            'quoteTokenAddress':"0x2956356cd2a2bf3202f771f50d3d14a367b48070",
            'baseTokenAddress': "0x8f8221afbb33998d8584a2b05749ba73c37a938a",
            'precision': {
                'amountBase': 10**18,
                'amountQuote': 10**18
            }
        }}

    ##Tests for calling and parsing orders
    def test_parse_order(self):
        parsed_order = {
            'id': '',
            'datetime': '',
            'timestamp': '',
            'status':    'open',
            'symbol':    'req/eth',
            'type':      'limit',
            'side':      'sell',
            'price':      0.00015,
            'amount':     2500,
            'filled':     0,
            'remaining':  2500,
            'trades':  '',
            'fee':{
                'currency': 'zrx',
                'cost': 0.0001,
            },
            'info': self.order,
        }

        out = self.exchange.parse_order(self.order)

        self.assertEqual(out, parsed_order)

class TestRadarRelayOrderExecution(TestCase):

    def setUp(self):
        self.exchange = radarrelay()

        self.fees = {
          "feeRecipient": "0xa258b39954cef5cb142fd567a46cddb31a670124",
          "makerFee": "100000000000000",
          "takerFee": "200000000000000"
        }

        self.order = {
          "exchangeContractAddress": "0x12459c951127e0c374ff9105dda097662a027093",
          "maker": "0x9e56625509c2f60af937f23b7b532600390e8c8b",
          "taker": "0x0000000000000000000000000000000000000000",
          "makerTokenAddress": "0x2956356cd2a2bf3202f771f50d3d14a367b48070",
          "takerTokenAddress": "0x8f8221afbb33998d8584a2b05749ba73c37a938a",
          "feeRecipient": "0xa258b39954cef5cb142fd567a46cddb31a670124",
          "makerTokenAmount": "375000000000000000",
          "takerTokenAmount": "2500000000000000000000",
          "makerFee": "100000000000000",
          "takerFee": "200000000000000",
          "expirationUnixTimestampSec": "42",
          "salt": "67006738228878699843088602623665307406148487219438534730168799356281242528500",
          "ecSignature": {
              "v": 27,
              "r": "0x61a3ed31b43c8780e905a260a35faefcc527be7516aa11c0256729b5b351bc33",
              "s": "0x40349190569279751135161d22529dc25add4f6069af05be04cacbda2ace2254"
          }
        }

        self.exchange.markets = {'req/eth':{'symbol':'req/eth',
            'quoteTokenAddress':"0x2956356cd2a2bf3202f771f50d3d14a367b48070",
            'baseTokenAddress': "0x8f8221afbb33998d8584a2b05749ba73c37a938a",
            'precision': {
                'amountBase': 10**18,
                'amountQuote': 10**18
            }
        }}

    ###TESTS FOR ANALYZE_ORDERBOOK2 METHOD
    @patch('radarrelay.radarrelay._fill_order')
    def test_analyze_orderbook_fillable(self, mock_fill):
        with open(os.getcwd() +'/orderbook_data_inv.json') as order_data:
            self.exchange.order_bk = json.load(order_data)

        pending, leftover = self.exchange._analyze_orderbook(7751.94, 0.258, 10**18, 10**18)

        self.assertEqual(leftover, 0)
        self.assertEqual(pending, ['0x12459c951127e0c374ff9105dda097662a027093', '0x12459c951127e0c374ff9105dda097662a027093'])

        self.exchange._fill_order.assert_called_with(0.048*(10**18), self.exchange.order_bk['asks'][-2])

    @patch('radarrelay.radarrelay._fill_order')
    def test_analyze_orderbook_unfillable(self, mock_fill):
        with open(os.getcwd() +'/orderbook_data_inv.json') as order_data:
            self.exchange.order_bk = json.load(order_data)
        pending, leftover = self.exchange._analyze_orderbook(6666.67, 0.3, 10**18, 10**18)

        self.assertEqual(leftover, 0.3)
        self.assertEqual(pending, [])

        self.exchange._fill_order.assert_not_called()

    @patch('radarrelay.radarrelay._fill_order')
    def test_analyze_orderbook2_partial_fill(self, mock_fill):
        with open(os.getcwd() +'/orderbook_data.json') as order_data:
            self.exchange.order_bk = json.load(order_data)

        pending, leftover = self.exchange._analyze_orderbook(0.000176, 15000, 10**18, 10**18)

        self.assertEqual(leftover, 5000)
        self.assertEqual(pending, ['0x12459c951127e0c374ff9105dda097662a027093'])

        self.exchange._fill_order.assert_called_with(10000*(10**18), self.exchange.order_bk['asks'][-1])

    @patch('radarrelay.radarrelay._fill_order')
    def test_analyze_orderbook2_market(self, mock_fill):
        with open(os.getcwd() +'/orderbook_data.json') as order_data:
            self.exchange.order_bk = json.load(order_data)

        pending, leftover = self.exchange._analyze_orderbook(float('inf'), 15000, 10**18, 10**18)

        self.assertEqual(leftover, 0)
        self.assertEqual(pending, ['0x12459c951127e0c374ff9105dda097662a027093', '0x12459c951127e0c374ff9105dda097662a027093'])

        self.exchange._fill_order.assert_called_with(5000*(10**18), self.exchange.order_bk['asks'][-2])

    ###TESTS FOR CREATE_ORDER2 METHOD
    def test_create_order_limit_no_price(self):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        with self.assertRaises(InvalidOrder):
            self.exchange.create_order('limit', '0x8f8221afbb33998d8584a2b05749ba73c37a938a', 1000, '0x2956356cd2a2bf3202f771f50d3d14a367b48070', time_ex=1)

    def test_create_order_limit_no_time(self):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        with self.assertRaises(InvalidOrder):
            self.exchange.create_order('limit', '0x8f8221afbb33998d8584a2b05749ba73c37a938a', 1000, '0x2956356cd2a2bf3202f771f50d3d14a367b48070', 0.129)

    def test_create_order_no_wallet(self):
        with self.assertRaises(AttributeError):
            self.exchange.create_order('limit', '0x8f8221afbb33998d8584a2b05749ba73c37a938a', 1000, '0x2956356cd2a2bf3202f771f50d3d14a367b48070', 0.129, time_ex=1)

    @patch('radarrelay.radarrelay.fetch_order_book')
    @patch('radarrelay.radarrelay._analyze_orderbook', return_value=[['0x12459c951127e0c374ff9105dda097662a027093', '0x12459c951127e0c374ff9105dda097662a027093'],0])
    @patch('radarrelay.radarrelay._post_order', return_value = ['',''])
    def test_create_order_sell_fillable(self, mock_post, mock_analyze, mock_order_bk):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        output = {
            'info': '',
            'id': '',
            'pending': ['0x12459c951127e0c374ff9105dda097662a027093', '0x12459c951127e0c374ff9105dda097662a027093']
        }

        order = self.exchange.create_order('limit', '0x2956356cd2a2bf3202f771f50d3d14a367b48070', 0.258, '0x8f8221afbb33998d8584a2b05749ba73c37a938a', 2000, time_ex=1)

        self.exchange._post_order.assert_not_called()
        self.assertEqual(order, output)

    @patch('radarrelay.radarrelay.fetch_order_book')
    @patch('radarrelay.radarrelay._analyze_orderbook', return_value=[[],0.3])
    @patch('radarrelay.radarrelay._post_order', return_value = ['' ,'0x12459c951127e0c374ff9105dda097662a027093'])
    def test_create_order_sell_unfillable(self, mock_post, mock_analyze, mock_order_bk):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        output = {
            'info': '',
            'id': '0x12459c951127e0c374ff9105dda097662a027093',
            'pending': []
        }

        order = self.exchange.create_order('limit', '0x2956356cd2a2bf3202f771f50d3d14a367b48070', 0.3, '0x8f8221afbb33998d8584a2b05749ba73c37a938a', 2000, time_ex=1)

        self.exchange._post_order.assert_called_with('0x2956356cd2a2bf3202f771f50d3d14a367b48070', 0.3*(10**18), '0x8f8221afbb33998d8584a2b05749ba73c37a938a', 2000*(10**18), 1)
        self.assertEqual(order, output)

    @patch('radarrelay.radarrelay.fetch_order_book')
    @patch('radarrelay.radarrelay._analyze_orderbook', return_value=[['0x12459c951127e0c374ff9105dda097662a027093'],5000])
    @patch('radarrelay.radarrelay._post_order', return_value = ['' ,'0x12459c951127e0c374ff9105dda097662a027093'])
    def test_create_order_buy_partial_fill(self, mock_post, mock_analyze, mock_order_bk):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        output = {
            'info': '',
            'id': '0x12459c951127e0c374ff9105dda097662a027093',
            'pending': ['0x12459c951127e0c374ff9105dda097662a027093']
        }

        order = self.exchange.create_order('limit', '0x8f8221afbb33998d8584a2b05749ba73c37a938a', 15000, '0x2956356cd2a2bf3202f771f50d3d14a367b48070', 2.64, time_ex=1)

        self.exchange._post_order.assert_called_with('0x8f8221afbb33998d8584a2b05749ba73c37a938a', 5000*(10**18), '0x2956356cd2a2bf3202f771f50d3d14a367b48070', 0.88*(10**18), 1)
        self.assertEqual(order, output)

    ###TESTS FOR _POST_ORDER METHOD
    def test_post_order(self):
        self.fail('Create tests for posting order.')

    ###TESTS FOR _fill_order
    def test_fill_order(self):
        self.fail('Create tests for filling order.')

    ###TESTS FOR cancel_order
    def test_cancel_order(self):
        self.fail("Create tests for cancel order function.")
