"""
    Risk Management module.
"""

import time
import cryptoalgotrading.lib_bittrex as lib_bittrex
import cryptoalgotrading.var as var
import cryptoalgotrading.aux as aux


class Bittrex:

    def __init__(self, key, secret):
        # connects to bittrex through Bittrex lib.
        self.conn = lib_bittrex.Bittrex(key, secret)
        # min_limit represents minimum value account needs, in order to remain working.
        self.min_limit = 1000
        # risk represents percentage of money bot could use each time it buy coins.
        self.risk = 0.05
        # available balances.
        self.available = {}
        for i in self.conn.get_balances()["result"]:
            if i["Available"] > 0:
                self.available[i["Currency"]] = i["Available"]

    def get_all_balances(self):
        # parser do get_balances
        return self.conn.get_balances()

    def get_coin_balance(self, coin):
        return self.conn.get_balance(coin)["result"]["Available"], \
               self.conn.get_balance(coin)["result"]["Pending"]

    def buy(self, coin, amount, price):
        """
        Method to buy coins.
        :param coin: coin to buy
        :param amount: amount of currency to buy
        :param price: limit price
        :return: tuple with info about the purchase
        """
        # Verify if has sufficient funds.
        if self.available[coin.split('-')[0]] > self.min_limit:

            # Calculate the amount of 'coin' to buy, based on rate and risk.
            to_spend = self.available[coin.split('-')[0]] * self.risk

            # Buy_limit
            res = self.conn.buy_limit(coin, rate/to_spend, rate)

            # Checks if the transaction is complete.
            if res["success"]:
                # REMOVE SLEEP
                time.sleep(1)
                order = self.conn.get_order(res["result"]["uuid"])

                # If order is open means the transaction didn't occur
                # and is necessary to cancel it.
                if order["result"]["IsOpen"]:
                    cancel = self.conn.cancel(res["result"]["uuid"])
                    # Couldn't buy at desired rate.
                    return False, cancel["message"]

                else:
                    # Returns True and price payed for coin.
                    return True, [order["result"]["PricePerUnit"], order["result"]["Quantity"]]

            else:
                # Buy_limit didn't went as predicted.
                return False, res["message"]

        else:
            # Insufficient funds.
            return False, "Cash under Minimum limit."

    def sell(self, coin, quantity, rate):

        self.conn.sell_limit(coin, quantity, rate)
        return True


class Binance:

    def __init__(self):
        # connects to Binance through Binance lib.
        self.conn = aux.Binance(var.bnc_ky, var.bnc_sct)
        # min_limit represents minimum value account needs, in order to remain working.
        self.min_limit = {'USDT': 100,
                          'BTC': 0.0005
                          }
        # risk represents percentage of money bot could use each time it buy coins.
        self.risk = 0.20
        # available balances.
        self.assets = {}

        self.refresh_balance()
        # for i in self.get_all_balances:
        #    self.available[i["asset"]] = i["free"]

        # self.available["USDT"] = self.conn.get_balance("USDT")["result"]["Available"]
        # self.available["BCT"] = self.conn.get_balance("BTC")["result"]["Available"]

    def refresh_balance(self) -> None:
        """
        Update balance for all pairs.
        """
        for coin in self.conn.get_account()["balances"]:
            self.assets[coin['asset']] = {'available': coin['free'],
                                          'pending': coin['locked']}

    def get_balances(self, coins=None) -> dict:
        """
        Get the current balance for one or multiple assets.
        :param coins: None for all assets, string for one asset and a list of strings for multiple assets
        :return: dict with assets.
        """
        self.refresh_balance()

        if not coins:
            return self.assets
        elif isinstance(coins, list):
            tmp_dict = {}
            for coin in coins:
                tmp_dict[coin] = self.assets['coin']
            return tmp_dict
        else:
            return self.assets['coins']

    def buy(self,
            coin: str,
            currency: str = 'USDT',
            amount: float = 0,
            price: float = 0) -> (bool, dict):
        """
        Buy method to use in real mode operation.
        :param currency:
        :param coin: pair to buy
        :param amount: quantity of asset to buy
        :param price: price to buy
        :return: bool with operation
        """
        # Verify if has sufficient funds.
        self.refresh_balance()

        cur_balance = self.assets[currency]['free'] + \
                      self.assets[currency]['pending']

        if cur_balance < self.min_limit[currency]:
            return False, {'error': 'Insufficient funds'}

        # Calculate quantity to buy based on preset risk
        quantity_to_buy = cur_balance * self.risk

        if quantity_to_buy > self.assets[currency]['free']:
            return False, {'error': 'Portfolio has no space for new assets'}

        buy_order = self.conn.order_market_buy(symbol=coin,
                                               quoteOrderQty=quantity_to_buy)

        return True, buy_order

    def sell(self,
             coin: str,
             currency: str = 'USDT',
             quantity: float = 0) -> (bool, dict):
        """
        Market sell assets.
        :param coin: pair to sell
        :param currency: quote coin to exchange with
        :param quantity: quantity of coin to sell
        :return: Tuple with operation success bool and dict with more info
        """
        # balance = client.get_asset_balance(asset=best_match[0])
        self.refresh_balance()

        if not quantity:
            quantity = round(float(self.assets[coin.replace(currency, '')]['free']) * 0.95, 2)

        sell_order = self.conn.order_market_sell(symbol=coin,
                                                 quantity=quantity)

        return True, sell_order
