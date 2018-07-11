"""
    exit.py

    Exit functions.
"""


def cross_smas(data, smas=[10, 20], emas=[10]):
    '''
    Checks if it's an exit point based on crossed smas.
    '''
    if data.Last.rolling(smas[0]).mean().iloc[-1] < \
       data.Last.rolling(smas[1]).mean().iloc[-1] and \
       data.Last.rolling(smas[0]).mean().iloc[-2] > \
       data.Last.rolling(smas[1]).mean().iloc[-2]:
        return True

    return False

