
import unittest

from cryptoalgotrading.aux import get_data_from_file
from cryptoalgotrading.exit import cross_smas


class TestExit(unittest.TestCase):


    def test_cross_smas(self):

        q = get_data_from_file("BTC-XRP", interval='10m')

        self.assertEqual(cross_smas(q[4778:4778+50],
                                    [4,8,12],
                                    [4,8,12]),
                        False)
        self.assertEqual(cross_smas(q[4779:4779+50],
                                    [4,8,12],
                                    [4,8,12]),
                        True)
        self.assertEqual(cross_smas(q[4780:4780+50],
                                    [4,8,12],
                                    [4,8,12]),
                        False)


if __name__ == '__main__':
    unittest.main()
