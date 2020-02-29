import unittest
import pandas
from cryptoalgotrading.var import data_dir
import cryptoalgotrading.aux as aux

class TestAux(unittest.TestCase):


    def test_trailing_stop_loss(self):
        self.assertEqual(aux.trailing_stop_loss(100, 110, 11), False)
        self.assertEqual(aux.trailing_stop_loss(100, 110, 10), False)
        self.assertEqual(aux.trailing_stop_loss(100, 110, 9), True)


    def test_stop_loss(self):
        self.assertEqual(aux.stop_loss(100, 110, 11), False)
        self.assertEqual(aux.stop_loss(100, 110, 10), False)
        self.assertEqual(aux.stop_loss(100, 110, 9), True)


    def test_check_market_name(self):
        self.assertEqual(aux.check_market_name("ETH"), "BTC-ETH")
        self.assertEqual(aux.check_market_name("go"),"BTC-GO")
        self.assertEqual(aux.check_market_name("gobtc",exchange='binance'),"GOBTC")

    def test_get_time_right(self):
        self.assertEqual(aux.get_time_right("1-2-2018"), '2018-2-1T00:00:00Z')
        self.assertEqual(aux.get_time_right("1-2-2018 23:23"), '2018-2-1T23:23:00Z')
        self.assertEqual(aux.get_time_right("1/2/2018 22:22"), '2018-2-1T22:22:00Z')
        self.assertEqual(aux.get_time_right("1/2"), '2020-2-1T00:00:00Z')
        self.assertEqual(aux.get_time_right("1-2"), '2020-2-1T00:00:00Z')


    def test_num_processors(self):
        self.assertEqual(aux.num_processors("low"), 1)
        self.assertEqual(aux.num_processors(2), 2)

    def test_beep(self):
        self.assertEqual(aux.beep(), 0)


    def test_log(self):
        self.assertEqual(aux.log("Running unit tests..."), 0)


    #def test_connect_db(self):
    #    self.assertEqual()


    def test_get_markets_list(self):
        self.assertIsInstance(aux.get_markets_list(),list)
        self.assertIsInstance(aux.get_markets_list(base='BTC'),list)
        self.assertIsInstance(aux.get_markets_list(exchange='binance',base='BTC'),list)
        self.assertIsInstance(aux.get_markets_list(exchange='cryptopia'),bool)

    def test_get_markets_on_files(self):
        self.assertCountEqual(aux.get_markets_on_files('10m'), ["BTC-SRN","BTC-XRP"])


    #def test_get_historical_data(self):
    #    self.assertEqual(4,4)


    #def test_get_last_data(self):
    #    self.assertEqual(4,4)


    def test_detect_init(self):
        self.assertIsInstance(aux.detect_init(aux.get_data_from_file("BTC-SRN",interval='10m')),
                                          pandas.core.frame.DataFrame)


    def test_plot_data(self):
        self.assertEqual(aux.plot_data(aux.get_data_from_file("BTC-SRN",
                                                      interval='10m'),
                                                      to_file=True),
                                                            True)
        self.assertEqual(aux.plot_data(aux.get_data_from_file("BTC-SRN",
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
        self.assertIsInstance(aux.get_data_from_file("BTC-SRN",
                                                 interval='10m'),
                              pandas.core.frame.DataFrame)
        self.assertIsInstance(aux.get_data_from_file("BTC-DCT",
                                                 interval='10s',
                                                 filetype='hdf'),
                              pandas.core.frame.DataFrame)

    def test_time_to_index(self):
        self.assertEqual(aux.time_to_index(aux.get_data_from_file("BTC-SRN",interval='10m'),
                                                        ['01-03-2018','04-03-2018']),
                                                            (33568, 33998))
        self.assertEqual(aux.time_to_index(aux.get_data_from_file("BTC-SRN",interval='10m'),
                                                        ['01-03-2018 00:00','04-03-2018']),
                                                            (33568, 33998))

    #def test_timeit(self):
    #    self.assertEqual(timeit(),)

    def test_file_lines(self):
        self.assertEqual(aux.file_lines(data_dir + "/hist-10s/BTC-DGB.csv"), 5088)


    def test_manage_files(self):
        self.assertEqual(aux.manage_files(["BTC-XRP"],'10m'),['BTC-XRP'])
        self.assertEqual(aux.manage_files(["BTC-XXX"],'10m'),[])


    def test_binance2btrx(self):
        self.assertEqual(aux.binance2btrx({'symbol': 'TIETABTC',
                                       'askPrice': '12',
                                       'bidPrice': '11',
                                       'count': '333',
                                       'highPrice': '15',
                                       'lastPrice': '11.5',
                                       'lowPrice': '10',
                                       'quoteVolume': '1000',
                                       'volume': '100'})
                                       ,{'MarketName': 'TIETABTC',
                                       'Ask': 12.0,
                                       'BaseVolume': 1000.0,
                                       'Bid': 11.0,
                                       'Count': 333.0,
                                       'High': 15.0,
                                       'Last': 11.5,
                                       'Low': 10.0,
                                       'Volume': 100.0})

if __name__ == '__main__':
    unittest.main()
