"""
    entry.py

    Entry functions.
"""


def cross_smas(data, smas=[5, 10], emas=[10]):
    '''
    Checks if it's an entry point based on crossed smas.
    '''
    if data.Last.rolling(smas[0]).mean().iloc[-1] > \
       data.Last.rolling(smas[1]).mean().iloc[-1] and \
       data.Last.rolling(smas[0]).mean().iloc[-2] < \
       data.Last.rolling(smas[1]).mean().iloc[-2]:
        return True

    return False
