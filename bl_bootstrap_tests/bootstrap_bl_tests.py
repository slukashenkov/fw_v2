from __future__ import absolute_import
from __future__ import print_function

import configparser
import json
import logging
import os
import glob
import platform
import re
import shlex
import signal
import sys
import time
import argparse

from builtins import Exception
from pathlib import Path
from subprocess import Popen, check_output

# imports for scp which used Paramico as transport
import paramiko
from fabric2 import Connection
from scp import SCPClient

logging.basicConfig(level = logging.DEBUG,
                    format = '%(asctime)-25s %(levelname)-6s %(name)-10s %(module)10s %(threadName)-10s %(funcName)-10s  %(message)s',
                    )

class GetBuildTests():
    
    
    def __init__ (self,
                  build_id = None,
                  sect_name_blds = 'builds_ids',
                  sect_name_tdir = 'tests_dir',
                  path_to_conf = None
                  ):
        
        """"""
        '''-----------------------------------------------------------------------------------------------------------'''
        '''GET BUILD AND TESTS SPECIFIC VARIABLES'''
        self.build_id = build_id
        self.sect_name_blds = sect_name_blds
        self.sect_name_tdir = sect_name_tdir
        '''-----------------------------------------------------------------------------------------------------------'''
        '''GET PARAMS'''
        '''Lets find ot the system we run on'''
        self.syst = platform.system()
        
        '''And where we are'''
        self.proj_abs_path = os.path.abspath(os.path.dirname(__file__))
        
        '''Still using config parser for INI'''
        self.bootstrap_cnf = configparser.ConfigParser()
        
        if path_to_conf == None:
            
            if self.syst == 'Linux':
    
                self.bootstrap_cnf_location = os.path.join(self.proj_abs_path,
                                                           "bootstrap_conf.ini")
                #self.bootstrap_cnf_location = '/home/slon/BL_tests_project/bl_frame_work/bl_bootstrap_tests/bootstrap_conf.ini'
            elif self.syst == 'Windows':
                self.bootstrap_cnf_location = os.path.join(self.proj_abs_path,
                                                           "bootstrap_conf.ini")
                #self.bootstrap_cnf_location = 'C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\gitlabAutotestingMussonBL2\\bl_bootstrap_tests\\bootstrap_conf.ini'
        
        else:
            self.bootstrap_cnf_location = path_to_conf
        self.bootstrap_cnf.read(self.bootstrap_cnf_location)
        '''-----------------------------------------------------------------------------------------------------------'''
        '''SET ALL THE NEEDED PARAMS'''
        '''!!!LOG STUFF!!! AS IT HAPPENS'''
        self.logger = logging.getLogger(__name__)
        
        '''-----------------------------------------------------------------------------------------------------------'''
        '''
        SETUP SSH
        '''
        self.ssh_build_ip   = self.bootstrap_cnf['SSH_PREFS']['SSH_HOST_BUILD']
        self.ssh_build_port = self.bootstrap_cnf['SSH_PREFS']['SSH_PORT_BUILD']
        self.ssh_build_user = self.bootstrap_cnf['SSH_PREFS']['SSH_USER_NAME_BUILD']
        self.ssh_build_pswd = self.bootstrap_cnf['SSH_PREFS']['SSH_PASSWD_BUILD']
        
        self.ssh_tests_ip   = self.bootstrap_cnf['SSH_PREFS']['SSH_HOST_TESTS']
        self.ssh_tests_port = self.bootstrap_cnf['SSH_PREFS']['SSH_PORT_TESTS']
        self.ssh_tests_user = self.bootstrap_cnf['SSH_PREFS']['SSH_USER_NAME_TESTS']
        self.ssh_tests_pswd = self.bootstrap_cnf['SSH_PREFS']['SSH_PASSWD_TESTS']
        
        self.ssh_sut_ip   = self.bootstrap_cnf['SSH_PREFS']['SSH_HOST_SUT']
        self.ssh_sut_port = self.bootstrap_cnf['SSH_PREFS']['SSH_PORT_SUT']
        self.ssh_sut_user = self.bootstrap_cnf['SSH_PREFS']['SSH_USER_NAME_SUT']
        self.ssh_sut_pswd = self.bootstrap_cnf['SSH_PREFS']['SSH_PASSWD_SUT']
        
        self.ssh_startup_dir_sut = self.bootstrap_cnf['SSH_PREFS']['SSH_STARTUP_DIR_SUT']
        self.ssh_install_dir_lib_sut = self.bootstrap_cnf['SSH_PREFS']['SSH_INSTALL_DIR_LIB_SUT']
        self.ssh_install_dir_bin_sut = self.bootstrap_cnf['SSH_PREFS']['SSH_INSTALL_DIR_BIN_SUT']
        '''-----------------------------------------------------------------------------------------------------------'''
        '''
        SETUP SCP
        '''
        self.ssh_source_dir = None
        self.ssh_target_dir = None
        '''-----------------------------------------------------------------------------------------------------------'''
        ''' STUFF SPECIFIC FOR BOOTSTRAP '''
        '''Directories for build, configs, install scripts'''
        self.ssh_scp_content_location_build = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_BUILD']
        self.ssh_scp_content_location_test = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_TESTS']
        self.ssh_scp_content_location_sut = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_SUT']


        '''Patterns for the latest file search'''
        self.ssh_scp_build_name_ptrn = self.bootstrap_cnf['SCP_PREFS']['SCP_BUILD_NAME_PATTERN']
        self.ssh_scp_tests_name_ptrn = self.bootstrap_cnf['SCP_PREFS']['SCP_TESTS_NAME_PATTERN']
        '''Modules configs'''
        self.ssh_scp_confs_name_ptrn = self.bootstrap_cnf['SCP_PREFS']['SCP_CONFIG_FILES_PATTERN']
        self.ssh_scp_confs_ver       = self.bootstrap_cnf['SCP_PREFS']['SCP_CONFIG_FILES_VER']
        '''Install script'''
        self.ssh_scp_scrpt_name_ptrn = self.bootstrap_cnf['SCP_PREFS']['SCP_INSTALL_SCRPT_PATTERN']

        '''System specific current build location'''
        if self.syst == 'Windows':

            '''Build under test location'''
            self.ssh_scp_content_location_cntrl_build = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_CONTROL_HOST_BLD']

            '''When build id is not used find the latest file'''
            if self.build_id != None:
                self.ssh_scp_content_location_cntrl_build = self.ssh_scp_content_location_cntrl_build + '\\' \
                                                            + 'BL2_alt7_baselibraries_D_build#' + str(self.build_id) + ".tar.gz"
            else:
                bld_ptrn = self.ssh_scp_build_name_ptrn
                curr_build_file = self.find_latest_file(dir_path = self.ssh_scp_content_location_cntrl_build,
                                                        f_name_ptrn = bld_ptrn)
                self.ssh_scp_content_location_cntrl_build = curr_build_file


            '''Tests specifics'''
            '''TESTS location full path'''
            self.ssh_scp_content_location_cntrl_tests = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_CONTROL_HOST_TESTS']

            '''Modules configs'''
            self.ssh_scp_content_location_mod_confs  = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_CONTROL_HOST_CONFS']
            self.ssh_scp_content_location_mod_confs = os.path.join(self.proj_abs_path,
                                                           self.ssh_scp_content_location_mod_confs)

            '''Module configs are stored with the bootstrap scripts'''
            '''use the latest'''
            self.ssh_scp_content_location_cntrl_confs =  self.find_latest_file(dir_path=self.ssh_scp_content_location_mod_confs,
                                                                                f_name_ptrn=self.ssh_scp_confs_name_ptrn)

            '''Installation script(s)'''
            self.ssh_scp_content_location_inst_srpts = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_CONTROL_HOST_SCRIPTS']
            self.ssh_scp_content_location_inst_srpts = os.path.join(self.proj_abs_path,
                                                                       self.ssh_scp_content_location_inst_srpts)

            '''Module configs are stored with the bootstrap scripts'''
            '''use the latest'''
            self.ssh_scp_content_location_inst_srpts = self.find_latest_file(dir_path=self.ssh_scp_content_location_inst_srpts,
                                                                            f_name_ptrn=self.ssh_scp_scrpt_name_ptrn)


            #self.ssh_scp_content_location_cntrl_confs = self.ssh_scp_content_location_cntrl_tests + '\\' + self.ssh_scp_confs_name_ptrn + self.ssh_scp_confs_ver +  ".tar.gz"

        
        elif self.syst == 'Linux':

            '''Build under test location'''
            self.ssh_scp_content_location_cntrl_build = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_CONTROL_HOST_BLD_LUNUX']

            '''When build id is not used find the latest file'''
            if self.build_id != None:
                self.ssh_scp_content_location_cntrl_build = self.ssh_scp_content_location_cntrl_build \
                                                            + 'BL2_alt7_baselibraries_D_build#'  + str(self.build_id) + ".tar.gz"
            else:
                bld_ptrn = self.ssh_scp_build_name_ptrn
                curr_build_file = self.find_latest_file(dir_path = self.ssh_scp_content_location_cntrl_build,
                                                        f_name_ptrn = bld_ptrn)

                self.ssh_scp_content_location_cntrl_build = curr_build_file

            '''Tests specifics'''
            '''TESTS location full path'''
            self.ssh_scp_content_location_cntrl_tests = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_CONTROL_HOST_TESTS_LINUX']

            '''Modules configs'''
            self.ssh_scp_content_location_mod_confs = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_CONTROL_HOST_CONFS_LIN']
            self.ssh_scp_content_location_mod_confs = os.path.join(self.proj_abs_path,
                                                                   self.ssh_scp_content_location_mod_confs)

            '''Module configs are stored with the bootstrap scripts'''
            '''use the latest'''
            self.ssh_scp_content_location_cntrl_confs = self.find_latest_file(dir_path=self.ssh_scp_content_location_mod_confs,
                                                                              f_name_ptrn=self.ssh_scp_confs_name_ptrn)

            '''Installation script(s)'''
            self.ssh_scp_content_location_inst_srpts = self.bootstrap_cnf['SCP_PREFS']['SCP_LOCATION_CONTROL_HOST_SCRIPTS_LIN']
            self.ssh_scp_content_location_inst_srpts = os.path.join(self.proj_abs_path,
                                                                    self.ssh_scp_content_location_inst_srpts)

            '''Module configs are stored with the bootstrap scripts'''
            '''use the latest'''
            self.ssh_scp_content_location_inst_srpts = self.find_latest_file(
                                                        dir_path=self.ssh_scp_content_location_inst_srpts,
                                                        f_name_ptrn=self.ssh_scp_scrpt_name_ptrn)
        
        '''-----------------------------------------------------------------------------------------------------------'''
        '''
        SETUP FABRIC CONNECTION
        '''
        self.fabric_connection = None
        '''-----------------------------------------------------------------------------------------------------------'''
        '''
        SETUP dict for sh commands to be executed remotely
        '''
        self.ssh_install_commands_to_exec = {}
        
        '''-----------------------------------------------------------------------------------------------------------'''
        '''SETUP a possibility to check commands execution of the remote host via dedicated script.
        The script command should be part of the above dictionary and key for it should be made known in advance.
        '''
        self.ssh_ded_test_key = None
        
        if self.syst == 'Windows':
            self.vm_vbox_manage = self.bootstrap_cnf['LOCAL_VBOX_DIRS']['VBOXMANAGE_DIR']
        elif self.syst == 'Linux':
            self.vm_vbox_manage = self.bootstrap_cnf['LOCAL_VBOX_DIRS_LINUX']['VBOXMANAGE_DIR']
        
        self.vm_alt_img = self.bootstrap_cnf['CLEAN_IMAGES']['CLEAN_ALT']
        self.vm_alt_img_snapshot = self.bootstrap_cnf['CLEAN_IMAGES']['CLEAN_ALT_SNAP']
        self.vm_astra_img = self.bootstrap_cnf['CLEAN_IMAGES']['CLEAN_ASTRA']
        self.vm_astra_img_snapshot = self.bootstrap_cnf['CLEAN_IMAGES']['CLEAN_ASTRA_SNAP']
        
        '''=========================================================================================================='''
        '''SETUP LOG SERVER'''
        if self.syst == 'Windows':
            self.log_srv_exec = self.bootstrap_cnf['LOGGER_SRV']['LOGGER_SRV_EXEC']
            self.log_srv_dir = self.bootstrap_cnf['LOGGER_SRV']['LOGGER_SRV_DIR']
        elif self.syst == 'Linux':
            self.log_srv_exec = self.bootstrap_cnf['LOGGER_SRV_LINUX']['LOGGER_SRV_EXEC']
            self.log_srv_dir = self.bootstrap_cnf['LOGGER_SRV_LINUX']['LOGGER_SRV_DIR']
        '''=========================================================================================================='''
        '''SETUP START UP SCRIPT FOR ACTUAL TESTS'''
        self.test_start_scrpt_dir = self.proj_abs_path
        if self.syst == 'Windows':
            self.test_start_scrpt_exec = self.bootstrap_cnf['TESTS_START_SCRPT']['START_CRPT_EXEC_WIN']
            
        elif self.syst == 'Linux':
            self.test_start_scrpt_exec = self.bootstrap_cnf['TESTS_START_SCRPT']['START_CRPT_EXEC_LIN']
        
        self.ssh_remote_commands_conf_start = None
        self.ssh_remote_commands_conf_stop = None
        
        '''-----------------------------------------------------------------------------------------------------------'''
        '''GET MAPPING OF TESTS TO BUILDS'''
        if self.syst == 'Windows':
            self.tests_to_builds_map = self.bootstrap_cnf['BUILD_TO_TEST_MAP']['MAP_LOCATION']
            self.tests_to_builds_map =  os.path.join(self.proj_abs_path,
                                                     self.tests_to_builds_map)
        if self.syst == 'Linux':
            self.tests_to_builds_map = self.bootstrap_cnf['BUILD_TO_TEST_MAP_LINUX']['MAP_LOCATION']
            self.tests_to_builds_map = os.path.join(self.proj_abs_path,
                                                    self.tests_to_builds_map)
        
        self.read_data = ReadData(self.tests_to_builds_map)
        self.read_data.read_json_to_map()
        self.builds_map_to_search = self.read_data.final_map
        
        '''-----------------------------------------------------------------------------------------------------------'''
        '''PASS PARAMS TO UTILITY SCRIPTS'''
        self.scripts = ExtScripts(self)

        '''Collect commands for testing and distr directory'''
        self.ssh_dir_commands_to_exec_keys = self.scripts.conf_key_to_arr(conf_parser=self.bootstrap_cnf,
                                                                          section_key='SUT_BUILD_COPY_COMMANDS',
                                                                              switch='keys')
        self.ssh_dir_commands_to_exec_values = self.scripts.conf_key_to_arr(conf_parser=self.bootstrap_cnf,
                                                                                section_key='SUT_BUILD_COPY_COMMANDS',
                                                                                switch='values')

        '''Final MAP of commands for execution over SSH on tests start'''
        self.ssh_dir_commands_to_exec = self.scripts.zip_to_map(to_zip01=self.ssh_dir_commands_to_exec_keys,
                                                                    to_zip02=self.ssh_dir_commands_to_exec_values)


        '''Collect commands for installation'''
        self.ssh_install_commands_to_exec_keys = self.scripts.conf_key_to_arr(conf_parser = self.bootstrap_cnf,
                                                                              section_key = 'SUT_BUILD_INSTALL_COMMANDS',
                                                                              switch = 'keys')
        self.ssh_install_commands_to_exec_values = self.scripts.conf_key_to_arr(conf_parser = self.bootstrap_cnf,
                                                                                section_key = 'SUT_BUILD_INSTALL_COMMANDS',
                                                                                switch = 'values')

        '''Final MAP of commands for execution over SSH on tests start'''
        self.ssh_install_commands_to_exec = self.scripts.zip_to_map(to_zip01 = self.ssh_install_commands_to_exec_keys,
                                                                    to_zip02 = self.ssh_install_commands_to_exec_values)

        '''Command to test execution of the previous installation steps'''
        if self.syst == 'Windows':
            self.ssh_commands_test_key = self.bootstrap_cnf['SUT_BUILD_INSTALL_TEST_KEY']['TEST_SCRPT_KEY']
            self.ssh_commands_test_path = self.bootstrap_cnf['SUT_BUILD_INSTALL_TEST_KEY']['TEST_SCRPT_PATH']
        elif self.syst == 'Linux':
            self.ssh_commands_test_key = self.bootstrap_cnf['SUT_BUILD_INSTALL_TEST_KEY_LINUX']['TEST_SCRPT_KEY']
            self.ssh_commands_test_path = self.bootstrap_cnf['SUT_BUILD_INSTALL_TEST_KEY_LINUX']['TEST_SCRPT_PATH']
        return
    
    '''UTILITY FUCTIONS'''
    def find_latest_file(self,
                         dir_path = None,
                         f_name_ptrn = None):

        files_path = os.path.join(dir_path, f_name_ptrn)
        files = sorted(glob.iglob(files_path), key=os.path.getctime, reverse=True)
        return files[0]

    
    def run_tests (self):
        self.scripts.script_exec = self.test_start_scrpt_exec
        self.scripts.script_dir = self.test_start_scrpt_dir
        self.scripts.run_script()
    
    
    def start_logserver (self):
        self.scripts.vm_log_srv_exec = self.log_srv_exec
        self.scripts.vm_log_srv_exec_dir = self.log_srv_dir
        self.scripts.start_log_server()
        return
    
    
    def stop_logserver (self):
        name = "javaw"
        if self.syst == 'Windows':
            log_srv_pid = check_output(["ps", "-laW"],
                                       universal_newlines = True)
        elif self.syst == 'Linux':
            log_srv_pid = check_output(["ps", "-afx"],
                                       universal_newlines = True)
        # os.kill(get_pid(whatever_you_search), signal.SIGTERM)  # or signal.SIGKILL
        # os.kill(check_output(["pidof", name]),
        #       signal.SIGTERM)  # or signal.SIGKILL
        proc_names_data = log_srv_pid.split('\n')
        pid = []
        pid = self.getPidByName(proc_name = name,
                                proc_data_in = proc_names_data)
        
        for i in pid:
            os.kill(i,
                    signal.SIGTERM)  # or signal.SIGKILL
        return
    
    
    '''=============================================================================================================='''
    '''For linux only'''
    '''=============================================================================================================='''
    
    
    def getPidByName (self,
                      proc_name = None,
                      proc_data_in = None):
        
        if proc_data_in != None:
            process = proc_data_in
        else:
            process = check_output(["ps", "-fea"]).split('\n')
        pid = []
        for x in range(0, len(process)):
            args_prep = re.sub("\s+", ",", process[x].strip())
            args = args_prep.split(',')
            for j in range(0, len(args)):
                part = args[j]
                if (proc_name in part):
                    pid.append(int(args[0]))
        return pid
    
    
    def get_pid_from_proc (self):
        for dirname in os.listdir('/proc'):
            if dirname == 'curproc':
                continue
            
            try:
                with open('/proc/{}/cmdline'.format(dirname), mode = 'rb') as fd:
                    content = fd.read().decode().split('\x00')
            except Exception:
                continue
            
            for i in sys.argv[1:]:
                if i in content[0]:
                    print('{0:<12} : {1}'.format(dirname, ' '.join(content)))
        return
    
    
    def get_build_tests (self):
        """"""
        '''GET FILE NAME OF THE TESTS CORRESPONDING TO THE CURRENT BUILD'''
        curr_tests_file = self.scripts.test_build_to_test(map_to_test = self.builds_map_to_search,
                                                          key_to_test = self.build_id,
                                                          sub_key_name_builds = self.sect_name_blds,
                                                          sub_key_name_tdir = self.sect_name_tdir) + self.ssh_scp_tests_name_ptrn
        
        '''SET EVERYTHING FOR SCP TESTS TO CONTROL HOST'''
        '''Where first'''
        self.scripts.ssh_target_ip = self.ssh_tests_ip
        self.scripts.ssh_target_port = self.ssh_tests_port
        self.scripts.ssh_target_user = self.ssh_tests_user
        self.scripts.ssh_target_pswd = self.ssh_tests_pswd
        
        '''What second'''
        self.scripts.ssh_scp_content_location = curr_tests_file
        self.scripts.ssh_target_dir = self.ssh_scp_content_location_cntrl_tests
        '''get the stuff'''
        '''TODO: cleanup dir first'''
        self.logger.info("<------- START PROCESS OF GETTING BUILD AND TESTS FROM SFTP ------> ")
        self.scripts.scp_get_files()
        
        '''GET FILE NAME OF THE CURRENT BUILD'''
        curr_build_file = self.ssh_scp_content_location_build + str(self.build_id) + self.ssh_scp_build_name_ptrn


        '''SET EVERYTHING FOR SCP BUILD TO CONTROL HOST'''
        '''Where first'''
        self.scripts.ssh_target_ip = self.ssh_build_ip
        self.scripts.ssh_target_port = self.ssh_build_port
        self.scripts.ssh_target_user = self.ssh_build_user
        self.scripts.ssh_target_pswd = self.ssh_build_pswd
        
        '''What second'''
        self.scripts.ssh_scp_content_location = curr_build_file
        self.scripts.ssh_target_dir = self.ssh_scp_content_location_cntrl_build
        '''get the stuff'''
        '''TODO: cleanup dir first'''
        self.scripts.scp_get_files()
        self.logger.info("<------ STOP PROCESS OF GETTING BUILD AND TESTS FROM SFTP ------> ")
        return
    
    
    def put_build_to_sut (self):
        """
        :return:
        """
        self.logger.info("<------- START PROCESS OF PUTTING CURRENT BUILD ON SUT ------> ")
        '''SET WHERE WE ARE GOING to PUT current BUILD'''
        '''SET EVERYTHING FOR SCP TESTS TO CONTROL HOST'''
        '''Where first'''
        self.scripts.ssh_target_ip = self.ssh_sut_ip
        self.scripts.ssh_target_port = self.ssh_sut_port
        self.scripts.ssh_target_user = self.ssh_sut_user
        self.scripts.ssh_target_pswd = self.ssh_sut_pswd
        
        '''deprecated there is a dedicated
        box for KD testing now'''
        '''Lets START VIRTUAL BOX FIRST'''
        #self.logger.info("<------- LETS START VBox FIRST ------> ")
        #self.scripts.vm_shutdown()
        #self.scripts.vm_start()
        #self.logger.info("<------- WOW VBox HAS STARTED ------> ")

        '''Check if dir for coping distr exists'''
        self.create_build_dir()
        
        '''Copy build'''
        if self.syst == 'Windows':
            self.scripts.ssh_scp_content_location = self.ssh_scp_content_location_cntrl_build
            #C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\workspace\\BL2_alt7_baselibraries_D_autotests\\BL2_alt7_baselibraries_D_build#445.tar.gz
            #C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\workspace\\BL2_alt7_baselibraries_D_autotests\\BL2_alt7_baselibraries_D_build#445.tar.gz
        if self.syst == 'Linux':
            self.scripts.ssh_scp_content_location = self.ssh_scp_content_location_cntrl_build
            
            
        self.scripts.ssh_target_dir = self.ssh_scp_content_location_sut
        '''get the stuff'''
        '''TODO: cleanup dir first'''
        self.scripts.scp_put_files()
        
        '''
        Copy module configs
        '''
        self.scripts.ssh_scp_content_location = self.ssh_scp_content_location_cntrl_confs
        self.scripts.ssh_target_dir = self.ssh_scp_content_location_sut
        self.scripts.scp_put_files()

        '''
        Copy install script
        '''
        self.scripts.ssh_scp_content_location = self.ssh_scp_content_location_inst_srpts
        self.scripts.ssh_target_dir = self.ssh_scp_content_location_sut
        self.scripts.scp_put_files()
        
        
        '''Deprecated
        it was assumed initially that tests have to be copied
        from some place  and then copied to ctrl station
        however now the need is not
        '''
        '''And also some tests'''
        '''
        self.scripts.ssh_scp_content_location = self.ssh_commands_test_path
        self.scripts.ssh_target_dir = self.ssh_startup_dir_sut
        self.scripts.scp_put_files()
        '''
        return

    def create_build_dir(self):
        self.scripts.ssh_commands_to_exec = self.ssh_dir_commands_to_exec
        '''SET EVERYTHING FOR SCP BUILD TO CONTROL HOST'''
        '''Where first'''
        self.scripts.ssh_target_ip = self.ssh_sut_ip
        self.scripts.ssh_target_port = self.ssh_sut_port
        self.scripts.ssh_target_user = self.ssh_sut_user
        self.scripts.ssh_target_pswd = self.ssh_sut_pswd

        self.scripts.ssh_ded_test_key = self.ssh_commands_test_key
        self.scripts.create_build_dir()
        return
    
    def install_new_build (self):
        self.scripts.ssh_commands_to_exec = self.ssh_install_commands_to_exec
        '''SET EVERYTHING FOR SCP BUILD TO CONTROL HOST'''
        '''Where first'''
        self.scripts.ssh_target_ip = self.ssh_sut_ip
        self.scripts.ssh_target_port = self.ssh_sut_port
        self.scripts.ssh_target_user = self.ssh_sut_user
        self.scripts.ssh_target_pswd = self.ssh_sut_pswd
        
        self.scripts.ssh_ded_test_key = self.ssh_commands_test_key
        self.scripts.install_build()
        return


class ExtScripts:
    
    
    def __init__ (self,
                  config_file = None,
                  commands_file = None,
                  script_location = None,
                  script_type = "win"
                  ):
        """
        :param commands_file:
        :param script_location:
        :param script_type:
        """
        
        '''SET ALL THE NEEDED PARAMS'''
        '''!!!LOG STUFF!!! AS IT HAPPENS'''
        self.logger = logging.getLogger(__name__)
        
        '''CONFIG ASSUMING ENV VARS'''
        self.commands_file = commands_file
        self.script_location = script_location
        self.script_type = script_type
        '''
        CONFIG FILE IS AN ABSTRACTION HERE
        SINCE THIS CLASS IS JUST REUSED ALMOST AS
        IS FOR SIMPLICITY THE GetBuildTest class
        which reads actual ini
        serves the role of config class from
        actual test suites.
        But the basic idea is the same
        setup of params used at the moment
        '''
        self.conf = config_file
        
        '''
        SETUP SSH
        '''
        self.ssh_target_ip = None
        self.ssh_target_port = None
        self.ssh_target_user = None
        self.ssh_target_pswd = None
        self.ssh_client = None
        '''
        SETUP SSH COPY
        '''
        self.ssh_scp_content_location = None
        self.ssh_target_dir = None
        '''
        SETUP FABRIC CONNECTION
        '''
        self.fabric_connection = None
        
        '''
        SETUP commands to be executed remotely
        '''
        self.ssh_commands_to_exec = {}
        
        '''
        SETUP a possibility to check commands execution
        of the remote host via dedicated script.
        The script command should be part of the above
        dictionary and key for that should be made known
        in advance
        '''
        self.ssh_ded_test_key = None
        
        '''
        SETUP PARAMS when CONFIG is available
        '''
        if self.conf == None:
            '''
            SETUP VIRT_BOX exec commands (VBoxmanage based) from conf file PREFS
            '''
            self.vm_start_cmnd = None
            self.vm_shutdown_cmnd = None
            self.vm_resnap_cmnd = None
            self.vm_makesnap_cmnd = None
        else:
            '''SETUP VIRT_BOX exec commands (VBoxmanage based)
            from conf file PREFS.
            These do things like restore to the proper snap, stop, start VBox image
            currenly used etc.
            '''
            self.set_vbox_manage()
            
            '''SETUP SSH Connection PARAMS'''
            '''These are general prefs for any ssh connection establishment
                and will be used to connect to
                build/test/sut machines in this BOOTSTRAP SCENARIO
            '''
            self.ssh_target_ip = None
            self.ssh_target_port = None
            self.ssh_target_user = None
            self.ssh_target_pswd = None
            
            '''
            SETUP SSH COPY.
            the same as above.
            Whether it is get or put they are to HELP.
            '''
            self.ssh_source_dir = None
            self.ssh_target_dir = None
            
            '''------------------------------------------------------------------------------------------------------'''
            ''' STUFF SPECIFIC FOR BOOTSTARP '''
            '''Files locations and ssh connections.
            Probably they must be deleted manages without them
            but such a illustration of not very well thought through
            'good intentions' pyving way to ... obviously
            there is always such a big temptation to be good.
            '''
            self.ssh_scp_content_location_build = None
            self.ssh_scp_content_location_test = None
            self.ssh_scp_content_location_sut = None
            
            '''Connections preferences'''
            self.ssh_target_build_ip = None
            self.ssh_target_build_port = None
            self.ssh_target_build_user = None
            self.ssh_target_build_pswd = None
            
            self.ssh_target_tests_ip = None
            self.ssh_target_tests_port = None
            self.ssh_target_tests_user = None
            self.ssh_target_tests_pswd = None
            
            self.ssh_target_sut_ip = None
            self.ssh_target_sut_port = None
            self.ssh_target_sut_user = None
            self.ssh_target_sut_pswd = None
            
            '''scp preferences '''
            self.ssh_scp_content_location_build = None
            self.ssh_scp_content_location_test = None
            self.ssh_scp_content_location_sut = None
            '''
            And they are all set to serve for FUCK knows what purpose.
            Lovely....
            Stupidity it is to think that anything can be prepared "in advance".
            '''
            # self.set_all_ssh_connections()
            '''------------------------------------------------------------------------------------------------------'''
            '''SETUP A PLACEHOLDER FOR ANY EXTERNAL SCRIPT EXEC PARAMS'''
            self.script_exec = None
            self.script_dir = None
        return
    
    
    def run_script (self):
        self.logger.debug("<== RUNNING EXTERNAL SCRIPT ==>")
        self.logger.debug(self.script_exec)
        p = Popen(self.script_exec,
                  shell = False,
                  cwd = self.script_dir
                  )
        stdout, stderr = p.communicate()
        p.terminate()
        p.kill()
        self.logger.debug("<== STOP RUNNING EXTERNAL SCRIPT -|DONE|- ==>")
        return
    
    
    '''--------------------------------------------------------------------------------------------------------------'''
    '''Functions for remote shell scripts execution'''
    
    
    def install_build (self):
        self.set_fabric_connection()
        self.fabric_run_commands()
        return

    def create_build_dir (self):
        self.set_fabric_connection()
        self.fabric_run_commands()
        return
    
    
    def start_sut (self):
        self.set_fabric_connection()
        self.fabric_run_commands()
        time.sleep(40)
        return
    
    
    def stop_sut (self):
        self.set_fabric_connection()
        self.fabric_run_commands()
        return
    
    
    def restart_sut (self):
        self.start_sut()
        self.stop_sut()
        return
    
    
    '''------------------------------------------------------------------------------------------------------------------'''
    '''Functions VM execution'''
    '''------------------------------------------------------------------------------------------------------------------'''
    
    
    def vm_start (self):
        self.logger.debug("<== Start  VM ==>")
        self.logger.debug(self.vm_start_cmnd)
        
        if self.conf.syst == 'Windows':
            p = Popen(self.vm_start_cmnd,
                      shell = False,
                      cwd = self.script_location
                      )
            stdout, stderr = p.communicate()
        elif self.conf.syst == 'Linux':
            # p = Popen(self.vm_shutdown_cmnd,
            p = Popen(shlex.split(self.vm_start_cmnd),
                      shell = False,
                      cwd = self.script_location
                      )
            stdout, stderr = p.communicate()
        
        '''It takes some time for Virtual box
        to start.
        
        SO here we are waiting while ssh session can be opened
        into box as a test.
        It is good enough indication that other
        activities can be performed on the REMOTE boX'''
        test = 1
        while test == 1:
            try:
                time.sleep(60)
                self.logger.debug("<==SSH client attempts to connect to VM ==>")
                
                self.create_Paramiko_SSHClient()
                ssh_trans = self.ssh_client.get_transport()
                ssh_conn_state = ssh_trans.is_active()
                
                if ssh_conn_state == True:
                    test = 2
                else:
                    raise Exception('Something UnPredictable is happening with SSH_Client')
                
                self.logger.debug("<==SSH client HAS CONNECTED to VM -|DONE|- ==>")
            except:
                try:
                    raise
                except TimeoutError:
                    self.ssh_client.close()
                    continue
                except Exception as e:
                    self.ssh_client.close()
                    continue
        
        p.terminate()
        p.kill()
        return
    
    
    def vm_shutdown (self):
        
        self.logger.debug("<==SHUTTING DOWN NEEDED image IF IT IS UP ==>")
        self.logger.debug(self.vm_shutdown_cmnd)
        
        if self.conf.syst == 'Windows':
            p = Popen(self.vm_shutdown_cmnd,
                      # p = Popen(shlex.split(self.vm_shutdown_cmnd),
                      shell = False,
                      cwd = self.script_location
                      )
            stdout, stderr = p.communicate()
            p.terminate()
            p.kill()
            self.logger.debug("<==SHUTTING DOWN NEEDED image -|DONE|- ==>")
            return
        elif self.conf.syst == 'Linux':
            # p = Popen(self.vm_shutdown_cmnd,
            p = Popen(shlex.split(self.vm_shutdown_cmnd),
                      shell = False,
                      cwd = self.script_location
                      )
            stdout, stderr = p.communicate()
            p.terminate()
            p.kill()
            self.logger.debug("<==SHUTTING DOWN NEEDED image -|DONE|- ==>")
            return
    
    
    def vm_restore_snap (self):
        self.logger.debug("<== RESTORING NEEDED SNAP ==>")
        self.logger.debug(self.vm_resnap_cmnd)
        p = Popen(self.vm_resnap_cmnd,
                  shell = False,
                  cwd = self.script_location
                  )
        stdout, stderr = p.communicate()
        p.terminate()
        p.kill()
        self.logger.debug("<== RESTORING NEEDED SNAP -|DONE|- ==>")
        return
    
    
    '''------------------------------------------------------------------------------------------------------------------'''
    '''Functions for LOGGING server control'''
    '''------------------------------------------------------------------------------------------------------------------'''
    
    
    def start_log_server (self):
        self.logger.debug("<== STARTING Log Server FOR BL to WRITE OUT its STATUS ==>")
        self._p = Popen(self.vm_log_srv_exec,
                        shell = False,
                        cwd = self.vm_log_srv_exec_dir
                        )
        stdout, stderr = self._p.communicate()
        log_srv_pid = self._p.pid
        self._p.terminate()
        self._p.kill()
        log_srv_pid = self._p.pid
        return
    
    
    '''------------------------------------------------------------------------------------------------------------------'''
    '''Functions for retrieving builds and tests'''
    '''------------------------------------------------------------------------------------------------------------------'''
    
    
    def test_build_to_test (self,
                            map_to_test = None,
                            key_to_test = None,
                            sub_key_name_builds = None,
                            sub_key_name_tdir = None):
        found = False
        if map_to_test != None:
            for key in map_to_test:
                res = map_to_test.get(key)
                builds = res[sub_key_name_builds]
                
                if int(key_to_test) in builds:
                    res02 = res[sub_key_name_tdir]
                    found = True
                    return res02
        # break
        if found != True:
            raise Exception("BUILD ID IS NOT IN CONF FILE")
        return
    
    
    def get_build (self):
        self.ssh_set_connection_params()
        self.set_fabric_connection()
        self.scp_files()
        return
    
    
    def get_tests (self):
        return
    
    
    '''------------------------------------------------------------------------------------------------------------------'''
    '''Common tools'''
    '''------------------------------------------------------------------------------------------------------------------'''
    '''Splitting on delimeter and getting element by index'''
    
    
    def str_split_get_pop_elem (self,
                                str_in = None,
                                delim_in = None,
                                which_elem = None):
        
        if (str_in or delim_in) == None:
            raise Exception("Missing some params")
        
        if (not (str(which_elem) == "FIRST")) and (not (str(which_elem) == "LAST")) and (
                not isinstance(which_elem, int)):
            raise Exception("INDEX PASSED is NOT a VALID 'FIRST or 'LAST' string OR  NOT a NUMBER" + which_elem)
        
        else:
            res_arr = str_in.split(delim_in)
            if which_elem == 'LAST':
                res = res_arr.pop()
                return res
            if which_elem == 'FIRST':
                res = res_arr.pop(0)
                return res
            else:
                # if isinstance(which_elem, int):
                res = res_arr.pop(which_elem)
                return res
        # else:
        #   raise Exception("INDEX PASSED is NOT a NUMBER")
        return
    
    
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
    
    
    '''Extracting some conf params to DICT
    '''
    
    
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
    
    
    ''' ENV VARS
    '''
    
    
    def load_env_vars (self):
        # def set_env_vars(self):
        """
           Run the cmd file to set env variables
           :param default_level:
           :param env_key:
           :return:
        """
        ''' Run the cmd file to set env variables'''
        if self.script_type == "win":
            p = Popen(self.commands_file,
                      shell = False,
                      cwd = self.script_location
                      )
            stdout, stderr = p.communicate()
            p.terminate()
            p.kill()
            
            return
        if self.script_type == "sh":
            return
    
    
    '''------------------------------------------------------------------------------------------------------------------'''
    '''Functions for SCP and remote commands exec over SSH'''
    '''------------------------------------------------------------------------------------------------------------------'''
    
    
    def scp_put_files (self):
        """"""
        '''SET CONFIG SCP PARAMS'''
        if self.conf != None:
            '''SET CONNECTION PREFS'''
            # self.set_connection_params()
            '''SET SSH CLIENT AND TRANSPORT'''
            self.create_Paramiko_SSHClient()
            scp = SCPClient(self.ssh_client.get_transport())
            '''SET PREFS AND COPY ALL CONFIGS AND SCRIPTS to DUT'''
            # self.set_scp_details()
            scp.put(self.ssh_scp_content_location, remote_path = self.ssh_target_dir)
            return
        else:
            raise ValueError("Configuration file is not PRESENT in the class")
    
    
    def scp_get_files (self):
        """"""
        if self.conf != None:
            '''SET CONNECTION PREFS'''
            # self.set_connection_params()
            '''SET SSH CLIENT AND TRANSPORT'''
            self.create_Paramiko_SSHClient()
            scp = SCPClient(self.ssh_client.get_transport())
            self.logger.info("<== SCP CLASS STARTED GETTING files ==> ")
            scp.get(remote_path = self.ssh_scp_content_location,
                    local_path = self.ssh_target_dir)
            scp.close()
            self.logger.info("<== SCP CLASS HAS GOT ==> ")
            
            '''Check if it is actually here'''
            f_name = self.str_split_get_pop_elem(str_in = self.ssh_scp_content_location,
                                                 delim_in = '/',
                                                 which_elem = 'LAST'
                                                 )
            if self.conf.syst == 'Windows':
                copied_file = Path(self.ssh_target_dir + '\\' + f_name)
            elif self.conf.syst == 'Linux':
                copied_file = Path(self.ssh_target_dir + '/' + f_name)
            
            if copied_file.is_file():
                self.logger.debug("<== File with name  ==> ")
                self.logger.debug("<==" + str(copied_file) + "==> ")
                self.logger.debug("<==  seems to be in place Now the question is it the right one  ---> ")
            else:
                raise ValueError("Configuration file is not PRESENT in the CLASS!!!")
        return
    
    
    def set_all_ssh_connections (self):
        """
        VAR SSH points connections
        :return:
        """
        self.ssh_target_build_ip = self.conf.ssh_build_ip
        self.ssh_target_build_port = self.conf.ssh_build_port
        self.ssh_target_build_user = self.conf.ssh_build_user
        self.ssh_target_build_pswd = self.conf.ssh_build_pswd
        
        self.ssh_target_tests_ip = self.conf.ssh_tests_ip
        self.ssh_target_tests_port = self.conf.ssh_tests_port
        self.ssh_target_tests_user = self.conf.ssh_tests_user
        self.ssh_target_tests_pswd = self.conf.ssh_tests_pswd
        
        self.ssh_target_sut_ip = self.conf.ssh_sut_ip
        self.ssh_target_sut_port = self.conf.ssh_sut_port
        self.ssh_target_sut_user = self.conf.ssh_sut_user
        self.ssh_target_sut_pswd = self.conf.ssh_sut_pswd
        
        '''
        SETUP SSH COPY
        '''
        self.ssh_scp_content_location_build = self.conf.ssh_scp_content_location_build
        self.ssh_scp_content_location_test = self.conf.ssh_scp_content_location_test
        self.ssh_scp_content_location_sut = self.conf.ssh_scp_content_location_sut
    
    
    def set_connection_params (self):
        """
        SET CONNECTION PREFS
        """
        if self.conf != None:
            self.ssh_target_ip = self.conf.ssh_host
            self.ssh_target_port = self.conf.ssh_port
            self.ssh_target_user = self.conf.ssh_user
            self.ssh_target_pswd = self.conf.ssh_pwd
        else:
            raise Exception('Configuration class is NOT loaded BUT needed. To early to set that!')
        return
    
    
    '''------------------------------------------------------------------------------------------------------------------'''
    '''SETTERS for VARIOUS PARAMS'''
    '''------------------------------------------------------------------------------------------------------------------'''
    
    
    def create_Paramiko_SSHClient (self):
        """
        Setup pure paramico SSH client
        :return:
        """
        if self.conf == None:
            self.set_connection_params()
        
        if self.ssh_client != None:
            self.ssh_client.close()
        
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        self.logger.debug(" <== CONNECTION PARAMS: " + self.ssh_target_ip + ": " + self.ssh_target_port + " ==>")
        
        self.ssh_client.connect(hostname = self.ssh_target_ip,
                                port = self.ssh_target_port,
                                username = self.ssh_target_user,
                                password = self.ssh_target_pswd
                                )
        return
    
    
    def set_fabric_connection (self):
        """
        SET CONNECTION PREFS
        """
        self.fabric_connection = Connection(host = self.ssh_target_ip,
                                            port = self.ssh_target_port,
                                            user = self.ssh_target_user)
        self.fabric_connection.connect_kwargs.password = self.ssh_target_pswd
        return
    
    
    def set_scp_details (self):
        """
        SET ALL THE PARAMS RELATED TO COPING
        :return:
        """
        self.ssh_scp_content_location = self.conf.ssh_content_to_copy
        self.ssh_target_dir = self.conf.ssh_target_dir
        return
    
    
    def set_vbox_manage (self):
        """
        SETUP VIRT_BOX exec commands (VBoxmanage based) from conf file PREFS
        """
        if self.conf != None:
            self.vm_start_cmnd = self.conf.vm_vbox_manage + ' startvm ' + self.conf.vm_alt_img + ' --type headless'
            self.vm_shutdown_cmnd = self.conf.vm_vbox_manage + ' controlvm ' + self.conf.vm_alt_img + ' poweroff'
            self.vm_resnap_cmnd = self.conf.vm_vbox_manage + ' snapshot ' + self.conf.vm_alt_img + ' restore ' + self.conf.vm_alt_img_snapshot
            self.vm_makeclone_cmnd = self.conf.vm_vbox_manage + ' clonevm ' + self.conf.vm_alt_img
        else:
            raise Exception("Test Suite`s conf file is not Present")
        return
    
    
    '''------------------------------------------------------------------------------------------------------------------'''
    '''UTILITY FUNCTIONS '''
    '''------------------------------------------------------------------------------------------------------------------'''
    
    
    def fabric_run_commands (self):
        """
        TODO: There must be a possibility of
        dedicated test on remote host with a ASH script
        which may be needed only in some
        cases. The script should be uploaded to the target machine
        in the same archive as config files and start scripts.
        For that configure special key on the class level and
        after check whether it exists pop a command for the script execution
        from common dict (may not be entirely good idea but will work)
        """
        
        ded_test_command = None
        if self.ssh_ded_test_key != None:
            ded_test_command = self.ssh_commands_to_exec.pop(self.ssh_ded_test_key)
        else:
            raise Exception("TESTING SCRIPT IS NOT PRESENT")
            return
        
        for key, command in self.ssh_commands_to_exec.items():
            
            if key == self.ssh_ded_test_key:
                # ded_test_command = self.ssh_commands_to_exec.pop(self.ssh_ded_test_key)
                continue
            else:
                self.logger.debug("<== THIS COMMAND is Going To be Executed REMOTELY ==>")
                self.logger.debug(str(command))
                self.logger.debug("<===================================================>")
                result = self.fabric_connection.run(command)
            
            if ded_test_command != None:
                result_dedicated_test = self.fabric_connection.run(ded_test_command)
            
            else:
                result_dedicated_test = None
            '''
            self.vm_ssh_cmds_exec_banner(command=command,
                                         ending=' for the key ' + str(key) + ' has been executed ',
                                         exec_res01='result.ok: ' + str(result.ok),
                                         exec_res02='result.return_code: ' + str(result.return_code),
                                         exec_res03='result_dedicated_test.return_code: ' + str(
                                             result_dedicated_test.return_code),
                                         logging_level='DEBUG',
                                         logger=self.logger
                                         )
            '''
            self.logger.debug("<===================================================>")
            self.logger.debug("<== WITH THE FOLLOWING RESULT ==>")
            self.logger.debug(str(result.ok) + ' ' + str(result.ok) + ' ' + str(result.return_code) + ' ' + str(
                result_dedicated_test.return_code))
            self.logger.debug("<===================================================>")
            if result.ok == True and result.return_code == 0 and (
                    result_dedicated_test != None or result_dedicated_test.return_code == 0):
                pass
            else:
                raise Exception('Last command did not go thru. Execution interrupted')
        return
    
    
    def set_test_env (self):
        """
        Function:
         1) starts VM
         2) copies current archive of configs and scripts to SUT Host
         3) sets predefined start SUT remote commands as default
         4) executes then in start)sut function
        :return:
        """
        
        '''make it avalable to the ScriptsControlling class'''
        # es.conf = sonata_conf
        self.vm_shutdown()
        self.vm_start()
        
        '''test whether files can be copied via scp'''
        self.scp_files()
        
        '''Do the test for actions on the remote host'''
        self.ssh_ded_test_key = 'test_exec'
        
        '''Start the SUT on the remote box'''
        self.ssh_commands_to_exec = self.sut_start_commands
        self.start_sut()
        return
    
    
    def tear_down__test_env (self):
        """
        Function:
         1) Stops SUT
         2) Stops VM
         3) Restores clean snap
        :return:
        """
        self.ssh_commands_to_exec.clear()
        self.ssh_commands_to_exec = self.sut_stop_commands
        self.stop_sut()
        self.vm_shutdown()
        self.vm_restore_snap()
        return
    
    
    '''
    class ReadData:
        def __init__(self,
                     data_location_map="C:\\data_from\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\test_bl\\test_sonata_plugin\\resources_sonata\\sonata_fields",
                     data_location_list="C:\\data_from\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\test_bl\\test_sonata_plugin\\resources_sonata\\sonata_fields"
                     ):
            self.data_location_map = data_location_map
            self.data_location_list = data_location_list
            self.final_map = None
            self.final_list = None
            return

        def read_file_to_map(self):
            map = {}
            with open(self.data_location_map) as f:
                for line in f:
                    (key, val) = line.split()
                    map[key] = val
            self.final_map = map
            return

        def read_file_to_list(self):
            list = []
            with open("file.txt") as f:
                for line in f:
                    (key, val) = line.split()
                    list.append(val)
            self.final_list = list
            return

        def read_json_to_map(self):
            with open(self.data_location_map, "r") as read_file:
                map = json.load(read_file)
                self.final_map = map
            return

        def read_json_to_list(self):
            return
    '''


class ReadData:
    
    
    def __init__ (self,
                  data_location_map = None,
                  data_location_list = None
                  ):
        self.data_location_map = data_location_map
        self.data_location_list = data_location_list
        self.final_map = None
        self.final_list = None
        return
    
    
    def read_file_to_map (self):
        map = {}
        with open(self.data_location_map) as f:
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
    

    def read_json_to_map (self):
        with open(self.data_location_map, "r") as read_file:
            map = json.load(read_file)
            self.final_map = map
        return
    
    
    def read_json_to_list (self):
        return

def create_parser ():
    parser = argparse.ArgumentParser()
    parser.add_argument('-id', help = 'Numerical ID of the build')
    return parser

def test_this (build_id = None,
               sect_name_blds = 'builds_ids',
               sect_name_tdir = 'tests_dir'
               ):
    # imports for scp which used Paramico as transport
    
    curr_build_id = build_id
    curr_sect_name_blds = sect_name_blds
    curr_sect_name_tdir = sect_name_tdir

    boot_str = GetBuildTests(build_id       = curr_build_id,
                             sect_name_blds = curr_sect_name_blds,
                             sect_name_tdir = curr_sect_name_tdir)
    
    print("--->>>>here should be log servers start<<<---")
    # boot_str.start_logserver()
    # boot_str.stop_logserver()
    
    #boot_str.get_build_tests()
    boot_str.put_build_to_sut()
    boot_str.install_new_build()
    #boot_str.run_tests()
    #boot_str.stop_logserver()
    
    return


if __name__ == "__main__":
    """
    To test above classes
    """
    # test_this()
    parser = create_parser()
    args = parser.parse_args()
    print(args)
    
    if args.id != None:
        print(args)
        test_this(build_id = args.id)
    else:
        test_this()

