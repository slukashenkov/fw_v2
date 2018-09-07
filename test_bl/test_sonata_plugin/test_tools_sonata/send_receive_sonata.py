import socket, random
import threading, multiprocessing
from time import sleep
from copy import deepcopy
import logging
from mimesis.schema import Field, Schema

from test_bl.test_bl_tools.udp_server import UdpServer, UdpPayloadHandler
from test_bl.test_bl_tools.udp_sender import UdpSender
from test_bl.test_sonata_plugin.configs_sonata import sonata_send_recieve_properties, sonata_suite_config
from test_bl.test_bl_tools import received_data, read_test_data, var_utils
from test_bl.test_sonata_plugin.structs_sonata import sonata_msg
from test_bl.test_sonata_plugin.test_tools_sonata import sonata_json_gen


class SendReceiveSonata():

    """
    18.05.2018
    We want to get all the information about connections.
    IP
    Protocol type
    ports
    from incoming object
    on initialisation
    """
    def __init__(self,
                 conf=None):
        """
        Connection establishment and in/out data_from fields setup.
        Configuration`s details should come from some source
        central for the test suite module
        """
        '''
        Configiration for current set of tests
        TODO: 
        There must be a Choice between conf class using 
        ENV VARS 
        and Json Cong files
        
        '''
        '''
        LETS NOT DO ANYTHING WITHOUT PROPER LOGGER
        '''
        if conf == None:
            raise Exception("Test suite config is not provived. \n CAN NOT LOG ANYTHING HERE!")
        else:
            '''
            SetUp logger and config file
            '''
            self.conf = conf
            self.logger = self.conf.logging_tools.get_logger(__name__)

        '''|--------------------------------------------------------------------------------------------------------|'''

        '''
        Configuration for test messages MNGMNT
        '''

        '''
        Configuring
        Current test id is needed to 
        obtaing its specific data
        '''
        self.curr_test = None
        self.set_curr_test_from_conf()

        '''
        Setup Structures for messages to be sent/and recieved
        keep references in config 
        '''
        self.messages_dir_json=self.conf.messages_dir_json
        self.messages_dir_txt = self.conf.messages_dir_txt
        self.messages_src = self.conf.messages_src
        self.messages_type = self.conf.messages_type

        '''
        Possible message types
        and
        data sources
        '''
        self.messages_src_txt = "TXT"
        self.messages_src_json = "JSON"
        self.messages_type_sonata = "SONATA"

        '''
        Config the ultimate receiver of 
        actual, properly formatted 
        TEST messages
        '''
        self.msgs_to_send = None
        '''
        Data sender UDP or any other type
        should not know anything about details
        all
        it suppose to do is iterate over values and send them out.
        Any concrete details of the test exist only on this level of
        Configuration/execution 
        '''
        self.msg_iterator = None

        '''|--------------------------------------------------------------------------------------------------------|'''
        ''' CONFIG for CLEAN data free from details of messaging format. DO not get why I have set empty arrays here...
            probable because loading of data happens later so we just need a setup here'''
        '''|--------------------------------------------------------------------------------------------------------|'''
        self.rd = received_data.RecievedData()
        self.data_received = self.rd.get_received_l_all()
        self.data_sent = self.rd.get_sent_m_all()

        '''|--------------------------------------------------------------------------------------------------------|'''
        ''' CONFIG HOW to send and receive TEST Messages '''
        '''|--------------------------------------------------------------------------------------------------------|'''
        self.logger.debug("Setting up UDP sender")
        '''
        TODO: setup SOCKET here and not inside sender???
        '''
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        '''---------------------------------------------------------'''
        '''CONFIG QUEUE IMPLEMENTSTION '''
        '''|--------------------------------------------------------------------------------------------------------|'''
        if self.conf.q_support == 1:
            self.q_support = self.conf.q_support
            self.msg_sent_evnt = self.conf.msg_sent_evnt
            self.msg_received_evnt = self.conf.msg_received_evnt
            self.msg_to_send_q = self.conf.msg_to_send_q
            self.msg_to_receive_q = self.conf.msg_to_receive_q
        else:
            self.q_support = None
            self.msg_sent_evnt = None
            self.msg_received_evnt = None
            self.msg_to_send_q = None
            self.msg_to_receive_q = None
        ''' CONFIG UDP messages SENDER '''
        self.udp_sender = None
        self.set_udp_sender()
        self.logger.debug("UDP sender is set up")

        '''|--------------------------------------------------------------------------------------------------------|'''
        ''' CONFIG UDP SERVER '''
        '''|--------------------------------------------------------------------------------------------------------|'''
        self.logger.debug("Setting up UDP server for incoming message from  BL")
        #self.traffic_handler = UdpPayloadHandler()
        '''
        self.udp_server = UdpServer(self.conf.listen_on,
                                    UdpPayloadHandler,
                                    self.conf.data_received,
                                    self.conf.logging_tools,
                                    self.conf)
        '''
        self.set_udp_server()
        '''|--------------------------------------------------------------------------------------------------------|'''

        self.logger.debug("UDP Server is set up")
        '''|--------------------------------------------------------------------------------------------------------|'''

    def set_udp_server(self):
        self.logger.debug("Setting up UDP server for incoming message from  BL")
        # self.traffic_handler = UdpPayloadHandler()
        self.udp_server = UdpServer(server_address  = self.conf.listen_on,
                                    handler_class   =   UdpPayloadHandler,
                                    data_in = self.conf.data_received,
                                    curr_log_tools = self.conf.logging_tools,
                                    conf_in = self.conf,
                                    msg_res_event = self.msg_received_evnt
                                    )

        return

    def set_udp_sender(self):
        self.msg_iterator = None

        if hasattr(self.conf.msgs_to_send, '__iter__'):
            self.msgs_to_send = self.conf.msgs_to_send
            self.msg_iterator = iter(self.conf.msgs_to_send)
        else:
            self.logger.debug("No test messages to iterate over")


        if self.udp_sender != None:
            self.udp_sender.close_socket()

        if self.q_support == 1:
            self.udp_sender = UdpSender(msg_iterator    = self.msg_iterator,
                                        delay           = self.conf.delay_btwn_msgs,
                                        logging_tools   = self.conf.logging_tools,
                                        ip_to           = self.conf.ip_to,
                                        port_to         = self.conf.port_to,
                                        msg_queue       = self.msg_to_send_q,
                                        msg_sent_evnt   = self.msg_sent_evnt,
                                        msg_src_slctr   = self.q_support
                                        )
        else:
            self.udp_sender = UdpSender(msg_iterator=self.msg_iterator,
                                        delay=self.conf.delay_btwn_msgs,
                                        logging_tools=self.conf.logging_tools,
                                        ip_to=self.conf.ip_to,
                                        port_to=self.conf.port_to
                                        )

        return

    def udp_send_to_threaded(self):
    #def udp_send_to(self):
        """
        connect to a listener
        :return:
        """

        '''----------------------------------------------------------------------------------------------------------'''
        '''SEND TEST UDP MESSAGES 
        '''
        '''----------------------------------------------------------------------------------------------------------'''
        '''
        Get current test messages to iterate over         
        '''
        #iterator = iter(self.conf.msgs_to_send)
        self.logger.info('=======================================================================================')
        self.logger.info('Start sending messages to KD')
        self.udp_sender.send_udp()
        self.logger.info('Stop sending messages to KD')
        self.logger.info('=======================================================================================')


    #def udp_send_to_threaded(self):
    def udp_send_to(self):
        """
        connect to a listener
        :return:
        """
        self.msgs_to_send_cntr = 0

        if self.q_support == 1:
            for msg in self.msg_iterator:
                self.msg_to_send_q.put(msg)
                self.msgs_to_send_cntr = self.msgs_to_send_cntr + 1


        '''----------------------------------------------------------------------------------------------------------'''
        '''SEND TEST UDP MESSAGES 
        '''
        '''----------------------------------------------------------------------------------------------------------'''
        '''
        Get current test messages to iterate over         
        '''
        #iterator = iter(self.conf.msgs_to_send)
        self.logger.info('=======================================================================================')
        self.logger.info('Start sending messages to KD')
        self.udp_sender.send_udp()
        self.logger.info('Stop sending messages to KD')
        self.logger.info('=======================================================================================')
        self.test_num_messages()
        sleep(random.randrange(1, 3))


    def udp_server_listen_on(self):
        self.logger.info('Starting up UDP Server to listen traffic from KD')
        self.t = threading.Thread(target=self.udp_server.serve_forever)
        self.t.setDaemon(True)  # don't hang on exit
        self.t.start()
        return self.udp_server

    def udp_server_stop_listen_on(self):
        self.logger.info('Stop UDP Server to listen traffic from KD')
        self.udp_server.stop_server()


    def close_UDP_socket(self):
        self.logger.info('Close socket on which test data_from is sent to KD')
        self.udp_sender.close_socket()



    def reset_test_messages_to_sent(self):
        """
        TODO:
        When needed a choice for what type of datasrtorage is
        to be reset either list or a dictionary
        :return:
        """
        '''
        RESET STRUCTURE 
        for 
        MESSAGES TO BE SENT 
        (DATA ONLY NO Specific formatting)
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
        # self.rd.reset_received_l()
        # self.data_received = self.rd.get_received_l_all()
        return

    def subdict(self,
                keywords,
                fragile=False):
        d = {}
        for k in keywords:
            try:
                d[k] = self.raw_test_data[k]
            except KeyError:
                if fragile:
                    raise
        return d

    def set_curr_test_from_conf(self):
        if self.conf.curr_test == None:
            self.curr_test = None
        else:
            self.curr_test = self.conf.curr_test
        return

    def test_num_messages(self):

        '''----------------------------------------------------------------------------------------------------------'''
        '''SETUP ALL TO CHECK COMPLETENESS OF SENDING/AND RECEIVING'''
        # sent_counter = sum(1 for _ in self.msg_iterator)
        msgs_sent_counter = len(self.msgs_to_send)
        msgs_received_data = self.conf.data_received
        received_counter = 0
        num_of_attemps = 10


        if self.conf.q_support == 1:
            #while msgs_sent_counter != received_counter:
            while self.msg_received_evnt.isSet():
                # Check whether we have received as many packets as sent
                self.logger.debug(
                    '=======================================================================================')
                self.logger.debug('Waiting for RECIEVED counter to be --> '
                                       + str(msgs_sent_counter)
                                       + ' while it is --> '
                                       + str(received_counter)
                                       )
                self.logger.debug(
                    '=======================================================================================')
                #self.conf.data_received_lock.acquire()
                #received_counter = len(msgs_received_data)
                #self.conf.data_received_lock.release()
                #sleep(random.randrange(3, 6))
                received_counter = received_counter + 1
                num_of_attemps = num_of_attemps - 1

                if num_of_attemps == 0:
                    self.logger.debug(
                        '=======================================================================================')
                    self.logger.debug(
                        'UDP SERVER has not RECEIVED ALL THE SENT MESSAGES. ONLY: ' + str(received_counter))
                    self.logger.debug(
                        '=======================================================================================')
                    break
                if received_counter == msgs_sent_counter:
                    self.logger.debug(
                        '=======================================================================================')
                    self.logger.debug(
                        'UDP SERVER RECEIVED ALL THE SENT MESSAGES. TOTAL: ' + str(received_counter))
                    self.logger.debug(
                        '=======================================================================================')
                    break

            received_counter_q = self.msg_to_receive_q.qsize()

            if received_counter_q == received_counter:
                return True
            else:
                return False
        else:
            while msgs_sent_counter != received_counter:
                # Check whether we have received as many packets as sent
                self.logger.debug(
                    '=======================================================================================')
                self.logger.debug('Waiting for RECIEVED counter to be --> '
                                       + str(msgs_sent_counter)
                                       + ' while it is --> '
                                       + str(received_counter)
                                       )
                self.logger.debug(
                    '=======================================================================================')
                self.conf.data_received_lock.acquire()
                received_counter = len(msgs_received_data)
                self.conf.data_received_lock.release()
                sleep(random.randrange(3, 6))
                num_of_attemps = num_of_attemps - 1

                if num_of_attemps == 0:
                    self.logger.debug(
                        '=======================================================================================')
                    self.logger.debug(
                        'UDP SERVER has not RECEIVED ALL THE SENT MESSAGES. ONLY: ' + str(received_counter))
                    self.logger.debug(
                        '=======================================================================================')
                    break

                if received_counter == msgs_sent_counter:
                    self.logger.debug(
                        '=======================================================================================')
                    self.logger.debug(
                        'UDP SERVER RECEIVED ALL THE SENT MESSAGES. ONLY: ' + str(received_counter))
                    self.logger.debug(
                        '=======================================================================================')
                break


def test_this():
    """
    send_receive class basic usage
    """

    '''Initial config'''
    # conf = sonata_send_recieve_properties.SonataSendReceiveProperties()
    '''INI based config'''
    conf = sonata_suite_config.SonataSuiteConfig()
    conf.curr_test = "test_sonata_messages01"
    # conf.set_current_test("test_sonata_messages01")
    # conf.set_current_test("test_sonata_messages02")
    sr = SendReceiveSonata(conf)
    sr = conf.sender_receiver
    # conf.curr_test_id = "test_sonata_messages01"
    conf.set_current_test("test_sonata_messages02")
    sr.load_test_messages()
    sr.set_udp_sender()
    # sr.curr_logger('Debug module send_receive_sonata ')
    curr_udp_srv = sr.udp_server_listen_on()
    '''
    Start UDP server listening for messages from KD
    '''
    logger = logging.getLogger('client')
    # logger.info('Server on %s:%s', self.c onf.)
    sr.udp_send_to()
    # sr.udp_send_to_threaded()
    sr.udp_server_stop_listen_on()
    sr.close_UDP_socket()


    logger = logging.getLogger('client')
    #logger.debug('Current status of UDP server is: ' + sr.udp_server.isAlive())
    return

def test_json_generator():

    from mimesis.schema import Field, Schema
    from test_bl.test_bl_tools.read_test_data import ReadData
    import time
    from test_bl.test_sonata_plugin.test_tools_sonata import send_receive_sonata, sonata_nmea_msgs_content_process

    test_case_name = "testSonata"
    test_case_msg_id = "msgSonata"

    s_json_gen = sonata_json_gen.SonataJsonDataGen(test_case_name=test_case_name,
                                                   test_case_msg_id=test_case_msg_id,
                                                   num_of_msgs = 20)


    conf = sonata_suite_config.SonataSuiteConfig()
    conf.curr_test = "testSonata_01"
    sr = conf.sender_receiver

    # conf.curr_test_id = "test_sonata_messages01"
    conf.set_current_test("test_sonata_messages01")
    sr.messages_dir_json = s_json_gen.gen_file_dir
    sr.load_test_messages()
    sr.set_udp_sender()
    curr_udp_srv = sr.udp_server_listen_on()

    logger = logging.getLogger('client')
    # logger.info('Server on %s:%s', self.c onf.)
    sr.udp_send_to()
    # sr.udp_send_to_threaded()

    '''Lets check what is uP'''
    time.sleep(random.randrange(3, 15))

    snmea = conf.content_proc
    total_messages = conf.data_received.__len__()

    indx = 0
    while indx < total_messages:
        snmea.packet_indx = indx
        snmea.parse_nmea()
        snmea.nmea_parser.data_to = snmea.data_to_list[indx]

        #snmea.key_sent = 'sonata_id=\"sonata_id\"'
        #snmea.compare_fields()

        res_sonata_id= snmea.nmea_parser.compare_fields(
            sonata_id="sonata_id"
        )

        res_lat = snmea.nmea_parser.compare_fields(
            lat="lat"
        )

        res_lon = snmea.nmea_parser.compare_fields(
            lon="lon"
        )

        res_vel = snmea.nmea_parser.compare_fields(
            vel="vel"
        )
        res_course = snmea.nmea_parser.compare_fields(
            course = "course"
        )

        res_vel_knots = snmea.nmea_parser.compare_fields(
            vel_knots = "vel_knots"
        )
        indx = indx + 1

    sr.udp_server_stop_listen_on()
    sr.close_UDP_socket()


    logger = logging.getLogger('client')

def test_content_processing_positive():
    import time
    from test_bl.test_sonata_plugin.test_tools_sonata import send_receive_sonata, sonata_nmea_msgs_content_process
    """
    send recieve class usage
    """

    '''Initial config'''
    # conf = sonata_send_recieve_properties.SonataSendReceiveProperties()
    '''INI based config'''
    conf = sonata_suite_config.SonataSuiteConfig()
    '''this needed to properly initialise sender i this test'''
    conf.curr_test = "test_sonata_messages01"
    # conf.set_current_test("test_sonata_messages01")
    # conf.set_current_test("test_sonata_messages02")
    sr = SendReceiveSonata(conf)
    sr = conf.sender_receiver
    # conf.curr_test_id = "test_sonata_messages01"
    # conf.set_current_test("test_sonata_messages05")
    conf.set_current_test("test_sonata_messages05")
    sr.load_test_messages()
    sr.set_udp_sender()
    # sr.curr_logger('Debug module send_receive_sonata ')
    curr_udp_srv = sr.udp_server_listen_on()

    '''
    Start UDP server listening for messages from KD
    '''
    logger = logging.getLogger('client')
    # logger.info('Server on %s:%s', self.c onf.)
    sr.udp_send_to()

    time. sleep(random.randrange(3, 6))


    '''positive case'''
    #snmea = sonata_nmea_msgs_content_process.SonataNmeaMsgsContentProcessing(conf,conf.data_received,conf.data_sent)

    snmea = conf.content_proc
    snmea.parse_nmea_auto()

    results=snmea.compare_fields_auto()


    sr.udp_server_stop_listen_on()
    sr.close_UDP_socket()


    logger = logging.getLogger('client')
    #logger.debug('Current status of UDP server is: ' + sr.udp_server.isAlive())
    return

def test_content_processing_negative():
    import time
    from test_bl.test_sonata_plugin.test_tools_sonata import send_receive_sonata, sonata_nmea_msgs_content_process
    """
    send recieve class usage
    """

    '''Initial config'''
    # conf = sonata_send_recieve_properties.SonataSendReceiveProperties()
    '''INI based config'''
    conf = sonata_suite_config.SonataSuiteConfig()
    '''this needed to properly initialise sender i this test'''
    conf.curr_test = "test_sonata_messages01"
    # conf.set_current_test("test_sonata_messages01")
    # conf.set_current_test("test_sonata_messages02")
    sr = SendReceiveSonata(conf)
    sr = conf.sender_receiver
    # conf.curr_test_id = "test_sonata_messages01"
    # conf.set_current_test("test_sonata_messages05")
    conf.set_current_test("test_sonata_messages02")
    sr.load_test_messages()
    sr.set_udp_sender()
    # sr.curr_logger('Debug module send_receive_sonata ')
    curr_udp_srv = sr.udp_server_listen_on()

    '''
    Start UDP server listening for messages from KD
    '''
    logger = logging.getLogger('client')
    # logger.info('Server on %s:%s', self.c onf.)
    sr.udp_send_to()

    time. sleep(random.randrange(3, 6))


    '''negative case'''

    snmea = conf.content_proc
    total_messages = conf.data_received.__len__()
    res_log_scan = snmea.nmea_parser.parse_log_auto()

    sr.udp_server_stop_listen_on()
    sr.close_UDP_socket()


    logger = logging.getLogger('client')
    #logger.debug('Current status of UDP server is: ' + sr.udp_server.isAlive())
    return


def test_content_processing_ind_values():
        from mimesis.schema import Field, Schema
        from test_bl.test_bl_tools.read_test_data import ReadData
        import time
        from test_bl.test_sonata_plugin.test_tools_sonata import send_receive_sonata, sonata_nmea_msgs_content_process

        conf = sonata_suite_config.SonataSuiteConfig()
        conf.curr_test = "test_sonata_messages01"
        sr = conf.sender_receiver
        # conf.curr_test_id = "test_sonata_messages01"
        conf.set_current_test("test_sonata_messages01")

        sr.load_test_messages()
        sr.set_udp_sender()
        curr_udp_srv = sr.udp_server_listen_on()

        logger = logging.getLogger('client')
        # logger.info('Server on %s:%s', self.c onf.)
        sr.udp_send_to()
        # sr.udp_send_to_threaded()

        '''Lets check what is uP'''
        time.sleep(random.randrange(3, 15))

        snmea = conf.content_proc
        total_messages = conf.data_received.__len__()

        indx = 0

        snmea.packet_indx = indx
        snmea.parse_nmea()
        snmea.nmea_parser.data_to = snmea.data_to_list[indx]

        # snmea.key_sent = 'sonata_id=\"sonata_id\"'
        # snmea.compare_fields()

        res_sonata_id = snmea.nmea_parser.compare_fields(
            sonata_id="sonata_id"
        )

        res_lat = snmea.nmea_parser.compare_fields(
            lat="lat"
        )

        res_lon = snmea.nmea_parser.compare_fields(
            lon="lon"
        )

        res_vel = snmea.nmea_parser.compare_fields(
            vel="vel"
        )
        res_course = snmea.nmea_parser.compare_fields(
            course="course"
        )

        res_vel_knots = snmea.nmea_parser.compare_fields(
            vel_knots="vel_knots"
        )


        sr.udp_server_stop_listen_on()
        sr.close_UDP_socket()


if __name__ == "__main__":
    # test_this()
    # test_json_generator()
    # test_content_processing_ind_values()
     test_content_processing_positive()
    #  test_content_processing_negative()
    # test_wrong_messages()


