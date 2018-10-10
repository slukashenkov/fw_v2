import logging
import os
from copy import deepcopy

from test_bl.test_bl_tools import read_test_data, logging_tools, config_test_env, send_receive, \
	process_received_data, external_scripts
from test_bl.test_trassa_plugin.structs_trassa import trassa_msg
from test_bl.test_trassa_plugin.test_tools_trassa import config_trassa_suite
from test_bl.test_trassa_plugin.test_tools_trassa import trassa_test_parser


class SetupTrassaSuite:
	
	
	def __init__ (self):
		"""
		"""
		'''-----------------------------------------------------------------------------------------------------------
		SETUP
		'''
		'''
		CURRENT LOCATION
		'''
		self.curr_dir_name = os.path.dirname(__file__)
		self.module_abs_path = os.path.abspath(os.path.dirname(__file__))
		# self.path_to_proj=re.findall(r".*\\test_bl",self.module_abs_path)
		'''-----------------------------------------------------------------------------------------------------------
		GET GENERAL PREFERENCES
		'''
		self.g_prefs = config_test_env.ConfigTestEnv()
		'''
		GET TEST SUITE PREFERENCES
		'''
		self.t_prefs = config_trassa_suite.ConfigTrassaSuite()
		self.g_prefs.set_suite_conf(self.t_prefs.get_trassa_configuration())
		'''-----------------------------------------------------------------------------------------------------------
		CONFIG LOGGING
		'''
		path_to_logging_conf = self.g_prefs.get_tests_logging_config()
		'''
		Logging for all classes used here 
		is configured from the config file in
		logging tools class.
		All configuration that pertains to individual modules 
		is there in the config
		'''
		self._config_loggers(path_to_logging_conf)
		self.logger = logging.getLogger(__name__)
		'''-----------------------------------------------------------------------------------------------------------
		SEND RECEIVE 
		'''
		self.positive_test_kword = "pass"
		self.negative_test_kword = "fail"
		self.no_data_sent_test_kword = "no_msg_sent"
		self.sr = send_receive.SendReceive(q_based = True)
		'''
		UDP SENDER (process based)
		'''
		'''Generally
		send receive preferences should hold 
		all connections params for the test
		'''
		send_res_prefs = self.t_prefs.get_send_res_prefs()
		
		ip_sender_01 = send_res_prefs["udp_ip_to_01"]
		port_sender_01 = send_res_prefs["udp_port_to_01"]
		ip_sender_02 = send_res_prefs["udp_ip_to_02"]
		port_sender_02 = send_res_prefs["udp_port_to_02"]
		
		'''2 senders will be needed
		1-for AIS msgs
		2-for NMEA msgs
		'''
		
		self.udp_snd_name_01 = self.sr.set_udp_sender(ip_to = ip_sender_01,
													  port_to = port_sender_01
													  )
		self.udp_snd_name_02 = self.sr.set_udp_sender(ip_to = ip_sender_02,
													  port_to = port_sender_02
													  )
		'''
		UDP SERVER (thread based)
		'''
		ip_server_01 = send_res_prefs["udp_ip_from_01"]
		port_server_01 = send_res_prefs["udp_port_from_01"]
		
		ip_server_02 = send_res_prefs["udp_ip_from_02"]
		port_server_02 = send_res_prefs["udp_port_from_02"]
		
		'''
		TRASSA is the case when we want to filter some
		of 
		the arriving messages
		'''
		self.udp_srv_name_01 = self.sr.set_udp_server(ip_address = ip_server_01,
													  port = port_server_01
													  )
		
		self.udp_srv_name_02 = self.sr.set_udp_server(ip_address = ip_server_02,
													  port = port_server_02)
		'''-----------------------------------------------------------------------------------------------------------
		DATA PROCESSING
		'''
		self.test_type_k_word = "test_type"
		self.test_skip_k_word = "skip"
		'''
		TEST SUITE TEST DATA
		path_to_data is module specific
		'''
		self.path_to_test_data = self.t_prefs.get_path_to_trassa_data(project_path = self.g_prefs.get_proj_dir_path())
		'''
		TEST DATA READER  
		'''
		self.rd = read_test_data.ReadData(data_location = self.path_to_test_data,
										  test_data_type = read_test_data.test_data_type.json)
		'''
		TARGET MESSAGE STRUCTURE (Trassa)
		'''
		self.trassa_msg_struct = trassa_msg.TrassaMsg()
		'''
		GET TEST DATA FOR MANIPULATIONS
		'''
		self._test_suite_test_data = self.rd.get_testsuite_data(self.trassa_msg_struct)
		'''------------------------------------------------------------------------------------------------------------
		TESTS TO EXCLUDE
		'''
		self.tests_to_exclude = self._set_excluded_tests()
		'''
		GET TEST CASES NAMES
		'''
		self._test_suite_test_names = self.rd.get_test_names()
		'''
		PARSER (module specific) 
		used by processing class       
		'''
		self._t_parser = trassa_test_parser.TrassaTestParser()
		'''
		RECEIVED TEST DATA PROCESSING
		processing class doing parsing of the received data and comparison with the data been sent out
		'''
		self.proc_data = process_received_data.ProcessReceivedData()
		'''------------------------------------------------------------------------------------------------------------
		COMPARISON (SENT/RECEIVED)
		stuctures to hold sent and received data 
		for further comparison
		'''
		self.test_suite_parsed_data = {}
		self.test_suite_compared_data = None
		self.test_suite_sent_data = {}
		
		'''------------------------------------------------------------------------------------------------------------
		SETUP VIRTUAL ENV FOR TESTS
		'''
		self.ext_scripts = external_scripts.ExtScripts()
		self.setup_external_scripts()
		'''------------------------------------------------------------------------------------------------------------
		END OF SETUP
		'''
	
	
	'''----------------------------------------------------------------------------------------------------------------
	TEST ACTIONS FUNCTIONS
	'''
	
	
	def send_receive_tdata (self,
							test_case_ids,
							udp_sender_id = None,
							udp_server_id = None,
							parser = None):
		"""
		:param test_case_ids: list of testcases` ids
		:param udp_sender_id:
		:param udp_server_id:
		:param parser:
		:return:
		"""
		for test_case_id in test_case_ids:
			if test_case_id in self._test_suite_test_data.keys():
				'''
				TODO: think about preloading data into enveloping object
				'''
				msg_type = self._get_msg_type(test_id = test_case_id)
				test_case_type = self.get_test_type(test_case_id)
				
				if 'ais_type05' in msg_type:
					ais_type05Arr = self._get_test_messages(test_case_id)
					messages_to_send = ais_type05Arr[0]
					#data_sent_arr = self._get_test_data(test_case_id)
					#data_sent = data_sent_arr[0]
				else:
					messages_to_send = self._get_test_messages(test_case_id)
				
				data_sent = self._get_test_data(test_case_id)
				
				
				
				if test_case_type == self.positive_test_kword:
					'''
					PASS ARRAY OF TEST MESSAGES TO SENDer`s Q
					and START sending and receiving for positive cases
					'''
					sender_id = ""
					server_id = ""
					
					if udp_sender_id != None:
						sender_id = udp_sender_id
						self.sr.udp_send_to(messages_list = messages_to_send,
											sender_id = udp_sender_id)
					else:
						sender_id = self.udp_snd_name
						self.sr.udp_send_to(messages_list = messages_to_send,
											sender_id = sender_id)
					'''
					TEST THAT ALL MESSAGES SENT BEING RECEIVED
					'''
					if udp_server_id != None:
						server_id = udp_server_id
						try:
							self.sr.test_messages_received(messages_list = messages_to_send,
													       server_id = server_id)
						except:
							raise Exception("Counter is excedded NO messages have been received")
					else:
						server_id = self.udp_srv_name
						self.sr.test_messages_received(messages_list = messages_to_send,
													   server_id = server_id)
					
					'''
					GET the queue to read from
					'''
					'''TODO check sonata is works when we pass buffer further '''
					received_q = self.sr.get_received_queue(server_id)
					logging.debug("DATA RECEIVED: ==>" + str(received_q) + "\n")
					if parser == None:
						parsed_data = self.proc_data.parse_received_data(parser = self._t_parser,
																		 received_data = received_q)
						self.test_suite_parsed_data[test_case_id] = deepcopy(parsed_data)
						self.test_suite_sent_data[test_case_id] = deepcopy(data_sent)
					else:
						parsed_data = self.proc_data.parse_received_data(parser = parser,
																		 received_data = received_q)
						self.test_suite_parsed_data[test_case_id] = deepcopy(parsed_data)
						self.test_suite_sent_data[test_case_id] = deepcopy(data_sent)
				
				elif test_case_type == self.negative_test_kword:
					'''
					PASS ARRAY OF TEST MESSAGES TO SENDer`s Q
					and 
					START sending and receiving for positive cases
					'''
					sender_id = ""
					server_id = ""
					if udp_sender_id != None:
						sender_id = udp_sender_id
						self.sr.udp_send_to(messages_list = messages_to_send,
											sender_id = udp_sender_id)
					else:
						sender_id = self.udp_snd_name
						self.sr.udp_send_to(messages_list = messages_to_send,
											sender_id = sender_id)
					'''
					TEST for ERROR MESSAGES IN LOG FILES
					'''
					parsed_data = self.proc_data.parse_sut_log(parser = self._t_parser,
															   path_to_sut_log = self.g_prefs.get_sut_logging_log_file_dir(),
															   data_sent = data_sent)
					self.test_suite_parsed_data[test_case_id] = parsed_data
				elif test_case_type == self.no_data_sent_test_kword:
					server_id = udp_server_id
					self.sr.test_receive_only()
					'''
					GET the queue to read from
					'''
					'''TODO check sonata is works when we pass buffer further '''
					received_q = self.sr.get_received_queue(server_id)
					logging.debug("DATA RECEIVED: ==>" + str(received_q) + "\n")
					if parser == None:
						parsed_data = self.proc_data.parse_received_data(parser = self._t_parser,
																		 received_data = received_q)
						self.test_suite_parsed_data[test_case_id] = deepcopy(parsed_data)
						self.test_suite_sent_data[test_case_id] = deepcopy(data_sent)
					else:
						parsed_data = self.proc_data.parse_received_data(parser = parser,
																		 received_data = received_q)
						self.test_suite_parsed_data[test_case_id] = deepcopy(parsed_data)
						self.test_suite_sent_data[test_case_id] = deepcopy(data_sent)
					
					return
			else:
				raise Exception("TEST CASE NAME IS UNKNOWN")
		return
	
	
	def compare_sent_received_tdata (self,
									 test_case_ids,
									 parser = None):
		result = {}
		for test_case_id in test_case_ids:
			if test_case_id in self._test_suite_test_data.keys():
				test_case_type = self.get_test_type(test_case_id)
				
				if test_case_type == self.positive_test_kword:
					data_sent = self.test_suite_sent_data[test_case_id]
					data_received = self.test_suite_parsed_data[test_case_id]
					
					if parser == None:
						result[test_case_id] = self.proc_data.compare_sent_received(parser = self._t_parser,
																					data_sent = data_sent,
																					data_received = data_received)
					else:
						result[test_case_id] = self.proc_data.compare_sent_received(parser = parser,
																					data_sent = data_sent,
																					data_received = data_received)
						for result in result[test_case_id]:
							for comparison in result:
								self.logger.error(comparison + ":==> " + str(result[comparison]))
								self.logger.error('\n')
				
				elif test_case_type == self.negative_test_kword:
					result = self.test_suite_parsed_data
					'''
					for comparison in result:
							self.logger.error(comparison + ":==> " + str(result[comparison]))
							self.logger.error('\n')
					'''
					self.test_suite_compared_data = deepcopy(result)
					return result
				
				elif test_case_type == self.no_data_sent_test_kword:
					data_sent = self.test_suite_sent_data[test_case_id]
					data_received = self.test_suite_parsed_data[test_case_id]
					if parser == None:
						result[test_case_id] = self.proc_data.compare_sent_received(parser = self._t_parser,
																					data_sent = data_sent,
																					data_received = data_received)
						for t_records in result[test_case_id]:
							for record in t_records:
								self.logger.error("comparison result :==>" + str(record))
								self.logger.error('\n')
					else:
						result[test_case_id] = self.proc_data.compare_sent_received(parser = parser,
																					data_sent = data_sent,
																					data_received = data_received)
				
				self.test_suite_compared_data = deepcopy(result)
				return result
	
	
	'''---------------------------------------------------------------------------------------------------------------
	UTILITY FUNCTIONS
	'''
	
	
	def get_test_result (self,
						 test_id,
						 msg_n = 0,
						 key = None):
		test_data = self.test_suite_compared_data[test_id]
		packet_data = test_data[msg_n]
		result = packet_data[key]
		return result
	
	
	def _set_excluded_tests (self):
		result = []
		for test_id in self._test_suite_test_data.keys():
			test_data = self._test_suite_test_data[test_id]
			if test_data[self.test_skip_k_word] == True:
				result.append(deepcopy(test_id))
		return result
	
	
	def get_test_suite_parsed_data (self):
		return self.test_suite_parsed_data
	
	
	def get_test_cases_ids (self):
		return self._test_suite_test_names
	
	
	def get_excluded_tests (self):
		return self.tests_to_exclude
	
	
	def _config_loggers (self,
						 path_to_logging_conf):
		"""
		:param path_to_logging_conf:
		:return:
		"""
		'''
		setup all loggers for all modules at once
		'''
		logging_tools.LoggingTools(path_to_json = path_to_logging_conf)
	
	
	def _get_test_messages (self,
							test_id
							):
		if test_id in self._test_suite_test_data.keys():
			test_messages = self.rd.get_testcase_messages(test_case_id = test_id)
		return test_messages
	
	
	def _get_msg_type (self,
					   test_id
					   ):
		if test_id in self._test_suite_test_data.keys():
			msg_type = self.rd.get_message_type(test_case_id = test_id)
		return msg_type
	
	
	def _get_test_data (self,
						test_id
						):
		if test_id in self._test_suite_test_data.keys():
			test_messages = self.rd.get_testcase_data(test_case_id = test_id)
		return test_messages
	
	
	def get_test_type (self,
					   test_id
					   ):
		if test_id in self._test_suite_test_data.keys():
			test_type = self.rd.get_test_type(test_case_id = test_id)
		return test_type
	
	
	def get_msg_ptrn (self,
					  test_id):
		if test_id in self._test_suite_test_data.keys():
			test_type = self.rd.get_msg_ptrn(test_case_id = test_id)
		return test_type
	
	
	def stop_udp_sender (self,
						 udp_snd_name = None):
		if udp_snd_name == None:
			self.sr.stop_sender(self.udp_snd_name)
		else:
			self.sr.stop_sender(udp_snd_name)
		return
	
	
	def stop_udp_server (self,
						 udp_srv_name = None):
		if udp_srv_name == None:
			self.sr.stop_udp_server(self.udp_srv_name)
		else:
			self.sr.stop_udp_server(udp_srv_name)
		return
	
	
	def start_logserver (self):
		self.ext_scripts.start_log_server()
		return
	
	
	def stop_logserver (self):
		self.ext_scripts.stop_logserver()
		return
	
	
	def stop_test_env (self):
		self.ext_scripts.tear_down_test_env()
		return
	
	
	def setup_external_scripts (self):
		self.ext_scripts.ssh_target_ip = self.g_prefs.get_sut_ssh_host()
		self.ext_scripts.ssh_target_port = self.g_prefs.get_sut_ssh_port()
		self.ext_scripts.ssh_target_user = self.g_prefs.get_sut_ssh_user()
		self.ext_scripts.ssh_target_pswd = self.g_prefs.get_sut_ssh_passwd()
		
		self.ext_scripts.vm_log_srv_exec = self.g_prefs.get_sut_logging_log_srv_exec()
		self.ext_scripts.vm_log_srv_exec_dir = self.g_prefs.get_sut_logging_log_srv_dir()
		self.ext_scripts.vm_log_srv_log_file = self.g_prefs.get_sut_logging_log_file_dir()
		
		self.ext_scripts.vm_start_cmnd = self.g_prefs.get_local_vbox_mng() + ' startvm ' + self.g_prefs.get_clean_vm_img() + ' --type headless'
		self.ext_scripts.vm_shutdown_cmnd = self.g_prefs.get_local_vbox_mng() + ' controlvm ' + self.g_prefs.get_clean_vm_img() + ' poweroff'
		self.ext_scripts.vm_resnap_cmnd = self.g_prefs.get_local_vbox_mng() + ' snapshot ' + self.g_prefs.get_clean_vm_img() + ' restore ' + self.g_prefs.get_clean_snap()
		self.ext_scripts.vm_makeclone_cmnd = self.g_prefs.get_local_vbox_mng() + ' clonevm ' + self.g_prefs.get_clean_vm_img()
		
		self.ext_scripts.ssh_scp_content_location = self.g_prefs.get_sut_config_files_path()
		self.ext_scripts.ssh_target_dir = self.g_prefs.get_sut_ssh_target_dir()
		
		self.ext_scripts.sut_start_commands = self.t_prefs.get_trassa_start_commands()
		self.ext_scripts.sut_stop_commands = self.t_prefs.get_trassa_stop_commands()
		return
	
	
	def setup_vir_env (self):
		self.ext_scripts.set_test_env()
		return
	
	
	def _inspect_atr (self,
					  cls,
					  exclude_methods = True):
		base_attrs = dir(type('dummy', (object,), {}))
		this_cls_attrs = dir(cls)
		res = []
		for attr in this_cls_attrs:
			if base_attrs.count(attr) or (callable(getattr(cls, attr)) and exclude_methods):
				continue
			res += [attr]
		return res


def test_this_paidd ():
	'''general test focused on AIVDM'''
	s_trassa = SetupTrassaSuite()
	'''
	TODO:
	finish with setup
	'''
	# s_trassa.setup_external_scripts()
	# s_sonata.start_logserver()
	# s_sonata.setup_vir_env()
	# t_case_name=["test_trassa_messages01","test_trassa_messages02"]
	# test_case_ids,
	udp_sender_id = None
	udp_server_id = None
	parser = None
	'''AIS Type 01 data'''
	#t_case_name = ["test_trassa_messages01"]
	'''AIS Type 18 data'''
	t_case_name = ["test_trassa_messages02"]
	
	# s_trassa.stop_udp_server(server_id)
	'''
	case when we want to filter some
	of 
	the arriving messages'''
	sender_id = s_trassa.udp_snd_name_01
	server_id = s_trassa.udp_srv_name_01
	ptrn_for_res = s_trassa.get_msg_ptrn(t_case_name[0])
	server = s_trassa.sr.udp_servers[server_id]
	pttrn = ptrn_for_res[0]
	m = pttrn.match('$PAIDD,1193046,3725.468,N,12209.80,W,101.9,34.5,41.0,071705.00*56')
	
	server.res_filter = ptrn_for_res
	s_trassa.sr.start_udp_server(server_id)
	# sleep(40)
	
	s_trassa.send_receive_tdata(test_case_ids = t_case_name,
								udp_sender_id = sender_id,
								udp_server_id = server_id)
	
	result = s_trassa.compare_sent_received_tdata(test_case_ids = t_case_name)
	s_trassa.stop_udp_server(udp_srv_name = server_id)
	# s_trassa.stop_udp_sender()
	# s_trassa.stop_test_env()
	# s_trassa.stop_logserver()
	return


def test_this_paisd ():
	'''general test focused on AIVDM'''
	s_trassa = SetupTrassaSuite()
	'''
	TODO:
	finish with setup
	'''
	# s_trassa.setup_external_scripts()
	# s_sonata.start_logserver()
	# s_sonata.setup_vir_env()
	# t_case_name=["test_trassa_messages01","test_trassa_messages02"]
	# test_case_ids,
	udp_sender_id = None
	udp_server_id = None
	parser = None
	'''
	AIS Type 5
	'''
	#t_case_name = ["test_trassa_messages02"]
	'''
	AIS Type 24ab
	'''
	t_case_name = ["test_trassa_messages03"]
	sender_id = s_trassa.udp_snd_name_01
	server_id = s_trassa.udp_srv_name_01
	# s_trassa.stop_udp_server(server_id)
	'''
	case when we want to filter some
	of 
	the arriving messages
	'''
	udp_server_id = s_trassa.udp_srv_name_01
	ptrn_for_res = s_trassa.get_msg_ptrn(t_case_name[0])
	server = s_trassa.sr.udp_servers[udp_server_id]
	pttrn_to_search = ptrn_for_res[0]
	m = pttrn_to_search.match('$PAISD,8989999,001100,Vsl_cl_sgn,Vsl_name*5B')
	server.res_filter = ptrn_for_res
	s_trassa.sr.start_udp_server(udp_server_id)
	
	s_trassa.send_receive_tdata(test_case_ids = t_case_name,
								udp_sender_id = sender_id,
								udp_server_id = server_id)
	result = s_trassa.compare_sent_received_tdata(test_case_ids = t_case_name)
	s_trassa.stop_udp_server(udp_srv_name = udp_server_id)
	# s_trassa.stop_udp_sender()
	# s_trassa.stop_test_env()
	# s_trassa.stop_logserver()
	return


def test_this_astd ():
	'''
	general test focused on ASTD
	uses different sender and UDP receiving server
	'''
	s_trassa = SetupTrassaSuite()
	
	'''
	TODO:
	finish with setup
	'''
	# s_trassa.setup_external_scripts()
	# s_sonata.start_logserver()
	# s_sonata.setup_vir_env()
	# t_case_name=["test_trassa_messages01","test_trassa_messages02"]
	# test_case_ids,
	udp_sender_id = None
	udp_server_id = None
	parser = None
	t_case_name = ["test_trassa_messages05"]
	sender_id = s_trassa.udp_snd_name_02
	server_id = s_trassa.udp_srv_name_02
	
	s_trassa.sr.start_udp_server(server_id)
	s_trassa.send_receive_tdata(test_case_ids = t_case_name,
								udp_sender_id = sender_id,
								udp_server_id = server_id)
	
	result = s_trassa.compare_sent_received_tdata(test_case_ids = t_case_name)
	s_trassa.stop_udp_server(udp_srv_name = server_id)
	
	# s_trassa.stop_udp_sender()
	# s_trassa.stop_test_env()
	# s_trassa.stop_logserver()
	return


def test_this_aialr ():
	'''
	general test focused on ASTD
	uses different sender and UDP receiving server
	'''
	s_trassa = SetupTrassaSuite()
	
	'''
	TODO:
	finish with setup
	'''
	# s_trassa.setup_external_scripts()
	# s_sonata.start_logserver()
	# s_sonata.setup_vir_env()
	# t_case_name=["test_trassa_messages01","test_trassa_messages02"]
	# test_case_ids,
	udp_sender_id = None
	udp_server_id = None
	parser = None
	
	sender_id = s_trassa.udp_snd_name_01
	server_id = s_trassa.udp_srv_name_01
	
	'''
	case when we want to filter some
	of 
	the arriving messages'''
	t_case_name = ["test_trassa_messages06"]
	udp_server_id = s_trassa.udp_srv_name_01
	ptrn_for_res = s_trassa.get_msg_ptrn(t_case_name[0])
	
	
	pttrn_to_search = ptrn_for_res[0]
	match = pttrn_to_search.match('$AITXT,1,1,21,External DGNSS in use*67')
	pttrn_to_search = ptrn_for_res[1]
	match = pttrn_to_search.match('$AIALR,133930.40,01,V,V,Tx malfunction*35')
	
	server = s_trassa.sr.udp_servers[udp_server_id]
	server.res_filter = ptrn_for_res
	s_trassa.sr.start_udp_server(server_id)
	s_trassa.send_receive_tdata(test_case_ids = t_case_name,
								udp_sender_id = sender_id,
								udp_server_id = server_id)
	
	result = s_trassa.compare_sent_received_tdata(test_case_ids = t_case_name)
	s_trassa.stop_udp_server(udp_srv_name = server_id)
	
	# s_trassa.stop_udp_sender()
	# s_trassa.stop_test_env()
	# s_trassa.stop_logserver()
	return


def test_this_peist ():
	'''
	general test focused on PEIST
	uses different sender and UDP receiving server
	'''
	s_trassa = SetupTrassaSuite()
	
	'''
	TODO:
	finish with setup
	'''
	# s_trassa.setup_external_scripts()
	# s_sonata.start_logserver()
	# s_sonata.setup_vir_env()
	# t_case_name=["test_trassa_messages01","test_trassa_messages02"]
	# test_case_ids,
	udp_sender_id = None
	udp_server_id = None
	parser = None
	
	sender_id = s_trassa.udp_snd_name_01
	server_id = s_trassa.udp_srv_name_01
	
	'''
	case when we want to filter some
	of 
	the arriving messages
	'''
	t_case_name = ["test_trassa_messages05"]
	udp_server_id = s_trassa.udp_srv_name_01
	ptrn_for_res = s_trassa.get_msg_ptrn(t_case_name[0])
	
	pttrn_to_search = ptrn_for_res[0]
	match = pttrn_to_search.match('$PEIST,141714.00,A*30')
	
	server = s_trassa.sr.udp_servers[udp_server_id]
	server.res_filter = ptrn_for_res
	s_trassa.sr.start_udp_server(server_id)
	s_trassa.send_receive_tdata(test_case_ids = t_case_name,
								udp_sender_id = sender_id,
								udp_server_id = server_id
								)
	
	result = s_trassa.compare_sent_received_tdata(test_case_ids = t_case_name)
	s_trassa.stop_udp_server(udp_srv_name = server_id)
	
	# s_trassa.stop_udp_sender()
	# s_trassa.stop_test_env()
	# s_trassa.stop_logserver()
	return


if __name__ == "__main__":
	# test_this_paidd()
	# test_this_paisd()
	# test_this_astd()
	test_this_aialr()
	#test_this_peist()
