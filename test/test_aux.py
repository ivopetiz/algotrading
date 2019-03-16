import unittest
import pandas
from cryptoalgotrading.var import data_dir
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
        self.assertEqual(check_market_name("gobtc",exchange='binance'),"GOBTC")

    def test_get_time_right(self):
        self.assertEqual(get_time_right("1-2-2018"), '2018-2-1T00:00:00Z')
        self.assertEqual(get_time_right("1-2-2018 23:23"), '2018-2-1T23:23:00Z')
        self.assertEqual(get_time_right("1/2/2018 22:22"), '2018-2-1T22:22:00Z')
        self.assertEqual(get_time_right("1/2"), '2019-2-1T00:00:00Z')
        self.assertEqual(get_time_right("1-2"), '2019-2-1T00:00:00Z')


    def test_num_processors(self):
        self.assertEqual(num_processors("low"), 1)
        self.assertEqual(num_processors(2), 2)

    def test_beep(self):
        self.assertEqual(beep(), 0)


    def test_log(self):
        self.assertEqual(log("Running unit tests..."), 0)


    #def test_connect_db(self):
    #    self.assertEqual()


    def test_get_markets_list(self):
        self.assertTrue(type(get_markets_list()) is list)
        self.assertTrue(type(get_markets_list(base='BTC')) is list)
        self.assertTrue(type(get_markets_list(exchange='binance',base='BTC')) is list)
        self.assertTrue(type(get_markets_list(exchange='cryptopia')) is bool)


    def test_get_markets_on_files(self):
        self.assertEqual(get_markets_on_files('10m'), ["BTC-SRN","BTC-XRP"])


    #def test_get_historical_data(self):
    #    self.assertEqual(4,4)


    #def test_get_last_data(self):
    #    self.assertEqual(4,4)


    def test_detect_init(self):
        self.assertIsInstance(detect_init(get_data_from_file("BTC-SRN",interval='10m')),
                                          pandas.core.frame.DataFrame)


    def test_plot_data(self):
        self.assertEqual(plot_data(get_data_from_file("BTC-SRN",
                                                      interval='10m'),
                                                      to_file=True), 
                                                            True)
        self.assertEqual(plot_data(get_data_from_file("BTC-SRN",
                                                      interval='10m'),
                                                      entry_points=[10,30,50],
                                                      exit_points=[20,40,60],
                                                      to_file=True,
                                                      show_smas=True,
                                                      show_emas=True,
                                                      show_bbands=True,
                                                      ),
                                                            True)

    #def test_get_histdata_to_file(self):
    #    self.assertEqual(,4)


    def test_get_data_from_file(self):
        self.assertIsInstance(get_data_from_file("BTC-SRN",
                                                 interval='10m'),
                              pandas.core.frame.DataFrame)
        #self.assertIsInstance(get_data_from_file("BTC-SRN",AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQUUUUUUUUUUUUUUUUUUUUUUUUUUUUUIIIIIIIIIIIIIIIIIIIIII
        #                                         interval='10m',
        #                                         filetype='hdf'),
        #                      pandas.core.frame.DataFrame)

    def test_time_to_index(self):
        self.assertEqual(time_to_index(get_data_from_file("BTC-SRN",interval='10m'),
                                                        ['01-03-2018','04-03-2018']),
                                                            (33568, 33998))
        self.assertEqual(time_to_index(get_data_from_file("BTC-SRN",interval='10m'),
                                                        ['01-03-2018 00:00','04-03-2018']),
                                                            (33568, 33998))

    #def test_timeit(self):
    #    self.assertEqual(timeit(),)

    def test_file_lines(self):
        self.assertEqual(file_lines(data_dir + "/hist-10s/BTC-DGB.csv"), 5088)


    def test_manage_files(self):
        self.assertEqual(manage_files(["BTC-XRP"],'10m'),['BTC-XRP'])
        self.assertEqual(manage_files(["BTC-XXX"],'10m'),[])


if __name__ == '__main__':
    unittest.main()
