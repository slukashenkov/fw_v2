import unittest, time, xmlrunner, logging

from collections import deque

from test_bl.test_sonata_plugin.test_tools_sonata import  setup_sonata_suite
from test_bl.test_sonata_plugin.test_tools_sonata import config_sonata_suite
from test_bl.test_bl_tools import var_utils, external_scripts, send_receive, udp_server, udp_sender,logging_tools


#import send_receive_sonata, sonata_nmea_msgs_content_process
#import sonata_send_recieve_properties, sonata_suite_config
#import var_utils, external_scripts


class SonataTests(unittest.TestCase):
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
            '''
            GET TOOLS OUT            
            '''
            self.__tools__ = var_utils.Varutils()
            '''
            LOGGING CONFIGURED
            '''
            self.curr_logger = logging.getLogger(__name__)
            '''---------------------------------------------------------------------------------------------------------
            SETUP 
            all the things needed for test
            using conf files under the hood
            
            CONFIG FILE FOR SUITE
            defines everything
            that pertains to sending/receiving (UDP Server/sender data and so on)
            and
            data extraction and comparison
            '''
            self.sonata_setup = setup_sonata_suite.SetupSonataSuite()
            '''SET TEST NAMES QUEUE'''
            self.test_case_ids = deque(self.sonata_setup.get_test_cases_ids())
            self.exclude_tests = self.sonata_setup.get_excluded_tests()
            '''
            SETUP TEST ENV
            '''
            self.sonata_setup.start_logserver()
            self.sonata_setup.setup_vir_env()
            return

        @classmethod
        def tearDownClass(self):
            self.sonata_setup.stop_udp_server()
            self.sonata_setup.stop_udp_sender()
            self.sonata_setup.stop_test_env()
            self.sonata_setup.stop_logserver()

            self.__tools__.build_test_banner(mod_name           = 'SONATA',
                                              suit_name         = 'SUITE' + __name__,
                                              ending            = 'TEARS DOWN TEST CLASS',
                                              logging_level     = 'DEBUG',
                                              logger            = self.curr_logger)
            return

        def setUp(self):
            """
            SETUP TEST DATA, UDP SENDER and SEND MESSAGE
            per test case
            :return:
            """
            if self.test_case_ids:
                self.curr_test_id = self.test_case_ids.popleft()
                '''
                if self.curr_test_id == self.exclude_tests[self.curr_test_id]:
                    self.skipTest("ID is in the list")
                '''
                t_case_name = [self.curr_test_id]
                self.sonata_setup.send_receive_tdata(test_case_ids=t_case_name)
                self.sonata_setup.compare_sent_received_tdata(test_case_ids=t_case_name)


        def tearDown(self):
            #self.ext_scripts.stop_logserver()
            time.sleep(4)
            self.curr_logger.info('Test'+__name__+ 'tearDown routine.')


        def test_sonata_messages01(self):
                """
                :return:
                """
                '''
                TEST that all fields passed to BL 
                FROM SONATA are properly repacked
                '''
                res_sonata_id = self.sonata_setup.get_test_result(test_id=self.curr_test_id,
                                                                  msg_n = 0,
                                                                  key = "sonata_id")
                resres_sonata_id = res_sonata_id[0]
                res_lat = self.sonata_setup.get_test_result(test_id=self.curr_test_id,
                                                                  msg_n = 0,
                                                                  key = "lat")
                res_lon = self.sonata_setup.get_test_result(test_id=self.curr_test_id,
                                                                  msg_n = 0,
                                                                  key = "lon")
                res_vel = self.sonata_setup.get_test_result(test_id=self.curr_test_id,
                                                                  msg_n = 0,
                                                                  key = "vel")
                res_course = self.sonata_setup.get_test_result(test_id=self.curr_test_id,
                                                                  msg_n = 0,
                                                                  key = "course")


                res_vel_knots = self.sonata_setup.get_test_result(test_id=self.curr_test_id,
                                                                  msg_n = 0,
                                                                  key = "vel_knots")

                self.assertTrue(res_sonata_id[0])
                self.assertTrue(res_lat[0])
                self.assertTrue(res_lon[0])
                self.assertTrue(res_vel[0])
                self.assertTrue(res_course[0])
                self.assertTrue(res_vel_knots[0])

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
            wrong_crc_res = self.sonata_setup.get_test_result(test_id=self.curr_test_id,
                                                              msg_n=0,
                                                              key="Wrong message CRC")
            if len(wrong_crc_res) == 0:
                wrong_crc_res = False
            else:
                wrong_crc_res = True

            msg_not_start = self.sonata_setup.get_test_result(test_id=self.curr_test_id,
                                                              msg_n=1,
                                                              key="Message does not start")
            if len(msg_not_start) == 0:
                msg_not_start = False
            else:
                msg_not_start = True

            msg_too_short = self.sonata_setup.get_test_result(test_id=self.curr_test_id,
                                                              msg_n=2,
                                                              key="Message too short")
            if len(msg_too_short) == 0:
                msg_too_short = False
            else:
                msg_too_short = True

            self.assertTrue(wrong_crc_res)
            self.assertTrue(msg_not_start)
            self.assertTrue(msg_too_short)

        @unittest.skip("test_sonata_messages02 is not needed now")
        def test_sonata_messages03(self):
                """
                :return:
                """
                '''
                HERE we suppose to test a "large" amount of generated messages 
                but
                as it was used to rest parser
                '''
                self.assertTrue(True)

if __name__ == '__main__':
        unittest.main()