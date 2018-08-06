"""
    indicators.py

    Need to import this file in order to use this framework. 
"""
########
### TODO
########
#   fix log presentation.
#   implement Binance.
# X use multiprocessing.
#   improve multiprocessing usage.
#   define processor usage.
#   implement MPI.
# > improve folders definition.
#   implement real buy() and sell().
#   log in every try/except.
# X plot in MP.
#   improve DB connection.
#   improve multiprocessing display information.
#   log multiple accesses.


import os
import var
import time
import logging
import pandas as pd

from functools import partial
from multiprocessing import Pool

from aux import *

logging.basicConfig(filename=var.LOG_FILENAME,
                    format='%(asctime)s - %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    level=logging.DEBUG)


def tick_by_tick(entry_funcs,
                 exit_funcs,
                 markets=[],
                 interval='10m',
                 smas=var.default_smas,
                 emas=var.default_volume_emas,
                 refresh_interval=60,
                 simulation=True):
    '''
    Simulates a working bot in realtime, using data from DB,
     to test a autonomous bot.
    '''

    if len(markets) < 1:
        markets = get_markets_list('BTC')

    buy_list = {}
    buy_present = {}

    while True:

        start_time = time.time()

        for market in markets:
            data = get_last_data(market, interval=interval)
            #if limit != (0,0):
            if market in buy_list.keys():
                if is_time_to_exit(data, exit_funcs,buy_list[market]):
                    #if not simulation:
                    #    buy(market)
                    print '+'
                    logging.info('[SELL]@ ' + str(data.Last.iloc[-1]) +\
                                 ' > ' + market)
                    
                    logging.info('[P&L] ' + market + '> ' +\
                                 str(round(((data.Last.iloc[-1]-\
                                            buy_list[market])/\
                                            buy_list[market])*100,2)) +\
                                 '%.')
                    
                    del buy_list[market]
                    del buy_present[market]
            
            else:
                if is_time_to_buy(data, entry_funcs):
                    #if not simulation:
                    #   sell(market)    
                    buy_list[market] = data.Last.iloc[-1]
                    buy_present[market] = 11
                    print '_'
                    logging.info('[BUY]@ ' + str(data.Last.iloc[-1]) +\
                    #             ' > ' + funcs.func_name +\
                                 ' > ' + market)
                    
                    if not simulation:
                        print '> https://bittrex.com/Market/Index?MarketName=' + \
                              market


            if market in buy_present.keys():
                buy_present[market] = buy_present[market] -1

        # In case of processing time is 
        if refresh_interval - (time.time() - start_time) < 0:
            pass
        else:
            time.sleep(refresh_interval - (time.time() - start_time))


def realtime(entry_funcs,
             exit_funcs,
             interval=var.default_interval,
             smas=var.default_smas,
             emas=var.default_volume_emas,
             refresh_interval=10,
             simulation=True,
             main_coins=["BTC","USDT"]):
    '''
    Bot using realtime data, doesn't need DB or csv files to work. 
    '''

    validate = smas[-1] + 5

    buy_list = {}
    buy_present = {}
    coins = {}
    
    if simulation:
        bt = lib_bittrex.Bittrex('', '')
    #else:
    #    bt = lib_bittrex.Bittrex(os.environ['API_KEY'], os.environ['API_SECRET'])

    logging.info("Starting Bot...\n")

    while True:

        start_time = time.time()

        markets=bt.get_market_summaries()['result']

        for market in markets:

            if market['MarketName'].split('-')[0] in main_coins:
                if str(market['MarketName']) in coins:
                    
                    if coins[str(market['MarketName'])] == validate: 
                        
                        locals()[str(market['MarketName'])]=pd.DataFrame.append(locals()[str(market['MarketName'])],[market]).tail(validate)
                        
                    else:
                        
                        locals()[str(market['MarketName'])]=pd.DataFrame.append(locals()[str(market['MarketName'])],[market])
                        coins[str(market['MarketName'])] += 1
                        continue

                else:
                    
                    locals()[str(market['MarketName'])]=pd.DataFrame([market])
                    coins[str(market['MarketName'])] = 1
                    continue
                
                data=locals()[str(market['MarketName'])]

                if str(market['MarketName']) in buy_list.keys():
                    if is_time_to_exit(data, exit_funcs, buy_list[str(market['MarketName'])], real_aux=0):
                        if not simulation:
                        #    buy(market)
                            print '> https://bittrex.com/Market/Index?MarketName=' + \
                                str(market['MarketName'])

                        logging.info('[SELL]@ ' + str(data.Bid.iloc[-1]) +\
                                    ' > ' + str(market['MarketName']))
                        
                        logging.info('[P&L] ' + str(market['MarketName']) + '> ' +\
                                    str(round(((data.Bid.iloc[-1]-\
                                                buy_list[str(market['MarketName'])])/\
                                                buy_list[str(market['MarketName'])])*100,2)) +\
                                    '%.')
                        
                        print '[SELL]@ ' + str(data.Bid.iloc[-1]) +\
                            ' > ' + str(market['MarketName'])
                        
                        print '[P&L] ' + str(market['MarketName']) + '> ' +\
                            str(round(((data.Bid.iloc[-1]-\
                                        buy_list[str(market['MarketName'])])/\
                                        buy_list[str(market['MarketName'])])*100,2)) +\
                                    '%.'
                        
                        del buy_list[str(market['MarketName'])]
                        del buy_present[str(market['MarketName'])]
                
                else:
                    if is_time_to_buy(data, entry_funcs, real_aux=0):

                        if not simulation:
                        #    sell(market)
                            print '> https://bittrex.com/Market/Index?MarketName=' + \
                                str(market['MarketName'])
                        #else:
                        #    print '-'

                        buy_list[str(market['MarketName'])] = data.Ask.iloc[-1]
                        buy_present[str(market['MarketName'])] = 11
                        logging.info('[BUY]@ ' + str(data.Ask.iloc[-1]) +\
                        #             ' > ' + funcs.func_name +\
                                    ' > ' + str(market['MarketName']))

                        print '[BUY]@ ' + str(data.Ask.iloc[-1]) + \
                            ' > ' + str(market['MarketName'])
                        #             ' > ' + funcs.func_name +\
                        
                if str(market['MarketName']) in buy_present.keys():
                    buy_present[str(market['MarketName'])] = buy_present[str(market['MarketName'])] -1

        # In case of processing time is bigger than *refresh_interval*
        if refresh_interval - (time.time() - start_time) > 0:
            time.sleep(refresh_interval - (time.time() - start_time))


def is_time_to_exit(data,
                    funcs,
                    entry_point,
                    limit_vol=5,
                    limit_drop=0,
                    smas=var.default_smas,
                    emas=var.default_emas,
                    real_aux=1):
    '''
    Detects when is time to exit trade.
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


def is_time_to_buy(data, 
                   funcs, 
                   limit=5,
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
             to_file = True,
             from_file=False,
             base_market='BTC',
             log_level=2,
             mp_level="medium"):
    '''
    Tests strategies.
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
    aux_price = 0
    #Tests several functions.
    for i in range(len(data)-50):
        if not aux_buy:
            if is_time_to_buy(data[i:i+50], entry_funcs, smas, emas):
                aux_price = data_init.Ask.iloc[i+49+date[0]]
                entry_points_x.append(i+49)
                entry_points_y.append(data_init.Ask.iloc[i+49+date[0]])
                if exit_funcs:
                    aux_buy = True
                if log_level > 0:
                    logging.info('[BUY]@ ' + str(data_init.Ask.iloc[i+49+date[0]]) +\
                                 #             ' > ' + funcs.func_name +\
                                 ' > ' + market)

        else:
            if is_time_to_exit(data[i:i+50], exit_funcs, data_init.Ask.iloc[i+49+date[0]], smas, emas):
                exit_points_x.append(i+49)
                exit_points_y.append(data_init.Bid.iloc[i+49+date[0]])
                aux_buy = False
                total += round(((data_init.Bid.iloc[i+49+date[0]] -
                                 aux_price) /
                                aux_price)*100, 2)
                if log_level > 0:
                    logging.info('[SELL]@ ' + str(data_init.Bid.iloc[i+49+date[0]]) +
                                 ' > ' + market)

                    logging.info('[P&L] ' + market + '> ' +
                                 str(total) + '%.')

    # Use plot_data for just a few markets. If you try to run plot_data for several markets, 
    # computer can start run realy slow.
    if plot:
        aux_plot = plot_data(data,
                            name=market,
                            date=[0,0],
                            smas=smas,
                            emas=[],
                            entry_points=(entry_points_x,entry_points_y),
                            exit_points=(exit_points_x,exit_points_y),
                            show_smas=True,
                            show_emas=False,
                            show_bbands=True,
                            to_file=to_file)


    if log_level > 0:
        if log_level > 1 and len(exit_points_x):
            print market + ' > ' + str(total)
        logging.info('[TOTAL] > ' + str(total))
    
    return total
    #total_markets += total
