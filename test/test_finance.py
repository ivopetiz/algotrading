import unittest
import pandas as pd
from numpy import nan as nan
from cryptoalgotrading.finance import bollinger_bands
from pandas.util.testing import assert_frame_equal

class TestFinance(unittest.TestCase):

    def test_bollinger_bands(self):

        a = [10,12,12,13,9,12,12,13]
        q = pd.DataFrame(a)

        res=(pd.DataFrame([nan,nan,nan,nan,16.129503,16.149725,16.149725,16.729503]),
             pd.DataFrame([nan,nan,nan,nan,6.270497,7.050275,7.050275,6.870497]),
             pd.DataFrame([nan,nan,nan,nan,11.2,11.6,11.6,11.8]))

        assert_frame_equal(bollinger_bands(q,5,3)[0],res[0])
        assert_frame_equal(bollinger_bands(q,5,3)[1],res[1])
        assert_frame_equal(bollinger_bands(q,5,3)[2],res[2])
