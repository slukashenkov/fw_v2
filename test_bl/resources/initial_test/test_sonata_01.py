import unittest


class SonataToNMEAConversionTestCase(unittest.TestCase):
    '''
    @classmethod
    def setUpClass(self):
        self.conf=set_send_recieve_properties
        self.sr=send_recieve_sonata.SendRecieveSonata(self.conf)
        self.curr_logger=self.sr.curr_logger
        self.sr.udp_server_listen_on()

    @classmethod
    def tearDownClass(self):
        self.sr.close_UDP_socket()
        self.sr.udp_server_stop_listen_on()


    def setUp(self):
        self.curr_logger.info('Test'+__name__+'setup routine. send recieve udp')

    def tearDown(self):
        self.curr_logger.info('Test'+__name__+ 'tearDown routine.')


    def test_longitude(self):
        self.curr_logger.info("sonata test longitude \n")
        self.assertEqual('longitude'.upper(), 'LONGITUDE')

    def test_lattitude(self):
        self.curr_logger.info("sonata test lattitude \n")
        self.assertTrue('LATTITUDE'.isupper())
        self.assertFalse('Lattitude'.isupper())


    def test_udp_messages01(self):
        self.curr_logger.info("sonata test send recieve udp \n")
        self.sr.udp_send_to()
        self.curr_logger.debug("RES_VAL: --->>>"+self.sr.conf.msgs_to_send[0]+ "\n")

        res01=self.sr.conf.msgs_to_send[0]
        res02=self.sr.conf.msgs_to_send[0]
        self.assertEqual(res01,res02)

    def test_udp_messages02(self):
        self.curr_logger.info("sonata test send recieve udp \n")
        self.sr.udp_send_to()
        self.curr_logger.info("RES_VAL: --->>>" + self.sr.conf.msgs_to_send[1] + "\n")
        self.curr_logger.info("RES_VAL: --->>>" + self.sr.conf.msgs_to_send[2] + "\n")
        res01=self.sr.conf.msgs_to_send[2]
        res02=self.sr.conf.msgs_to_send[2]
        self.assertEqual(res01,res02)

    def test_sonata_messages01(self):
        return
    '''

if __name__ == '__main__':
    '''
    unittest.main()
    '''