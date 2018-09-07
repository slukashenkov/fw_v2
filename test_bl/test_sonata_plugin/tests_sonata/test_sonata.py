import unittest, time, xmlrunner

from collections import deque

from test_bl.test_sonata_plugin.test_tools_sonata import send_receive_sonata, sonata_nmea_msgs_content_process
from test_bl.test_sonata_plugin.configs_sonata import sonata_send_recieve_properties, sonata_suite_config
from test_bl.test_bl_tools import var_utils, external_scripts

#import send_receive_sonata, sonata_nmea_msgs_content_process
#import sonata_send_recieve_properties, sonata_suite_config
#import var_utils, external_scripts


class SonataToNMEAConversionTests(unittest.TestCase):
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
            self.udp_srv = self.sr.udp_server_listen_on()

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

            #self.exclude_tests = []
            self.exclude_tests = ["test_sonata_messages01",
                                  "test_sonata_messages02",
                                  "test_sonata_messages03",
                                  "test_sonata_messages04"]

            return

        @classmethod
        def tearDownClass(self):
            self.ext_scripts.stop_logserver()
            self.sr.close_UDP_socket()
            self.sr.udp_server_stop_listen_on()
            self.ext_scripts.tear_down_test_env()

            self.__tools__.build_test_banner(mod_name           = 'SONATA',
                                              suit_name         = 'SUITE' + __name__,
                                              ending            = 'TEARS DOWN TEST CLASS',
                                              logging_level     = 'DEBUG',
                                              logger            = self.curr_logger)
            return

        def setUp(self):
            #self.ext_scripts.stop_logserver()
            #time.sleep(5)
            #self.ext_scripts.start_log_server()
            #time.sleep(5)
            """Setup all the common things for the test"""
            #self.test_case_ids = "test_sonata_messages04"
            #self.sr.set_udp_sender()
            # self.ext_scripts.start_log_server()

            currentTest = self.id().split('.')[-1]

            '''SETUP TEST DATA, UDP SENDER and SEND MESSAGES'''
            self.conf.set_current_test(self.test_case.popleft())
            curr_test = self.conf.curr_test
            if curr_test in self.exclude_tests:
                self.skipTest("ID is in the list")

            #self.conf.set_current_test("test_sonata_messages02")
            self.conf.reset_test_messages_received()
            self.conf.reset_test_messages_sent()

            self.__tools__.build_test_banner(mod_name='SONATA',
                                             suit_name='SUITE' + __name__,
                                             ending='SETS UP SENDER FOR TEST CLASS ' + self.conf.curr_test,
                                             logging_level='DEBUG',
                                             logger=self.curr_logger)
            self.sr.load_test_messages()
            self.sr.set_udp_sender()
            self.sr.udp_send_to()
            time.sleep(6)
            return

        def tearDown(self):
            #self.ext_scripts.stop_logserver()
            time.sleep(4)
            self.curr_logger.info('Test'+__name__+ 'tearDown routine.')
            return

        #@unittest.skip("test_sonata_messages01 is not needed now")
        def test_sonata_messages01(self):
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
                snmea = self.conf.content_proc
                total_messages = self.conf.data_received.__len__()
                snmea.packet_indx = 0
                snmea.parse_nmea()

                res_sonata_id = snmea.nmea_parser.compare_fields(
                    sonata_id="sonata_id"
                )

                res_lat = snmea.nmea_parser.compare_fields(
                    lat="lat"
                )

                res_lon = snmea.nmea_parser.compare_fields(
                    lon="lon"
                )

                res_vel = snmea.nmea_parser.compare_fields(
                    vel="vel"
                )
                res_course = snmea.nmea_parser.compare_fields(
                    course="course"
                )

                res_vel_knots = snmea.nmea_parser.compare_fields(
                    vel_knots="vel_knots"
                )

                self.assertTrue(res_sonata_id)
                self.assertTrue(res_lat)
                self.assertTrue(res_lon)
                self.assertTrue(res_vel)
                self.assertTrue(res_course)
                self.assertTrue(res_vel_knots)

        #@unittest.skip("test_sonata_messages01 is not needed now")
        def test_sonata_messages02(self):
            """
            :return:
            """
            #self.ext_scripts.stop_logserver()
            '''
            DO AN ACTION ASSUMED TO BE DONE BY EQUIPMENT.
            MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
            LISTENER HAS BEEN SETUP THEN AS WELL
            '''
            self.__tools__.build_test_banner(mod_name='SONATA',
                                             suit_name='SUITE' + __name__,
                                             ending='EXECUTES TEST BODY ' + self.conf.curr_test,
                                             logging_level='DEBUG',
                                             logger=self.curr_logger)
            '''
            Test for proper error in CASE Sonata message has wrong CRC
            '''
            snmea = self.conf.content_proc
            result_search_strings = snmea.nmea_parser.parse_log("Wrong message CRC")

            if result_search_strings.__len__() > 0:
                test_res = True
            elif result_search_strings.__len__() == 0:
                test_res = False
            self.assertTrue(test_res)

       # @unittest.skip("test_sonata_messages02 is not needed now")
        def test_sonata_messages03(self):
                """
                :return:
                """
                '''
                DO AN ACTION ASSUMED TO BE DONE BY EQUIPMENT.
                MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
                LISTENER HAS BEEN SETUP THEN AS WELL
                '''
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name='SUITE' + __name__,
                                                 ending='EXECUTES TEST BODY ' + self.conf.curr_test,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                '''
                Test for proper error in CASE Sonata message has wrong CRC
                '''
                snmea = self.conf.content_proc
                result_search_strings = snmea.nmea_parser.parse_log("Message does not start")

                if result_search_strings.__len__() > 0:
                    test_res = True
                elif result_search_strings.__len__() == 0:
                    test_res = False

                self.assertTrue(test_res)

        #@unittest.skip("test_sonata_messages04 is not needed now")
        def test_sonata_messages04(self):
                """
                :return:
                """

                '''
                DO AN ACTION ASSUMED TO BE DONE BY EQUIPMENT.
                MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
                LISTENER HAS BEEN SETUP THEN AS WELL
                '''
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name='SUITE' + __name__,
                                                 ending='EXECUTES TEST BODY ' + self.conf.curr_test,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                '''
                Test for proper error in CASE Sonata message has wrong CRC
                '''
                snmea = self.conf.content_proc
                result_search_strings = snmea.nmea_parser.parse_log("Message too short")

                if result_search_strings.__len__() > 0:
                    test_res = True
                elif result_search_strings.__len__() == 0:
                    test_res = False

                self.assertTrue(test_res)

        #@unittest.skip("test_sonata_messages05 is not needed now")
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
                snmea = self.conf.content_proc
                snmea.parse_nmea_auto()
                res_sonata = snmea.compare_fields_auto()

                for res in res_sonata:
                    self.assertTrue(res)

        #@unittest.skip("test_sonata_messages06 is not needed now")
        def test_sonata_messages06(self):
                """
                :return:
                """

                '''
                DO AN ACTION ASSUMED TO BE DONE BY EQUIPMENT.
                MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
                LISTENER HAS BEEN SETUP THEN AS WELL
                '''
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name='SUITE' + __name__,
                                                 ending='EXECUTES TEST BODY ' + self.conf.curr_test,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                '''
                Test for proper error in CASE Sonata message has wrong CRC
                '''
                snmea = self.conf.content_proc
                result_search_strings = snmea.nmea_parser.parse_log_auto()

                if result_search_strings.__len__() > 0:
                    test_res = True
                elif result_search_strings.__len__() == 0:
                    test_res = False

                self.assertTrue(test_res)

        def test_sonata_messages07(self):
                """
                :return:
                """

                '''
                DO AN ACTION ASSUMED TO BE DONE BY EQUIPMENT.
                MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
                LISTENER HAS BEEN SETUP THEN AS WELL
                '''
                self.__tools__.build_test_banner(mod_name='SONATA',
                                                 suit_name='SUITE' + __name__,
                                                 ending='EXECUTES TEST BODY ' + self.conf.curr_test,
                                                 logging_level='DEBUG',
                                                 logger=self.curr_logger)
                '''
                Test for proper error in CASE Sonata message has wrong CRC
                '''
                snmea = self.conf.content_proc
                result_search_strings = snmea.nmea_parser.parse_log_auto()

                if result_search_strings.__len__() > 0:
                    test_res = True
                elif result_search_strings.__len__() == 0:
                    test_res = False

                self.assertTrue(test_res)



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