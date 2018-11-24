import unittest
from cryptoalgotrading.aux import *

class TestAux(unittest.TestCase):


    def test_trailing_stop_loss(self):
        self.assertEqual(trailing_stop_loss(100, 110, 11), False)
        self.assertEqual(trailing_stop_loss(100, 110, 10), False)
        self.assertEqual(trailing_stop_loss(100, 110, 9), True)


    def test_stop_loss(self):
        self.assertEqual(stop_loss(100, 110, 11), False)
        self.assertEqual(stop_loss(100, 110, 10), False)
        self.assertEqual(stop_loss(100, 110, 9), True)


    def test_check_market_name(self):
        self.assertEqual(check_market_name("ETH"), "BTC-ETH")
        self.assertEqual(check_market_name("go"),"BTC-GO")


    def test_get_time_right(self):
        self.assertEqual(get_time_right("1-2-2018"), '2018-2-1T00:00:00Z')
        self.assertEqual(get_time_right("1-2-2018 23:23"), '2018-2-1T23:23:00Z')
        self.assertEqual(get_time_right("1/2/2018 22:22"), '2018-2-1T22:22:00Z')


    def test_num_processors(self):
        self.assertEqual(num_processors("low"), 1)


    def test_beep(self):
        self.assertEqual(beep(), 0)


    def test_log(self):
        self.assertEqual(log("Running unit tests..."), 0)
    
    
    #def test_connect_db(self):
    #    self.assertEqual()


    #def test_get_markets_list(self):
    #    self.assertEqual(4,4)


    #def test_get_markets_on_files(self):
    #    self.assertEqual(4,4)


    #def test_get_historical_data(self):
    #    self.assertEqual(4,4)


    #def test_get_last_data(self):
    #    self.assertEqual(4,4)


    #def test_detect_init(self):
    #    self.assertEqual(4,4)


    #def test_plot_data(self):
    #    self.assertEqual(4,4)


    #def test_get_histdata_to_file(self):
    #    self.assertEqual(4,4)


    #def test_get_data_from_file(self):
    #    self.assertEqual(4,4)


    #def test_time_to_index(self):
    #    self.assertEqual(4,4)


    #def test_timeit(self):
    #    self.assertEqual(timeit(),)

    def test_file_lines(self):
        self.assertEqual(file_lines("../hist-10s/BTC-DGB.csv"), 5088)


if __name__ == '__main__':
    unittest.main()
