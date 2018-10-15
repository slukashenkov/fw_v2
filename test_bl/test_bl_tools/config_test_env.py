import configparser
import os
import platform
import re

from test_bl.test_bl_tools import logging_tools, var_utils


class ConfigTestEnv:
	
	
	def __init__ (self):
		"""
		Connection establishment and in/out data_from fields setup
		"""
		'''Lets find ot the system we run on'''
		self.syst = platform.system()
		'''And where we are'''
		self.module_abs_path = os.path.abspath(os.path.dirname(__file__))
		self.path_to_proj = ""
		
		if self.syst == 'Windows':
			self.test_bl_config_json = self.vm_logsrv_cnf_location = os.path.join(self.module_abs_path,
																				  "..\\test_bl_configs\\test_bl_conf.json")
		elif self.syst == 'Linux':
			self.test_bl_config_json = self.vm_logsrv_cnf_location = os.path.join(self.module_abs_path,
																				  "../test_bl_configs/test_bl_conf.json")
		'''get some tools ready'''
		self.__utils__ = var_utils.Varutils()
		'''MAP OF CONFIG PARAMS FROM JSON'''
		self.test_bl_config = self.__utils__.read_json_to_map(data_location = self.test_bl_config_json)
		'''FIND OUT ABS PATH TO PROJ SO IT CAN BE USED TO FIND THINGS INSIDE IT'''
		self.path_to_proj = self.get_proj_dir_path()
		
		'''---------------------------------------------------------------------------------------------------------
		INI CONF REMAINS TODO: delete complitely
		'''
		
		'''MAP OF CONFIG PARAMS FROM INI'''
		if self.syst == 'Windows':
			self.test_bl_config_ini = self.vm_logsrv_cnf_location = os.path.join(self.module_abs_path,
																				 "..\\test_bl_configs\\test_bl_conf.ini")
		elif self.syst == 'Linux':
			self.test_bl_config_ini = self.vm_logsrv_cnf_location = os.path.join(self.module_abs_path,
																				 "../test_bl_configs/test_bl_conf.ini")
		self.test_bl_conf = configparser.ConfigParser()
		self.test_bl_conf.read(self.test_bl_config_ini)
		'''---------------------------------------------------------------------------------------------------------
		START CONFIGURATION
		'''
		'''SET VM and LOG SERVER PREFS'''
		'''Location of VM manage command used to restart SUT VM'''
		if self.syst == 'Windows':
			self.vm_vbox_manage = self.test_bl_conf['LOCAL_VBOX_DIRS']['VBOXMANAGE_DIR']
		elif self.syst == 'Linux':
			self.vm_vbox_manage = self.test_bl_conf['LOCAL_VBOX_DIRS_LINUX']['VBOXMANAGE_DIR']
		'''VM clean snap`s name'''
		self.vm_alt_img = self.test_bl_conf['CLEAN_IMAGES']['CLEAN_ALT']
		self.vm_alt_img_snapshot = self.test_bl_conf['CLEAN_IMAGES']['CLEAN_ALT_SNAP']
		'''SET SUT SSH PREFS COMMON FOR ALL TEST SUITES'''
		self.ssh_host = self.test_bl_conf['SSH_PREFS']['SSH_HOST']
		self.ssh_port = self.test_bl_conf['SSH_PREFS']['SSH_PORT']
		self.ssh_user = self.test_bl_conf['SSH_PREFS']['SSH_USER_NAME']
		self.ssh_pwd = self.test_bl_conf['SSH_PREFS']['SSH_PASSWD']
		self.ssh_target_dir = self.test_bl_conf['SSH_PREFS']['SSH_TARGET_DIR']
		'''Here an assumption is made that
		all configs and
		all scripts for all modules are in the same archive
		with predetermined directory(es) structure'''
		if self.syst == 'Windows':
			self.sut_all_confs = self.test_bl_conf['BL_CONFIG_FILES']['BL_CONF_FILES_ARCH']
		elif self.syst == 'Linux':
			self.sut_all_confs = self.test_bl_conf['BL_CONFIG_FILES_LINUX']['BL_CONF_FILES_ARCH']
		'''
		|-----------------------------------------------------------------------------------------------------------
		'''
		'''
		SET PREFS FOR LOGGING FACILITIES OF THE TEST MODULES
		'''
		'''
		CHAINSAW log server specifics (start script)
		'''
		if self.syst == 'Windows':
			self.vm_log_srv_exec = self.test_bl_conf['LOGGER_SRV']['LOGGER_SRV_EXEC']
			self.vm_log_srv_dir = self.test_bl_conf['LOGGER_SRV']['LOGGER_SRV_DIR']
		elif self.syst == 'Linux':
			self.vm_log_srv_exec = self.test_bl_conf['LOGGER_SRV_LINUX']['LOGGER_SRV_EXEC']
			self.vm_log_srv_dir = self.test_bl_conf['LOGGER_SRV_LINUX']['LOGGER_SRV_DIR']
		'''
		SET LOCATION OF THE SUT LOG USED IN TESTS
		'''
		if self.syst == 'Windows':
			self.bl_log_dir = self.test_bl_conf['BL_LOG_FILE']['BL_LOG_FILE_DIR']
		elif self.syst == 'Linux':
			self.bl_log_dir = self.test_bl_conf['BL_LOG_FILE_LINUX']['BL_LOG_FILE_DIR_LINUX']
		
		'''
		|---------------------------------------------------------------------------------------------------------------
		'''
		'''
		VARS TO DEFINE Connections PREFERENCES
		for TEST DATA SENDERS and RECEIVERS
		'''
		'''SET SENDERS'''
		self.ip_to = self.test_bl_conf['CONNECTION_PREFS']['BL_IP_TO']
		self.port_to = int(self.test_bl_conf['CONNECTION_PREFS']['BL_PORT_TO'])
		self.protocol_to = self.test_bl_conf['CONNECTION_PREFS']['BL_PROT_TO']
		
		'''SET RECEIVERS'''
		self.ip_on = self.test_bl_conf['CONNECTION_PREFS']['BL_IP_ON']
		self.port_on = int(self.test_bl_conf['CONNECTION_PREFS']['BL_PORT_ON'])
		self.buff_size = self.test_bl_conf['CONNECTION_PREFS']['BL_BUFFSZ_ON']
		'''Combine prefs'''
		self.listen_on = (self.ip_on, self.port_on)
	
	
	'''
	|---------------------------------------------------------------------------------------------------------------
	'''
	'''UTILITY FUNCTIONS FOR CONFIGURATION'''
	
	
	def config_loggers (path_to_json):
		"""
		This function just sets up all
		loggers for all modules at ones
		based on logging_conf.json
		:return: nothing
		"""
		import os
		
		'''current location of the project'''
		module_abs_path = os.path.abspath(os.path.dirname(__file__))
		'''config logging'''
		path_to_logging_conf = path_to_json
		path_to_logging_conf = os.path.join(module_abs_path, path_to_logging_conf)
		'''setup all loggers for all modules at once'''
		logging_tools.LoggingTools(path_to_json = path_to_logging_conf)
	
	
	'''----------------------------------------------------------------------------------------------------------'''
	'''GETTERS for CONFIG VALUES'''
	
	
	def get_test_bl_configuration (self,
								   key = "test_bl_configuration"):
		
		if self.test_bl_config:
			config = self.test_bl_config[key]
			return config
		else:
			raise Exception("No TEST_BL config map")
	
	
	def get_local_vbox_dir (self,
							key = None):
		if self.test_bl_config:
			conf_map = self.get_test_bl_configuration()
			if key == None:
				vbox_dirs = conf_map["local_vbox_dirs"]
			else:
				vbox_dirs = conf_map[key]
			
			if self.syst == 'Windows':
				vbox_dir = vbox_dirs["windows"]["vbox_dir"]
				return vbox_dir
			elif self.syst == 'Linux':
				vbox_dir = vbox_dirs["linux"]["vbox_dir"]
				return vbox_dir
	
	
	def get_local_vbox_mng (self,
							key = None):
		if self.test_bl_config:
			conf_map = self.get_test_bl_configuration()
			if key == None:
				vbox_dirs = conf_map["local_vbox_dirs"]
			else:
				vbox_dirs = conf_map[key]
			
			if self.syst == 'Windows':
				vbox_dir = vbox_dirs["windows"]["vbox_dir_manage"]
				return vbox_dir
			elif self.syst == 'Linux':
				vbox_dir = vbox_dirs["linux"]["vbox_dir_manage"]
				return vbox_dir
	
	
	def get_clean_vm_img (self,
						  key = None,
						  type = "alt"):
		if self.test_bl_config:
			conf_map = self.get_test_bl_configuration()
			if key == None:
				clean_img = conf_map["clean_vm_img"]
				if type == 'alt':
					vbox_dir = clean_img["alt"]["clean_alt_img"]
					return vbox_dir
				else:
					type = type
					vbox_dir = clean_img["type"]["clean_astra_img"]
					return vbox_dir
			else:
				clean_imgs = conf_map[key]
			return
	
	
	def get_clean_snap (self,
						key = None,
						type = "alt"):
		if self.test_bl_config:
			conf_map = self.get_test_bl_configuration()
			if key == None:
				clean_img = conf_map["clean_vm_img"]
				if type == 'alt':
					clean_snap = clean_img["alt"]["clean_alt_snap"]
					return clean_snap
				else:
					type = type
					clean_snap = clean_img["type"]["clean_alt_snap"]
					return clean_snap
	
	
	def get_sut_ssh_prefs (self,
						   key = None):
		conf_map = self.get_test_bl_configuration()
		if key == None:
			all_ssh_prefs = conf_map["sut_ssh_prefs"]
			return all_ssh_prefs
		else:
			all_ssh_prefs = conf_map[key]
		return all_ssh_prefs
	
	
	def get_sut_ssh_host (self):
		conf_map = self.get_test_bl_configuration()
		all_ssh_prefs = conf_map["sut_ssh_prefs"]
		ssh_host = all_ssh_prefs["sut_ssh_host"]
		return ssh_host
	
	
	def get_sut_ssh_port (self):
		conf_map = self.get_test_bl_configuration()
		all_ssh_prefs = conf_map["sut_ssh_prefs"]
		ssh_host = all_ssh_prefs["sut_ssh_port"]
		return ssh_host
	
	
	def get_sut_ssh_user (self):
		conf_map = self.get_test_bl_configuration()
		all_ssh_prefs = conf_map["sut_ssh_prefs"]
		ssh_host = all_ssh_prefs["sut_ssh_user"]
		return ssh_host
	
	
	def get_sut_ssh_passwd (self):
		conf_map = self.get_test_bl_configuration()
		all_ssh_prefs = conf_map["sut_ssh_prefs"]
		ssh_host = all_ssh_prefs["sut_ssh_passwd"]
		return ssh_host
	
	
	def get_sut_ssh_target_dir (self):
		conf_map = self.get_test_bl_configuration()
		all_ssh_prefs = conf_map["sut_ssh_prefs"]
		ssh_host = all_ssh_prefs["sut_ssh_target_dir"]
		return ssh_host
	
	
	def get_sut_config_files_path (self,
								   key = None):
		if self.test_bl_config:
			conf_map = self.get_test_bl_configuration()
			compiled_pattern = self.get_proj_dir_pttrn()
			if key == None:
				sut_config_files_paths = conf_map["sut_config_files"]
				
				if self.syst == 'Windows':
					self.path_to_proj = compiled_pattern.findall(self.module_abs_path)
					
					sut_config_files_path = sut_config_files_paths["windows"]["sut_config_files"]
					sut_config_files_path = os.path.join(str(self.path_to_proj[0]), sut_config_files_path)
					return sut_config_files_path
				elif self.syst == 'Linux':
					self.path_to_proj = compiled_pattern.findall(self.module_abs_path)
					
					sut_config_files_path = sut_config_files_paths["linux"]["sut_config_files"]
					sut_config_files_path = os.path.join(str(self.path_to_proj[0]), sut_config_files_path)
					return sut_config_files_path
			else:
				sut_config_files_paths = conf_map[key]
				if self.syst == 'Windows':
					self.path_to_proj = compiled_pattern.findall(self.module_abs_path)
					
					sut_config_files_path = sut_config_files_paths["windows"]["sut_config_files"]
					sut_config_files_path = os.path.join(str(self.path_to_proj[0]), sut_config_files_path)
					return sut_config_files_path
				elif self.syst == 'Linux':
					self.path_to_proj = compiled_pattern.findall(self.module_abs_path)
					
					sut_config_files_path = sut_config_files_paths["linux"]["sut_config_files"]
					sut_config_files_path = os.path.join(str(self.path_to_proj[0]), sut_config_files_path)
					return sut_config_files_path
	
	
	def get_sut_logging_config (self,
								key = None):
		if self.test_bl_config:
			conf_map = self.get_test_bl_configuration()
			if key == None:
				logging_conf_full = conf_map["sut_logging_config"]
				if self.syst == 'Windows':
					logging_conf_full_w = logging_conf_full["windows"]
					return logging_conf_full_w
				elif self.syst == 'Linux':
					logging_conf_full_l = logging_conf_full["linux"]
					return logging_conf_full_l
			else:
				logging_conf_full = conf_map[key]
				if self.syst == 'Windows':
					logging_conf_full_w = logging_conf_full["windows"]
					return logging_conf_full_w
				elif self.syst == 'Linux':
					logging_conf_full_l = logging_conf_full["linux"]
					return logging_conf_full_l
	
	
	def get_tests_logging_config (self):
		if self.test_bl_config:
			conf_map = self.get_test_bl_configuration()
			logging_conf_conf_file = conf_map["tests_logging_conf"]
			if self.syst == 'Windows':
				logging_conf_part_w = logging_conf_conf_file["windows"]["loggers_conf"]
				tests_logging_config_w = os.path.join(self.path_to_proj, logging_conf_part_w)
				return tests_logging_config_w
			elif self.syst == 'Linux':
				logging_conf_part_l = logging_conf_conf_file["linux"]["loggers_conf"]
				tests_logging_config_l = os.path.join(self.path_to_proj, logging_conf_part_l)
				return tests_logging_config_l
	
	
	def get_sut_logging_log_srv_exec (self):
		logging_conf = self.get_sut_logging_config()
		log_srv_exec = logging_conf["log_srv_exec"]
		return log_srv_exec
	
	
	def get_sut_logging_log_srv_dir (self):
		logging_conf = self.get_sut_logging_config()
		log_srv_dir = logging_conf["log_srv_dir"]
		return log_srv_dir
	
	
	def get_sut_logging_log_file_dir (self):
		logging_conf = self.get_sut_logging_config()
		log_srv_dir = logging_conf["log_file_dir"]
		return log_srv_dir
	
	
	def get_send_receive_prefs (self,
								key = None):
		conf_map = self.get_test_bl_configuration()
		send_receive_prefs = conf_map["send_receive_prefs"]
		return send_receive_prefs
	
	
	def get_udp_ip_to (self):
		sensend_receive_prefs = self.get_send_receive_prefs()
		udp_ip_to = sensend_receive_prefs["udp_ip_to"]
		return udp_ip_to
	
	
	def get_udp_port_to (self):
		sensend_receive_prefs = self.get_send_receive_prefs()
		udp_port_to = sensend_receive_prefs["udp_port_to"]
		return udp_port_to
	
	
	def get_udp_ip_from (self):
		sensend_receive_prefs = self.get_send_receive_prefs()
		udp_ip_from = sensend_receive_prefs["udp_ip_from"]
		return udp_ip_from
	
	
	def get_udp_port_from (self):
		sensend_receive_prefs = self.get_send_receive_prefs()
		udp_port_from = sensend_receive_prefs["udp_port_from"]
		return udp_port_from
	
	
	def get_udp_buffsize_from (self):
		sensend_receive_prefs = self.get_send_receive_prefs()
		udp_buffsize_from = sensend_receive_prefs["udp_buffsize_from"]
		return udp_buffsize_from
	
	
	def get_proj_dir_pttrn (self):
		if self.test_bl_config:
			conf_map = self.get_test_bl_configuration()
			if self.syst == 'Windows':
				win_pttrn = str(conf_map["proj_dir_pttrn"]["windows"])
				compiled_pattern = re.compile(win_pttrn)
				return compiled_pattern
			elif self.syst == 'Linux':
				lin_pttrn = str(conf_map["proj_dir_pttrn"]["linux"])
				compiled_pattern = re.compile(lin_pttrn)
				return compiled_pattern
	
	
	def get_proj_dir_path (self):
		compiled_pattern = self.get_proj_dir_pttrn()
		self.path_to_proj = compiled_pattern.findall(self.module_abs_path)
		return str(self.path_to_proj[0])
	
	
	def set_suite_conf (self,
						test_suite_conf_map):
		self.test_bl_config["test_suite_conf"] = test_suite_conf_map
		return


def test_this ():
	sc = ConfigTestEnv()
	full_config = sc.get_test_bl_configuration()
	vbox_dir = sc.get_local_vbox_dir()
	vbox_mng = sc.get_local_vbox_mng()
	clean_vm_img = sc.get_clean_vm_img()
	clean_snap = sc.get_clean_snap()
	
	ssh_full = sc.get_sut_ssh_prefs("sut_ssh_prefs")
	ssh_host = sc.get_sut_ssh_host()
	ssh_port = sc.get_sut_ssh_port()
	ssh_user = sc.get_sut_ssh_user()
	ssh_passwd = sc.get_sut_ssh_passwd()
	ssh_target_dir = sc.get_sut_ssh_target_dir()
	sut_conf_files_dir = sc.get_sut_config_files_dir()
	log_srv_exec = sc.get_sut_logging_log_srv_exec()
	log_srv_dir = sc.get_sut_logging_log_srv_dir()
	log_file_dir = sc.get_sut_logging_log_file_dir()
	udp_ip_to = sc.get_udp_ip_to()
	udp_port_to = sc.get_udp_port_to()
	udp_ip_from = sc.get_udp_ip_from()
	udp_port_from = sc.get_udp_ip_from()
	udp_buff_size_from = sc.get_udp_buffsize_from()
	return


if __name__ == '__main__':
	test_this()
