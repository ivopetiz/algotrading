"""
    Risk Management module.
"""

import time
import lib_bittrex

class RiskManagement:

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
                self.available[i["Currency"]]=i["Available"]

        #self.available["USDT"] = self.conn.get_balance("USDT")["result"]["Available"]
        #self.available["BCT"] = self.conn.get_balance("BTC")["result"]["Available"]


    def get_all_balances(self):
        # parser do get_balances
        return self.conn.get_balances()


    def get_coin_balance(self, coin):
        return self.conn.get_balance(coin)["result"]["Available"], \
               self.conn.get_balance(coin)["result"]["Pending"]
        

    def buy(self, coin, rate):
        # Verify if has sufficient funds.
        if self.available[coin.split('-')[0]] > self.min_limit:

            # Calculate the amount of 'coin' to buy, based on rate and risk.
            to_spend = self.available[coin.split('-')[0]] * self.risk
            
            # Buy_limit
            res = self.conn.buy_limit(coin, rate/to_spend, rate)
            
            # Checks if the transaction is complete.
            if res["success"] == True:
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
