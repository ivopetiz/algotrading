"""
    var.py
    
    Framework predefined variables.

    It is important to define some environment variables before use this 
    framework if user wants to use DB and Exchanges' credentials.
"""

import os
import lib_bittrex

log = True


# DATABASE VARIABLES
# Best option should be define vars on system 
# and then get environment variables to here.
try:
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWD']
    db_name = os.environ['DB_NAME']
    data_dir = os.environ['DATA_DIR']
    logs_dir = os.environ['LOGS_DIR']
    LOG_FILENAME = logs_dir + '/indicators.log'
except:
    db_user = "user"
    db_password = ""
    db_name = "db"
    data_dir = "."
    logs_dir = "."
    LOG_FILENAME = logs_dir + '/indicators.log'

db_host = 'localhost'
db_port = 8086

# interval must be coincident with Influxdb intervals.
default_interval = '10m'

default_smas = [10,20,30]
default_emas = [2,4,8]
default_volume_smas = [3,6]
default_volume_emas = [3,6]
default_mom = 4

validade = 50
refresh_interval = 60 # interval in seconds.

# pairs first market.
main_coins=["BTC","USDT"]

exchange = 'bittrex'

# Add API Key and API Secret as variables if needed.
try:
    bt = lib_bittrex.Bittrex(os.environ['API_KEY'], os.environ['API_SECRET'])

except:
    bt = lib_bittrex.Bittrex("","")
