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
		
		'''Get names of
		UDP senders and servers since in
		these tests they should be started and an stopped on test case basis
		'''
		self.sender_id_01 = self.trassa_setup.udp_snd_name_01
		self.server_id_01 = self.trassa_setup.udp_srv_name_01
		
		self.sender_id_02 = self.trassa_setup.udp_snd_name_02
		self.server_id_02 = self.trassa_setup.udp_srv_name_02
		
		'''SET TEST NAMES QUEUE'''
		self.test_case_ids = deque(self.trassa_setup.get_test_cases_ids())
		self.exclude_tests = self.trassa_setup.get_excluded_tests()
		'''SETUP TEST ENV
		'''
		self.trassa_setup.start_logserver()
		self.trassa_setup.setup_vir_env()
		return
	
	
	@classmethod
	def tearDownClass (self):
		self.trassa_setup.stop_udp_server()
		#self.trassa_setup.stop_udp_server(udp_srv_name = self.server_id_01)
		#self.trassa_setup.stop_udp_server(udp_srv_name = self.server_id_02)
		
		self.trassa_setup.stop_udp_sender()
		#self.trassa_setup.stop_udp_sender(udp_snd_name = self.sender_id_01)
		#self.trassa_setup.stop_udp_sender(udp_snd_name = self.sender_id_02)
		
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
			if self.curr_test_id in self.exclude_tests:
				self.skipTest("ID: " + str(self.curr_test_id) + " is in the list")
			else:
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
				if (self.curr_test_id == "test_trassa_messages01")\
				or (self.curr_test_id == "test_trassa_messages02")\
				or (self.curr_test_id == "test_trassa_messages03")\
				or (self.curr_test_id == "test_trassa_messages04") \
				or (self.curr_test_id == "test_trassa_messages05") \
				or (self.curr_test_id == "test_trassa_messages07") \
				or (self.curr_test_id == "test_trassa_messages08"):
					'''
					We want to filter PAIDD messages for comparison from the stream
					'''
					sender_id = self.trassa_setup.udp_snd_name_01
					server_id = self.trassa_setup.udp_srv_name_01
					ptrn_for_res = self.trassa_setup.get_msg_ptrn(t_case_name[0])
					server = self.trassa_setup.sr.udp_servers[server_id]
					pttrn = ptrn_for_res[0]
					
					
					m_paidd = pttrn.match('$PAIDD,1193046,3725.468,N,12209.80,W,101.9,34.5,41.0,071705.00*56')
					m_paisd = pttrn.match('$PAISD,8989999,001100,Vsl_cl_sgn,Vsl_name*5B')
					m_peist = pttrn.match('$PEIST,141714.00,A*30')
					
					server.res_filter = ptrn_for_res
					self.trassa_setup.sr.start_udp_server(server_id)

					self.trassa_setup.send_receive_tdata(test_case_ids = t_case_name,
													 udp_sender_id = sender_id,
													 udp_server_id = server_id
													 )
					self.trassa_setup.compare_sent_received_tdata(test_case_ids = t_case_name)
				if self.curr_test_id == "test_trassa_messages06":
					
					'''We want to filter PCMST messages
					for comparison from the stream on different from the previous server
					'''
					
					sender_id = self.trassa_setup.udp_snd_name_02
					server_id = self.trassa_setup.udp_srv_name_02
			
					self.trassa_setup.sr.start_udp_server(server_id)
					
					self.trassa_setup.send_receive_tdata(test_case_ids = t_case_name,
														 udp_sender_id = sender_id,
														 udp_server_id = server_id
														 )
					self.trassa_setup.compare_sent_received_tdata(test_case_ids = t_case_name)
	
	
	def tearDown (self):
		#self.ext_scripts.stop_logserver()
		time.sleep(4)
		self.curr_logger.info('Test' + __name__ + 'tearDown routine.')
	
	
	def test_trassa_messages01 (self):
		"""
		:return:
		"""
		'''
		TEST that all fields passed to BL
		FROM SONATA are properly repacked
		'''
		res_ais01 = self.trassa_setup.test_suite_compared_data
		
		'''Get comparable fields'''
		
		MMSI = res_ais01[self.curr_test_id][0]['MMSI']
		self.assertTrue(MMSI[0])
		
		SOG  = res_ais01[self.curr_test_id][0]['SOG']
		self.assertTrue(SOG[0])
		
		longitude = res_ais01[self.curr_test_id][0]['longitude']
		self.assertTrue(longitude[0])
		
		latitude = res_ais01[self.curr_test_id][0]['latitude']
		self.assertTrue(latitude[0])
		
		COG = res_ais01[self.curr_test_id][0]['COG']
		self.assertTrue(COG[0])
		
		TrueHeading = res_ais01[self.curr_test_id][0]['TrueHeading']
		self.assertTrue(TrueHeading[0])
		
		return
	
	def test_trassa_messages02 (self):
		"""
		:return:
		"""
		'''
		TEST that all fields passed to BL
		FROM SONATA are properly repacked
		'''
		res_ais01_18 = self.trassa_setup.test_suite_compared_data
		
		'''Get comparable fields'''
		
		MMSI = res_ais01_18[self.curr_test_id][0]['MMSI']
		self.assertTrue(MMSI[0])
		
		SOG = res_ais01_18[self.curr_test_id][0]['SOG']
		self.assertTrue(SOG[0])
		
		longitude = res_ais01_18[self.curr_test_id][0]['longitude']
		self.assertTrue(longitude[0])
		
		latitude = res_ais01_18[self.curr_test_id][0]['latitude']
		self.assertTrue(latitude[0])
		
		COG = res_ais01_18[self.curr_test_id][0]['COG']
		self.assertTrue(COG[0])
		
		TrueHeading = res_ais01_18[self.curr_test_id][0]['TrueHeading']
		self.assertTrue(TrueHeading[0])
	
		return
	
	
	# for res in res_ais01_18:
	#	self.assertTrue(res[0][0])
	
	# @unittest.skip("test_sonata_messages01 is not needed now")
	def test_trassa_messages03 (self):
		res_ais05 = self.trassa_setup.test_suite_compared_data
		
		'''Get comparable fields'''
		
		MMSI = res_ais05[self.curr_test_id][0]['MMSI']
		self.assertTrue(MMSI[0])
		
		IMOnumber = res_ais05[self.curr_test_id][0]['IMOnumber']
		self.assertTrue(IMOnumber[0])
		
		callsign = res_ais05[self.curr_test_id][0]['callsign']
		self.assertTrue(callsign[0])
		
		name = res_ais05[self.curr_test_id][0]['name']
		self.assertTrue(name[0])
		
		
		return
	
	def test_trassa_messages04 (self):
		res_ais24a = self.trassa_setup.test_suite_compared_data
		
		'''Get comparable fields'''
		
		MMSI = res_ais24a[self.curr_test_id][0]['MMSI']
		self.assertTrue(MMSI[0])
		
		return
	
	def test_trassa_messages05 (self):
		res_ais24b = self.trassa_setup.test_suite_compared_data
		
		'''Get comparable fields'''
		
		MMSI = res_ais24b[self.curr_test_id][0]['MMSI']
		self.assertTrue(MMSI[0])
		
		callsign = res_ais24b[self.curr_test_id][0]['callsign']
		self.assertTrue(callsign[0])
		
		name = res_ais24b[self.curr_test_id][0]['name']
		self.assertTrue(MMSI[0])
		
		return
	
	def test_trassa_messages06 (self):
		res_astd = self.trassa_setup.test_suite_compared_data
		
		'''Get comparable fields'''
		
		v_f_msg = res_astd[self.curr_test_id][0]
		self.assertTrue(v_f_msg[0])
		
		a_g_msg = res_astd[self.curr_test_id][1]
		self.assertTrue(a_g_msg[0])
		
		return
	
	def test_trassa_messages07 (self):
		res_aitxt = self.trassa_setup.test_suite_compared_data
		
		'''Get comparable fields'''
		
		v_f_msg = res_aitxt[self.curr_test_id]
		self.assertTrue(v_f_msg[0])
		
		a_g_msg = res_aitxt[self.curr_test_id]
		self.assertTrue(a_g_msg[1])
		
		return
	
	def test_trassa_messages08 (self):
		res_peist = self.trassa_setup.test_suite_compared_data
		
		'''Get comparable fields'''
		
		peist = res_peist[self.curr_test_id]['peist']
		self.assertTrue(peist[0])
		
		return



if __name__ == '__main__':
	unittest.main()
