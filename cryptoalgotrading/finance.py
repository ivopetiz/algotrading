"""
finance.py

Finance functions responsible for data ***
"""


def bollinger_bands(price, window_size=10, num_of_std=3):
    """Gets bolinger bands."""
    rolling_mean = price.rolling(window=window_size).mean()
    rolling_std = price.rolling(window=window_size).std()
    upper_band = rolling_mean + (rolling_std * num_of_std)
    lower_band = rolling_mean - (rolling_std * num_of_std)

    return upper_band, lower_band, rolling_mean
