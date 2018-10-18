import os
import logging

from subprocess import Popen
import configparser, platform
import threading, multiprocessing, queue

from test_bl.test_bl_tools import received_data, logging_tools, external_scripts, var_utils, read_test_data
from test_bl.test_sonata_plugin.structs_sonata import sonata_msg
from test_bl.test_sonata_plugin.test_tools_sonata import sonata_nmea_msgs_content_process, send_receive_sonata

class SonataSuiteConfig:

        def __init__(self):
            """
            Connection establishment and in/out data_from fields setup
            """
            '''Lets find ot the system we run on'''
            self.syst = platform.system()
            '''And where we are'''
            self.proj_abs_path = os.path.abspath(os.path.dirname(__file__))

            '''
            Set all configs params to be used in ALL TESTS of THIS SUITE dealing with SONATA messages.
            TODO: Good idea would be to read variables that are needed for configuration
            from the same .cmd or .bash script that sets
            them to 
            be checked and assigned into config values structure to be used during the course
            of tests execution. How to do such dynamic assignment? And where static part of it would be?        
            '''
            self.__utils__=var_utils.Varutils()

            '''
            |---------------------------------------------------------------------------------------------------------------        
            '''
            '''
            SET VARIOUS Config files           
            '''
            '''SET PARAMS for LOCAL VM MANAGEMENT and start of LOG SERVER serving BL remotely'''
            self.vm_logsrv_cnf = configparser.ConfigParser()
            if self.syst == 'Windows':

                self.vm_logsrv_cnf_location = os.path.join(self.proj_abs_path,
                                                           "..\\..\\test_bl_configs\\LocalVM_RemBL_LogSRVconf.ini")
            
                self.vm_logsrv_cnf.read(self.vm_logsrv_cnf_location)
                
            elif self.syst == 'Linux':
                self.vm_logsrv_cnf_location = os.path.join(self.proj_abs_path,
                                                           "../../test_bl_configs/LocalVM_RemBL_LogSRVconf.ini")
          
                self.vm_logsrv_cnf.read(self.vm_logsrv_cnf_location)

            '''SET SONATA`S GENERAL CONFIG'''
            self.sonata_cnf = configparser.ConfigParser()
            if self.syst == 'Windows':
                self.sonata_cnf_location = os.path.join(self.proj_abs_path,"sonata_conf.ini")

                #self.sonata_cnf_location = 'C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\test_bl\\test_sonata_plugin\\configs_sonata\\sonata_conf.ini'
                self.sonata_cnf.read(self.sonata_cnf_location)
            elif self.syst == 'Linux':
                self.sonata_cnf_location = os.path.join(self.proj_abs_path, "sonata_conf.ini")
                #self.sonata_cnf_location = '/home/slon/BL_tests_project/bl_frame_work/test_bl/test_sonata_plugin/configs_sonata/sonata_conf.ini'
                self.sonata_cnf.read(self.sonata_cnf_location)

            '''SET SSH PREFS FOR BL CONFIG AND RESTART HANDLING'''
            self.bl_ssh_cnf = configparser.ConfigParser()
            if self.syst == 'Windows':
                self.bl_ssh_cnf_location = os.path.join(self.proj_abs_path,
                                                           "..\\..\\test_bl_configs\\ssh_bl_conf_files.ini")
                #self.bl_ssh_cnf_location = 'C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\test_bl\\test_bl_configs\\ssh_bl_conf_files.ini'
                self.bl_ssh_cnf.read(self.bl_ssh_cnf_location)
            elif self.syst == 'Linux':
                self.bl_ssh_cnf_location = os.path.join(self.proj_abs_path,
                                                        "../../test_bl_configs/ssh_bl_conf_files.ini")
                #self.bl_ssh_cnf_location = '/home/slon/BL_tests_project/bl_frame_work/test_bl/test_bl_configs/ssh_bl_conf_files.ini'
                self.bl_ssh_cnf.read(self.bl_ssh_cnf_location)

            '''
            |---------------------------------------------------------------------------------------------------------------        
            '''
            '''SET VM and LOG SERVER PREFS'''
            if self.syst == 'Windows':
                self.vm_vbox_manage  = self.vm_logsrv_cnf['LOCAL_VBOX_DIRS']['VBOXMANAGE_DIR']
            elif self.syst == 'Linux':
                self.vm_vbox_manage = self.vm_logsrv_cnf['LOCAL_VBOX_DIRS_LINUX']['VBOXMANAGE_DIR']

            self.vm_alt_img             = self.vm_logsrv_cnf['CLEAN_IMAGES']['CLEAN_ALT']
            self.vm_alt_img_snapshot    = self.vm_logsrv_cnf['CLEAN_IMAGES']['CLEAN_ALT_SNAP']

            if self.syst == 'Windows':
                self.vm_log_srv_exec        = self.vm_logsrv_cnf['LOGGER_SRV']['LOGGER_SRV_EXEC']
                self.vm_log_srv_dir         = self.vm_logsrv_cnf['LOGGER_SRV']['LOGGER_SRV_DIR']
            elif self.syst == 'Linux':
                self.vm_log_srv_exec = self.vm_logsrv_cnf['LOGGER_SRV_LINUX']['LOGGER_SRV_EXEC']
                self.vm_log_srv_dir = self.vm_logsrv_cnf['LOGGER_SRV_LINUX']['LOGGER_SRV_DIR']

            '''SET SSH PREFS COMMON FOR ALL TEST SUITES'''
            self.ssh_host               = self.bl_ssh_cnf['SSH_PREFS']['SSH_HOST']
            self.ssh_port               = self.bl_ssh_cnf['SSH_PREFS']['SSH_PORT']
            self.ssh_user               = self.bl_ssh_cnf['SSH_PREFS']['SSH_USER_NAME']
            self.ssh_pwd                = self.bl_ssh_cnf['SSH_PREFS']['SSH_PASSWD']
            self.ssh_target_dir         = self.bl_ssh_cnf['SSH_PREFS']['SSH_TARGET_DIR']

            '''Here an assumption is made that all configs and all scripts for all modules are in the same archive
            with predetermined directoryes structure'''
            if self.syst == 'Windows':
                self.sut_all_confs  = self.bl_ssh_cnf['BL_CONFIG_FILES']['BL_CONF_FILES_ARCH']
            elif self.syst == 'Linux':
                self.sut_all_confs = self.bl_ssh_cnf['BL_CONFIG_FILES_LINUX']['BL_CONF_FILES_ARCH']

            '''
            |---------------------------------------------------------------------------------------------------------------        
            '''
            '''SET REMOTE ACTIONS SPECIFIC FOR SONATA TESTS'''
            '''First we need to copy configs and bash scripts over over.
               Here an assumption is made that all configs and all '''
            if self.syst == 'Windows':
                self.sut_sonata_confs    = self.sonata_cnf['BL_SONATA_CONFIG_FILES']['SONATA_CONF_FILES_ARCH']
            elif self.syst == 'Linux':
                self.sut_sonata_confs = self.sonata_cnf['BL_SONATA_CONFIG_FILES_LINUX']['SONATA_CONF_FILES_ARCH']

            '''ssh_content_to_copy VAR is known to external scripts that care only about source for files to be copied'''
            self.ssh_content_to_copy = self.sut_sonata_confs

            '''SET BL HANDLING PREFS'''
            '''Second we ought for fill up a map of connamds to be executed remotely'''


            '''These settings handle everything that pertains to BL restart and configuration changes'''

            '''SET COMMANDS to be executed on BL Snapshotrestore/Reboot/FirstStart of Tests'''
            #self.ssh_remote_commands_keys = [key for key in self.sonata_cnf['SUT_CONTROL_COMMANDS_START']]
            self.ssh_remote_commands_keys = self.__utils__.conf_key_to_arr(conf_parser=self.sonata_cnf,
                                                                           section_key='SUT_CONTROL_COMMANDS_START',
                                                                           switch='keys')
            #self.ssh_remote_commands_vals = [value for value in self.sonata_cnf['SUT_CONTROL_COMMANDS_START'].values()]
            self.ssh_remote_commands_vals = self.__utils__.conf_key_to_arr(conf_parser=self.sonata_cnf,
                                                                           section_key='SUT_CONTROL_COMMANDS_START',
                                                                           switch='values')

            '''Final MAP of commands for execution over SSH on tests start'''
            self.ssh_remote_commands_conf_start = self.__utils__.zip_to_map(to_zip01=self.ssh_remote_commands_keys,
                                                                                to_zip02=self.ssh_remote_commands_vals)


            self.ssh_remote_commands_keys = self.__utils__.conf_key_to_arr(conf_parser=self.sonata_cnf,
                                                                           section_key='SUT_CONTROL_COMMANDS_STOP',
                                                                           switch='keys')
            #temp03 = self.sonata_cnf['SUT_CONTROL_COMMANDS_START']
            #self.ssh_remote_commands_vals = [value for value in self.sonata_cnf['SUT_CONTROL_COMMANDS_START'].values()]
            self.ssh_remote_commands_vals = self.__utils__.conf_key_to_arr(conf_parser=self.sonata_cnf,
                                                                           section_key='SUT_CONTROL_COMMANDS_STOP',
                                                                           switch='values')

            '''Final MAP of commands for execution over SSH on tests start'''
            self.ssh_remote_commands_conf_stop = self.__utils__.zip_to_map(to_zip01=self.ssh_remote_commands_keys,
                                                                            to_zip02=self.ssh_remote_commands_vals)



            '''
            self.ssh_remote_keys_vals_combined = zip(self.ssh_remote_commands_keys, self.ssh_remote_commands_vals)

            self.ssh_remote_commands_conf_start = {}
            #Final ARRAY of commands for execution over SSH
            for key, val in self.ssh_remote_keys_vals_combined:
                self.ssh_remote_commands_conf_start[key]=val
            '''
            '''
            |---------------------------------------------------------------------------------------------------------------        
            '''
            '''
            SET PREFS FOR LOGGING FACILITIES OF THE TEST MODULES            
            '''

            if self.syst == 'Windows':
                self.logging_dir = self.sonata_cnf['LOGGING_PREFS']['BL_LOGGING_DIR']
                self.log_file = self.sonata_cnf['LOGGING_PREFS']['BL_LOG_CONF_FNAME']
                self.log_file_dir = self.sonata_cnf['LOGGING_PREFS']['BL_LOG_CONF_PATH']
                self.log_conf_full = self.sonata_cnf['LOGGING_PREFS']['BL_LOG_CONF_PATH_TOF']
                self.default_level =  self.sonata_cnf['LOGGING_PREFS']['BL_LOGGING_LEVEL']
            elif self.syst == 'Linux':
                self.logging_dir = self.sonata_cnf['LOGGING_PREFS_LINUX']['BL_LOGGING_DIR']
                self.log_file = self.sonata_cnf['LOGGING_PREFS_LINUX']['BL_LOG_CONF_FNAME']
                self.log_file_dir = self.sonata_cnf['LOGGING_PREFS_LINUX']['BL_LOG_CONF_PATH']
                self.log_conf_full = self.sonata_cnf['LOGGING_PREFS_LINUX']['BL_LOG_CONF_PATH_TOF']
                self.default_level = self.sonata_cnf['LOGGING_PREFS_LINUX']['BL_LOGGING_LEVEL']

            self.default_path = 'C:\\data_from\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\test_bl\\test_bl_configs\\logging_conf.json'


            self.logging_tools = logging_tools.LoggingTools(self.default_path,
                                                            self.default_level,
                                                            self.logging_dir,
                                                            self.log_file,
                                                            self.log_file_dir,
                                                            self.log_conf_full
                                                            )
            '''
            |---------------------------------------------------------------------------------------------------------------        
            |    SET VARS TO DEFINE for TEST DATA RETRIEVAL and TESTS` NAMES    
            |---------------------------------------------------------------------------------------------------------------
            '''
            '''VARS TO DEFINE MESSAGES USED BY SENDING TOOLS AGAINST MODULES
            '''
            '''SET THE TYPE OF MESSAGES TO BE USED IN
                TESTS        
            '''
            self.messages_type = self.sonata_cnf['TEST_DATA']['BL_MESSAGES_TYPE']
            self.messages_src =  self.sonata_cnf['TEST_DATA']['BL_MESSAGES_SRC']
            if self.syst == 'Windows':
                self.messages_dir_json =  self.sonata_cnf['TEST_DATA']['BL_MESSAGES_PATH_JSON']
            elif self.syst == 'Linux':
                self.messages_dir_json = self.sonata_cnf['TEST_DATA']['BL_MESSAGES_PATH_JSON_LINUX']


            '''IN CASE TEST MESSAGES WILL BE SET WITHOUT INTERMEDIATE FORMAT'''
            self.messages_dir_txt = self.sonata_cnf['TEST_DATA']['BL_MESSAGES_PATH_TXT']

            '''SET TEST NAMES FOR AUTO LOADING OF TEST DATA FOR SPECIFIC TEST'''

            '''Initially test names were doubled in sonata_conf.ini and test data file sonata_test_data.json.
               This seemed illogical. To make situation more straightforward now lets get tests` names from one place
               where they will be searched for anyway at some point in order to form data packets.
               KEEP conf commented for now.  
            '''
            '''
            self.sonata_tests_names = self.__utils__.conf_key_to_arr(conf_parser=self.sonata_cnf,
                                                                           section_key='SONATA_TEST_NAMES',
                                                                           switch='values')
            '''
            read_t_data = read_test_data.ReadData(data_location_map = self.messages_dir_json)
            self.sonata_tests_names = read_t_data.get_test_names()

            '''
            Default not used.
            It is here just in case.
            '''
            self.def_mgs_location = "C:\\data_from\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\resources\\messages.json"

            '''======================================================================================================'''
            '''
            SET params for test data transmission. MOSTLY USELESS NOW.
            '''
            self.pause_flag = bool(self.sonata_cnf['TEST_DATA']['SENDER_PAUSE_FLAG'])
            self.quit_flag = bool(self.sonata_cnf['TEST_DATA']['SENDER_STOP_FLAG'])
            self.num_msgs_to_send = int(self.sonata_cnf['TEST_DATA']['NUM_OF_MSGS'])
            self.delay_btwn_msgs = int(self.sonata_cnf['TEST_DATA']['DEL_BTWN_MSGS'])
            '''======================================================================================================'''
            '''
            SET LOCATION OF THE LOG FOLE FOR ANALYSYS
            '''
            if self.syst == 'Windows':
                self.bl_log_dir = self.sonata_cnf['BL_LOG_FILE']['BL_LOG_FILE_DIR']
            elif self.syst == 'Linux':
                self.bl_log_dir = self.sonata_cnf['BL_LOG_FILE_LINUX']['BL_LOG_FILE_DIR_LINUX']

            '''
            VARS TO DEFINE actual SENDING/RECEIVING 
            and 
            TEST DATA CHOICES PER TEST
            '''
            '''======================================================================================================'''

            '''SET Data structures
                for storing
                and
                retrieving
                test
                data_from(input / output)
            '''
            self.rd = received_data.RecievedData()
            self.data_received = self.rd.get_received_l_all()
            '''
            SET LOCK FOR RECEIVED DATA
            '''
            self.data_received_lock = threading.RLock()
            self.data_sent = self.rd.get_sent_m_all()
            self.data_sent_list = self.rd.get_sent_l_all()
            '''
            |---------------------------------------------------------------------------------------------------------------        
            '''
            ''' Set the empty storing 
                structures in everything
            '''
            self.content_proc = sonata_nmea_msgs_content_process.SonataNmeaMsgsContentProcessing(conf = self,
                                                                                                 data_from = self.data_received,
                                                                                                 data_to = self.data_sent,
                                                                                                 data_to_list = self.data_sent_list
                                                                                                 )
            '''
            |---------------------------------------------------------------------------------------------------------------        
            '''

            ''' Setup for the test suite and current test which uses this configuration
                also
                used by setting up all that pertains to sending receiving data
            '''
            self.curr_test_suite = None
            self.curr_test = None
            ''' Actual constructed messages that are out 
                to be sent  in each test case
            '''
            self.msgs_to_send = None
            '''Initially plain list was used to put messages directly'''
            '''For both sending and receiving'''
            self.messages_use_events = self.sonata_cnf.getboolean('TEST_DATA','USE_EVENTS')
            self.messages_use_queue = self.sonata_cnf.getboolean('TEST_DATA','USE_QUEUE')

            if self.messages_use_events == True and self.messages_use_queue == True:
                    self.q_support = 1
                    self.msg_sent_evnt = threading.Event()
                    self.msg_received_evnt = threading.Event()
                    self.msg_to_send_q = queue.Queue()
                    self.msg_to_receive_q = queue.Queue()
            else:
                self.q_support = 0
                self.msg_sent_evnt = None
                self.msg_received_evnt = None
                self.msg_to_send_q = None
                self.msg_to_receive_q = None

            '''======================================================================================================'''
            '''
            VARS TO DEFINE Connections PREFERENCES
            for TEST DATA SENDERS and RECEIVERS
            '''
            '''SET SENDERS'''
            self.ip_to = self.sonata_cnf['CONNECTION_PREFS']['BL_IP_TO']
            self.port_to = int(self.sonata_cnf['CONNECTION_PREFS']['BL_PORT_TO'])
            self.protocol_to = self.sonata_cnf['CONNECTION_PREFS']['BL_PROT_TO']

            '''SET RECEIVERS'''
            self.ip_on = self.sonata_cnf['CONNECTION_PREFS']['BL_IP_ON']
            self.port_on = int(self.sonata_cnf['CONNECTION_PREFS']['BL_PORT_ON'])
            self.buff_size = self.sonata_cnf['CONNECTION_PREFS']['BL_BUFFSZ_ON']
            '''Combine prefs'''
            self.listen_on = (self.ip_on, self.port_on)
            '''======================================================================================================'''
            '''
            |---------------------------------------------------------------------------------------------------------------        
            '''
            '''SETUP SENDER/RECIVER class doing all the work before TESTS start
            '''
            ''' Actual, properly constructed messages that are out 
                to be sent in each test case are configured on the sender/receiver level
                and passed as iterator to UDP sender
            '''
            self.sender_receiver = send_receive_sonata.SendReceiveSonata(self)
            #self.sender_receiver =  send_receive_sonata_threads.SendReceiveSonataTreaded()

            '''
            |---------------------------------------------------------------------------------------------------------------        
            '''
            '''
            TODO: reset whatever NEEDED to be reset
            '''
            '''
            |---------------------------------------------------------------------------------------------------------------        
            '''

        def config_sonata_test(self):
            return

        def reset_test_messages_received(self):
            """
            TODO:
            When needed a choice for what type of datasrtorage is
            to be reset either list or a dictionarys
            :return:
            """
            '''
            RESET STRUCTURE for MESSAGES TO BE RECEIVED
            '''
            self.data_received.clear()
            # self.rd.reset_received_l()
            # self.data_received = self.rd.get_received_l_all()
            return

        def reset_test_messages_sent(self):
            """
            TODO:
            When needed a choice for what type of datasrtorage is
            to be reset either list or a dictionarys
            :return:
            """
            '''
            RESET STRUCTURE for MESSAGES TO BE RECEIVED
            '''
            self.data_sent_list.clear()
            # self.rd.reset_received_l()
            # self.data_received = self.rd.get_received_l_all()
            return


        def set_sender_and_messages(self):
            self.sender_receiver.load_test_messages()
            self.sender_receiver.set_udp_sender()
            return

        def set_current_test(self,
                             test_name):
            self.curr_test=test_name
            self.sender_receiver.set_curr_test_from_conf()

def test_this():
    sc = SonataSuiteConfig()
    return

if __name__ == '__main__':
        test_this()
