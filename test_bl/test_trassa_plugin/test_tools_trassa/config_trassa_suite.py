import os
import platform

from test_bl.test_bl_tools import var_utils


class ConfigTrassaSuite:
	
	
	def __init__ (self):
		"""
		Connection establishment and in/out data_from fields setup
		"""
		'''Lets find ot the system we run on'''
		self.syst = platform.system()
		'''And where we are'''
		self.module_abs_path = os.path.abspath(os.path.dirname(__file__))
		if self.syst == 'Windows':
			self.trassa_suite_config_json = self.vm_logsrv_cnf_location = os.path.join(self.module_abs_path,
																					   "..\\configs_trassa\\trassa_conf.json")
		elif self.syst == 'Linux':
			self.trassa_suite_config_json = self.vm_logsrv_cnf_location = os.path.join(self.module_abs_path,
																					   "../configs_trassa/trassa_conf.json")
		'''get some tools ready'''
		self.__utils__ = var_utils.Varutils()
		'''MAP OF CONFIG PARAMS FROM JSON'''
		self.trassa_suite_config = self.__utils__.read_json_to_map(data_location = self.trassa_suite_config_json)
	
	
	'''GETTERS for CONFIG VALUES'''
	
	
	def get_trassa_configuration (self):
		if self.trassa_suite_config:
			for key in self.trassa_suite_config:
				configs = self.trassa_suite_config[key]
			return configs
		else:
			raise Exception("No TEST_BL config map")
	
	
	def get_send_res_prefs (self):
		if self.trassa_suite_config:
			conf_map = self.get_trassa_configuration()
		send_res_prefs = conf_map["send_receive_prefs"]
		return send_res_prefs
	
	
	def get_path_to_trassa_data (self,
								 project_path,
								 key = None):
		if self.trassa_suite_config_json:
			conf_map = self.get_trassa_configuration()
			if key == None:
				path_to_data = conf_map["test_data_trassa"]
			else:
				path_to_data = conf_map[key]
			
			if self.syst == 'Windows':
				path = os.path.join(project_path, path_to_data["windows"]["test_data_location"])
				return path
			elif self.syst == 'Linux':
				path = os.path.join(project_path, path_to_data["linux"]["test_data_location"])
				return path
	
	
	def get_trassa_start_commands (self,
								   key = None):
		if self.trassa_suite_config:
			conf_map = self.get_trassa_configuration()
			if key == None:
				sut_start_commands = conf_map["sut_control_commands_start"]
				return sut_start_commands
			else:
				sut_start_commands = conf_map[key]
				return sut_start_commands
	
	
	def get_trassa_stop_commands (self,
								  key = None):
		if self.trassa_suite_config:
			conf_map = self.get_trassa_configuration()
			if key == None:
				sut_stop_commands = conf_map["sut_control_commands_stop"]
				return sut_stop_commands
			else:
				sut_stop_commands = conf_map[key]
				return sut_stop_commands


def test_this ():
	tc = ConfigTrassaSuite()
	full_config_sonata = tc.get_trassa_configuration()
	path_to_test_data = tc.get_path_to_trassa_data()
	trassa_start_cmnds = tc.get_trassa_start_commands()
	trassa_stop_cmnds = tc.get_trassa_stop_commands()
	
	return


if __name__ == '__main__':
	test_this()
