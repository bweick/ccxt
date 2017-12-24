from __future__ import division
import datetime
import time
import json

from ccxt.base.exchange import Exchange
from ccxt.base.errors import BaseError, InvalidOrder

class radarrelay(Exchange):

    def __init__(self):
        #self.exchange =
        pass

    def describe(self):
        return self.deep_extend(super(radarrelay, self).describe(), {
            'id': 'radarrelay',
            'name': 'RadarRelay',
            'countries': 'US',
            'rateLimit': 500,
            'hasCORS': False,
            # obsolete metainfo interface
            'hasFetchTickers': False,
            'hasFetchOHLCV': False,
            'hasFetchMyTrades': False,
            'hasFetchOrder': True,
            'hasFetchOrders': True,
            'hasFetchOpenOrders': True,
            'hasWithdraw': False,
            # new metainfo interface
            'has': {
                'fetchTickers': False,
                'fetchOHLCV': False,
                'fetchMyTrades': False,
                'fetchOrder': True,
                'fetchOrders': True,
                'fetchOpenOrders': True,
                'withdraw': False,
            },
            'urls': {
                'api': {
                    'public': 'https://api.radarrelay.com/0x/v0/',
                },
                'www': 'https://www.radarrelay.com',
                'doc': 'https://radarrelay.com/standard-relayer-api',
            },
            'api': {
                'public': {
                    'get': [
                        'token_pairs',
                        'orders',
                        'order/',
                        'orderbook'
                    ],
                    'post':[
                        'fees',
                        'order',
                    ],
                },
            },
            'wallet':''
        })

    def set_wallet(self):
        pass

    def check_wallet(self):
        if type(self.wallet) is list and len(self.wallet) != 0:
            pass
        else:
            raise AttributeError("Wallet(s) must be linked for this function. Set exchange.wallet=address")

    def get_symbol(address):
        pass

    def fetch_markets(self):
        response = self.public_get_token_pairs()
        result = []
        for pair in response:
            precision = {
                'amount': 10**min(int(pair['tokenB']['precision']), int(pair['tokenA']['precision']))
                'amountBase': 10**int(pair['tokenB']['precision']),
                'amountQuote':10**int(pair['tokenA']['precision'])
                'price': pair['tokenA']['precision']
            }
            limits = {
                'amount': {
                    'min': pair['tokenA']['minAmount'],
                    'max': pair['tokenB']['maxAmount']
                },
                'price': {
                    'min': 0,
                    'max': None
                },
                'cost': {
                    'min': 0,
                    'max': None
                }
            }

            base_symbol = self.get_symbol(pair['tokenB']['address'])
            quote_symbol = self.get_symbol(pair['tokenA']['address'])
            asset = {
                'id':'',
                'symbol':base_symbol + '/' + quote_symbol,
                'base': base_symbol,
                'baseTokenAddress': pair['tokenB']['address'],
                'quote':quote_symbol,
                'quoteTokenAddress': pair['tokenA']['address'],
                'precision': precision,
                'limits': limits,
                'info': pair
            }
            result.append(asset)
        return result

    def parse_order_book(self, market, orderbook, timestamp):
        base_precision = int(market['precision']['amountBase'])
        quote_precision = int(market['precision']['amountQuote'])

        bids, asks = [], []
        for bid in orderbook['bids']:
            price = (int(bid['makerTokenAmount'])/quote_precision)/(int(bid['takerTokenAmount'])/base_precision)
            amount = int(bid['takerTokenAmount'])/base_precision
            bids.append([price, amount])

        for ask in orderbook['asks']:
            price = (int(ask['takerTokenAmount'])/quote_precision)/(int(ask['makerTokenAmount'])/base_precision)
            amount = int(ask['makerTokenAmount'])/base_precision
            asks.append([price, amount])

        parsed_book = {
            'bids': bids,
            'asks': asks,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp)
        }
        return parsed_book

    def fetch_order_book(self, symbol, params={}, raw=False):
        self.load_markets()
        market = self.market(symbol)
        orderbook = self.publicGetOrderbook(self.extend({
            'quoteTokenAddress':market['quoteTokenAddress'],
            'baseTokenAddress':market['baseTokenAddress']
        }, params))
        timestamp = self.milliseconds()

        if raw:
            return orderbook
        else:
            return self.parse_order_book(market, orderbook, timestamp)

    def fetch_trades(self, symbol, since=None, limit=None, params={}):
        self.load_markets()
        market = self.market(symbol)

        req = {
            'symbol': symbol
        }
        ####MUST figure out if radar has query to get recent trades

    def fetch_tickers(self, symbols, params):
        pass
        ####MUST get a tickers endpoint in API

    def fetch_balance(self, params={}):
        self.check_wallet()

        balances = {}
        for address in self.wallet:
            pass
            '''
            Add logic that takes self.wallet and queries blockchain for current
            balances. Return open orders as well as unconfirmed trades in dict
            object that lays out exposures.
            '''

    def parse_order(self, response, symbol=None):
        return response

    def fetch_order(self, order_id, params={}):
        response = self.public_get_order(self.extend({'order_id':order_id}, params))
        return self.parse_order(response)

    def fetch_orders(self, symbol=None, params={}):
        self.check_wallet()

        if symbol is None:
            request = {'trader': self.wallet[0]}
        else:
            self.load_markets()
            market = self.market(symbol)
            request = {
                'trader': self.wallet[0],
                'tokenA': market['baseTokenAddress'],
                'tokenB': market['quoteTokenAddress']
            }

        response = self.public_get_orders(self.extend(request, params))
        orders =[self.parse_order(order, symbol) for order in response]
        return orders

    def fetch_open_orders(self, symbol=None, params={}):
        self.check_wallet()

        if symbol is None:
            request = {'maker': self.wallet[0]}
        else:
            self.load_markets()
            market = self.market(symbol)
            request = {
                'trader': self.wallet[0],
                'tokenA': market['baseTokenAddress'],
                'tokenB': market['quoteTokenAddress']
            }

        response = self.public_get_orders(self.extend(request, params))
        out = []
        empty = "0x0000000000000000000000000000000000000000"
        for order in response:
            if order['maker'] == empty or order['taker'] == empty:
                out.append(self.parse_order(order, symbol))
        return out

    def fetch_closed_orders(self, symbol=None, params={}):
        self.check_wallet()

        if symbol is None:
            request = {'trader': self.wallet[0]}
        else:
            self.load_markets()
            market = self.market(symbol)
            request = {
                'trader': self.wallet[0],
                'tokenA': market['baseTokenAddress'],
                'tokenB': market['quoteTokenAddress']
            }

        response = self.public_get_orders(self.extend(request, params))
        out = []
        empty = "0x0000000000000000000000000000000000000000"
        for order in response:
            if (order['maker'] != empty and order['taker'] == self.wallet[0]) or (order['taker'] != empty and order['maker'] == self.wallet[0]):
                out.append(self.parse_order(order, symbol))
        return out

    def _analyze_orderbook(self, symbol, side, price, amount):
        self.load_markets()
        market = self.market(symbol)
        base_precision = market['precision']['amountBase']
        quote_precision = market['precision']['amountQuote']

        leftover = amount*base_precision
        pending = []

        if side == 'buy':
            for ask in self.order_bk['asks'][::-1]: ##Reversed order
                if ((int(ask['takerTokenAmount'])/quote_precision)/(int(ask['makerTokenAmount'])/base_precision)) <= price and leftover > 0:
                    if int(ask['makerTokenAmount']) < leftover:
                        self._fill_order(int(ask['makerTokenAmount']), ask)
                        leftover -= int(ask['makerTokenAmount'])
                        pending.append(ask['exchangeContractAddress']) #stand in for tx_hash
                    else:
                        self._fill_order(leftover, ask)
                        leftover -= leftover
                        pending.append(ask['exchangeContractAddress']) #stand in for tx_hash
                else:
                    break
        else:
            for bid in self.order_bk['bids'][::-1]: ##Reversed order
                if ((int(bid['makerTokenAmount'])/quote_precision)/(int(bid['takerTokenAmount'])/base_precision)) >= price and leftover > 0:
                    if int(bid['takerTokenAmount']) < leftover:
                        self._fill_order(int(bid['takerTokenAmount']), bid)
                        leftover -= int(bid['takerTokenAmount'])
                        pending.append(bid['exchangeContractAddress']) #stand in for tx_hash
                    else:
                        self._fill_order(leftover, bid)
                        leftover -= leftover
                        pending.append(bid['exchangeContractAddress']) #stand in for tx_hash
                else:
                    break

        return pending, leftover

    def create_order(self, symbol, style, side, amount, price=None, time_ex=None, params={}):
        self.check_wallet()

        if style == 'limit' and price == None:
            raise InvalidOrder("Price must be specified in limit order")
        elif style == 'limit' and time_ex == None:
            raise InvalidOrder("Time to expiration must be specified for limit orders")

        if style == 'market' and side == 'buy':
            price = float('inf')
        elif style == 'market' and side == 'sell':
            price = 0

        self.order_bk = self.fetch_order_book(symbol, params={}, raw=True)
        pending, leftover = self._analyze_orderbook(symbol, side, price, amount)

        if leftover != 0:
            if side == 'buy':
                response, order_hash = self._buy_post(symbol, leftover, price, time_ex, params)
            elif side == 'sell':
                response, order_hash = self._sell_post(symbol, leftover, price, time_ex, params)
        else:
            response, order_hash = '', ''

        out = {
            'info': response,
            'id': order_hash,
            'pending': pending
        }
        return out

    def _fill_order(self, amount, ticket):
        pass

    def _buy_post(self, symbol, amount, price, time_ex, params={}):
        self.load_markets()
        market = self.market(symbol)

        takerAmount = amount*market['precision']['baseAmount']
        makerAmount = amount*price*market['precision']['quoteAmount']

        ##get exchangeContractAddress
        ##get salt

        order = {
            "exchangeContractAddress": "",
            "maker": self.wallet[0],
            "taker": "0x0000000000000000000000000000000000000000",
            "makerTokenAddress": market['quoteTokenAddress'],
            "takerTokenAddress": market['baseTokenAddress'],
            "makerTokenAmount": str(makerAmount),
            "takerTokenAmount": str(takerAmount),
            "expirationUnixTimestampSec":str(self.milliseconds() + time_ex*60000),
            "salt": ""
        }

        fees = self.public_post_fees(params, body=json.dumps(order)) ####error handling here
        order = self.extend(order, fees)
        order_hash = '0x12459c951127e0c374ff9105dda097662a027093' ###will be fxn
        sig = {} ##get signature
        order['ecSignature'] = sig
        ##validate order

        out = self.public_post_order(params, body=json.dumps(order)) ###error handling
        return out, order_hash

    def _sell_post(self, symbol, amount, price, time_ex, params={}):
        self.load_markets()
        market = self.market(symbol)

        makerAmount = amount*market['precision']['baseAmount']
        takerAmount = amount*price*market['precision']['quoteAmount']

        ##get exchangeContractAddress
        ##get salt

        order = {
            "exchangeContractAddress": "",
            "maker": self.wallet[0],
            "taker": "0x0000000000000000000000000000000000000000",
            "makerTokenAddress": market['baseTokenAddress'],
            "takerTokenAddress": market['quoteTokenAddress'],
            "makerTokenAmount": str(makerAmount),
            "takerTokenAmount": str(takerAmount),
            "expirationUnixTimestampSec":str(self.milliseconds + time_ex*60000),
            "salt": ""
        }

        fees = self.public_post_fees(params, body=json.dumps(order)) ####error handling here
        order = self.extend(order, fees)
        order_hash = '0x12459c951127e0c374ff9105dda097662a027093' ###will be fxn
        sig = {} ##get signature
        order['ecSignature'] = sig
        ##validate order

        out = self.public_post_order(params, body=json.dumps(order)) ###error handling
        return out, order_hash

    def create_limit_buy_order(self, symbol, amount, price, time_ex):
        return self.create_order(symbol, 'limit', 'buy', amount=amount, price=price, time_ex=time_ex)

    def create_limit_sell_order(self, symbol, amount, price, time_ex):
        return self.create_order(symbol, 'limit', 'sell', amount=amount, price=price, time_ex=time_ex)

    def cancel_order(self, order_id, params={}):
        pass

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'][api]
        url += path
        if params:
            if 'order_hash' in params:
                url += params['order_hash']
            else:
                url += '?' + self.urlencode(params)
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

if __name__ == "__main__":
    #response = radarrelay().public_get_order({'order_hash':'0x8f8221afbb33998d8584a2b05749ba73c37a938a'})
    # order = {
    #     "exchangeContractAddress": "",
    #     "maker": '0x9e56625509c2f60af937f23b7b532600390e8c8b',
    #     "taker": "0x0000000000000000000000000000000000000000",
    #     "makerTokenAddress": '0x323b5d4c32345ced77393b3530b1eed0f346429d',
    #     "takerTokenAddress": "0xef7fff64389b814a946f3e92105513705ca6b990",
    #     "makerTokenAmount": '10000000000000000',
    #     "takerTokenAmount": "20000000000000000",
    #     "expirationUnixTimestampSec":str(time.time() + 300000),
    #     "salt": ""
    # }
    #
    # response = radarrelay().public_post_fees(body=json.dumps(order))

    exch = radarrelay()
    exch.wallet = ["0x225eeb18854f81f846bec07728a1175e0ebb751c"]
    response = exch.fetch_open_orders()
    print(len(response))
