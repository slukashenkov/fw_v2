import unittest, time, xmlrunner

from collections import deque

from test_bl.test_sonata_plugin.test_tools_sonata import send_receive_sonata, sonata_nmea_msgs_content_process
from test_bl.test_sonata_plugin.configs_sonata import sonata_send_recieve_properties, sonata_suite_config
from test_bl.test_bl_tools import var_utils, external_scripts

#import send_receive_sonata, sonata_nmea_msgs_content_process
#import sonata_send_recieve_properties, sonata_suite_config
#import var_utils, external_scripts


class SonataToNMEAConversionTests02(unittest.TestCase):

        @classmethod
        def setUpClass(self):
            """
            SETUP ENV FOR Sonata Module Test Suite :
            1) INITIAL CONFIG
            2) UDP SERVER to listen for BL responses
            3) UDP Sender
            4) Start Test VM from appropriate image
            5) Start BL with Sonata configs copied to test VM
            :return:
            """
            time.sleep(4)

            '''GET TOOLS OUT'''
            self.__tools__ = var_utils.Varutils()

            '''SETUP CONFIG FILE FOR SUITE'''
            self.conf = sonata_suite_config.SonataSuiteConfig()
            '''SET TEST NAMES QUEUE'''
            self.test_case = deque(self.conf.sonata_tests_names)

            self.curr_logger = self.conf.logging_tools.get_logger(__name__)
            self.__tools__.build_test_banner(mod_name          = 'SONATA',
                                             suit_name         = 'SUITE' + __name__,
                                             ending            = 'SETS UP SENDER AND RECIEVER FOR TEST CLASS',
                                             logging_level     = 'DEBUG',
                                             logger            = self.curr_logger)


            '''SETUP EVERYTHING that pertains to sending receiving (UDP Server/sender data and so on)'''
            self.sr = self.conf.sender_receiver
            curr_udp_srv = self.sr.udp_server_listen_on()

            '''SETUP VIRTUAL TEST ENVIRONMENT ON THIS HOST (VBOX AND IMAGES ASSUMED)'''
            self.__tools__.build_test_banner(mod_name       ='SONATA',
                                             suit_name      ='SUITE' + __name__,
                                             ending         ='SETS UP VIRTUAL ENV FOR TEST CLASS',
                                             logging_level  ='DEBUG',
                                             logger         =self.curr_logger)

            self.ext_scripts = external_scripts.ExtScripts(self.conf)
            '''Log server is started from bootstrap script BUT for for debugging it should be turned on here'''
            #self.ext_scripts.start_log_server()
            self.ext_scripts.set_test_env()
            return

        @classmethod
        def tearDownClass(self):
            self.sr.close_UDP_socket()
            #self.ext_scripts.stop_logserver()
            self.sr.udp_server_stop_listen_on()
            self.ext_scripts.tear_down_test_env()

            self.__tools__.build_test_banner(mod_name           = 'SONATA',
                                              suit_name         = 'SUITE' + __name__,
                                              ending            = 'TEARS DOWN TEST CLASS',
                                              logging_level     = 'DEBUG',
                                              logger            = self.curr_logger)
            return

        def setUp(self):
            """Setup all the common things for the test"""
            #self._testMethodName = "test_sonata_messages01"
            #self.sr.set_udp_sender()


            '''SETUP TEST DATA, UDP SENDER and SEND MESSAGES'''
            self.conf.set_current_test(self.test_case.popleft())
            self.conf.reset_test_messages_received()

            self.__tools__.build_test_banner(mod_name='SONATA',
                                             suit_name='SUITE' + __name__,
                                             ending='SETS UP SENDER FOR TEST CLASS ' + self.conf.curr_test,
                                             logging_level='DEBUG',
                                             logger=self.curr_logger)
            self.sr.load_test_messages()
            self.sr.set_udp_sender()
            self.sr.udp_send_to()
            return

        def tearDown(self):
            time.sleep(4)
            self.curr_logger.info('Test'+__name__+ 'tearDown routine.')
            return

        def test_sonata_messages01(self):
            """
            :return:      """

            '''
            DO AN ACTION ASSUMED TO BE DONE BY EQUPMENT
            MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
            LISTENER HAS BEEN SETUP THEN AS WELL
            '''
            self.__tools__.build_test_banner(mod_name='SONATA',
                                             suit_name='SUITE' + __name__,
                                             ending='EXECUTES TEST BODY ' + self.conf.curr_test,
                                             logging_level='DEBUG',
                                             logger=self.curr_logger)
            '''
            Actual messages that have been sent
            '''
            res01 = self.conf.msgs_to_send[0]
            self.__tools__.build_test_banner(mod_name='SONATA',
                                             suit_name=__name__ + ' running test ' +  self.conf.curr_test,
                                             ending='SENT THIS SONAMTEA MESSAGE: ' + res01,
                                             logging_level='DEBUG',
                                             logger=self.curr_logger)


            '''
            DATA used in messages
            '''
            res02 = self.conf.data_received[0]
            self.__tools__.build_test_banner(mod_name='SONATA',
                                             suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                             ending='SENT THIS SONAMTEA MESSAGE: ' + res02,
                                             logging_level='DEBUG',
                                             logger=self.curr_logger)
            res03=self.conf.data_sent
            self.__tools__.build_test_banner(mod_name='SONATA',
                                             suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                             ending='RECEIVED THIS NMEA MESSAGE: ' + str(res03),
                                             logging_level='DEBUG',
                                             logger=self.curr_logger)

            '''
                CONTENT PROCESSING IS A STARTING POINT for 
                ALL DATA content MANIPULATIONS IN TEST.
                IT DOES:
                    1) Parse RAW data received from BL (router out) 
                    2) Possesses knowledge of data been sent initially
                    3) Makes comparisons         
            '''
            snmea = sonata_nmea_msgs_content_process.SonataNmeaMsgsContentProcessing(self.conf.data_received,
                                                                                     self.conf.data_sent)

            '''
            PARSE one of the received 
            messages into a structure 
            ready for comparison         
            '''
            snmea.packet_indx = 1
            snmea.parse_nmea()
            '''
            Non optimal way
            TOO FAR REMOVED FROM THE TEST
            comparison can be done inside
            enveloping class 
            for 
            CONTENT PROCESSING
            '''
            snmea.key_sent="sonata_id"
            snmea.key_received = "label2"

            snmea.compare_fields()

            '''
            GET VALUES ONLY
            '''
            result01 = int(snmea.get_field_in())
            result02 = snmea.get_field_out()

            '''
                TODO:
                Comparison is should be as selective as possible  
                
            '''
            #snmea.compare_with

            self.curr_logger.info("INIT_VAL sent to Sonata: --->>>" + res01)
            self.curr_logger.info("RES_VAL Nmea from Sonata: --->>>" + res02)

            self.curr_logger.info("Field --->>> " + str(snmea.key_sent) + " <<<--- was sent to Sonata: --->>> " + str(result01))
            self.curr_logger.info("Field --->>> " + str(snmea.key_received) + " <<<--- was received in Nmea message from Sonata: --->>> " + str(result02))

            self.assertEqual(result01,
                             result02)



        #@unittest.skip("Testing various test suite configs")
        def test_sonata_messages02(self):
                """
                :return:
                """

                ''' DO AN ACTION ASSUMED TO BE DONE BY EQUPMENT
                    MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
                    LISTENER HAS BEEN SETUP THEN AS WELL
                '''

                '''

                self.curr_logger.info("===============================================================================|")
                self.curr_logger.info("02 sonata message send send via udp")
                self.conf.set_current_test("test_sonata_messages02")
                # self.conf.load_test_messages()
                '''
                '''
                Setup UDP Server
                '''
                '''
                self.conf.reset_test_messages_received()

                self.sr.load_test_messages()
                self.sr.set_udp_sender()
                self.sr.udp_send_to()
                '''
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name='SUITE' + __name__,
                                                 ending='EXECUTES TEST BODY ' + self.conf.curr_test,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                ''' Actual messages being sent
                '''
                res01 = self.conf.msgs_to_send[0]
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + res01,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)

                '''
                #DATA used in messages
                '''
                res02 = self.conf.data_received[0]
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + res02,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                res03 = self.conf.data_sent
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + str(res03),
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)

                ''' CONTENT PROCESSING IS A STARTING POINT for
                    ALL DATA content MANIPULATIONS IN TEST.
                    IT DOES:
                        1) Parse RAW data received from BL (router out)
                        2) Possesses knowledge of data been sent initially
                        3) Makes comparisons
                '''
                snmea = sonata_nmea_msgs_content_process.SonataNmeaMsgsContentProcessing(self.conf.data_received,
                                                                                         self.conf.data_sent)

                ''' PARSE one of the received
                    messages into a structure
                    ready for comparison
                '''
                snmea.packet_indx = 0
                snmea.parse_nmea()

                '''
                #Non optimal way
                #TOO FAR REMOVED FROM THE TEST
                #comparison can be done inside
                #enveloping class
                #for
                #CONTENT PROCESSING
                '''

                snmea.key_sent = "sonata_id"
                snmea.key_received = "label2"

                snmea.compare_fields()
                '''
                '''
                #GET VALUES ONLY
                '''
                '''
                result01 = int(snmea.get_field_in())
                result02 = snmea.get_field_out()
                '''
                '''
                #TODO:
                #Comparison is should be as selective as possible
                '''
                # snmea.compare_with
                '''
                self.curr_logger.debug("INIT_VAL sent to Sonata: --->>>" + res01)
                self.curr_logger.debug("RES_VAL Nmea from Sonata: --->>>" + res02)

                self.curr_logger.debug("Field " + str(snmea.key_sent) + " sent to Sonata: --->>>" + str(result01))
                self.curr_logger.debug(
                    "Field " + str(snmea.key_received) + "received in Nmea message from Sonata: --->>>" + str(result02))

                self.assertNotEqual(result01,
                                 result02)

        def test_sonata_messages03(self):
                """
                :return:
                """

                ''' DO AN ACTION ASSUMED TO BE DONE BY EQUPMENT
                    MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
                    LISTENER HAS BEEN SETUP THEN AS WELL
                '''

                '''

                self.curr_logger.info("===============================================================================|")
                self.curr_logger.info("02 sonata message send send via udp")
                self.conf.set_current_test("test_sonata_messages02")
                # self.conf.load_test_messages()
                '''
                '''
                Setup UDP Server
                '''
                '''
                self.conf.reset_test_messages_received()

                self.sr.load_test_messages()
                self.sr.set_udp_sender()
                self.sr.udp_send_to()
                '''
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name='SUITE' + __name__,
                                                 ending='EXECUTES TEST BODY ' + self.conf.curr_test,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                ''' Actual messages being sent
                '''
                res01 = self.conf.msgs_to_send[0]
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + res01,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)

                '''
                #DATA used in messages
                '''
                res02 = self.conf.data_received[0]
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + res02,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                res03 = self.conf.data_sent
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + str(res03),
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)

                ''' CONTENT PROCESSING IS A STARTING POINT for
                    ALL DATA content MANIPULATIONS IN TEST.
                    IT DOES:
                        1) Parse RAW data received from BL (router out)
                        2) Possesses knowledge of data been sent initially
                        3) Makes comparisons
                '''
                snmea = sonata_nmea_msgs_content_process.SonataNmeaMsgsContentProcessing(self.conf.data_received,
                                                                                         self.conf.data_sent)

                ''' PARSE one of the received
                    messages into a structure
                    ready for comparison
                '''
                snmea.packet_indx = 0
                snmea.parse_nmea()

                '''
                #Non optimal way
                #TOO FAR REMOVED FROM THE TEST
                #comparison can be done inside
                #enveloping class
                #for
                #CONTENT PROCESSING
                '''

                snmea.key_sent = "sonata_id"
                snmea.key_received = "label2"

                snmea.compare_fields()
                '''
                '''
                #GET VALUES ONLY
                '''
                '''
                result01 = int(snmea.get_field_in())
                result02 = snmea.get_field_out()
                '''
                '''
                #TODO:
                #Comparison is should be as selective as possible
                '''
                # snmea.compare_with
                '''
                self.curr_logger.debug("INIT_VAL sent to Sonata: --->>>" + res01)
                self.curr_logger.debug("RES_VAL Nmea from Sonata: --->>>" + res02)

                self.curr_logger.debug("Field " + str(snmea.key_sent) + " sent to Sonata: --->>>" + str(result01))
                self.curr_logger.debug(
                    "Field " + str(snmea.key_received) + "received in Nmea message from Sonata: --->>>" + str(result02))

                self.assertNotEqual(result01,
                                 result02)


        def test_sonata_messages04(self):
                """
                :return:
                """

                ''' DO AN ACTION ASSUMED TO BE DONE BY EQUPMENT
                    MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
                    LISTENER HAS BEEN SETUP THEN AS WELL
                '''

                '''

                self.curr_logger.info("===============================================================================|")
                self.curr_logger.info("02 sonata message send send via udp")
                self.conf.set_current_test("test_sonata_messages02")
                # self.conf.load_test_messages()
                '''
                '''
                Setup UDP Server
                '''
                '''
                self.conf.reset_test_messages_received()

                self.sr.load_test_messages()
                self.sr.set_udp_sender()
                self.sr.udp_send_to()
                '''
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name='SUITE' + __name__,
                                                 ending='EXECUTES TEST BODY ' + self.conf.curr_test,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                ''' Actual messages being sent
                '''
                res01 = self.conf.msgs_to_send[0]
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + res01,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)

                '''
                #DATA used in messages
                '''
                res02 = self.conf.data_received[0]
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + res02,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                res03 = self.conf.data_sent
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + str(res03),
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)

                ''' CONTENT PROCESSING IS A STARTING POINT for
                    ALL DATA content MANIPULATIONS IN TEST.
                    IT DOES:
                        1) Parse RAW data received from BL (router out)
                        2) Possesses knowledge of data been sent initially
                        3) Makes comparisons
                '''
                snmea = sonata_nmea_msgs_content_process.SonataNmeaMsgsContentProcessing(self.conf.data_received,
                                                                                         self.conf.data_sent)

                ''' PARSE one of the received
                    messages into a structure
                    ready for comparison
                '''
                snmea.packet_indx = 0
                snmea.parse_nmea()

                '''
                #Non optimal way
                #TOO FAR REMOVED FROM THE TEST
                #comparison can be done inside
                #enveloping class
                #for
                #CONTENT PROCESSING
                '''

                snmea.key_sent = "sonata_id"
                snmea.key_received = "label2"

                snmea.compare_fields()
                '''
                '''
                #GET VALUES ONLY
                '''
                '''
                result01 = int(snmea.get_field_in())
                result02 = snmea.get_field_out()
                '''
                '''
                #TODO:
                #Comparison is should be as selective as possible
                '''
                # snmea.compare_with
                '''
                self.curr_logger.debug("INIT_VAL sent to Sonata: --->>>" + res01)
                self.curr_logger.debug("RES_VAL Nmea from Sonata: --->>>" + res02)

                self.curr_logger.debug("Field " + str(snmea.key_sent) + " sent to Sonata: --->>>" + str(result01))
                self.curr_logger.debug(
                    "Field " + str(snmea.key_received) + "received in Nmea message from Sonata: --->>>" + str(result02))

                self.assertNotEqual(result01,
                                 result02)


        def test_sonata_messages05(self):
                """
                :return:
                """

                ''' DO AN ACTION ASSUMED TO BE DONE BY EQUPMENT
                    MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
                    LISTENER HAS BEEN SETUP THEN AS WELL
                '''

                '''

                self.curr_logger.info("===============================================================================|")
                self.curr_logger.info("02 sonata message send send via udp")
                self.conf.set_current_test("test_sonata_messages02")
                # self.conf.load_test_messages()
                '''
                '''
                Setup UDP Server
                '''
                '''
                self.conf.reset_test_messages_received()

                self.sr.load_test_messages()
                self.sr.set_udp_sender()
                self.sr.udp_send_to()
                '''
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name='SUITE' + __name__,
                                                 ending='EXECUTES TEST BODY ' + self.conf.curr_test,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                ''' Actual messages being sent
                '''
                res01 = self.conf.msgs_to_send[0]
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + res01,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)

                '''
                #DATA used in messages
                '''
                res02 = self.conf.data_received[0]
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + res02,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                res03 = self.conf.data_sent
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name=__name__ + ' running test ' + self.conf.curr_test,
                                                 ending='SENT THIS SONAMTEA MESSAGE: ' + str(res03),
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)

                ''' CONTENT PROCESSING IS A STARTING POINT for
                    ALL DATA content MANIPULATIONS IN TEST.
                    IT DOES:
                        1) Parse RAW data received from BL (router out)
                        2) Possesses knowledge of data been sent initially
                        3) Makes comparisons
                '''
                snmea = sonata_nmea_msgs_content_process.SonataNmeaMsgsContentProcessing(self.conf.data_received,
                                                                                         self.conf.data_sent)

                ''' PARSE one of the received
                    messages into a structure
                    ready for comparison
                '''
                snmea.packet_indx = 0
                snmea.parse_nmea()

                '''
                #Non optimal way
                #TOO FAR REMOVED FROM THE TEST
                #comparison can be done inside
                #enveloping class
                #for
                #CONTENT PROCESSING
                '''

                snmea.key_sent = "sonata_id"
                snmea.key_received = "label2"

                snmea.compare_fields()
                '''
                '''
                #GET VALUES ONLY
                '''
                '''
                result01 = int(snmea.get_field_in())
                result02 = snmea.get_field_out()
                '''
                '''
                #TODO:
                #Comparison is should be as selective as possible
                '''
                # snmea.compare_with
                '''
                self.curr_logger.debug("INIT_VAL sent to Sonata: --->>>" + res01)
                self.curr_logger.debug("RES_VAL Nmea from Sonata: --->>>" + res02)

                self.curr_logger.debug("Field " + str(snmea.key_sent) + " sent to Sonata: --->>>" + str(result01))
                self.curr_logger.debug(
                    "Field " + str(snmea.key_received) + "received in Nmea message from Sonata: --->>>" + str(result02))

                self.assertNotEqual(result01,
                                 result02)




if __name__ == '__main__':
        unittest.main()
        '''
        unittest.main(testRunner=xmlrunner.XMLTestRunner(
                                                        output='C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\test_bl\\test_sonata_plugin\\tests_sonata\\sonata-xml-test-reports'),
                                                        failfast=False, buffer=False, catchbreak=False
                                                        )
                                                        '''
        '''
        with open('./sonata-xml-test-reports/results.xml', 'wb') as output:
            unittest.main(
                testRunner=xmlrunner.XMLTestRunner(output=output),
                failfast=False, buffer=False, catchbreak=False)
        '''
        '''
           def suite():
           '''
        '''
        Current test set configuration
        '''
        '''
        this_suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SonataToNMEAConversionTests))
        return this_suite
        '''
        '''
        this_suite=suite()
        runner = unittest.TextTestRunner()
        runner.run(this_suite)
        '''