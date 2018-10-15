import json
from pathlib import Path


class Varutils():
	
	
	def __init__ (self):
		return
	
	
	'''
	READ JSON TO MAP
	'''
	
	
	def read_json_to_map (self,
						  data_location = None):
		check_data_location = Path(data_location)
		if check_data_location.is_file():
			with open(data_location, "r") as read_file:
				map = json.load(read_file)
			return map
		else:
			raise Exception("File is not found")
	
	
	'''--------------------------------------------------------------------------------------------------------------'''
	'''ZIPPING 2 maps together'''
	
	
	def zip_to_map (self,
					to_zip01 = None,
					to_zip02 = None,
					):
		
		vals_combined = zip(to_zip01, to_zip02)
		
		final_var = {}
		'''Final ARRAY of commands for execution over SSH'''
		for key, val in vals_combined:
			final_var[key] = val
		return final_var
	
	
	def conf_key_to_arr (self,
						 conf_parser = None,
						 section_key = None,
						 switch = None):  # possible values: keys, values
		
		final_arr = []
		if switch == 'keys':
			final_arr = [key for key in conf_parser[section_key]]
		elif switch == 'values':
			final_arr = [key for key in conf_parser[section_key].values()]
		return final_arr
	
	
	'''--------------------------------------------------------------------------------------------------------------'''
	'''LOGGERS BANNERS'''
	
	
	def build_test_banner (self,
						   mod_name = None,
						   suit_name = None,
						   ending = None,
						   logging_level = 'INFO',
						   logger = None):
		
		if logging_level == 'DEBUG':
			logger.debug('=====================================================================================|')
			logger.debug('Test suite for ' + str(suit_name) + ' module ' + str(mod_name) + '---> ' + str(ending))
			logger.debug('=====================================================================================|')
		if logging_level == 'INFO':
			logger.info('=====================================================================================|')
			logger.info('Test suite for ' + str(suit_name) + ' module ' + str(mod_name) + '---> ' + str(ending))
			logger.info('=====================================================================================|')
		return
	
	
	def build_srv_banner (self,
						  server_name = None,
						  server_ip = None,
						  server_port = None,
						  ending = None,
						  logging_level = 'INFO',
						  logger = None):
		
		if logging_level == 'DEBUG':
			logger.debug('=====================================================================================|')
			logger.debug('SERVER ' + server_name + ' on ' + str(server_ip) + ':' + str(server_port) + '---> ' + ending)
			logger.debug('=====================================================================================|')
		if logging_level == 'INFO':
			logger.info('=====================================================================================|')
			logger.info('SERVER ' + server_name + ' on ' + str(server_ip) + ':' + str(server_port) + '---> ' + ending)
			logger.info('=====================================================================================|')
		return
	
	
	def sender_receiver_messages (self,
								  server_name = None,
								  server_ip = None,
								  server_port = None,
								  ending = None,
								  logging_level = 'INFO',
								  logger = None
								  ):
		
		return
	
	
	def build_VM_ssh_test_banner (self,
								  server_ip = None,
								  server_port = None,
								  ending = None,
								  logging_level = 'INFO',
								  logger = None):
		
		if logging_level == 'DEBUG':
			logger.debug('=====================================================================================|')
			logger.debug('PARAMICO SSH: ' + str(server_ip) + ':' + str(server_port) + '---> ' + ending)
			logger.debug('=====================================================================================|')
		if logging_level == 'INFO':
			logger.info('=====================================================================================|')
			logger.info('PARAMICO SSH: ' + str(server_ip) + ':' + str(server_port) + '---> ' + ending)
			logger.info('=====================================================================================|')
		return
	
	
	def remote_commands_exec_banner (self,
									 command = None,
									 exec_res01 = None,
									 exec_res02 = None,
									 exec_res03 = None,
									 ending = None,
									 logging_level = 'INFO',
									 logger = None
									 ):
		
		if logging_level == 'DEBUG':
			logger.debug('=====================================================================================|')
			logger.debug('bash command over SSH: ' + command + '---> ' + ending + ' with_results: ' + str(
				exec_res01) + ':' + str(exec_res02) + ':' + str(exec_res02))
			logger.debug('=====================================================================================|')
		if logging_level == 'INFO':
			logger.info('=====================================================================================|')
			logger.info('bash command over SSH: ' + command + '---> ' + ending + ' with_results: ' + str(
				exec_res01) + ':' + str(exec_res02) + ':' + str(exec_res02))
			logger.info('=====================================================================================|')
		return
	
	
	'''--------------------------------------------------------------------------------------------------------------'''
