import logging
import time
import unittest
from collections import deque

from test_bl.test_bl_tools import var_utils
from test_bl.test_trassa_plugin.test_tools_trassa import setup_trassa_suite


class TrassaTests(unittest.TestCase):
	
	
	@classmethod
	def setUpClass (self):
		"""
		SETUP ENV FOR Trassa Module Test Suite :
		1) INITIAL CONFIG
		2) UDP SERVER(s) to listen for BL responses (one for ASTD, other for Trassa)
		3) UDP Sender(s) (one to simulate traffic coming from AIS, other from TRASSA)
		4) Start Test VM from appropriate image
		5) Start BL with TRASSA configs copied to the test VM
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
		self.trassa_setup = setup_trassa_suite.SetupTrassaSuite()
		'''SET TEST NAMES QUEUE'''
		self.test_case_ids = deque(self.trassa_setup.get_test_cases_ids())
		self.exclude_tests = self.trassa_setup.get_excluded_tests()
		'''
		SETUP TEST ENV
		'''
		self.trassa_setup.start_logserver()
		# self.trassa_setup.setup_vir_env()
		return
	
	
	@classmethod
	def tearDownClass (self):
		self.trassa_setup.stop_udp_server()
		self.trassa_setup.stop_udp_sender()
		self.trassa_setup.stop_test_env()
		self.trassa_setup.stop_logserver()
		
		self.__tools__.build_test_banner(mod_name = 'TRASSA',
										 suit_name = 'SUITE' + __name__,
										 ending = 'TEARS DOWN TEST CLASS',
										 logging_level = 'DEBUG',
										 logger = self.curr_logger)
		return
	
	
	def setUp (self):
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
			'''
			Unlike Sonata Trassa needs a separate setup for each message type.
			It is done to account for data filtering
			as well as for choice of UDP sender and Server
			since 2 data "channels" are configured on KD under test
			'''
			if t_case_name == 'test_trassa_messages01':
				'''
				We want to filter PAIDD messages for comparison from the stream
				'''
				sender_id = s_trassa.udp_snd_name_01
				udp_server_id = s_trassa.udp_srv_name_01
				ptrn_for_res = s_trassa.get_msg_ptrn(t_case_name[0])
				server = s_trassa.sr.udp_servers[udp_server_id]
				pttrn = ptrn_for_res[0]
				m = pttrn.match('$PAIDD,1193046,3725.468,N,12209.80,W,101.9,34.5,41.0,071705.00*56')
				
				server.res_filter = ptrn_for_res
				s_trassa.sr.start_udp_server(udp_server_id)
				
			self.trassa_setup.send_receive_tdata(test_case_ids = t_case_name)
			self.trassa_setup.compare_sent_received_tdata(test_case_ids = t_case_name)
	
	
	def tearDown (self):
		# self.ext_scripts.stop_logserver()
		time.sleep(4)
		self.curr_logger.info('Test' + __name__ + 'tearDown routine.')
	
	
	def test_trassa_ais_type01_18 (self):
		"""
		:return:
		"""
		'''
		TEST that all fields passed to BL
		FROM SONATA are properly repacked
		'''
		res_ais01_18 = self.trassa_setup.get_test_result(test_id = self.curr_test_id)
		
		for res in res_ais01_18:
			self.assertTrue(res[0][0])
	
	
	# @unittest.skip("test_sonata_messages01 is not needed now")
	def test_trassa_ais_type05_24ab (self):
		pass
	
	
	@unittest.skip("to_do")
	def test_trassa_astd (self):
		pass
	
	
	@unittest.skip("to_do")
	def test_trassa_peist (self):
		pass
	
	
	@unittest.skip("to_do")
	def test_trassa_aitxt_alr (self):
		pass


if __name__ == '__main__':
	unittest.main()
