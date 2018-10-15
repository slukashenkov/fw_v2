import copy
import json
import logging
import re
from enum import Enum


class test_data_type(Enum):
	json = 1
	text = 2


class ReadData:
	
	
	def __init__ (self,
				  data_location,
				  test_data_type = None
				  ):
		self.logger = logging.getLogger(__name__)
		self.data_location = data_location
		
		if test_data_type == None:
			self.test_data_type = test_data_type.json
		else:
			self.test_data_type = test_data_type
		self.final_map = None
		self.final_list = None
		self.test_suite_map = {}
		self.test_suite_sut_data = []
		self.test_type_k_word = "test_type"
		self.test_skip_k_word = "skip"
		self.msg_ptrn_k_word = "res_ptrn"
		self.test_data_k_ignore = [self.test_type_k_word, self.test_skip_k_word]
		return
	
	
	def read_file_to_map (self,
						  data_location = None):
		map = {}
		with open(self.data_location) as f:
			for line in f:
				(key, val) = line.split()
				map[key] = val
		self.final_map = map
		return
	
	
	def read_file_to_list (self):
		list = []
		with open("file.txt") as f:
			for line in f:
				(key, val) = line.split()
				list.append(val)
		self.final_list = list
		return
	
	
	def read_json_to_map (self,
						  data_location = None):
		with open(self.data_location, "r") as read_file:
			map = json.load(read_file)
			self.final_map = map
		return
	
	
	def read_json_to_list (self):
		return
	
	
	def get_test_names (self):
		self.read_json_to_map()
		test_names = []
		for key, value in self.final_map.items():
			test_names.append(key)
		return test_names
	
	
	def get_testsuite_data (self,
							msg_struct):
		"""
		:param msg_struct:  class that knows how to make actual message from data
							and produces dict of values used to form it that may be
							needed for comparison
		:return:
		"""
		if self.test_data_type == self.test_data_type.json:
			'''
			Get RAW test data
			'''
			self.read_json_to_map()
			msgs_data_map = {}
			prev_type = ""
			curr_type = ""
			first_data = None
			first_data_name = ""
			for test_name in self.final_map:
				test_data = self.final_map[test_name]
				test_status = test_data[self.test_skip_k_word]
				del test_data[self.test_skip_k_word]
				
				for msg_name in test_data:
					
					msg = test_data[msg_name]
					'''
					Check test data consistency
					only positive or negative
					test messages are allowed
					'''
					curr_test_data = msg_struct.set_values_from_json_map(msg)
					'''
					Find out whether we deal withdfata
					for positive
					or
					negative test (two types are not allowed to mix)
					because we either want to scan log or analyze
					networked data
					'''
					curr_type = str(curr_test_data[2])
					if prev_type == "":
						prev_type = curr_type
						first_data = curr_test_data
						first_data_name = msg_name
						msgs_data_map[first_data_name] = first_data
					
					elif prev_type == curr_type and first_data != None and first_data_name != None:
						if first_data != None:
							msgs_data_map[msg_name] = curr_test_data
							first_data = None
					
					elif prev_type != curr_type:
						self.test_suite_map.clear()
						raise Exception("DATA FOR POSITIVE AND NEGATIVE CASES CANNOT MIX")
					else:
						msgs_data_map[msg_name] = curr_test_data
				
				msgs_data_map[self.test_type_k_word] = curr_type
				msgs_data_map[self.test_skip_k_word] = test_status
				self.test_suite_map[test_name] = copy.deepcopy(msgs_data_map)
				
				'''
				Cleanup before next test case
				'''
				msgs_data_map.clear()
				prev_type = ""
				curr_type = ""
				first_data = None
				first_data_name = ""
			return self.test_suite_map
		
		elif self.test_data_type.text:
			return
		
		
		def subdict (self,
					 keywords,
					 fragile = False):
			d = {}
			for k in keywords:
				try:
					d[k] = self.raw_test_data[k]
				except KeyError:
					if fragile:
						raise
			return d
		
		
		def set_curr_test_from_conf (self):
			if self.conf.curr_test == None:
				self.curr_test = None
			else:
				self.curr_test = self.conf.curr_test
			return
	
	
	def get_testcase_messages (self,
							   test_case_id):
		"""
		:param test_case_id: id of the test case
		:return: list of messages ready to send
		"""
		if test_case_id in self.test_suite_map.keys():
			test_messages = []
			test_messages_arr = self.test_suite_map[test_case_id]
			for key in test_messages_arr:
				if key not in self.test_data_k_ignore:
					data_tuple = test_messages_arr[key]
					test_messages.append(data_tuple[0])
			return test_messages
		else:
			raise Exception("No such test case ID")
	
	
	def get_message_type (self,
						  test_case_id):
		
		if test_case_id in self.test_suite_map.keys():
			test_messages_arr = self.test_suite_map[test_case_id]
			msg_type = []
			for key in test_messages_arr:
				if key not in self.test_data_k_ignore:
					data_tuple = test_messages_arr[key]
					msg_type.append(data_tuple[1]['msg_type'])
		return msg_type
	
	
	def get_testcase_data (self,
						   test_case_id):
		if test_case_id in self.test_suite_map.keys():
			
			test_data = []
			test_data_arr = self.test_suite_map[test_case_id]
			
			for key in test_data_arr:
				if key not in self.test_data_k_ignore:
					data_tuple = test_data_arr[key]
					test_data.append(data_tuple[1])
				else:
					continue
			
			return test_data
		else:
			raise Exception("No such test case ID")
	
	
	def get_test_type (self,
					   test_case_id
					   ):
		if test_case_id in self.test_suite_map.keys():
			test_data_arr = self.test_suite_map[test_case_id]
			test_type = test_data_arr[self.test_type_k_word]
			return test_type
		else:
			raise Exception("No such test case ID")
	
	
	def get_msg_ptrn (self,
					  test_case_id
					  ):
		if test_case_id in self.test_suite_map.keys():
			test_data_arr = self.test_suite_map[test_case_id]
			msg_ptrn = []
			msg_ptrn_compiled = []
			for key in test_data_arr:
				if key != self.test_skip_k_word and key != self.test_type_k_word:
					msg = test_data_arr[key]
					ptrn = msg[1][self.msg_ptrn_k_word]
					if ptrn not in msg_ptrn:
						msg_ptrn.append(ptrn)
						cmpled_ptrn = re.compile(ptrn)
						msg_ptrn_compiled.append(cmpled_ptrn)
			return msg_ptrn_compiled
		else:
			raise Exception("No such test case ID")
	
	
	def get_sut_data (self,
					  sut_q):
		while not sut_q.empty():
			self.test_suite_sut_data.append(sut_q.get())
		return self.test_suite_sut_data
	
	
	def load_received_messages (self,
								server_id = None):
		if server_id in self.udp_servers.keys():
			curr_receive_q = self.udp_servers[server_id].data_in_queue
		else:
			raise Exception("No such UDP server")
		
		while not curr_receive_q.empty():
			self.messages_received.append(curr_receive_q.get())
		return self.messages_received


def test_this ():
	import os
	from test_bl.test_sonata_plugin.structs_sonata import sonata_msg
	from test_bl.test_bl_tools import logging_tools
	
	"""
	BASIC TEST BASIC CONFIG
	"""
	'''
	Read test data from json
	'''
	'''And where we are'''
	module_abs_path = os.path.abspath(os.path.dirname(__file__))
	path_to_data = "..\\test_sonata_plugin\\resources_sonata\\sonata_test_data.json"
	def_mgs_location = os.path.join(module_abs_path, path_to_data)
	path_to_log_conf = "..\\test_bl_configs\\logging_conf.json"
	
	lt = logging_tools.LoggingTools(path_to_json = path_to_log_conf
									)
	logger = lt.get_logger(__name__)
	
	rd = ReadData(def_mgs_location,
				  test_data_type = test_data_type.json)
	
	sonata_msg_struct = sonata_msg.SonataMsg(logging_tools = lt)
	rd.read_json_to_map()
	testsuite_data = rd.get_testsuite_data(msg_struct = sonata_msg_struct)
	test_ids = ["test_sonata_messages01", "test_sonata_messages05", "test_sonata_messages02",
				"test_sonata_messages07", "test_sonata_messages05"]
	for id in test_ids:
		test_messages = rd.get_testcase_messages(id)
		test_data = rd.get_testcase_data(id)
	logger.info("test messages collected: " + str(test_messages) + "\n")
	logger.info("test data collected: " + str(test_data) + "\n")
	logger.info("End of test read data_from")


if __name__ == '__main__':
	test_this()
