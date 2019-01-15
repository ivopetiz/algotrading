"""
    aux.py

    Aux functions needed to do some data manipulation, plot data, etc.
"""


import var
import sys
import matplotlib.pylab as plt

from os import system, listdir, path
from numpy import isnan
from pandas import read_csv, DataFrame
from time import time, localtime
from datetime import datetime, timedelta
from finance import bollinger_bands
from influxdb import InfluxDBClient
from lib_bittrex import Bittrex
from multiprocessing import cpu_count
from logging import basicConfig, debug, DEBUG

plt.ion()

plt.style.use('ggplot')

# Initiates log file.
basicConfig(filename=var.LOG_FILENAME,
                    format='%(asctime)s - %(message)s',
                    datefmt='%d/%m/%Y %H:%M:%S',
                    level=DEBUG)


#####################################################################
## Decorators
def timeit(method):
    '''
    Decorator to measure functions duration.
    '''
    def timed(*args, **kw):
        ts = time()
        result = method(*args, **kw)
        te = time()

        log('Duration: %2.2f sec' % (te-ts), 1)
        return result

    return timed


def safe(method):
    '''
    Decorator to return safe in case of error.
    '''
    def ret(*args, **kw):
        try:
            return method(*args, **kw)

        except Exception as e:
            log(str(e), 2)

        #return result
    return ret
#####################################################################


def connect_db():
    '''
    Connects to Infludb.
    '''

    # returning InfluxDBClient object.
    try:
        conn = InfluxDBClient(var.db_host,
                              var.db_port,
                              var.db_user,
                              var.db_password,
                              var.db_name)

    except Exception as err:
        log("[ERROR] " + str(err))
        sys.exit(1)

    return conn


def get_markets_list(base='BTC', exchange='bittrex'):
    '''
    Gets all coins from a certain market.

    Args:
    - base: if you want just one market. Ex: BTC.
        Empty for all markets.

    Returns:
    - list of markets.
    '''
    if exchange=='bittrex':
        bt = Bittrex('', '')
        ret = [i['MarketName'] for i in bt.get_markets()['result'] if i['MarketName'].startswith(base)]

    #elif exchange=='binance':
    #   TODO

    return ret


def get_markets_on_files(interval, base='BTC'):
    '''
    Gets all coins from a certain market, available on files.

    Args:
    - interval: data interval.
    - base: if you want just one market. Ex: BTC.
        Empty for all markets.

    Returns:
    - list of markets.
    '''
    markets_list=[]

    for file_ in listdir(var.data_dir + '/hist-' + interval):
        if file_.startswith(base):
            markets_list.append(file_.split('.')[0])

    return markets_list


def get_historical_data(market,
                        interval=var.default_interval,
                        init_date=0,
                        end_date=0,
                        exchange='bittrex'):
    '''
    Gets all historical data stored on DB, from a certain market.

    Args:
    - market: str with market.
    - interval: str with time between measures.
        Empty for default_interval.
    - init_date: str with initial datetime.
        Default is 2017-07-10 21:30:00.
    - end_date: str with end datetime.
    - exchange: str with exchange name.

    Returns:
    - market data in pandas.DataFrame.
    '''
    verified_market = check_market_name(market, exchange='bittrex')

    if not init_date:
        init_date = '2018-02-02 00:00:00'
    else:
        init_date = get_time_right(init_date)

    time = "time > \'" + init_date + "\'"

    if end_date:
        end_date = get_time_right(end_date)
        time += " AND time < \'" + end_date + "\'"

    # Gets data from Bittex exchange.
    if exchange is 'bittrex':
        command = "SELECT last(Last) AS Last," +\
            " last(BaseVolume) AS BaseVolume," +\
            " last(High) AS High," +\
            " last(Low) AS Low," +\
            " last(Ask) AS Ask," +\
            " last(Bid) AS Bid," +\
            " last(OpenBuyOrders) AS OpenBuy," +\
            " last(OpenSellOrders) AS OpenSell " + \
            "FROM bittrex WHERE " + time + \
            " AND MarketName='" + verified_market + \
            "' GROUP BY time(" + interval + ")"
    
    # Gets data from Binance exchange.
    elif exchange is 'binance':
        command = "SELECT last(Last) AS Last," +\
            " last(BaseVolume) AS BaseVolume," +\
            " last(High) AS High," +\
            " last(Low) AS Low," +\
            " last(Ask) AS Ask," +\
            " last(Bid) AS Bid," +\
            "FROM bittrex WHERE " + time + \
            " AND MarketName='" + verified_market + \
            "' GROUP BY time(" + interval + ")"
            #" last(OpenBuyOrders) AS OpenBuy," +\
            #" last(OpenSellOrders) AS OpenSell " + \

    #print command
    db_client = connect_db()

    res = db_client.query(command)

    # returning Pandas DataFrame.
    #return pd.DataFrame(list(res.get_points(measurement=exchange)))
    return detect_init(DataFrame(list(res.get_points(measurement=var.exchange))))


def get_last_data(market,
                  last='24',
                  interval=var.default_interval,
                  exchange='bittrex',
                  db_client=0):
    '''
    Gets last data from DB.

    Args:
    - market: str with market.
    - last: int with number of hours from now to get.
        Empty for 24 hours.
    - interval: str with time between measures.
        Empty for default_interval.

    Returns:
    - market data in pandas.DataFrame.
    '''

    end_date = 'now()'

    # date and time format> 2018-02-02 00:00:00
    start_date = format(datetime.now() -
                        timedelta(hours=last),
                        '%Y-%m-%d %H:%M:%S')

    return get_historical_data(market,
                        interval=interval,
                        init_date=start_date,
                        end_date=end_date,
                        exchange=exchange,
                        db_client=db_client)


def detect_init(data):
    '''
    Remove data without without info in case of market
    has started after the implementation of the BD.
    '''
    
    #TODO try to implement this on DB query.
    for i in range(len(data)):
        #TODO remove numpy lib and use other method to detect NaN.
        if not isnan(data.Last.iloc[i]):
            return data[i:len(data)]


def plot_data(data,
              name='',
              date=[0, 0],
              smas=var.default_smas,
              emas=var.default_emas,
              entry_points=[],
              exit_points=[],
              market_name='',
              to_file=False,
              show_smas=False,
              show_emas=False,
              show_bbands=False):
    '''
    Plots selected data.
    entry_points is a tuple of lists: (entry_points_x,entry_points_y)
    '''
    #plt.clf()

    # For when it's called outside backtest.
    if date != [0, 0]:
        if len(data) != date[1] - date[0]:
            data = data[date[0]:date[1]]

    f, (ax1, ax2, ax3) = plt.subplots(3,
                                sharex=True,
                                figsize=(9, 4),
                                gridspec_kw={'height_ratios': [3, 1, 1]})

    ax1.grid(True)
    ax2.grid(True)
    ax3.grid(True)

    # var date is causing conflicts. using name date.
    if date[1] == 0:
        end_date = len(data)
    else:
        end_date = date[1]

    x = range(date[0], end_date)

    ax1.plot(x, data.Last, color='black', linewidth=1, alpha=0.65)

    if show_bbands:
        bb_upper, bb_lower, bb_sma = bollinger_bands(data.Last, 10, 2)
        #ax1.plot(x, bb_upper, color='red', linestyle='none', linewidth=1)
        #ax1.plot(x, bb_lower, color='green', linestyle='none', linewidth=1)

        ax1.fill_between(x, bb_sma, bb_upper, color='green', alpha=0.3)
        ax1.fill_between(x, bb_lower, bb_sma, color='red', alpha=0.3)

    if show_smas:
        for sma in smas:
            ax1.plot(x, data.Last.rolling(sma).mean())

    if show_emas:
        for ema in emas:
            ax1.plot(x, data.Last.ewm(ema).mean())

    if len(entry_points):
        ax1.plot(entry_points[0],
                 entry_points[1],
                 marker='o',
                 linestyle='None',
                 color='green',
                 alpha=0.75)

    if len(exit_points):
        ax1.plot(exit_points[0],
                 exit_points[1],
                 marker='o',
                 linestyle='None',
                 color='red',
                 alpha=0.75)

    ax2.bar(x, data.BaseVolume.iloc[:], 1, color='black', alpha=0.55)

    ax3.plot(x, data.OpenSell.iloc[:])

    plt.xlim(date[0], end_date)
    plt.tight_layout()
    f.subplots_adjust(hspace=0)
    if to_file:
        if not name:
            name = 'fig_test' + str(time())
        f.savefig(var.fig_dir + name + '.pdf', bbox_inches='tight')
        plt.close(f)
    #plt.show()

    return True


def get_histdata_to_file(markets=[],
                         interval=var.default_interval,
                         base_market='BTC',
                         exchange='bittrex'):
    '''
    Gets data from DB to file.
    Prevents excess of DB accesses.
    Saves files to 'hist-<interval>.csv'

    Args:
    - market: list of str with markets.
    - interval: str with time between measures.
        Empty for default_interval.

    Returns:
    - 'True'
    '''

    if type(markets) is str: markets = [markets]

    if not markets: markets = get_markets_list(base_market)

    for market in markets:
        verified_market = check_market_name(market, exchange=exchange)
        print verified_market
        get_historical_data(verified_market,
                            interval=interval, 
                            exchange=exchange).to_csv(
            var.data_dir + '/hist-' + interval +
            '/' + verified_market + '.csv')

    return True


def get_data_from_file(market, interval=var.default_interval, exchange='bittrex'):
    '''
    Gets data from file.

    Args:
    - market: str with market.
    - interval: str with time between measures.
        Empty for default_interval.

    Returns:
    - pd.DataFrame
    '''
    verified_market = check_market_name(market, exchange=exchange)

    return read_csv(var.data_dir + '/hist-' + interval 
                    + '/' + verified_market + '.csv',
                    sep=',', engine='c',            # Optimized for a faster
                    index_col=0, low_memory=True)   # csv reading.


def check_market_name(market, exchange='bittrex'):
    '''
    Avoids abbreviations and lowercases failures.
    '''
    market = market.upper()

    if '-' in market:  # and len(market) > 5:
        return market

    return 'BTC-' + market


def time_to_index(data, _datetime):
    '''
    Converts input time to DB time.
    '''
    #TODO
    # Improve date presentation

    #2017-09-09T06:25:00Z
    #d[(d.time>'2017-09-09T06:25:00Z') & (d.time<'2017-09-09T07:25:00Z')]

    #'1-1-2017 11:10'

    #year, month, day = time.strftime("%Y,%m,%d").split(',')
    dtime = []

    for t in _datetime:

        if ' ' in t:
            t_date, t_time = t.split()
        else:
            t_date = t
            t_time = '00:00'

        try:
            t_day, t_month, t_year = t_date.split('-')
        except:
            t_day, t_month = t_date.split('-')
            t_year = localtime(time())[0]

        t_hour, t_minute = t_time.split(':')

        dtime.append(str(t_year) + '-' +
                     str(t_month) + '-' +
                     str(t_day) + 'T' +
                     str(t_hour) + ':' +
                     str(t_minute) + ':00Z')

    d = data[(data.time > dtime[0]) & (data.time < dtime[1])]

    return d.index[0], d.index[-1]


def get_time_right(date_n_time):

    if ' ' in date_n_time:
        t_date, t_time = date_n_time.split()
    else:
        t_date = date_n_time
        t_time = '00:00'

    if '-' in date_n_time:
        try:
            t_day, t_month, t_year = t_date.split('-')
        except:
            t_day, t_month = t_date.split('-')
            t_year = str(localtime()[0])

    elif '/' in date_n_time:
        try:
            t_day, t_month, t_year = t_date.split('/')
        except:
            t_day, t_month = t_date.split('/')
            t_year = str(localtime()[0])

    t_hour, t_minute = t_time.split(':')

    return t_year + '-' +\
        t_month + '-' +\
        t_day + 'T' +\
        t_hour + ':' +\
        t_minute + ':00Z'


def trailing_stop_loss(last, higher, percentage=10):
    '''
    Trailing stop loss function.
    
    Receives structure with:
        - Last price.
        - Entry point x.
        - Exit percentage [0.1-99.9]
    
    Returns true when trigged.
    '''

    if last <= higher * (1 - (percentage*0.01)):
        return True

    return False


def stop_loss(last, entry_point_x, percentage=5):
    '''
    Stop loss function.
        
    Receives structure with:
        - Last price.
        - Entry point x.
    
    Returns true when trigged.
    '''

    if last <= entry_point_x * (1 - (percentage*0.01)):
        return True

    return False


def num_processors(level="medium"):
    '''
    Decides how many cores will use.
    
    level options:
        low             = 1 core
        medium          = half of available cores.
        high            = left 1 free core.
        max|extreme     = uses all available cores.
        <cores number>  = uses the number of cores specified.
    '''
    mp = cpu_count()
    n_threads = 0

    if level == "low":
        n_threads = 1
    elif level == "medium":
        n_threads = mp/2
    elif level == "high":
        n_threads = mp-1
    elif level == "extreme" or level == "max":
         n_threads = mp
    elif isinstance(level,int) and 0<level<=mp:
        n_threads = level
    else:
        n_threads = mp/2

    log("[INFO] Using " + str(n_threads) + " threads.", 1)

    return n_threads


def beep(duration=0.5):
    '''
    It beeps!
    Used to alert for possible manual entry or exit.
    '''
    freq = 440  # Hz
    system('play --no-show-progress --null --channels 1 synth %s sine %f' %
              (duration, freq))

    return 0


def log(message, level=1, func_level=2):
    '''
    Log function to select the type of log will be done.
    
    Receives:
        - message: str
        - level: int (default=2)

    Returns 0
    '''
    
    #if level > var.global_log_level: return 1
    if func_level > level:
        if level >= 0: debug(message)
        if level >= 1: print message

    return 0


def manage_files(markets, interval='1m'):
    '''
    Manage market files in order to improve framework performance.
    '''
    all_files = []
    markets_name = []

    for market in markets:
        markets_name.append(check_market_name(market))

    if not path.isdir(var.data_dir + "/hist-" + interval):
    	log(var.data_dir + "/hist-" + \
    		interval + "doesn't exist.",0)
    	sys.exit(1)

    for f in listdir(var.data_dir + "/hist-" + interval):
        for market in markets_name:
            if f.startswith(market):
                all_files.append(f.split('.')[0])
                continue

    return all_files


def file_lines(filename):
    '''
    Counts the number of lines in a file
    '''

    f = open(filename)
    lines = 0
    buf_size = 1024 * 1024
    read_f = f.read # loop optimization

    buf = read_f(buf_size)
    while buf:
        lines += buf.count('\n')
        buf = read_f(buf_size)

    return lines


