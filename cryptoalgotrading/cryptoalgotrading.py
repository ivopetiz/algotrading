"""
    indicators.py

    Need to import this file in order to use this framework. 
"""
########
### TODO
########
#   fix log presentation.
# > implement Binance.
#   improve multiprocessing usage.
#   define processor usage.
#   implement MPI.
#   log in every try/except.
#   improve DB connection.
#   improve multiprocessing display information.
#   log multiple accesses.
#   break big files into smaller ones.
#   backtest based on pandas.Dataframe.

import var
import pandas as pd
from sys import exit
from time import time, sleep

from warnings import simplefilter
from riskmanagement import RiskManagement

from functools import partial
from multiprocessing import Pool

from aux import *

# Prevents FutureWarning from Pandas. 
simplefilter(action='ignore', category=FutureWarning)

def tick_by_tick(entry_funcs,
                 exit_funcs,
                 markets=[],
                 interval='10m',
                 smas=var.default_smas,
                 emas=var.default_volume_emas,
                 refresh_interval=60,
                 log_level=2):
    '''
    Simulates a working bot in realtime, using data from DB,
     to test a autonomous bot.

    Args:
        entry_funcs(list): list of entry functions to test.
        exit_funcs(list): list of entry functions to test.
        markets(string): list with markets to backtest or empty to run all available markets.
        interval(string): time between measures.
        smas(list): list of SMA values to use.
        emas(list): list of EMA values to use.
        refresh_interval(int): Data refresh rate.
    '''

    if len(markets) < 1:
        markets = get_markets_list('BTC')

    buy_list = {}

    while True:

        start_time = time()

        for market in markets:
            data = get_last_data(market, interval=interval)
            #if limit != (0,0):
            if market in buy_list.keys():
                if is_time_to_exit(data, exit_funcs,buy_list[market], ):

                    log('[SELL]@ ' + str(data.Bid.iloc[-1]) +\
                                 ' > ' + market, log_level)
                    
                    log('[P&L] ' + market + '> ' +\
                                 str(round(((data.Bid.iloc[-1]-\
                                            buy_list[market])/\
                                            buy_list[market])*100,2)) +\
                                 '%.', log_level)
                    
                    del buy_list[market]
            
            else:
                if is_time_to_buy(data, entry_funcs):

                    buy_list[market] = data.Ask.iloc[-1]

                    log('[BUY]@ ' + str(data.Ask.iloc[-1]) +\
                    #             ' > ' + funcs.func_name +\
                                 ' > ' + market, log_level)

        # In case of processing time is bigger than refresh interval avoid sleep.
        if refresh_interval - (time() - start_time) > 0:
            sleep(refresh_interval - (time() - start_time))


def realtime(entry_funcs,
             exit_funcs,
             interval=var.default_interval,
             smas=var.default_smas,
             emas=var.default_volume_emas,
             refresh_interval=10,
             simulation=True,
             main_coins=["BTC","USDT"],
             log_level=2):
    '''
    Bot using realtime data, doesn't need DB or csv files to work. 

    Args:
        entry_funcs(list): list of entry functions to test.
        exit_funcs(list): list of entry functions to test.
        markets(string): list with markets to backtest or empty to run all available markets.
        interval(string): time between measures.
        smas(list): list of SMA values to use.
        emas(list): list of EMA values to use.
        refresh_interval(int): Data refresh rate.
        simulation(bool): Defines if it's running as a simulation or real money mode.
        main_coins(list): 
    '''

    #log_level:
    #   0 - Only presents total.
    #   1 - Writes logs to file.
    #   2 - Writes logs to file and prints on screen.
    #   Default is 2.

    validate = smas[-1] + 5

    buy_list = {}  # Owned coins list.
    coins = {}

    if simulation:
        bt = Bittrex('', '')
        log("Starting Bot")
    else:
        try:
            bt = RiskManagement(var.ky, var.sct)
        except:
            log("Error connecting to Bittrex")
            exit()

    while True:

        start_time = time()

        markets = bt.get_market_summaries()['result']

        for market in markets:

            # Needed to pass unicode to string.
            market_name = str(market['MarketName'])

            # Checks if pair is included in main coins.
            if market_name.split('-')[0] in main_coins:

                # Checks if market already exists in analysed coins.
                if market_name in coins:
                    
                    # Checks if has enough data to analyse.
                    if coins[market_name] == validate: 
                        locals()[market_name] = pd.DataFrame.append(locals()[market_name],
                                                                 [market]).tail(validate)
                    # If not adds data and keep going.
                    else:
                        locals()[market_name] = pd.DataFrame.append(locals()[market_name],
                                                                 [market])
                        coins[market_name] += 1
                        continue

                # If not adds coin to system.
                else:
                    locals()[market_name] = pd.DataFrame([market])
                    coins[market_name] = 1
                    continue
                
                data=locals()[market_name]

                # Checks if coin is in buy portfolio and looks for a sell opportunity.
                if market_name in buy_list:

                    # Needed to make use of stop loss and trailing stop loss functions.
                    if buy_list[market_name]['max_price'] < data.Bid.iloc[-1]:
                        buy_list[market_name]['max_price'] = data.Bid.iloc[-1]

                    if is_time_to_exit(data,
                                       exit_funcs,
                                       bought_at = buy_list[market_name]['bought_at'],
                                       max_price = buy_list[market_name]['max_price'],
                                       count     = buy_list[market_name]['count'],
                                       real_aux = 0):

                        if not simulation:
                            sell_res = bt.sell(market_name,
                                               buy_list[market_name]['quantity'],
                                               data.Bid.iloc[-1])
                            
                            # MUDAR
                            sold_at = 10

                            log('[SELL]@ ' + str(sold_at) +\
                                    ' > ' + market_name, log_level)
                            
                            log('[P&L] ' + market_name + '> ' +\
                                    str(round(((sold_at-\
                                                buy_list[market_name]['bought_at'])/\
                                                buy_list[market_name]['bought_at'])*100,2)) +\
                                    '%.', log_level)

                        else:
                            print '> https://bittrex.com/Market/Index?MarketName=' + \
                                market_name

                            log('[SELL]@ ' + str(data.Bid.iloc[-1]) +\
                                        ' > ' + market_name, log_level)
                            log('[P&L] ' + market_name + '> ' +\
                                        str(round(((data.Bid.iloc[-1]-\
                                                    buy_list[market_name]['bought_at'])/\
                                                    buy_list[market_name]['bought_at'])*100,2)) +\
                                        '%.', log_level)
                        
                        del buy_list[market_name]
                
                else:
                    if is_time_to_buy(data, 
                                      entry_funcs, 
                                      real_aux=0):

                        if not simulation:
                            sucs, msg = bt.buy(market, data.Ask.iloc[-1]*1.01)
                            
                            if sucs:
                                buy_list[market_name] = {}
                                buy_list[market_name]['bought_at'] = msg[0]
                                buy_list[market_name]['max_price'] = msg[1]
                                buy_list[market_name]['quantity']  = msg[2]

                                log('[BUY]@ ' + str(msg[0]) +\
                                    #' > ' + funcs.func_name +\
                                    ' > ' + market_name)

                            else:
                                log("[XXXX] Could not buy @ " + data.Ask.iloc[-1] * 1.01 +
                                     "\n[MSG>] " + msg, log_level)
                        else:
                            print '> https://bittrex.com/Market/Index?MarketName=' + \
                                market_name

                            log('[BUY]@ ' + str(data.Ask.iloc[-1]) +\
                                #' > ' + funcs.func_name +\
                                ' > ' + market_name)
   
        # In case of processing time is bigger than *refresh_interval* doesn't sleep.
        if refresh_interval - (time()-start_time) > 0:
            sleep(refresh_interval - (time()-start_time))


def is_time_to_exit(data,
                    funcs,
                    smas=var.default_smas,
                    emas=var.default_emas,
                    stop=0,
                    bought_at=0,
                    max_price=0,
                    count=-1,
                    real_aux=1):
    '''
    Detects when is time to exit trade.

    stop variable:
    0 -> no stop loss [DANGEROUS]
    1 -> regular stop loss
    2 -> trailing stop loss
    '''

    if not real_aux:
        data = data.rename(index=str, columns={
                            "OpenBuyOrders": "OpenBuy",
                            "OpenSellOrders": "OpenSell"})

    if count == 0:
        return True

    if stop == 1:
        if stop_loss(data.Last.iloc[-1], bought_at, percentage=10):
            return True
    elif stop == 2:
        if trailing_stop_loss(data.Last.iloc[-1], max_price, percentage=10):
            return True

    if type(funcs) is not list:
        funcs = [funcs]

    for func in funcs:
        if func(data, smas=smas, emas=emas):
            return True
    
    return False 


def is_time_to_buy(data, 
                   funcs, 
                   smas=var.default_smas,
                   emas=var.default_emas,
                   real_aux=1):
    '''
    Detects when is time to enter trade.
    '''

    if not real_aux:
        data = data.rename(index=str, columns={
                           "OpenBuyOrders": "OpenBuy", 
                           "OpenSellOrders": "OpenSell"})

    if type(funcs) is not list:
        funcs = [funcs]

    for func in funcs:
        if func(data, smas=smas, emas=emas):
            return True

    return False


@timeit
def backtest(markets,
             entry_funcs,
             exit_funcs=[],
             _date=[0,0],
             smas=var.default_smas,
             emas=var.default_emas,
             interval=var.default_interval,
             plot=False,
             to_file=True,
             from_file=False,
             base_market='BTC',
             log_level=2,
             mp_level="medium"):
    '''
    Backtests strategies.

    Args:
        markets(list): list with markets to backtest or empty to test all available markets.
        entry_funcs(list): list of entry functions to test.
        exit_funcs(list): list of entry functions to test.
        _date(list): init and end point to backtest.
        smas(list): list of SMA values to use.
        emas(list): list of EMA values to use.
        interval(string): time between measures.
        plot(bool): plot data.
        to_file(bool): plot to file.
        from_file(bool): get data from file.
        base_market(string): base market to use.
        log_level(int): log level - 0-2.
        mp_level(string): multiprocessing level - [low, medium, high].

    Returns:
        bool: returns True in case of success.
    '''

    #log_level:
    #   0 - Only presents total.
    #   1 - Writes logs to file.
    #   2 - Writes logs to file and prints on screen.
    #   Default is 2.

    if not len(markets):
        y = 'y'#raw_input("Want to run all markets? ")
        if y == 'y':
            if from_file:
                markets = get_markets_on_files(interval, base=base_market)
            else:
                markets = get_markets_list(base=base_market)
        else:
            return False

    # Prevents errors from markets and funcs as str.
    if type(markets) is str:
        markets=[markets]
    if type(entry_funcs) is not list:
        entry_funcs=[entry_funcs]
    if type(exit_funcs) is not list:
        exit_funcs=[exit_funcs]
    
    pool = Pool(num_processors(mp_level))  # Create a multiprocessing Pool
    
    # Display information about pool.

    total = pool.map(partial(backtest_market,
                             entry_funcs,
                             exit_funcs,
                             interval,
                             _date,
                             smas,
                             emas,
                             from_file,
                             to_file,
                             plot), 
                             markets)

    pool.close()
    pool.join()

    print '+ Total > ' + str(sum(total))

    return True


def backtest_market(entry_funcs, 
                    exit_funcs, 
                    interval, 
                    _date, 
                    smas, 
                    emas, 
                    from_file,
                    to_file,
                    plot, 
                    market):
    '''
    Backtests strategies for a specific market.

    Args:
        entry_funcs(list): list of entry functions to test.
        exit_funcs(list): list of entry functions to test.
        interval(string): time between measures.
        _date(list): init and end point to backtest.
        smas(list): list of SMA values to use.
        emas(list): list of EMA values to use.
        to_file(bool): plot to file.
        from_file(bool): get data from file.
        plot(bool): plot data.
        markets(string): list with markets to backtest or empty to test all available markets.

    Returns:
        float: returns backtests profit & loss value for applied strategies.
    '''
    
    date = [0,0]

    log_level = 2
    total = 0
    market = check_market_name(market)

    entry_points_x = []
    entry_points_y = []

    exit_points_x = []
    exit_points_y = []

    if from_file:
        try:
            data = get_data_from_file(market, interval=interval)
        except Exception as e:
            print e
            print 'Can\'t find', market, 'in files.'
            return 1
            #continue

        data_init = data

        if type(_date[0]) is str:
            date[0], date[1] = time_to_index(data, _date)

        if date[1] == 0:
            data = data[date[0]:]
        else:
            data = data[date[0]:date[1]]

    else:
        try:
            data = get_historical_data(
                                       market, 
                                       interval=interval, 
                                       init_date=_date[0], 
                                       end_date=_date[1])
            date[0], date[1] = 0, len(data)
            data_init = data
            
        except Exception as e:
            print e
            print 'Can\'t find', market, 'in BD.'
            return 1
            #continue

    aux_buy = False
    buy_price = 0
    high_price = 0
    #Tests several functions.
    for i in range(len(data)-50):
        if not aux_buy:
            if is_time_to_buy(data[i:i+50], entry_funcs, smas, emas):
                
                buy_price = data_init.Ask.iloc[i+49+date[0]]
                high_price = buy_price
                
                entry_points_x.append(i + 49)
                entry_points_y.append(data_init.Ask.iloc[i + 49 + date[0]])
                
                if exit_funcs:
                    aux_buy = True
                
                log('> ' + str(data_init.time.iloc[i + 49 + date[0]]) + \
                     ' < [BUY]  @ ' + str(data_init.Ask.iloc[i + 49 + date[0]]) + \
                    #' > ' + funcs.func_name +\
                     ' > ' + market, log_level)

        else:
            # Used for trailing stop loss.
            if data_init.Last.iloc[i+49+date[0]] > high_price:
                high_price = data_init.Last.iloc[i+49+date[0]]

            if is_time_to_exit(data[i:i+50],
                               exit_funcs,
                               smas,
                               emas,
                               stop = 1,
                               bought_at=buy_price,
                               max_price=high_price):
            
                exit_points_x.append(i+49)
                exit_points_y.append(data_init.Bid.iloc[i+49+date[0]])
                aux_buy = False
                total += round(((data_init.Bid.iloc[i+49+date[0]] -
                                 buy_price) /
                                buy_price)*100, 2)
                log('> ' + str(data_init.time.iloc[i + 49 + date[0]]) + \
                    ' < [SELL] @ ' + str(data_init.Bid.iloc[i + 49 + date[0]]) + \
                    ' > ' + market,log_level)

                log('[P&L] ' + market + '> ' + \
                    str(total) + '%.', log_level)

    # Use plot_data for just a few markets. If you try to run plot_data for several markets, 
    # computer can start run realy slow.
    try:
        if plot:
            aux_plot = plot_data(data,
                                 name=market,
                                 date=[0,0],
                                 smas=smas,
                                 emas=[],
                                 entry_points=(entry_points_x, entry_points_y),
                                 exit_points=(exit_points_x,exit_points_y),
                                 show_smas=True,
                                 show_emas=False,
                                 show_bbands=True,
                                 to_file=to_file)
    except Exception as e:
        log("[ERROR] ploting data: " + str(e), log_level)


    if len(exit_points_x):
        log(market + ' > ' + str(total), log_level)

    log('[TOTAL] > ' + str(total), log_level)
    
    return total
    #total_markets += total
