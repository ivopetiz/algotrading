# Quickstart guide

Follow this guide to get started with this repository.

[Prerequisites](#prerequisites)

- Linux distribution (tested with Ubuntu 20.04 LTS)
- Python 3.6+ (tested with 3.8.10)
- Ipython3 / Jupyter Notebook
- Pip
- Virtualenv
- Git

[Steps](#steps)

- Clone the repository

    ```bash
    git clone git@github.com:ivopetiz/algotrading.git
    ```

- Enter a virtual environment

    ```bash
    cd algotrading
    virtualenv -p python3.6 env
    source env/bin/activate
    ```

- Install requirements

    ```bash
    pip install -r requirements.txt
    ```

- Get Binance API keys

  - [Create a Binance trading account here](https://www.binance.com/en/activity/referral/offers/claim?ref=CPA_004GZBGTP3&utm_campaign=web_share_copy), if you don't have an account yet.

  - [Get Binance API keys](https://www.binance.com/en/my/settings/api-management).

- Add keys to OS environment variables

    ```bash
    export BINANCE_API_KEY=<your_api_key>
    export BINANCE_API_SECRET=<your_api_secret>
    ```

- Run Crypto Algo Trading in realtime (Fake money mode)

    ```python
    import cryptoalgotrading.entry as entries
    import cryptoalgotrading.exit as exits
    import cryptoalgotrading.cryptoalgotrading as cat

    cat.realtime('binance', 
        entries.cross_smas, 
        exits.cross_smas, 
        interval='1m', 
        refresh_interval=60)
    ```

    You can run the script above in a Jupyter notebook, Ipython or as a Python script.

- Get results

  - A file named `indicators.log` will be created in the current directory.
  - Can be checked in realtime using the command `tail -f indicators.log`

- Next steps:
  
  - Create your own strategies to enter and exit trades.
  - Test your strategies in backtest mode.
  - Run in real money mode.
