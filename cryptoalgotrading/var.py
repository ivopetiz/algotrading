"""
    var.py

    Framework predefined variables.

    It is important to define some environment variables before use this
    framework if user wants to use DB and Exchanges' credentials.
"""

from os import getenv
#import lib_bittrex

log = True
global_log_level = 2

# DATABASE VARIABLES
# Best option should be define vars on system
# and then get environment variables.
db_user = getenv('DB_USER') or "user"
db_password = getenv('DB_PASSWD') or "passwd"
db_name = getenv('DB_NAME') or "bd"

data_dir = getenv('DATA_DIR') or "."
logs_dir = getenv('LOGS_DIR') or "."

LOG_FILENAME = logs_dir + '/indicators.log'

fig_dir = "figs/"

db_host = getenv('db_host') or 'localhost'
db_port = getenv('db_port') or 8086

# interval must be coincident with Influxdb intervals.
default_interval = '10m'

default_smas = [10, 20, 30]
default_emas = [2, 4, 8]
default_volume_smas = [3, 6]
default_volume_emas = [3, 6]
default_mom = 4

validade = 50
refresh_interval = 60 # interval in seconds.

# pairs first market.
main_coins = ["BTC", "USDT"]

exchange = 'bittrex'

ky = getenv('API_KEY') or ""
sct = getenv('API_SECRET') or ""

# Add API Key and API Secret as variables if needed.
#try:
#    bt = lib_bittrex.Bittrex(environ['API_KEY'], environ['API_SECRET'])
#except Exception as e:
#    bt = lib_bittrex.Bittrex("","")
