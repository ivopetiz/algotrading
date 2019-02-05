"""
    cryptoalgotrading.py

    Need to import this file in order to use this framework.
"""
########
### TODO
########
# > implement Binance.
#   improve multiprocessing usage.
#   implement MPI.
#   improve DB connection.
#   improve multiprocessing display information.
#   break big files into smaller ones.
#   backtest based on pandas.Dataframe.

import var
import sys
import signal

import pandas as pd
import matplotlib.pyplot as plt
from numpy import isnan
from time import time, sleep
from warnings import simplefilter
from functools import partial
from matplotlib import animation
from riskmanagement import RiskManagement
from multiprocessing import Pool
from aux import get_markets_list, \
                log, Bittrex, stop_loss, trailing_stop_loss, \
                timeit, safe, connect_db, get_markets_on_files, \
                manage_files, num_processors, plot_data, \
                check_market_name, get_data_from_file, \
                time_to_index, get_historical_data


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)

# Prevents FutureWarning from Pandas.
simplefilter(action='ignore', category=FutureWarning)


@safe
def is_time_to_exit(data,
                    funcs,
                    smas=var.default_smas,
                    emas=var.default_emas,
                    stop=1,
                    bought_at=0,
                    max_price=0,
                    count=-1):
    '''
    Detects when is time to exit trade.

    stop variable:
    0 -> no stop loss [DANGEROUS]
    1 -> regular stop loss
    2 -> trailing stop loss
    '''

    if count == 0: return True

    if stop == 1:
        if stop_loss(data.Last.iloc[-1], bought_at, percentage=10):
            return True
    elif stop == 2:
        if trailing_stop_loss(data.Last.iloc[-1], max_price, percentage=10):
            return True

    for func in funcs:
        if func(data, smas=smas, emas=emas):
            return True

    return False


@safe
def is_time_to_buy(data,
                   funcs,
                   smas=var.default_smas,
                   emas=var.default_emas):
    '''
    Detects when is time to enter trade.
    '''

    for func in funcs:
        if func(data, smas=smas, emas=emas):
            return True

    return False


def tick_by_tick(market,
                 entry_funcs,
                 exit_funcs,
                 interval=var.default_interval,
                 smas=var.default_smas,
                 emas=var.default_emas,
                 refresh_interval=1,
                 from_file=True,
                 plot=False,
                 log_level=2):
    '''
    Simulates a working bot, in realtime or in faster speed, 
     using pre own data from DB or file,
     to test an autonomous bot on a specific market.

    Args:
        markets(string): list with markets to backtest or 
            empty to run all available markets.
        entry_funcs(list): list of entry functions to test.
        exit_funcs(list): list of entry functions to test.
        interval(string): time between measures.
        smas(list): list of SMA values to use.
        emas(list): list of EMA values to use.
        refresh_interval(int): Refresh rate.
        main_coins(list): 
    '''
    #log_level:
    #   0 - Only presents total.
    #   1 - Writes logs to file.
    #   2 - Writes logs to file and prints on screen.
    #   Default is 2.

    plt.ion()

    var.global_log_level = log_level

    signal.signal(signal.SIGINT, signal_handler)

    date = [0,0]

    total = 0

    #market = check_market_name(market)

    entry_points_x = []
    entry_points_y = []

    exit_points_x = []
    exit_points_y = []

    if type(entry_funcs) is not list: entry_funcs=[entry_funcs]
    if type(exit_funcs) is not list: exit_funcs=[exit_funcs]

    print '[Market analysis]: ' + market + '\n'

    if from_file:
        try:
            data = get_data_from_file(market, interval=interval)
        except Exception as e:
            log(str(e), 1)
            log('[ERROR] Can\'t find ' + market + ' in files.', 1)
            return 0

        data_init = data

        #if type(_date[0]) is str:
        #    date[0], date[1] = time_to_index(data, _date)

        #if date[1] == 0:
        #    data = data[date[0]:]

        #else:
        #    data = data[date[0]:date[1]]

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
            log(str(e), 1)
            log('[ERROR] Can\'t find ' + market + ' in BD.', 1)
            return 0
            #continue

    aux_buy = False
    buy_price = 0
    high_price = 0

    plt.show()

    #Tests several functions.
    for i in xrange(len(data)-50):
        start_time = time()
        #print data_init.Last.iloc[i]
        if not aux_buy:
            if is_time_to_buy(data[i:i+50], entry_funcs, smas, emas):

                buy_price = data_init.Ask.iloc[i + 49 + date[0]]
                high_price = buy_price

                entry_points_x.append(i + 49)
                entry_points_y.append(data_init.Ask.iloc[i + 49 + date[0]])

                if exit_funcs:
                    aux_buy = True

                print str(data_init.time.iloc[i + 49 + date[0]]) + \
                    ' [BUY] @ ' + str(data_init.Ask.iloc[i + 49 + date[0]]) + '\n'

        else:
            # Used for trailing stop loss.
            if data_init.Last.iloc[i + 49 + date[0]] > high_price:
                high_price = data_init.Last.iloc[i + 49 + date[0]]

            if is_time_to_exit(data[i:i+50],
                            exit_funcs,
                            smas,
                            emas,
                            stop = 0,
                            bought_at=buy_price,
                            max_price=high_price):

                exit_points_x.append(i+49)
                exit_points_y.append(data_init.Bid.iloc[i + 49 + date[0]])

                aux_buy = False

                total += round(((data_init.Bid.iloc[i + 49 + date[0]] -
                                buy_price) /
                                buy_price)*100, 2)

                print str(data_init.time.iloc[i + 49 + date[0]]) + \
                    ' [SELL]@ ' + str(data_init.Bid.iloc[i + 49 + date[0]]) + '\n'

                print '[P&L] > ' + str(total) + '%.' + '\n'

        #plt.plot(data.Last.iloc[i:i+50])
        #plt.draw()
        #plt.clf()
        # In case of processing time is bigger than *refresh_interval* doesn't sleep.

        if refresh_interval - (time()-start_time) > 0:
            sleep(refresh_interval - (time()-start_time))

    return total


def realtime(entry_funcs,
             exit_funcs,
             interval=var.default_interval,
             smas=var.default_smas,
             emas=var.default_volume_emas,
             refresh_interval=10,
             simulation=True,
             main_coins=["BTC","USDT"],
             log_level=1):
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

    #var.global_log_level = log_level

    signal.signal(signal.SIGINT, signal_handler)

    validate = smas[-1] + 5

    if not isinstance(entry_funcs, list): entry_funcs=[entry_funcs]
    if not isinstance(exit_funcs, list): exit_funcs=[exit_funcs]

    buy_list = {}  # Owned coins list.
    coins = {}

    if simulation:
        bt = Bittrex('', '')
        log("Starting Bot", 1, log_level)
        #print 'starting...'
    else:
        try:
            bt = RiskManagement(var.ky, var.sct)
        except:
            log("[Error] Couldn't connect to Bittrex", 0, log_level)
            sys.exit(1)

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

                data = locals()[market_name].rename(index=str,
                                columns={
                                    "OpenBuyOrders": "OpenBuy",
                                    "OpenSellOrders": "OpenSell"})

                # Checks if coin is in buy portfolio and looks for a sell opportunity.
                if market_name in buy_list:

                    # Needed to make use of stop loss and trailing stop loss functions.
                    if buy_list[market_name]['max_price'] < data.Bid.iloc[-1]:
                        buy_list[market_name]['max_price'] = data.Bid.iloc[-1]

                    if is_time_to_exit(data,
                                       exit_funcs,
                                       bought_at = buy_list[market_name]['bought_at'],
                                       max_price = buy_list[market_name]['max_price'],
                                       count     = buy_list[market_name]['count']):

                        if not simulation:
                            #REAL
                            sell_res = bt.sell(market_name,
                                               buy_list[market_name]['quantity'],
                                               data.Bid.iloc[-1])

                            # MUDAR
                            sold_at = sell_res

                            log('[SELL]@ ' + str(sold_at) +\
                                    ' > ' + market_name, 1, log_level)

                            log('[P&L] ' + market_name + '> ' +\
                                    str(round(((sold_at-\
                                                buy_list[market_name]['bought_at'])/\
                                                buy_list[market_name]['bought_at'])*100,2)) +\
                                    '%.', 1, log_level)

                        else:
                            #SIMULATION
                            #print '> https://bittrex.com/Market/Index?MarketName=' + market_name

                            log('[SELL]@ ' + str(data.Bid.iloc[-1]) +\
                                        ' > ' + market_name, 1, log_level)

                            log('[P&L] ' + market_name + '> ' +\
                                        str(round(((data.Bid.iloc[-1]-\
                                                    buy_list[market_name]['bought_at'])/\
                                                    buy_list[market_name]['bought_at'])*100,2)) +\
                                        '%.', 1, log_level)

                        del buy_list[market_name]

                    #if not time to exit increment count.
                    else:
                        buy_list[market_name]['count'] += 1

                # if has no coins from a certain market checks if is time to buy.
                else:
                    if is_time_to_buy(data, entry_funcs):

                        if not simulation:
                            #REAL
                            sucs, msg = bt.buy(market, data.Ask.iloc[-1]*1.01)

                            if sucs:
                                buy_list[market_name] = {}
                                buy_list[market_name]['bought_at'] = msg[0]
                                buy_list[market_name]['max_price'] = msg[0]
                                buy_list[market_name]['quantity']  = msg[1]
                                buy_list[market_name]['count']  = 0

                                log('[BUY]@ ' + str(msg[0]) +\
                                    #' > ' + funcs.func_name +\
                                    ' > ' + market_name, 1, log_level)

                            else:
                                log("[XXXX] Could not buy @ " + data.Ask.iloc[-1] * 1.01 +
                                     "\n[MSG>] " + msg, 0, log_level)

                        else:
                            #SIMULATION
                            buy_list[market_name] = {}
                            buy_list[market_name]['bought_at'] = data.Ask.iloc[-1]
                            buy_list[market_name]['max_price'] = data.Ask.iloc[-1]
                            buy_list[market_name]['quantity']  = 1
                            buy_list[market_name]['count']  = 0

                            #print '> https://bittrex.com/Market/Index?MarketName='+market_name

                            log('[BUY]@ ' + str(data.Ask.iloc[-1]) +\
                                #' > ' + funcs.func_name +\
                                ' > ' + market_name, 1, log_level)

        # In case of processing time is bigger than *refresh_interval* doesn't sleep.
        if refresh_interval - (time()-start_time) > 0:
            sleep(refresh_interval - (time()-start_time))


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
             log_level=1,
             mp_level="medium"):
    '''
    Backtests strategies.

    Args:
        markets(list): list with markets to backtest or empty to test all available markets.
        entry_funcs(list): list of entry functions to test.
        exit_funcs(list): list of entry functions to test.
        _date(list): init and end point to backtest.
            Ex: '1-1-2017 11:10'
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

    log_level:
       0 - Only presents total.
       1 - Writes logs to file.
       2 - Writes logs to file and prints on screen.
       Default is 2.
    '''

    if not from_file:
    # Connects to DB.
        try:
            db_client = connect_db()
        except Exception as e:
            log(str(e), 0, log_level)
            sys.exit(1)
    else:
        db_client = 0

    # For all markets.
    if not len(markets):
        y = 'y'#raw_input("Want to run all markets? ")
        if y == 'y':
            if from_file:
                markets = get_markets_on_files(interval, base=base_market)
            else:
                markets = get_markets_list(base=base_market)
        else:
            log("Without files to analyse.", 0, log_level)

    # Prevents errors from markets and funcs as str.
    if not isinstance(markets,list): markets=[markets]
    if not isinstance(entry_funcs,list): entry_funcs=[entry_funcs]
    if not isinstance(exit_funcs,list): exit_funcs=[exit_funcs]

    # For selected markets.
    if from_file: markets = manage_files(markets, interval=interval)
    
    log(str(len(markets)) + " files/chunks to analyse...", 1, log_level)

    # Create a multiprocessing Pool
    pool = Pool(num_processors(mp_level))  

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
                             plot,
                             db_client,
                             log_level),
                             markets)

    pool.close()
    pool.join()

    log(" Total > " + str(sum(total)), 1, log_level)

    return sum(total)


def backtest_market(entry_funcs,
                    exit_funcs,
                    interval,
                    _date,
                    smas,
                    emas,
                    from_file,
                    to_file,
                    plot,
                    db_client,
                    log_level,
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

    total = 0

    #market = check_market_name(market)

    entry_points_x = []
    entry_points_y = []

    exit_points_x = []
    exit_points_y = []

    full_log = '[Market analysis]: ' + market + '\n'

    if from_file:
        try:
            data = get_data_from_file(market, interval=interval)
        except Exception as e:
            log(str(e), 0, log_level)
            log('[ERROR] Can\'t find ' + market + ' in files.', 0, log_level)
            return 0

        data_init = data

        if isinstance(_date[0], str):
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
            log(str(e), 0, log_level)
            log('[ERROR] Can\'t find ' + market + ' in BD.', 0, log_level)
            return 0
            #continue

    aux_buy = False
    buy_price = 0
    high_price = 0

    #Tests several functions.
    for i in xrange(len(data)-50):
        if not aux_buy:
            if is_time_to_buy(data[i:i+50], entry_funcs, smas, emas):

                buy_price = data_init.Ask.iloc[i + 49 + date[0]]
                high_price = buy_price

                entry_points_x.append(i + 49)
                entry_points_y.append(data_init.Ask.iloc[i + 49 + date[0]])

                if exit_funcs:
                    aux_buy = True

                full_log += str(data_init.time.iloc[i + 49 + date[0]]) + \
                    ' [BUY] @ ' + str(data_init.Ask.iloc[i + 49 + date[0]]) + '\n'

        else:
            # Used for trailing stop loss.
            if data_init.Last.iloc[i + 49 + date[0]] > high_price:
                high_price = data_init.Last.iloc[i + 49 + date[0]]

            if is_time_to_exit(data[i:i+50],
                            exit_funcs,
                            smas,
                            emas,
                            stop = 0,
                            bought_at=buy_price,
                            max_price=high_price):

                exit_points_x.append(i+49)
                exit_points_y.append(data_init.Bid.iloc[i + 49 + date[0]])

                aux_buy = False

                total += round(((data_init.Bid.iloc[i + 49 + date[0]] -
                                buy_price) /
                                buy_price)*100, 2)

                full_log += str(data_init.time.iloc[i + 49 + date[0]]) + \
                    ' [SELL]@ ' + str(data_init.Bid.iloc[i + 49 + date[0]]) + '\n'

                full_log += '[P&L] > ' + str(total) + '%.' + '\n'

    del data_init

    # Use plot_data for just a few markets. If you try to run plot_data for several markets, 
    # computer can start run really slow.
    try:
        if plot:
            plot_data(data,
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
        log("[ERROR] Ploting data: " + str(e), 0, log_level)

    del data
    #if len(exit_points_x):
    #    log(market + ' > ' + str(total), log_level)

    log('[' + market + '][TOTAL]> ' + str(total)  + '%.', 0, log_level)

    log(full_log, 1, log_level)

    if isnan(total): return 0

    return total