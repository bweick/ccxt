import json
import urllib
import os
import time

from unittest import TestCase
from mock import Mock, patch
from radarrelay import radarrelay
from ccxt.base.errors import BaseError, InvalidOrder

class TestRadarRelayCCXT(TestCase):

    def setUp(self):
        self.exchange = radarrelay()
        with open(os.getcwd() +'/orderbook_data.json') as order_data:
            self.exchange.order_bk = json.load(order_data)

    def test_set_wallet(self):
        self.fail("create set_wallet function.")

    def test_fetch_balance_no_wallet(self):
        with self.assertRaises(AttributeError):
            self.exchange.fetch_balance()

    ###TESTS FOR CREATE_ORDER METHOD
    def test_create_order_limit_no_price(self):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        with self.assertRaises(InvalidOrder):
            self.exchange.create_order('', 'limit', 'buy', 1000, time_ex=1)

    def test_create_order_limit_no_time(self):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        with self.assertRaises(InvalidOrder):
            self.exchange.create_order('', 'limit', 'buy', 1000, price=0.000129)

    def test_create_order_no_wallet(self):
        with self.assertRaises(AttributeError):
            self.exchange.create_order('req/eth', 'limit', 'sell', 2000, price=0.000129, time_ex=1)

    @patch('radarrelay.radarrelay.fetch_order_book')
    @patch('radarrelay.radarrelay._analyze_orderbook', return_value=[['0x12459c951127e0c374ff9105dda097662a027093', '0x12459c951127e0c374ff9105dda097662a027093'],0])
    @patch('radarrelay.radarrelay._sell_post', return_value = ['',''])
    def test_create_order_sell_fillable(self, mock_post, mock_analyze, mock_order_bk):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        output = {
            'info': '',
            'id': '',
            'pending': ['0x12459c951127e0c374ff9105dda097662a027093', '0x12459c951127e0c374ff9105dda097662a027093']
        }

        order = self.exchange.create_order('req/eth', 'limit', 'sell', 2000, price=0.000129, time_ex=1)

        self.exchange._sell_post.assert_not_called()
        self.assertEqual(order, output)

    @patch('radarrelay.radarrelay.fetch_order_book')
    @patch('radarrelay.radarrelay._analyze_orderbook', return_value=[[],2000])
    @patch('radarrelay.radarrelay._sell_post', return_value = ['' ,'0x12459c951127e0c374ff9105dda097662a027093'])
    def test_create_order_sell_unfillable(self, mock_post, mock_analyze, mock_order_bk):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        output = {
            'info': '',
            'id': '0x12459c951127e0c374ff9105dda097662a027093',
            'pending': []
        }

        order = self.exchange.create_order('req/eth', 'limit', 'sell', 2000, price=0.00015, time_ex=1)

        self.exchange._sell_post.assert_called_with('req/eth', 2000, .00015, 1, {})
        self.assertEqual(order, output)

    @patch('radarrelay.radarrelay.fetch_order_book')
    @patch('radarrelay.radarrelay._analyze_orderbook', return_value=[['0x12459c951127e0c374ff9105dda097662a027093'],5000])
    @patch('radarrelay.radarrelay._buy_post', return_value = ['' ,'0x12459c951127e0c374ff9105dda097662a027093'])
    def test_create_order_buy_partial_fill(self, mock_post, mock_analyze, mock_order_bk):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        output = {
            'info': '',
            'id': '0x12459c951127e0c374ff9105dda097662a027093',
            'pending': ['0x12459c951127e0c374ff9105dda097662a027093']
        }
        order = self.exchange.create_order('req/eth', 'limit', 'buy', 15000, price=0.000176, time_ex=1)

        self.exchange._buy_post.assert_called_with('req/eth', 5000, .000176, 1, {})
        self.assertEqual(order, output)

    ###TESTS FOR ANALYZE_ORDERBOOK METHOD
    @patch('radarrelay.radarrelay._fill_order')
    def test_analyze_orderbook_fillable(self, mock_fill):
        pending, leftover = self.exchange._analyze_orderbook('sell', 0.000129, 2000)

        self.assertEqual(leftover, 0)
        self.assertEqual(pending, ['0x12459c951127e0c374ff9105dda097662a027093', '0x12459c951127e0c374ff9105dda097662a027093'])

        self.exchange._fill_order.assert_called_with(500*(10**18), self.exchange.order_bk['bids'][-2])

    @patch('radarrelay.radarrelay._fill_order')
    def test_analyze_orderbook_unfillable(self, mock_fill):
        pending, leftover = self.exchange._analyze_orderbook('sell', 0.00015, 2000)

        self.assertEqual((leftover)/(10**18), 2000)
        self.assertEqual(pending, [])

        self.exchange._fill_order.assert_not_called()

    @patch('radarrelay.radarrelay._fill_order')
    def test_analyze_orderbook_partial_fill(self, mock_fill):
        pending, leftover = self.exchange._analyze_orderbook('buy', 0.000176, 15000)

        self.assertEqual((leftover)/(10**18), 5000)
        self.assertEqual(pending, ['0x12459c951127e0c374ff9105dda097662a027093'])

        self.exchange._fill_order.assert_called_with(10000*(10**18), self.exchange.order_bk['asks'][-1])

    @patch('radarrelay.radarrelay._fill_order')
    def test_analyze_orderbook_market(self, mock_fill):
        pending, leftover = self.exchange._analyze_orderbook('buy', float('inf'), 15000)

        self.assertEqual(leftover, 0)
        self.assertEqual(pending, ['0x12459c951127e0c374ff9105dda097662a027093', '0x12459c951127e0c374ff9105dda097662a027093'])

        self.exchange._fill_order.assert_called_with(5000*(10**18), self.exchange.order_bk['asks'][-2])

    def test_fill_order(self):
        self.fail("When wrapper finished write this code block")

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

    ###TESTS FOR SELL_POST AND BUY_POST
    @patch('radarrelay.radarrelay.load_markets', return_value={})
    def test_buy_post(self, mock_load):
        self.exchange.wallet = ['0x9e56625509c2f60af937f23b7b532600390e8c8b']
        self.exchange.markets = {'req/eth':{'symbol':'req/eth',
            'quoteTokenAddress':"0x2956356cd2a2bf3202f771f50d3d14a367b48070",
            'baseTokenAddress': "0x8f8221afbb33998d8584a2b05749ba73c37a938a"
        }}

        with patch.object(self.exchange, 'public_post_fees') as mock_fees:
            mock_fees.return_value = self.fees
            with patch.object(self.exchange, 'public_post_order') as mock_order:
                out = self.exchange._buy_post('req/eth', 2500, 0.00015, 1)

                self.exchange.public_post_order.assert_called_with({}, body=json.dumps(self.order))
                self.assertEqual(out, self.order)

    ###Tests for calling and parsing orders
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
            'fee':      {
                'currency': 'zrx',
                'cost': 0.0001,
            },
            'info': self.order,
        }

        out = self.exchange.parse_order(self.order)

        self.assertEqual(out, parsed_order)
