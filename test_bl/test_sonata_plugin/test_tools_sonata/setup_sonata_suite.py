import os, socket, random, collections, threading, multiprocessing, queue, logging, pytest, inspect,re
from time import sleep
from copy import deepcopy

from test_bl.test_bl_tools.udp_server import UdpServer, UdpPayloadHandler
from test_bl.test_bl_tools.udp_sender import UdpSender, UdpSenderProcess
from test_bl.test_bl_tools import received_data, read_test_data, var_utils, \
                                  logging_tools, config_test_env, send_receive, \
                                  process_received_data, external_scripts

from  test_bl.test_sonata_plugin.test_tools_sonata import sonata_test_parser
from  test_bl.test_sonata_plugin.structs_sonata import sonata_msg
from  test_bl.test_sonata_plugin.test_tools_sonata import config_sonata_suite

class SetupSonataSuite:
    def __init__(self):
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
        #self.path_to_proj=re.findall(r".*\\test_bl",self.module_abs_path)
        '''-----------------------------------------------------------------------------------------------------------
        GET GENERAL PREFERENCES
        '''
        self.g_prefs = config_test_env.ConfigTestEnv()
        '''
        GET TEST SUITE PREFERENCES
        '''
        self.s_prefs=config_sonata_suite.ConfigSonataSuite()
        self.g_prefs.set_suite_conf(self.s_prefs.get_sonata_configuration())
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
        self.sr = send_receive.SendReceive(q_based=True)
        '''
        UDP SENDER (process based)
        '''
        self.udp_snd_name = self.sr.set_udp_sender(ip_to    =self.g_prefs.get_udp_ip_to(),
                                                    port_to =self.g_prefs.get_udp_port_to())
        '''
        UDP SERVER (thread based)
        '''
        self.udp_srv_name = self.sr.set_udp_server(ip_address   =self.g_prefs.get_udp_ip_from(),
                                                    port        =self.g_prefs.get_udp_port_from())
        self.sr.start_udp_server(self.udp_srv_name)

        '''-----------------------------------------------------------------------------------------------------------
        DATA PROCESSING
        '''
        self.test_type_k_word = "test_type"
        self.test_skip_k_word = "skip"
        '''
        TEST SUITE TEST DATA
        path_to_data is module specific
        '''
        self.path_to_test_data = self.s_prefs.get_path_to_sonata_data(project_path=self.g_prefs.get_proj_dir_path())
        '''
        TEST DATA READER  
        '''
        self.rd = read_test_data.ReadData(data_location=self.path_to_test_data,
                                          test_data_type=read_test_data.test_data_type.json)
        '''
        TARGET MESSAGE STRUCTURE (Sonata)
        '''
        self.sonata_msg_struct = sonata_msg.SonataMsg()
        '''
        GET TEST DATA FOR MANIPULATIONS
        '''
        self._test_suite_test_data = self.rd.get_testsuite_data(self.sonata_msg_struct)
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
        self._s_parser = sonata_test_parser.SonataTestParser()
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
    def send_receive_tdata(self,
                           test_case_ids,
                           udp_sender_id=None,
                           udp_server_id=None,
                           parser=None):
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
                    TODO: think about preloading data into obenveloping object
                    '''
                    messages_to_send = self._get_test_messages(test_case_id)
                    data_sent = self._get_test_data(test_case_id)
                    test_case_type = self.get_test_type(test_case_id)

                    if test_case_type == self.positive_test_kword:
                        '''
                        PASS ARRAY OF TEST MESSAGES TO SENDer`s Q
                        and START sending and receiving for positive cases
                        '''
                        sender_id=""
                        server_id=""
                        if udp_sender_id != None:
                            sender_id = udp_sender_id
                            self.sr.udp_send_to(messages_list   = messages_to_send,
                                                sender_id       = udp_sender_id)
                        else:
                            sender_id = self.udp_snd_name
                            self.sr.udp_send_to(messages_list   = messages_to_send,
                                                sender_id       = sender_id)
                        '''
                        TEST THAT ALL MESSAGES SENT BEING RECEIVED
                        '''
                        if udp_server_id !=None:
                            server_id=udp_server_id
                            self.sr.check_all_messages_received(messages_list    = messages_to_send,
																server_id       = udp_server_id)
                        else:
                            server_id=self.udp_srv_name
                            self.sr.check_all_messages_received(messages_list    = messages_to_send,
																server_id        = server_id)

                        '''get the queue to read from'''
                        '''TODO check sonata is works when we pass buffer further '''
                        received_q = self.sr.get_received_queue(server_id)
                        logging.debug("DATA RECEIVED: ==>" + str(received_q) + "\n")
                        if parser ==None:
                            parsed_data = self.proc_data.parse_received_data(parser=self._s_parser,
                                                                             received_data=received_q)
                            self.test_suite_parsed_data[test_case_id] = deepcopy(parsed_data)
                            self.test_suite_sent_data[test_case_id] = deepcopy(data_sent)
                        else:
                            parsed_data = self.proc_data.parse_received_data(parser=parser,
                                                                             received_data=received_q)
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
                            self.sr.udp_send_to(messages_list=messages_to_send,
                                                sender_id=udp_sender_id)
                        else:
                            sender_id = self.udp_snd_name
                            self.sr.udp_send_to(messages_list=messages_to_send,
                                                sender_id=sender_id)
                        '''
                        TEST for ERROR MESSAGES IN LOG FILES
                        '''
                        '''Lets wait a bit sometimes logs are added too slowly'''
                        sleep(20)
                        parsed_data = self.proc_data.parse_sut_log(parser = self._s_parser,
                                                                   path_to_sut_log = self.g_prefs.get_sut_logging_log_file_dir(),
                                                                   data_sent=data_sent)
                        self.test_suite_parsed_data[test_case_id] = parsed_data


                else:
                    raise Exception("TEST CASE NAME IS UNKNOWN")
            return


    def compare_sent_received_tdata(self,
                                    test_case_ids,
                                    parser=None):
        result = {}
        for test_case_id in test_case_ids:
            if test_case_id in self._test_suite_test_data.keys():
                test_case_type = self.get_test_type(test_case_id)
                if test_case_type == self.positive_test_kword:
                    data_sent = self.test_suite_sent_data[test_case_id]
                    data_received = self.test_suite_parsed_data[test_case_id]
                    if parser == None:
                        result[test_case_id] = self.proc_data.compare_sent_received(parser=self._s_parser,
                                                                                    data_sent=data_sent,
                                                                                    data_received=data_received)
                    else:
                        result[test_case_id] = self.proc_data.compare_sent_received(parser=parser,
                                                                                    data_sent=data_sent,
                                                                                    data_received=data_received)

                        for result in result[test_case_id]:
                            for comparison in result:
                                self.logger.error(comparison + ":==> " + str(result[comparison]))
                                self.logger.error('\n')               

                elif test_case_type == self.negative_test_kword:
                                result = self.test_suite_parsed_data
                                for comparison in result:
                                        self.logger.error(comparison + ":==> " + str(result[comparison]))
                                        self.logger.error('\n')

        self.test_suite_compared_data = deepcopy(result)
        return result
    '''---------------------------------------------------------------------------------------------------------------
    UTILITY FUNCTIONS
    '''
    def get_test_result(self,
                        test_id,
                        msg_n=0,
                        key=None):
        test_data= self.test_suite_compared_data[test_id]
        packet_data = test_data[msg_n]
        result = packet_data[key]
        return result

    def _set_excluded_tests(self):
        result=[]
        for test_id in self._test_suite_test_data.keys():
            test_data =  self._test_suite_test_data[test_id]
            if test_data[self.test_skip_k_word] == True:
                result.append(deepcopy(test_id))
        return result

    def get_test_suite_parsed_data(self):
        return self.test_suite_parsed_data

    def get_test_cases_ids(self):
        return self._test_suite_test_names

    def get_excluded_tests(self):
        return self.tests_to_exclude

    def _config_loggers(self,
                        path_to_logging_conf):
        """
        :param path_to_logging_conf:
        :return:
        """
        '''
        setup all loggers for all modules at once
        '''
        logging_tools.LoggingTools(path_to_json=path_to_logging_conf)

    def _get_test_messages(self,
                           test_id
                           ):
        if test_id in self._test_suite_test_data.keys():
            test_messages = self.rd.get_testcase_messages(test_case_id=test_id)
        return test_messages

    def _get_test_data(self,
                       test_id
                       ):
        if test_id in self._test_suite_test_data.keys():
            test_messages = self.rd.get_testcase_data(test_case_id=test_id)
        return test_messages

    def get_test_type(self,
                      test_id
                      ):
        if test_id in self._test_suite_test_data.keys():
            test_type = self.rd.get_test_type(test_case_id=test_id)
        return test_type



    def stop_udp_sender(self):
        self.sr.stop_sender(self.udp_snd_name)
        return

    def stop_udp_server(self):
        self.sr.stop_udp_server(self.udp_srv_name)
        return

    def start_logserver(self):
        self.ext_scripts.start_log_server()
        return
    def stop_logserver(self):
        self.ext_scripts.stop_logserver()
        return
    def stop_test_env(self,
                      no_VM = None):
        if no_VM ==  None:
            self.ext_scripts.tear_down_test_env()
        else:
            self.ext_scripts.tear_down_test_env(no_VM = True)
    
        return



    def setup_external_scripts(self):
        self.ext_scripts.ssh_target_ip   = self.g_prefs.get_sut_ssh_host()
        self.ext_scripts.ssh_target_port = self.g_prefs.get_sut_ssh_port()
        self.ext_scripts.ssh_target_user = self.g_prefs.get_sut_ssh_user()
        self.ext_scripts.ssh_target_pswd = self.g_prefs.get_sut_ssh_passwd()

        self.ext_scripts.vm_log_srv_exec = self.g_prefs.get_sut_logging_log_srv_exec()
        self.ext_scripts.vm_log_srv_exec_dir = self.g_prefs.get_sut_logging_log_srv_dir()
        self.ext_scripts.vm_log_srv_log_file = self.g_prefs.get_sut_logging_log_file_dir()

        self.ext_scripts.vm_start_cmnd = self.g_prefs.get_local_vbox_mng() + ' startvm ' + self.g_prefs.get_clean_vm_img() + ' --type headless'
        self.ext_scripts.vm_shutdown_cmnd = self.g_prefs.get_local_vbox_mng() + ' controlvm ' + self.g_prefs.get_clean_vm_img()+ ' poweroff'
        self.ext_scripts.vm_resnap_cmnd = self.g_prefs.get_local_vbox_mng() + ' snapshot ' + self.g_prefs.get_clean_vm_img() + ' restore ' + self.g_prefs.get_clean_snap()
        self.ext_scripts.vm_makeclone_cmnd = self.g_prefs.get_local_vbox_mng() + ' clonevm ' + self.g_prefs.get_clean_vm_img()

        self.ext_scripts.ssh_scp_content_location = self.g_prefs.get_sut_config_files_path()
        self.ext_scripts.ssh_target_dir = self.g_prefs.get_sut_ssh_target_dir()

        self.ext_scripts.sut_start_commands = self.s_prefs.get_sonata_start_commands()
        self.ext_scripts.sut_stop_commands = self.s_prefs.get_sonata_stop_commands()
        return

    def setup_vir_env(self,
                      no_VM = None):
        if no_VM == None:
            self.ext_scripts.set_test_env()
        elif no_VM == True:
            self.ext_scripts.set_test_env(no_VM = True)
        else:
            raise Exception("no_VM flag is not Boolean")
            
        return

    def _inspect_atr(self,
                     cls,
                     exclude_methods=True):
        base_attrs = dir(type('dummy', (object,), {}))
        this_cls_attrs = dir(cls)
        res = []
        for attr in this_cls_attrs:
            if base_attrs.count(attr) or (callable(getattr(cls, attr)) and exclude_methods):
                continue
            res += [attr]
        return res

def test_this():
    s_sonata = SetupSonataSuite()
    s_sonata.setup_external_scripts()
    #s_sonata.start_logserver()
    s_sonata.setup_vir_env(no_VM = True)
    t_case_name=["test_sonata_messages01","test_sonata_messages02"]
    s_sonata.send_receive_tdata(test_case_ids=t_case_name)
    s_sonata.compare_sent_received_tdata(test_case_ids=t_case_name)
    s_sonata.stop_udp_server()
    s_sonata.stop_udp_sender()
    s_sonata.stop_test_env(no_VM = True)
    #s_sonata.stop_logserver()

    return

if __name__ == "__main__":
    test_this()