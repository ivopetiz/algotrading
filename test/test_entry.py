
import unittest

from cryptoalgotrading.aux import get_data_from_file
from cryptoalgotrading.entry import cross_smas


class TestEntry(unittest.TestCase):


    def test_cross_smas(self):

        q = get_data_from_file("BTC-XRP", interval='10m')

        self.assertEqual(cross_smas(q[4416:4416+50],
                                    [4,8,12],
                                    [4,8,12]),
                        False)
        self.assertEqual(cross_smas(q[4417:4417+50],
                                    [4,8,12],
                                    [4,8,12]),
                        True)
        self.assertEqual(cross_smas(q[4418:4418+50],
                                    [4,8,12],
                                    [4,8,12]),
                        False)


if __name__ == '__main__':
    unittest.main()
