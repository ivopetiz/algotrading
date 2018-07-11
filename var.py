"""
    var.py
    
    Framework predefined variables.

    It is important to define some environment variables before use this 
    framework if user wants to use DB and Exchanges' credintials.
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

except:
    db_user = "random"
    db_password = ""
    db_name = "db"

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
refresh_interval = 60

exchange = 'bittrex'

LOG_FILENAME = 'indicators.log'

# Add API Key and API Secret as variables if needed.
try:
    bt = lib_bittrex.Bittrex(os.environ['API_KEY'], os.environ['API_SECRET'])

except:
    bt = lib_bittrex.Bittrex("","")
