"""
    cryptoalgotrading.py

    Need to import this file in order to use this framework.
"""
# TODO - improve multiprocessing usage.
# TODO - implement MPI.
# TODO - improve DB connection.
# TODO - improve multiprocessing display information.
# TODO - break big files into smaller ones.
# TODO - backtest based on pandas.Dataframe.

import sys
import signal

import pandas as pd
from numpy import isnan
from time import time, ctime, sleep
from binance.client import Client as Binance
from warnings import simplefilter
from functools import partial
import cryptoalgotrading.var as var
from cryptoalgotrading.riskmanagement import Bittrex
from cryptoalgotrading.riskmanagement import Binance as Bnb
from multiprocessing import Pool, Manager
from cryptoalgotrading.aux import get_markets_list, \
                Bittrex, stop_loss, trailing_stop_loss, \
                timeit, safe, connect_db, get_markets_on_files, \
                manage_files, num_processors, plot_data, \
                get_data_from_file, time_to_index, \
                get_historical_data, binance2btrx, \
                desktop_notification
import logging as log

manager = Manager()
cached = manager.dict()

# Prevents FutureWarning from Pandas.
simplefilter(action='ignore', category=FutureWarning)


def signal_handler():
    log.info(f"You pressed Ctrl+C!")
    sys.exit(0)


@safe
def is_time_to_exit(data,
                    funcs,
                    smas=var.default_smas,
                    emas=var.default_emas,
                    stop=1,
                    bought_at: float = 0,
                    max_price: float = 0,
                    count=-1):
    """
    Detects when is time to exit trade.

    stop variable:
    0 -> no stop loss [DANGEROUS]
    1 -> regular stop loss
    2 -> trailing stop loss
    """

    #if count == 0:
    #    return True

    if stop == 1:
        if stop_loss(data.Last.iloc[-1], 
                     bought_at, 
                     percentage=var.stop_loss_prcnt):
            log.debug(f"[FUNC] Stop-loss")
            return True
    elif stop == 2:
        if trailing_stop_loss(data.Last.iloc[-1], 
                              max_price, 
                              percentage=var.trailing_loss_prcnt):
            log.debug(f"[FUNC] Trailing stop-loss")
            return True

    for func in funcs:
        if func(data, smas=smas, emas=emas):
            log.debug(f"[FUNC] {func.__name__}")
            return True

    return False


@safe
def is_time_to_buy(data,
                   funcs,
                   smas=var.default_smas,
                   emas=var.default_emas):
    """
    Detects when is time to enter.
    """

    for func in funcs:
        if func(data, smas=smas, emas=emas):
            log.debug(f"[FUNC] {func.__name__}")
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
                 # plot=False
                 ):
    """
    Simulates a working bot, in realtime or in faster speed,
     using pre own data from DB or file,
     to test an autonomous bot on a specific market.

    Args:
        market(string): list with markets to backtest or
            empty to run all available markets.
        entry_funcs(list): list of entry functions to test.
        exit_funcs(list): list of entry functions to test.
        interval(string): time between measures.
        smas(list): list of SMA values to use.
        emas(list): list of EMA values to use.
        refresh_interval(int): Refresh rate.
        main_coins(list):
    """

    #plt.ion()

    signal.signal(signal.SIGINT, signal_handler)

    date = [0,0]

    total = 0

    # market = check_market_name(market)

    entry_points_x = []
    entry_points_y = []

    exit_points_x = []
    exit_points_y = []

    if not isinstance(entry_funcs, list): entry_funcs=[entry_funcs]
    if not isinstance(exit_funcs, list): exit_funcs=[exit_funcs]

    log.info(f"[Market analysis]: {market}")

    if from_file:
        try:
            data = get_data_from_file(market, interval=interval)
        except Exception as e:
            log.error(f"Unable to get data from file: {e}")
            log.error(f"Unable to find {market} in files.")
            return 0

        data_init = data

        # if type(_date[0]) is str:
        #    date[0], date[1] = time_to_index(data, _date)

        # if date[1] == 0:
        #    data = data[date[0]:]

        # else:
        #    data = data[date[0]:date[1]]

    else:
        try:
            data = get_historical_data(
                                    market,
                                    interval=interval)
            date[0], date[1] = 0, len(data)
            data_init = data
            
        except Exception as e:
            log.error(f"Unable to get data from file: {e}")
            log.error(f"Unable to find {market} in DB.")
            return 0

    aux_buy = False
    buy_price = 0
    high_price = 0

    # plt.show()

    # Tests several functions.
    for i in range(len(data)-110):
        start_time = time()
        # print(data_init.Last.iloc[i])
        if not aux_buy:
            if is_time_to_buy(data[i:i+110], entry_funcs, smas, emas):

                buy_price = data_init.Ask.iloc[i + 109 + date[0]]
                high_price = buy_price

                entry_points_x.append(i + 109)
                entry_points_y.append(data_init.Ask.iloc[i + 109 + date[0]])

                if exit_funcs:
                    aux_buy = True

                log.info(f'''{data_init.time.iloc[i + 109 + date[0]]} \
                     [BUY] @ {data_init.Ask.iloc[i + 109 + date[0]]}''')

        else:
            # Used for trailing stop loss.
            if data_init.Last.iloc[i + 109 + date[0]] > high_price:
                high_price = data_init.Last.iloc[i + 109 + date[0]]

            if is_time_to_exit(data[i:i+110],
                               exit_funcs,
                               smas,
                               emas,
                               stop=1,
                               bought_at=buy_price,
                               max_price=high_price):

                exit_points_x.append(i+109)
                exit_points_y.append(data_init.Bid.iloc[i + 109 + date[0]])

                aux_buy = False

                total += round(((data_init.Bid.iloc[i + 109 + date[0]] -
                                buy_price) /
                                buy_price)*100, 2)

                log.info(f'''{data_init.time.iloc[i + 109 + date[0]]} \
                     [SELL]@ {data_init.Bid.iloc[i + 109 + date[0]]}''')

                log.info(f'[P&L] > {total}%.')

        # plt.plot(data.Last.iloc[i:i+50])
        # plt.draw()
        # plt.clf()

        # In case of processing time is bigger than *refresh_interval* doesn't sleep.
        if refresh_interval - (time()-start_time) >= 0:
            sleep(refresh_interval - (time()-start_time))

    return total


def realtime(exchanges,
             entry_funcs,
             exit_funcs,
             trading_markets=None,
             interval=var.default_interval,
             smas=var.default_smas,
             emas=var.default_volume_emas,
             refresh_interval=10,
             simulation=True,
             main_coins=("BTC", "USDT"),
             log_level=1):
    """
    Bot using realtime data, doesn't need DB or csv files to work.

    Args:
        exchanges(list): list of exchanges.
        entry_funcs(list): list of entry functions to test.
        exit_funcs(list): list of entry functions to test.
        markets(string): list with markets to backtest or empty to run all available markets.
        interval(string): time between measures.
        smas(list): list of SMA values to use.
        emas(list): list of EMA values to use.
        refresh_interval(int): Data refresh rate.
        simulation(bool): Defines if it's running as a simulation or real money mode.
        main_coins(tuple): tuple of main coins.
        log_level: log level
    """
    markets = []

    if trading_markets is None:
        trading_markets = []

    signal.signal(signal.SIGINT, signal_handler)

    validate = smas[-1] + 5

    nr_exchanges = len(exchanges)

    if not isinstance(exchanges, list):
        exchanges = [exchanges]
    if not isinstance(entry_funcs, list):
        entry_funcs = [entry_funcs]
    if not isinstance(exit_funcs, list):
        exit_funcs = [exit_funcs]

    portfolio = {}  # Owned coins list.
    coins = {}

    # Bittrex exchange
    if "bittrex" in exchanges:
        log.debug(f"Starting Bot with Bittrex")
        if simulation:
            log.debug("[MODE] Simulation")
            bt = Bittrex('', '')
            nr_exchanges -=1
        else:
            log.debug("[MODE] Simulation")
            try:
                bt = Bittrex(var.ky, var.sct)
            except Exception as e:
                log.error(f"Unable to connect to Bittrex: {e}")
                return 1
            
    # Binance exchange
    if "binance" in exchanges:
        log.debug("Starting Bot with Binance")
        if simulation:
            log.debug("[MODE] Simulation")
            try:
                bnb = Binance('', '')
                nr_exchanges -= 1
            except Exception as e:
                log.error(f"Unable to connect to Binance: {e}")
        else:
            log.debug("[MODE] Real Money")
            try:
                bnb = Bnb()
            except Exception as e:
                log.error(f"Unable to connect to Binance - {e}")
                return 1

    if not nr_exchanges:
        log.error('sin exchanges jose')
        sys.exit(1)

    while True:
        start_time = time()

        if "bittrex" in exchanges:
            markets += bt.get_market_summaries()['result']
        if "binance" in exchanges:
            markets += bnb.get_ticker()

        for market in markets:
            if 'MarketName' in market:
                market_name = 'BT_' + str(market['MarketName'])
            elif 'symbol' in market:
                market = binance2btrx(market)
                market_name = 'BN_' + market['MarketName']

            global_market_name = str(market['MarketName'])

            # Check if it's on of the trading pairs.
            if len(trading_markets) > 0:
                if market_name not in trading_markets:
                    continue

            # Checks if pair is included in main coins.
            if (market_name.startswith('BT_') and market_name.split('-')[0] in main_coins) or \
                    (market_name.startswith('BN_') and market_name.endswith(main_coins)):

                # Checks if market already exists in analysed coins.
                if market_name in coins:

                    # Checks if has enough data to analyse.
                    if coins[market_name] == validate:
                        locals()[market_name] = pd.DataFrame.append(locals()[market_name],
                                                                    [market]).tail(validate)
                    # If not, adds data and keep going.
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

                if '-' in market_name:
                    # Renames OpenBuy and OpenSell in Bittrex
                    data = locals()[market_name].rename(index=str,
                                                        columns={
                                                            "OpenBuyOrders": "OpenBuy",
                                                            "OpenSellOrders": "OpenSell"})
                else:
                    data = locals()[market_name]

                # Checks if coin is in portfolio and looks for a sell opportunity.
                if market_name in portfolio:

                    # Needed to make use of stop loss and trailing stop loss functions.
                    if portfolio[market_name]['max_price'] < data.Bid.iloc[-1]:
                        portfolio[market_name]['max_price'] = data.Bid.iloc[-1]

                    if is_time_to_exit(data,
                                       exit_funcs,
                                       bought_at=float(portfolio[market_name]['bought_at']),
                                       max_price=float(portfolio[market_name]['max_price']),
                                       count=portfolio[market_name]['count'],
                                       stop=var.stop_type):

                        if not simulation:
                            # Binance market
                            if market_name.startswith('BN_'):
                                # Market Sell
                                success, sell_res = bnb.sell(market_name.replace('BN_', ''))
                                #portfolio[market_name]['quantity']
                                #data.Bid.iloc[-1])

                                if success:
                                    sold_at = float(sell_res['fills'][0]['price'])

                            # Bittrex market
                            elif market_name.startswith('BT_'):
                                success, sell_res = bt.sell(market_name.replace('BT_', ''),
                                                            portfolio[market_name]['quantity'],
                                                            data.Bid.iloc[-1])
                                if success:
                                    sold_at = sell_res

                            if not success:
                                log.error(f'[ERROR] {sell_res}')
                                continue

                            log.info(f'[SELL] {global_market_name} @ {sold_at}')
                            if var.desktop_info:
                                desktop_notification(global_market_name, f'Sold @ {sold_at}')

                            res = ((sold_at - portfolio[market_name]['bought_at']) /
                                   portfolio[market_name]['bought_at'])*100

                        # SIMULATION
                        else:
                            log.info(f'[SELL] {global_market_name} @ {data.Bid.iloc[-1]}')

                            res = ((data.Bid.iloc[-1] - portfolio[market_name]['bought_at']) /
                                   portfolio[market_name]['bought_at'])*100

                        if var.commission:
                            res -= var.bnb_commission
                        log.info(f'[P&L] {global_market_name} > {res:.2f}%.')

                        locals()[market_name].to_csv(f"df_{market_name}-{ctime(time())}.csv")
                        del locals()[market_name]
                        del portfolio[market_name]
                        coins.pop(market_name)

                    # If it's not time to exit, increment count.
                    else:
                        portfolio[market_name]['count'] += 1

                # If the coin is not on portfolio, checks if it's time to buy.
                else:
                    if is_time_to_buy(data, entry_funcs):
                        # REAL
                        if not simulation:
                            # Binance
                            if market_name.startswith('BN_'):
                                # Limit buy
                                # success, msg = bnb.buy(market, data.Ask.iloc[-1]*1.01)
                                # Market buy
                                success, ret = bnb.buy(market_name.replace('BN_', ''))

                            # Bittrex
                            elif market_name.startswith('BT_'):
                                success, ret = bt.buy(market_name.replace('BT_', ''), data.Ask.iloc[-1]*1.01)

                            if success:
                                # TODO - Implement portfolio for Bittrex
                                portfolio[market_name] = {
                                    'bought_at': float(ret['fills'][0]['price']),
                                    'max_price': float(ret['fills'][0]['price']),
                                    'quantity': float(ret['executedQty']),
                                    'count': 0}

                                log.info(f"[BUY] {global_market_name} @ {portfolio[market_name]['bought_at']}")
                                if var.desktop_info:
                                    desktop_notification(global_market_name,
                                                         f"Buy @ {portfolio[market_name]['bought_at']}")

                            elif 'error' in ret:
                                log.info(f"[ERROR] Unable to buy {global_market_name} @ {data.Ask.iloc[-1]}")
                                log.info(f"       [MSG] {ret['error']}")

                        # SIMULATION
                        else:
                            portfolio[market_name] = {
                                'bought_at': data.Ask.iloc[-1],
                                'max_price': data.Ask.iloc[-1],
                                'quantity': 1,
                                'count': 0
                            }
                            log.info(f'[BUY] {global_market_name} @ {data.Ask.iloc[-1]}')

        del markets
        markets = []
        # In case of processing time is bigger than *refresh_interval* doesn't sleep.
        if refresh_interval - (time()-start_time) >= 0:
            sleep(refresh_interval - (time()-start_time))


@timeit
def backtest(markets,
             entry_funcs,
             exit_funcs=None,
             _date=None,
             smas=var.default_smas,
             emas=var.default_emas,
             interval=var.default_interval,
             plot=False,
             to_file=True,
             from_file=False,
             exchange="bittrex",
             base_market='BTC',
             log_level=1,
             mp_level="medium"):
    """
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
    """

    if _date is None:
        _date = [0, 0]

    if exit_funcs is None:
        exit_funcs = []

    signal.signal(signal.SIGINT, signal_handler)

    # global cached

    if not from_file:
        # Connects to DB.
        try:
            db_client = connect_db()
        except Exception as e:
            log.exception(e)
            sys.exit(1)
    else:
        db_client = 0

    # For all markets.
    if not len(markets):
        y = 'y'  # raw_input("Want to run all markets? ")
        if y == 'y':
            if from_file:
                markets = get_markets_on_files(interval, base=base_market)
            else:
                markets = get_markets_list(base_market, exchange)
        else:
            log.error(f"Without files to analyse.")

    # Prevents errors from markets and funcs as str.
    if not isinstance(markets, list):
        markets = [markets]
    if not isinstance(entry_funcs, list):
        entry_funcs = [entry_funcs]
    if not isinstance(exit_funcs, list):
        exit_funcs = [exit_funcs]

    # For selected markets.
    if from_file: 
        markets = manage_files(markets, interval=interval)

    log.debug(f"{str(len(markets))} files/chunks to analyse...")

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
                             exchange,
                             db_client,
                             log_level),
                     markets)

    pool.close()
    pool.join()

    log.info(f' Total > {sum(total)}')
    if var.desktop_info:
        desktop_notification("Backtest completed", f'Result: {sum(total)}')

    for k in cached.keys():
        if cached[k]['last'] < 1:
            del cached[k]
        else:
            cached[k]['last'] = cached[k]['last']-1

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
                    exchange,
                    db_client,
                    log_level,
                    market):
    """
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
        market(string): market to backtest.

    Returns:
        float: returns backtests profit & loss value for applied strategies.
    """

    date = [0, 0]

    total = 0

    # market = check_market_name(market)
    # global cached
    is_cached = False 

    entry_points_x = []
    entry_points_y = []

    exit_points_x = []
    exit_points_y = []

    full_log = '[Market analysis]: ' + market + '\n'

    if from_file:
        try:
            data = get_data_from_file(market, interval=interval)
        except Exception as e:
            log.exception(e)
            log.error(f"Can\'t find {market} in files")
            return 0

        data_init = data

        if isinstance(_date[0], str):
            date[0], date[1] = time_to_index(data, _date)
        else:
            date = _date
        
        if date[1] == 0:
            data = data[date[0]:]
        else:
            data = data[date[0]:date[1]]

    else:
        if market in cached and \
           cached[market]['interval'] == interval and \
           cached[market]['init_date'] == _date[0] and \
           cached[market]['end_date'] == _date[1]:
            # Check if cached data is the same as you want.
            data = cached[market]['data']
            cached[market]['last'] = 2
            is_cached = True
        else:
            try:
                data = get_historical_data(
                                        market,
                                        interval=interval,
                                        init_date=_date[0],
                                        end_date=_date[1],
                                        exchange=exchange)
                date[0], date[1] = 0, len(data)
            except Exception as e:
                log.exception(e)
                log.error(f"Unable to find {market} in BD.")
                return 0
            # continue

        data_init = data

    aux_buy = False
    buy_price = 0
    high_price = 0

    # Test for volume.
    # if data.BaseVolume.mean() < 20:
    #    log(full_log, 1, log_level)
    #    del data
    #    del data_init
    #    return 0

    # Tests several functions.
    for i in range(len(data)-110):
        if not aux_buy:
            if is_time_to_buy(data[i:i+110], entry_funcs, smas, emas):
                buy_price = data_init.Ask.iloc[i + 109 + date[0]]
                high_price = buy_price

                entry_points_x.append(i + 109)
                entry_points_y.append(data_init.Ask.iloc[i + 109 + date[0]])

                if exit_funcs:
                    aux_buy = True

                full_log += str(data_init.time.iloc[i + 109 + date[0]]) + \
                    ' [BUY] @ ' + str(data_init.Ask.iloc[i + 109 + date[0]]) + '\n'

        else:
            # Used for trailing stop loss.
            if data_init.Last.iloc[i + 109 + date[0]] > high_price:
                high_price = data_init.Last.iloc[i + 109 + date[0]]

            if is_time_to_exit(data[i:i+110],
                               exit_funcs,
                               smas,
                               emas,
                               stop=1,
                               bought_at=buy_price,
                               max_price=high_price):

                exit_points_x.append(i+109)
                exit_points_y.append(data_init.Bid.iloc[i + 109 + date[0]])

                aux_buy = False

                total += round(((data_init.Bid.iloc[i + 109 + date[0]] -
                                buy_price) /
                                buy_price)*100, 2)

                if var.commission:
                    total -= var.bnb_commission

                full_log += str(data_init.time.iloc[i + 109 + date[0]]) + \
                    ' [SELL]@ ' + str(data_init.Bid.iloc[i + 109 + date[0]]) + '\n'

                full_log += '[P&L] > ' + str(total) + '%.' + '\n'

    del data_init

    # Use plot_data for just a few markets. If you try to run plot_data for several markets,
    # computer can start run really slow.
    try:
        if plot:
            plot_data(data,
                      name=market,
                      date=[0, 0],
                      smas=smas,
                      emas=emas,
                      entry_points=(entry_points_x, entry_points_y),
                      exit_points=(exit_points_x, exit_points_y),
                      show_smas=True,
                      show_emas=False,
                      show_bbands=False,
                      to_file=to_file)

    except Exception as e:
        log.exception(e)
        log.error(f"Unable to plot data.")

    if not is_cached:
        cached[market] = {'interval': interval,
                          'init_date': _date[0],
                          'end_date': _date[1],
                          'data': data,
                          'last': 2}

    # if len(exit_points_x):
    #    log(market + ' > ' + str(total), log_level)

    log.info(f"[{market}][TOTAL]> {total:.2f}")

    log.debug(full_log)

    if isnan(total):
        log.error("Total is isnan")
        return 0

    return total
