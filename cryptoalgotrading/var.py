"""
    var.py

    Framework predefined variables.

    It is important to define some environment variables before use this 
    framework if user wants to use DB and Exchanges' credentials.
"""

from os import environ
from aux import log
#import lib_bittrex

#log = True
global_log_level = 2

# DATABASE VARIABLES
# Best option should be define vars on system 
# and then get environment variables.
try:
    db_user = environ['DB_USER']
    db_password = environ['DB_PASSWD']
    db_name = environ['DB_NAME']

except:
    #log("Could not use environment user and password variables.", 0)
    db_user = "user"
    db_password = "passwd"
    db_name = "bd"

if 'DATA_DIR' in environ:
    data_dir = environ['DATA_DIR']
else:
    data_dir = "."

if 'LOGS_DIR' in environ:
    logs_dir = environ['LOGS_DIR']
else:
    logs_dir = "."

LOG_FILENAME = logs_dir + '/indicators.log'

fig_dir = "figs/"

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

try:
    ky = environ['API_KEY'] 
    sct= environ['API_SECRET']
except Exception:
    log("Could not use environment variables for key and secret.", 1)
    #pass

# Add API Key and API Secret as variables if needed.
#try:
#    bt = lib_bittrex.Bittrex(environ['API_KEY'], environ['API_SECRET'])
#except:
#    bt = lib_bittrex.Bittrex("","")
