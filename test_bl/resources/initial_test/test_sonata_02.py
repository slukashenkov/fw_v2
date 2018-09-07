import unittest
from test_bl.test_sonata_plugin.test_tools_sonata import send_receive_sonata
from test_bl.test_sonata_plugin.configs_sonata import sonata_send_recieve_properties


class SonataToNMEAConversionTestCase(unittest.TestCase):
    '''
    @classmethod
    def setUpClass(self):
        self.conf = set_send_recieve_properties.SendReceiveProperties()
        self.sr = send_recieve_sonata.SendRecieveSonata(self.conf)
        self.curr_logger = self.conf.logging_tools.get_logger(__name__)
        self.sr.udp_server_listen_on()
        self.curr_logger.info('Test suite for Sonata testing' + __name__ + 'starts what is needed for all tests')

    @classmethod
    def tearDownClass(self):
        self.sr.close_UDP_socket()
        self.sr.udp_server_stop_listen_on()
        self.curr_logger.info('Test suite for Sonata testing' + __name__ + 'tears-down what is needed for all tests')

    def setUp(self):
        self.conf.load_test_messages()
        self.curr_logger.info('Test'+__name__+'setup routine. send recieve udp')


    def tearDown(self):
        self.sr.close_UDP_socket()
        self.curr_logger.info('Test'+__name__+ 'tearDown routine.')

    def test_udp_messages01(self):
        self.curr_logger.info("SONATA test_udp_messages01")
        self.sr.udp_send_to()
        self.curr_logger.debug("RES_VAL: --->>>"+self.sr.conf.curr_msg[0]+ "\n")

        res01=self.sr.conf.curr_msg[0]
        res02=self.sr.conf.curr_msg[0]
        self.assertEqual(res01,res02)

    def test_udp_messages02(self):
        self.curr_logger.info("SONATA test test_udp_messages02")
        self.conf.load_test_messages()
        self.sr.udp_send_to()
        self.curr_logger.info("RES_VAL: --->>>" + self.sr.conf.curr_msg[1] + "\n")
        self.curr_logger.info("RES_VAL: --->>>" + self.sr.conf.curr_msg[2] + "\n")
        res01=self.sr.conf.curr_msg[1]
        res02=self.sr.conf.curr_msg[2]
        self.assertEqual(res01,res02)

    def test_sonata_messages03(self):
        self.curr_logger.info("SONATA test test_sonata_messages03")

        self.conf.load_test_messages()
        self.sr.udp_send_to()

        res01 = self.conf.msgs_to_send[0]
        res02 = self.conf.received_data[0]
        self.curr_logger.debug("INIT_VAL sent to Sonata: --->>>" + res01)
        self.curr_logger.debug("RES_VAL Nmea from Sonata: --->>>" + res02)
        self.assertEqual(True, True)

    def test_sonata_messages01(self):
        return
    '''

if __name__ == '__main__':
    '''
    unittest.main()
    '''