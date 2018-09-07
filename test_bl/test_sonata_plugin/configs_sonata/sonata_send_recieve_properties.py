import os
import logging

from subprocess import Popen
from test_bl.test_bl_tools import received_data, logging_tools, external_scripts
from test_bl.test_sonata_plugin.structs_sonata import sonata_msg
from test_bl.test_sonata_plugin.test_tools_sonata import sonata_nmea_msgs_content_process

class SonataSendReceiveProperties:

    def __init__(self):
        """
        Connection establishment and in/out data_from fields setup
        """
        '''
        Set env variables for all configs to use.
        TODO: Good idea would be to read variables that are needed for configuration
        to be read from the same .cmd or .bash script that sets
        them to 
        be checked and assigned into config values structure to be used during the course
        of tests execution         
        '''
        #cmd_path_commands = 'C:\\data_from\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\env_setup.cmd',
        #cmd_path = 'C:\\data_from\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\'
        '''
        Locations for the .cmd script setting ENV variables
        '''
        self.cmd_path_commands = 'C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\env_setup.cmd'
        self.cmd_path = 'C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work'

        self.vm_vbox_manage = ''
        self.vm_alt_img = ''
        self.vm_alt_img_snapshot = ''
        self.ssh_remote_commands_conf_start = ''
        self.ssh_remote_commands_conf_stop = ''
        self.logging_tools = None
        self.ssh_host = ''
        self.ssh_port = ''
        self.ssh_user = ''
        self.ssh_pwd = ''
        self.vm_log_srv_exec = ''
        self.vm_log_srv_dir = ''

        '''
        ----------------------------------------------------------------------------------------------------------------
        '''
        '''
        SET ENV VARIABLES
        '''
        self.ext_scripts=external_scripts.ExtScripts(self,
                                                    self.cmd_path_commands,
                                                    self.cmd_path
                                                    )
        self.ext_scripts.load_env_vars()
        '''
        self.set_env_vars(self.curr_cmd_path_commands,
                          self.curr_cmd_path
                          )
        '''
        '''
        ----------------------------------------------------------------------------------------------------------------
        '''
        '''
        SET VARS TO DEFINE LOGGING FACILITIES FOR TEST MODULES
        BASED on ENV VARS
        '''

        self.default_path = 'C:\\data_from\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\test_bl\\test_bl_configs\\logging_conf.json'

        self.env_key_default_level='BL_LOGGING_LEVEL'
        self.env_key_logging_dir = 'BL_LOGGING_DIR'
        self.env_key_log_file = 'BL_LOG_CONF_FNAME'
        self.env_key_log_file_dir = 'BL_LOG_CONF_PATH'
        self.env_key_log_conf_full = 'BL_LOG_CONF_PATH_TOF'

        self.logging_dir = os.getenv(self.env_key_logging_dir, None)
        self.log_file = os.getenv(self.env_key_log_file, None)
        self.log_file_dir = os.getenv(self.env_key_log_file_dir, None)
        self.log_conf_full = os.getenv(self.env_key_log_conf_full, None)
        self.default_level = os.getenv(self.env_key_default_level, None)


        self.logging_tools= logging_tools.LoggingTools(self.default_path,
                                                       self.default_level,
                                                       self.logging_dir,
                                                       self.log_file,
                                                       self.log_file_dir,
                                                       self.log_conf_full
                                                       )
        '''
        ----------------------------------------------------------------------------------------------------------------
        '''
        '''
        SET VARS TO DEFINE for TEST DATA RETRIVAL
        '''
        '''
        ----------------------------------------------------------------------------------------------------------------
        '''
        '''
        VARS TO DEFINE MESSAGES USED BY SENDING TOOLS AGAINST MODULES
        '''

        self.env_key_message_type = 'BL_MESSAGES_TYPE'
        self.env_key_message_src = 'BL_MESSAGES_SRC'
        self.env_key_msgs_dir_json = 'BL_MESSAGES_PATH_JSON'
        self.env_key_msgs_dir_txt = 'BL_MESSAGES_PATH_TXT'


        '''
        SET THE TYPE OF MESSAGES TO BE USED IN
        TESTS        
        '''
        self.messages_type = os.getenv(self.env_key_message_type,
                                       None)
        self.messages_src = os.getenv(self.env_key_message_src,
                                       None)
        self.messages_dir_json = os.getenv(self.env_key_msgs_dir_json,
                                       None)
        self.messages_dir_txt = os.getenv(self.env_key_msgs_dir_txt,
                                           None)

        '''
        Default not used.
        It is here just in case.
        '''
        self.def_mgs_location = "C:\\data_from\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\resources\\messagesUDP.txt"
        '''
        VARS TO DEFINE TEST DATA  
        TODO: Think about it how to do it better
        req:
        1) messages should be test specific 
        2) facility for choosing specific set per test case should exist
        in load test method   
        Why bother? just use what is needed this time...
        '''
        '''
        Data structures for storing
        and
        retrieving test data_from (input/output)
        '''
        '''
        TODO: reset whatever         
        '''
        self.rd = received_data.RecievedData()
        self.data_received = self.rd.get_received_l_all()
        self.data_sent = self.rd.get_sent_m_all()

        '''
        Set the empty storing 
        structures in everything
        '''
        self.content_proc = sonata_nmea_msgs_content_process.SonataNmeaMsgsContentProcessing(self.data_received,
                                                                                             self.data_sent)

        '''
        Actual constructed messages that are out 
        to be sent  in each test case
        '''
        self.msgs_to_send = None

        #self.load_test_messages()

        '''
        Test data_from transmission control fields
        '''
        self.env_key_pause_flag = "SENDER_PAUSE_FLAG"
        self.env_key_quit_flag = "SENDER_STOP_FLAG"
        self.env_key_num_msgs_to_send = "NUM_OF_MSGS"
        self.env_key_delay_btwn_msgs = "DEL_BTWN_MSGS"

        self.pause_flag = os.getenv(self.env_key_pause_flag,
                                    None)
        self.quit_flag = os.getenv(self.env_key_quit_flag,
                                    None)
        self.num_msgs_to_send = int(os.getenv(self.env_key_num_msgs_to_send,
                                            None))
        self.delay_btwn_msgs = int(os.getenv(self.env_key_delay_btwn_msgs,
                                            None))

        '''
        |---------------------------------------------------------------------------------------------------------------        
        '''
        '''
        VARS TO DEFINE Connections PREFERENCES
        for TEST DATA senders and RECEIVERS
        '''
        '''
        SENDING ENV KEYS
        '''
        self.env_key_ip_to = "BL_IP_TO"
        self.env_key_port_to = "BL_PORT_TO"
        self.env_key_protocol_to = "BL_PROT_TO"

        self.ip_to = os.getenv(self.env_key_ip_to,
                                       None)
        self.port_to = int(os.getenv(self.env_key_port_to,
                                       None))
        self.toInfo = ' '.join((self.ip_to, ':', str(self.port_to)))

        '''
        self.env_key_ip_to = "10.11.10.11" #int()
        self.env_key_port_to = 55555 #int()
        self.env_key_toInfo = ' '.join((self.ip_to, ':', str(self.port_to)))
        '''

        '''
        RECEIVEING ENV KEYS
        '''
        self.env_key_ip_on = "BL_IP_ON"
        self.env_key_port_on = "BL_PORT_ON"
        self.env_key_buff_size =  "BL_BUFFSZ_ON"

        self.ip_on = os.getenv(self.env_key_ip_on,
                                       None)
        self.port_on = int(os.getenv(self.env_key_port_on,
                                       None))
        self.buff_size = os.getenv(self.env_key_buff_size,
                                       None)
        self.listen_on = (self.ip_on, self.port_on)

        '''
        self.ip_on = "10.11.10.12"
        self.port_on = 55556  # int()
        self.buff_size = 4096  # int()
        '''
        self.listen_on = (self.ip_on, self.port_on)
        #self.onInfo = ' '.join((self.ip_on, ':', str(self.port_on)))


        '''
        Setup for the test suite and current test which uses this configuration
        also
        used by setting up all that pertains to sending receiving data
        '''
        self.curr_test_suite=None
        self.curr_test = None


    ''' utility functions--------------------------------------------------------------------------------------------------------------'''
    def set_env_vars(self,
                     cmd_path_commands,
                     cmd_path):

        """
        '''="C:\\data_from\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\env_setup.cmd"'''
        '''="C:\\data_from\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\"'''
        Run the cmd file to set env variables

               :param default_level:
               :param env_key:
               :return:
        """

        p = Popen(cmd_path_commands,
                  shell=False,
                  cwd=cmd_path
                  )
        stdout, stderr = p.communicate()
        p.terminate()
        p.kill()

        #return

    def load_test_messages(self):

        """
        self.messages_type,
        self.messages_src,
        self.messages_dir_json

        Here we want to pick messages for the test selectively.
            1) In the simplest case by loading them from the text file as it was done for the case of prototype sending UDP
            2) In more elaborate cases use some utility classes to load data_from from json into proper structure
            for later usage it in the test
        :return:
        """
        '''
        Store messages to be sent out
        '''
        udp_msgs = []

        '''
        Clean up ultimate receiver of 
        actual, properly formatted 
        TEST messages
        '''
        self.msgs_to_send = None

        '''
        Clean up DATA STORAGE used for 
        DATA FIELDS USED to CONSTRUCT 
        actual, properly formatted 
        TEST messages
        in
        ultimate receiver above
        '''
        self.reset_test_messages_to_sent()

        if self.messages_src == "TXT":
            if self.messages_type == "SONATA":
                '''
                TODO:
                Better more flexible mechanism
                for data storage 
                should be used.
                Ideally look up 
                
                FOR NOW
                an assumption is that 
                NEEDED granularity for message
                content control
                is one message
                because messages can be 
                diverse in some cases
                
                So HERE (Sonata) in OTHER cases
                other message types are 
                constructed per 
                individual data for that particular message
                pattern provided from some source                
                '''

                s_msg = sonata_msg.SonataMsg(self)
                s_msg.set_sonata_values_map()
                msg = s_msg.get_msg()

                s_msg_range = [1, 2, 3]


                for i in s_msg_range:
                    try:
                        udp_msgs.append(''.join([msg, '\n\n']))
                    except (OSError, IOError) as e:
                        print(str(e))
                self.msgs_to_send = udp_msgs
                return
            else:
                '''            
                Read stuff from the file directly
                '''
                try:
                     # with open(filename, 'r') as fin:
                    with open(self.message_dir, 'r') as fin:

                        for line in fin:
                                start = line.find('$')
                                msg = (line[start:] if start != -1 else line).strip()
                                '''do not get this messaging yet '''
                                # msg = filter_message(msg, msg_filter)
                                if not msg:
                                    continue
                                udp_msgs.append(''.join([msg, '\n\n']))
                except (OSError, IOError) as e:
                        print(str(e))
                self.msgs_to_send=udp_msgs
                return

        elif self.messages_src == "JSON":
            '''
            Read stuff from the JSON config.
            TODO: the JSON reading part 
            For now 5.06.18
            just get a couple of Sonata messages
            for 
            testing purposes
            '''
            if self.messages_type == "SONATA":
                s_msg=sonata_msg.SonataMsg(self)
                s_msg.set_sonata_values_map()
                msg = s_msg.get_msg()
                s_msg_range=[1,2,3]
                for i in s_msg_range:
                    try:
                        udp_msgs.append(''.join([msg, '\n\n']))
                    except (OSError, IOError) as e:
                        print(str(e))
            self.msgs_to_send = udp_msgs
            return

    def reset_test_messages_to_sent(self):
        """
        TODO:
        When needed a choice for what type of datasrtorage is
        to be reset either list or a dictionary
        :return:
        """
        '''
        RESET STRUCTURE for MESSAGES TO BE SENT
        '''
        self.data_sent.clear()
        self.rd.reset_sent_map()
        self.data_sent = self.rd.get_sent_m_all()
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
        #self.rd.reset_received_l()
        #self.data_received = self.rd.get_received_l_all()
        return


if __name__=="__main__":
    sr=SonataSendReceiveProperties()
    sr.load_test_messages()