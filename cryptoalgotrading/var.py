"""
    var.py

    Framework predefined variables.

    It is important to define some environment variables before use this
    framework, if user wants to use DB and Exchanges' credentials.
"""

from os import getenv, getcwd


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

# Stop type:
# - 0: No stop loss method
# - 1: Stop loss
# - 2: Trailing stop loss
# - 3: Both stop loss methods
stop_type = 3
stop_loss_prcnt = 0.5
trailing_loss_prcnt = 1.0

smaller_qnt = 20

validade = 50
refresh_interval = 60  # interval in seconds.

# pairs first market.
main_coins = ["BTC", "USDT"]

default_exchange = 'binance'

ky = getenv('API_KEY') or ""
sct = getenv('API_SECRET') or ""

bnb_ky = getenv('BNC_API_KEY') or ""
bnb_sct = getenv('BNC_API_SECRET') or ""

bnb_commission = 0.075
commission = True

# Uses system notification to present relevant info
desktop_info = True
# Add special effects to notifications
desktop_cool_mode = True

img_profit = f'{getcwd()}/img/profit.png'
img_loss = f'{getcwd()}/img/loss.png'
