import app
import urllib2
import json

order_book_url = 'https://www.bitstamp.net/api/order_book/'

class OrderBook(object):
    bids = None
    asks = None
    last_updated = None

    def _convert(self, bids):
        return [[float(price), float(num)] for price,num in bids]

    def request_orders(self):
        data = json.load(urllib2.urlopen(order_book_url))
        self.last_updated = data.get('timestamp')
        self.bids = self._convert(data.get('bids'))
        self.asks = self._convert(data.get('asks'))

    def get_asks(self):
        return self.asks

    def get_bids(self):
        return self.bids

    def get_last_updated(self):
        return self.last_updated

def weighted_avg(orders):
    num_purchase = sum([num for price,num in orders])
    return sum([price*num for price,num in orders])/num_purchase

def _btc_book(usd, orders):
    ret = []
    usd = float(usd)
    for price, num in orders:
        if usd == 0:
            break
        num_coins = min(usd/price, num)
        usd = usd - num_coins*price
        ret.append([price, num_coins])
    return ret

def btc_buy(usd, book):
    """
    Given usd, returns the # of btc that that would buy
    Assumes that the commission has been adjusted already
    """
    purchase_orders = _btc_book(usd, book.get_asks())
    return weighted_avg(purchase_orders)

def btc_sell(usd, book):
    """
    Given usd, returns the # of btc that that would sell
    Assumes that the commission has been adjusted already
    """
    purchase_orders = _btc_book(usd, book.get_bids())
    return weighted_avg(purchase_orders)

def _usd_book(btc, orders):
    ret = []
    for price, num in orders:
        if btc == 0:
            break
        num_coins = min(btc, num)
        btc = btc - num_coins
        ret.append([price, num_coins])
    return ret

def usd_buy(btc, book):
    """
    Given btc, returns the # of usd that that would buy
    Assumes that the commission has been adjusted already
    """
    purchase_orders = _usd_book(btc, book.get_asks())
    return weighted_avg(purchase_orders)

def usd_sell(btc, book):
    """
    Given btc, returns the # of usd that that would buy
    Assumes that the commission has been adjusted already
    """
    purchase_orders = _usd_book(btc, book.get_bids())
    return weighted_avg(purchase_orders)

def get_commission(quantity):
    return quantity*.01
