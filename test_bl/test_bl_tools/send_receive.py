import socket, random, collections, threading, multiprocessing, queue, logging, pytest,re
from time import sleep
from copy import deepcopy

from test_bl.test_bl_tools.udp_server import UdpServer, UdpPayloadHandler
from test_bl.test_bl_tools.udp_sender import UdpSender, UdpSenderProcess
from test_bl.test_bl_tools import received_data, read_test_data, var_utils, logging_tools

class SendReceive:
    """
    16.08.2018
    This is a testing support class.
    It should be a centralised place
    where test designer can
    establish control over sending/receiving test data over network
    needed for testing facilities in generalised way.
    The idea is to provide plain interface
    for receiving/sending data
    """
    def __init__(self,
                 q_based            = None,
                 conf               = None):
        """
        :param logging_tools: logging to centalise coniguration (can change)
        :param q_based:  True-all excanges with UDP sender or server happen over queue; False - list is used directly from udp_send_to
        :param conf: if there will be a support for config file rather than one by on eparam passing
        """

        '''
        LETS NOT DO ANYTHING WITHOUT PROPER LOGGER
        '''
        self.logger = logging.getLogger(__name__)


        if conf == None:
            '''--------------------------------------------------------------------------------------------------------|        
            Configuration for test messages MNGMNT
            '''
            self.msgs_to_send       = None
            self.msg_sent_status    = None
            self.msgs_to_get        = None
            self.event_msg_send     = None
            if q_based != None:
                self.q_based = q_based
            else:
                raise Exception("param q_based must be provided")
        else:
            '''
            Get params from config file
            '''
            self.conf = conf
            self.logger = self.conf.logging_tools.get_logger(__name__)
        '''--------------------------------------------------------------------------------------------------------        
        Configuration for utility stuctures
        '''
        ''' Lets assume internal struct to deal with sending
            before data gets into queue for the simple way 
            for doing things
        '''
        '''
        UDP sender
        '''
        self.msgs_to_send  = []
        self.msg_iterator  = None
        '''
        Store reference to all used UDP senders
           so they can be reffered by name in case 
           different message types have to be sent by a
           different sender
        '''
        self.udp_senders_cnt        = 1
        self.udp_sender_name        = "udp-sender_"
        self.udp_sender_name_def    = "udp-sender_1"
        self.udp_senders            = {}

        '''UDP server'''
        self.udp_servers_cnt        = 1
        self.udp_server_name        = "udp-server_"
        self.udp_server_name_def    = "udp-server_1"
        self.udp_servers            = {}
        self.udp_servers_treads     = {}
        self.event_msg_received     = None
        self.received_data          = {}
        self.received_data_cntr     = 0

        '''List of received messages'''
        self.messages_received = []

    '''
    UDP SENDER        
    '''
    def set_udp_sender(self,
                       ip_to                ="10.11.10.12",
                       port_to              ="55555"
                       ):
        """
        :param ip_to:   address where traffic supposed to be sent
        :param port_to: port where traffic supposed to be sent
        :return: (string) id of the created sender; should be used to send messages stop senders
        """
        if self.q_based == True:
            event_msg_send        = multiprocessing.Event()
            msgs_queue            = multiprocessing.Queue()
            msg_sent_status_queue = multiprocessing.Queue()
            self.udp_sender=UdpSenderProcess(ip_to=ip_to,
                                             port_to=port_to,
                                             event_msg_send=event_msg_send,
                                             msgs_queue=msgs_queue,
                                             msg_sent_status_queue=msg_sent_status_queue
                                            )
            #multiprocessing.log_to_stderr(logging.DEBUG)
            self.udp_sender.name = self.udp_sender_name+str(self.udp_senders_cnt)
            self.udp_senders_cnt = self.udp_senders_cnt + 1
            self.udp_senders[self.udp_sender.name] = self.udp_sender
            self.udp_sender.daemon=True
            self.udp_sender.start()
            return self.udp_sender.name

        else:
            self.msg_iterator = None

            if hasattr(self.msgs_to_send, '__iter__'):
                self.msg_iterator = iter(self.msgs_to_send)
            else:
                self.logger.debug("No test messages to iterate over")


            if self.udp_sender != None:
                self.udp_sender.close_socket()

            if self.q_support == 1:
                self.udp_sender = UdpSender(msg_iterator    = self.msg_iterator,
                                            logging_tools   = self.lt,
                                            ip_to           = self.ip_to,
                                            port_to         = self.port_to,
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
            return self.udp_sender.name

    def udp_send_to(self,
                    messages_list = None,
                    sender_id = None):
        if self.q_based == True:

            '''SEND TEST UDP MESSAGES (using sender in a separate process)'''

            if sender_id == None:
                if self.udp_sender_name_def in self.udp_senders.keys():
                    curr_sender = self.udp_senders[self.udp_sender_name_def]
            else:
                curr_sender = self.udp_senders[sender_id]

            self.msgs_to_send       = curr_sender.msgs_queue
            self.msg_sent_status    = curr_sender.msg_sent_status_queue
            self.event_msg_send     = curr_sender.event_msg_send

            num_msgs = len(messages_list)
            conf_res_cnt = 0
            if num_msgs > 0:
                for msg in messages_list:
                    self.msgs_to_send.put(msg)
                    #self.logger.debug("put message: " + str(msg) + "to queue \n")
                self.event_msg_send.set()

                while True:
                    if self.msg_sent_status.get() == "done" and self.msgs_to_send.qsize() != 0:
                        if conf_res_cnt <= num_msgs:
                            self.event_msg_send.set()
                            conf_res_cnt = conf_res_cnt + 1
                            self.logger.debug("UDP sender waited " + str(conf_res_cnt) + " times \n")
                    else:
                         break
            else:
                raise Exception("List of test values is empty")

        else:
            '''------------------------------------------------------------------------------------------------------'''
            '''SEND TEST UDP MESSAGES (initial implementation)
            '''
            '''
            Get current test messages to iterate over         
            '''
            iterator = iter(messages_list)
            self.logger.info('=======================================================================================')
            self.logger.info('Start sending messages to KD')
            self.udp_sender.send_udp()
            self.logger.info('Stop sending messages to KD')
            self.logger.info('=======================================================================================')
            self.test_num_messages()
            sleep(random.randrange(1, 3))

    def udp_send_to_one(self,
                        messages_list = None,
                        sender_id = None):
        result = None
        if self.q_based == True:
            '''------------------------------------------------------------------------------------------------------'''
            '''SEND TEST UDP MESSAGES (using sender in a separate process)
            '''
            if sender_id == None:
                if self.udp_sender_name_def in self.udp_senders.keys():
                    curr_sender = self.udp_senders[self.udp_sender_name_def]
                else:
                    raise Exception("No UDP senders configured")
            else:
                curr_sender = self.udp_senders[sender_id]

            self.msgs_to_send       = curr_sender.msgs_queue
            self.msg_sent_status    = curr_sender.msg_sent_status_queue
            self.event_msg_send     = curr_sender.event_msg_send

            if messages_list == None and self.msgs_to_send.qsize() != 0:
                self.event_msg_send.set()
                conf_res_cnt = 1
                while True:
                    if self.msg_sent_status.get() == "done" and self.msgs_to_send.qsize() != 0:
                        break
                    else:
                        pass


                if self.msgs_to_send.qsize():
                    result = True
                else:
                    result = False
                return result
            elif len(messages_list) > 0:
                for msg in messages_list:
                    self.msgs_to_send.put(msg)
                    # self.logger.debug("put message: " + str(msg) + "to queue \n")
                return
            else:
                raise Exception("Either queue is empty or data list")
        else:
            '''------------------------------------------------------------------------------------------------------'''
            '''SEND TEST UDP MESSAGES (initial implementation)
            '''
            '''
            Get current test messages to iterate over         
            '''
            iterator = iter(messages_list)
            self.logger.info('=======================================================================================')
            self.logger.info('Start sending messages to KD')
            self.udp_sender.send_udp()
            self.logger.info('Stop sending messages to KD')
            self.logger.info('=======================================================================================')
            self.test_num_messages()
            sleep(random.randrange(1, 3))
            return True

    def stop_sender(self,
                    sender_id=None):
        curr_sender = self.udp_senders[sender_id]
        curr_sender.terminate()

        while True:
            status = curr_sender.is_alive()
            if status == False:
                del self.udp_senders[sender_id]
                break
        return
    '''
    |-------------------------------------------------------------------------------------------------------------------
    UDP SERVER       
    '''
    def set_udp_server(self,
                       ip_address="127.0.0.1",
                       port     = 55556
                        ):

        server_address = (ip_address, port)
        data_in_queue = queue.Queue(maxsize=0)
        status_queue = queue.Queue(maxsize=0)
        self.event_msg_received = threading.Event()

        self.logger.debug("Setting up UDP server")
        udp_server = UdpServer(server_address           = server_address,
                                    handler_class       = UdpPayloadHandler,
                                    data_in_queue       = data_in_queue,
                                    status_queue        = status_queue,
                                    msg_res_event       = self.event_msg_received
                                    )

        curr_udp_server_name = self.udp_server_name + str(self.udp_servers_cnt)
        self.udp_servers_cnt = self.udp_servers_cnt + 1
        udp_server.name      = curr_udp_server_name
        self.udp_servers[curr_udp_server_name] = udp_server
        #self.start_udp_server(curr_udp_server_name)
        return curr_udp_server_name

    def start_udp_server(self,
                         srv_id):

        if srv_id in self.udp_servers.keys():
            self.logger.info('Starting up UDP Server to listen traffic from KD')
            curr_udp_srv = self.udp_servers.get(srv_id)
            t = threading.Thread(target=curr_udp_srv.serve_forever)
            self.udp_servers_treads[srv_id]=t
            t.setDaemon(True)  # don't hang on exit
            t.start()
        else:
            raise Exception("UDP server is not KNOWN, check its ID")



    def stop_udp_server(self,
                        server_id = None
                        ):
        if server_id == None:
            server_id = self.udp_server_name_def
        else:
            server_id=server_id

        if server_id in self.udp_servers.keys():
            udp_server = self.udp_servers.get(server_id)
            self.logger.info('Stop UDP Server to listen traffic from KD')
            udp_server.stop_server()

    def test_messages_received(self,
                              messages_list=None,
                              server_id = None
                               ):
        '''----------------------------------------------------------------------------------------------------------'''
        '''SETUP ALL TO CHECK COMPLETENESS OF SENDING/AND RECEIVING'''
        if messages_list != None:
            msgs_sent_counter = len(messages_list)
            received_counter = 0
            num_of_attemps = 10
        else:
            raise Exception("No messages to compare against")

        if server_id in self.udp_servers.keys():
            curr_receive_q =  self.udp_servers[server_id].data_in_queue
            curr_status_q =  self.udp_servers[server_id].status_queue
        else:
            raise Exception("No such UDP server")

        if self.q_based == 1:
            #while msgs_sent_counter != received_counter:
            #while self.event_msg_received.isSet():
            while 1:
                # Check whether we have received as many packets as sent
                if not curr_status_q.empty():
                    received_message = curr_status_q.get()
                    if received_message == "received":
                        received_counter = received_counter + 1
                if num_of_attemps == 0:
                    self.logger.debug(
                        '=======================================================================================')
                    self.logger.debug(
                        'UDP SERVER EXCEEDED NUM OF ATTEMPTS TO RECONCILE ITS COUNTERS')
                    self.logger.debug(
                        '=======================================================================================')
                    break
                if received_counter == msgs_sent_counter:
                    received_counter_q = curr_receive_q.qsize()
                    if received_counter_q == received_counter:
                        self.received_data_cntr = received_counter
                        self.logger.debug(
                            '=======================================================================================')
                        self.logger.debug(
                            'UDP SERVER RECEIVED ALL THE SENT MESSAGES. TOTAL: ' + str(received_counter) + " <-- received_counter_mgs" + " " +str(received_counter_q) + " <-- received_counter_q")
                        self.logger.debug(
                            '=======================================================================================')
                        break
                    num_of_attemps = num_of_attemps - 1
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
                received_counter = len(messages_list)
                self.conf.data_received_lock.release()
                #sleep(random.randrange(3, 6))
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

    def test_messages_received_filter(self,
                                       messages_list=None,
                                       server_id=None,
                                       flt_regex=None
                                       ):
        '''----------------------------------------------------------------------------------------------------------'''
        '''SETUP ALL TO CHECK COMPLETENESS OF SENDING/AND RECEIVING'''
        if messages_list != None:
            msgs_sent_counter = len(messages_list)
            received_counter = 0
            num_of_attemps = 5
            search_packet=[re.compile(regex) for regex in flt_regex ]
            matched_packet = None
        else:
            raise Exception("No messages to compare against")

        if server_id in self.udp_servers.keys():
            curr_receive_q = self.udp_servers[server_id].data_in_queue
            curr_status_q = self.udp_servers[server_id].status_queue
        else:
            raise Exception("No such UDP server")

        if self.q_based == 1:
            # while msgs_sent_counter != received_counter:
            # while self.event_msg_received.isSet():
            while 1:
                # Check whether we have received particular messages as a reply to the msg sent
                if not curr_receive_q.empty():
                    while not curr_receive_q.empty():
                        msg_res_bin = curr_receive_q.get()
                        msg_str = str(msg_res_bin)
                        ptrn = search_packet[0]
                        match = ptrn.match(msg_str)

                        #matched_packets = [i.match(msg_str) for i in search_packet]

                        #if len(matched_packets) == msgs_sent_counter:
                        if match:
                           # for msg in matched_packets:
                            self.messages_received.append(msg_str)
                            break

                        received_counter = received_counter + 1
                        num_of_attemps = num_of_attemps - 1

                        if received_counter == msgs_sent_counter:
                                        self.logger.debug(
                                            '=======================================================================================')
                                        self.logger.debug(
                                            'UDP SERVER RECEIVED ALL THE SENT MESSAGES. TOTAL: ' + str(
                                                received_counter) + " <-- received_counter_mgs")
                                        self.logger.debug(
                                            '=======================================================================================')
                                        break
                        if num_of_attemps == 0:
                                    self.logger.debug(
                                        '=======================================================================================')
                                    self.logger.debug(
                                        'UDP SERVER EXCEEDED NUM OF ATTEMPTS TO RECONCILE ITS COUNTERS')
                                    self.logger.debug(
                                        '=======================================================================================')
                                    break


    def test_num_messages(self,
                          messages_list=None):
        '''----------------------------------------------------------------------------------------------------------'''
        '''SETUP ALL TO CHECK COMPLETENESS OF SENDING/AND RECEIVING'''
        # sent_counter = sum(1 for _ in self.msg_iterator)
        msgs_sent_counter = len(messages_list)
        msgs_received_data = self.conf.data_received
        received_counter = 0
        num_of_attemps = 10

        if self.conf.q_support == 1:
            #while msgs_sent_counter != received_counter:
            while self.event_msg_received.isSet():
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

    def get_received_queue(self,
                            server_id = None
                           ):
        """
        :param server_id: id of the server which queue has to be processed
        :return: list of received payloads
        """
        received_data=[]
        if server_id in self.udp_servers.keys():
            while not self.udp_servers[server_id].data_in_queue.empty():
                received_data.append(self.udp_servers[server_id].data_in_queue.get())

            self.received_data[server_id] = deepcopy(received_data)
            return received_data

        elif server_id == None:
            raise Exception("UDP server`s ID is not provided")
        else:
            raise Exception("No such UDP server")


def test_this():
    import multiprocessing, collections
    from test_bl.test_bl_tools import received_data, read_test_data, var_utils, logging_tools
    """
    send_receive class basic usage
    """
    lt = logging_tools.LoggingTools(
        default_path="C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_git_branching\\test_bl\\test_bl_configs\\logging_conf.json"
        )
    logger = lt.get_logger(__name__)
    sr = SendReceive(logging_tools=lt,
                     q_based=True
                     )

    udp_snd_01_name = sr.set_udp_sender(ip_to="10.11.10.12",
                                        port_to="55556")
    udp_srv_name = sr.set_udp_server(ip_address="10.11.10.12",
                                     port=55556)



    messages = ["msg01 \n", "msg02 \n", "msg03 \n", "msg04 \n", "msg05 \n", "msg06 \n", "msg07  \n", "msg08 \n"]
    sr.udp_send_to(messages_list=messages,
                    sender_id=udp_snd_01_name)
    sr.test_messages_received(messages_list=messages,
                              server_id=udp_srv_name)

    received_q = sr.get_received_queue(udp_srv_name)
    logger.debug("--->>>num of messages in received Q == " + str(received_q.qsize()))
    result = []
    while not received_q.empty():

        result.append(received_q.get())
    logging.debug("==>>>" + str(result))
    result.clear()

    messages_file = get_test_messages()
    sr.udp_send_to(messages_list=messages_file,
                   sender_id=udp_snd_01_name)
    sr.test_messages_received(messages_list=messages_file,
                              server_id=udp_srv_name)
    while not received_q.empty():

        result.append(received_q.get())
    logging.debug("==>>>" + str(result))
    result.clear()

    ''''''
    messages = ["msg01 \n", "msg02 \n", "msg03 \n", "msg04 \n", "msg05 \n", "msg06 \n"]
    '''Put messages in ONLY'''
    sr.udp_send_to_one(messages_list=messages,
                      sender_id=udp_snd_01_name)
    '''Send one ONLY'''
    sr.udp_send_to_one(sender_id=udp_snd_01_name)

    sr.test_messages_received( messages_list=["msg01 \n"],
                              server_id = udp_srv_name)

    sr.udp_send_to_one(sender_id=udp_snd_01_name)
    sr.test_messages_received(messages_list=["msg02 \n"],
                              server_id=udp_srv_name)

    sr.udp_send_to_one(sender_id=udp_snd_01_name)
    sr.test_messages_received(messages_list=["msg03 \n"],
                              server_id=udp_srv_name)

    sr.udp_send_to_one(sender_id=udp_snd_01_name)
    sr.test_messages_received(messages_list=["msg04 \n"],
                              server_id=udp_srv_name)


    sr.udp_send_to(messages_list=messages,
                    sender_id=udp_snd_01_name)
    sr.test_messages_received(messages_list=messages,
                              server_id=udp_srv_name)

    return

def test_this_sender():
    import multiprocessing, collections
    from test_bl.test_bl_tools import received_data, read_test_data, var_utils, logging_tools
    """
    send_receive class basic usage
    """
    lt = logging_tools.LoggingTools(default_path="C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\FW_28_08_2018\\test_bl\\test_bl_configs\\logging_conf.json"
                                    )
    logger = lt.get_logger(__name__)
    sr=SendReceive(logging_tools    = lt,
                   q_based          = True
                    )

    messages = ["msg01 \n", "msg02 \n", "msg03 \n","msg04 \n", "msg05 \n", "msg06 \n"]
    udp_snd_01_name = sr.set_udp_sender(ip_to="10.11.10.12",
                                       port_to="55555"
                                       )
    sr.udp_send_to(messages_list=messages,
                   sender_id=udp_snd_01_name)


    udp_snd_02_name = sr.set_udp_sender(ip_to="10.11.10.12",
                                       port_to="55556"
                                       )
    sr.udp_send_to(messages_list=messages,
                   sender_id=udp_snd_02_name)

    sr.stop_sender(udp_snd_01_name)

    udp_snd_03_name = sr.set_udp_sender(ip_to="10.11.10.12",
                                       port_to="55557"
                                       )
    sr.udp_send_to(messages_list=messages,
                   sender_id=udp_snd_03_name)

    return

def test_this_server():
    import multiprocessing, collections
    from test_bl.test_bl_tools import received_data, read_test_data, var_utils, logging_tools
    """
    send_receive class basic usage
    """
    lt = logging_tools.LoggingTools(default_path="C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\FW_28_08_2018\\test_bl\\test_bl_configs\\logging_conf.json"
                                    )
    logger = lt.get_logger(__name__)
    sr=SendReceive(logging_tools    = lt,
                   q_based          = True
                    )
    sr.set_udp_server(ip_address="10.11.10.12",
                      port=55556)
    sr.stop_udp_server()
    return

'''
UTILITY FUNCTIONS-------------------------------------------------------------------------------------------------------
'''
def config_loggers():
    import  os
    '''here we are'''
    module_abs_path = os.path.abspath(os.path.dirname(__file__))
    '''config logging'''
    path_to_logging_conf = "..\\test_bl_configs\\logging_conf.json"
    path_to_logging_conf = os.path.join(module_abs_path, path_to_logging_conf)
    '''setup all loggers for all modules at once'''
    logging_tools.LoggingTools(path_to_json=path_to_logging_conf)

def get_test_messages(test_case_id):
    import os
    from test_bl.test_sonata_plugin.structs_sonata import sonata_msg
    from test_bl.test_bl_tools import logging_tools, read_test_data
    """
    BASIC TEST BASIC CONFIG
    """
    logger = logging.getLogger(__name__)
    '''here we are'''
    module_abs_path = os.path.abspath(os.path.dirname(__file__))

    '''
    Read test data from json    '''

    #path_to_data = "..\\test_sonata_plugin\\resources_sonata\\sonata_test_data.json"
    #path_to_data = "..\\test_sonata_plugin\\resources_sonata\\sonata_test_data_gen.json"
    #path_to_data = "..\\test_sonata_plugin\\resources_sonata\\failig_test_data.json"
    #path_to_data = "..\\test_sonata_plugin\\resources_sonata\\sonata_test_data_gen_over_500.json"
    path_to_data = "..\\test_sonata_plugin\\resources_sonata\\sonata_test_data_gen500.json"
    #path_to_data = "..\\test_sonata_plugin\\resources_sonata\\sonata_test_data_vel_knots presision.json"
    #path_to_data = "D:\\data\\python\\projects\\bl_frame_work\\bl_frame_work\\test_bl\\test_sonata_plugin\\resources_sonata\sonata_test_data.json"
    #path_to_data = "C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\test_bl\\test_sonata_plugin\\resources_sonata\\sonata_test_data.json"

    path_to_data = os.path.join(module_abs_path, path_to_data)
    rd = read_test_data.ReadData(path_to_data,
                                 test_data_type=read_test_data.test_data_type.json)
    sonata_msg_struct = sonata_msg.SonataMsg()
    tests_data = rd.get_testsuite_data(msg_struct=sonata_msg_struct)
    # test_ids = ["test_sonata_messages01", "test_sonata_messages05", "test_sonata_messages02", "test_sonata_messages07","test_sonata_messages05"]
    #test_ids = ["test_sonata_messages05","test_sonata_messages06","test_sonata_messages07"]

    test_messages_list = rd.get_testcase_messages(test_case_id=test_case_id)
    test_data_list = rd.get_testcase_data(test_case_id=test_case_id)
    result = (test_messages_list, test_data_list)
    return result
'''
TESTS ------------------------------------------------------------------------------------------------------------------
'''
def test_this_read_data():
    import multiprocessing, collections
    from test_bl.test_bl_tools import received_data, read_test_data, var_utils, logging_tools
    """
    send_receive class basic usage
    """
    lt = logging_tools.LoggingTools(
        default_path="C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_git_branching\\test_bl\\test_bl_configs\\logging_conf.json"
        )
    logger = lt.get_logger(__name__)
    sr = SendReceive(logging_tools=lt,
                     q_based=True
                     )

    udp_snd_01_name = sr.set_udp_sender(ip_to="10.11.10.11",
                                        port_to="55555")
    udp_srv_name = sr.set_udp_server(ip_address="10.11.10.12",
                                     port=55556)

    received_q = sr.get_received_queue(udp_srv_name)
    test_ids = ["test_sonata_messages05", "test_sonata_messages06", "test_sonata_messages07"]
    for index in test_ids:
        messages_file = get_test_messages(test_case_id=index)
        sr.udp_send_to(messages_list=messages_file,
                       sender_id=udp_snd_01_name)
        sr.test_messages_received(messages_list=messages_file,
                                  server_id=udp_srv_name)
        result = sr.get_received_queue(server_id=udp_srv_name)
        logging.debug("DATA RECEIVED: ==>"+str(result)+"\n")

    '''
    result = []
    while not received_q.empty():

        result.append(received_q.get())
    logging.debug("==>>>" + str(result))
    result.clear()
    '''

    sr.stop_sender(udp_snd_01_name)
    sr.stop_udp_server(udp_srv_name)
    return

def test_this_read_and_parse():
    import multiprocessing, collections, copy
    from test_bl.test_bl_tools import received_data, read_test_data, var_utils, logging_tools, process_received_data
    from test_bl.test_sonata_plugin.test_tools_sonata import sonata_test_parser
    """
    send_receive class basic usage
    """
    config_loggers()
    logger = logging.getLogger(__name__)
    sr = SendReceive(q_based=True)
    udp_snd_01_name = sr.set_udp_sender(ip_to="10.11.10.11",
                                        port_to="55555")
    udp_srv_name = sr.set_udp_server(ip_address="10.11.10.12",
                                     port=55556)
    received_q = sr.get_received_queue(udp_srv_name)
    #test_ids = ["test_sonata_messages05", "test_sonata_messages06", "test_sonata_messages07"]
    test_ids = ["test_sonata_messages05", "test_sonata_messages06", "test_sonata_messages07"]
    test_suite_parsed_data = {}
    test_suite_sent_data = {}
    s_parser = sonata_test_parser.SonataTestParser()
    proc_data = process_received_data.ProcessReceivedData()


    for index in test_ids:
        test_data_messages = get_test_messages(test_case_id=index)
        messages_to_send = test_data_messages[0]
        data_sent = test_data_messages[1]

        sr.udp_send_to(messages_list=messages_to_send,
                       sender_id=udp_snd_01_name)
        sr.test_messages_received(messages_list=messages_to_send,
                                  server_id=udp_srv_name)
        result = sr.get_received_queue(server_id=udp_srv_name)
        logging.debug("DATA RECEIVED: ==>" + str(result) + "\n")
        parsed_data = proc_data.parse_received_data(parser=s_parser,
                                                    received_data=result)
        test_suite_parsed_data[index] = copy.deepcopy(parsed_data)
        test_suite_sent_data[index] = copy.deepcopy(data_sent)

    '''Data comparison step'''
    test_ids = ["test_sonata_messages05", "test_sonata_messages06", "test_sonata_messages07"]
    result = {}
    for index in test_ids:
        data_sent       = test_suite_sent_data[index]
        data_received   = test_suite_parsed_data[index]
        result[index]=proc_data.compare_sent_received(parser           =s_parser,
                                                      data_sent        =data_sent,
                                                      data_received    =data_received)

    '''
    result = []
    while not received_q.empty():

        result.append(received_q.get())
    logging.debug("==>>>" + str(result))
    result.clear()
    '''
    sr.stop_sender(udp_snd_01_name)
    sr.stop_udp_server(udp_srv_name)
    return

def test_this_read_and_parse_and_json_gen():
        """
        test function for the current class
        :return: 
        """
        import multiprocessing, collections, copy, os
        from test_bl.test_bl_tools import received_data, read_test_data, var_utils, logging_tools, process_received_data
        from test_bl.test_sonata_plugin.test_tools_sonata import sonata_test_parser

        '''
        send_receive class basic usage example        '''
        '''SETUP-----------------------------------------------------------------------------------------------------'''
        '''here we are'''
        module_abs_path = os.path.abspath(os.path.dirname(__file__))

        '''config logging'''
        '''
        Logging for all classes used here 
        is configured from the config file in
        logging tools class.
        All configuration that pertains to individual modules 
        is there in the config
        '''
        config_loggers()
        logger = logging.getLogger("test_bl.test_bl_tools.send_receive")

        '''setup tested class'''
        sr = SendReceive(q_based=True)
        sr.logger = logger
        '''setup senders receivers'''
        udp_snd_01_name = sr.set_udp_sender(ip_to="10.11.10.11",
                                            port_to="55555")
        udp_srv_name = sr.set_udp_server(ip_address="10.11.10.12",
                                         port=55556)

        '''stuctures to hold sent and received data 
           for further comparison
        '''
        test_suite_parsed_data = {}
        test_suite_sent_data = {}
        '''parser class to be passed in various calls to processing class'''
        s_parser = sonata_test_parser.SonataTestParser()
        '''processing class doing parsing of the received data and comparison with the data been sent out'''
        proc_data = process_received_data.ProcessReceivedData()
        '''END OF SETUP---------------------------------------------------------------------------------------------'''


        '''ACTION---------------------------------------------------------------------------------------------------'''

        '''list of test cases names to iterate over
            while sending receiving and processing
            By the end of this process data for comparison 
            is available            
        '''
        # test_ids = ["test_sonata_messages05", "test_sonata_messages06", "test_sonata_messages07"]
        # test_ids = ["test_sonata_messages05", "test_sonata_messages06", "test_sonata_messages07"]
        # test_ids = ["".join("test_sonata_messages_0"+str(i)) for i in range(1,100) ]
        test_ids = ["test_sonata_messages_01"]
        for index in test_ids:
            test_data_messages = get_test_messages(test_case_id=index)
            messages_to_send = test_data_messages[0]
            data_sent = test_data_messages[1]

            sr.udp_send_to(messages_list=messages_to_send,
                           sender_id=udp_snd_01_name)
            sr.test_messages_received(messages_list=messages_to_send,
                                      server_id=udp_srv_name)
            '''get the queue to read from'''
            received_q = sr.get_received_queue(udp_srv_name)
            logging.debug("DATA RECEIVED: ==>" + str(received_q) + "\n")
            parsed_data = proc_data.parse_received_data(parser=s_parser,
                                                        received_data=received_q)
            test_suite_parsed_data[index] = copy.deepcopy(parsed_data)
            test_suite_sent_data[index] = copy.deepcopy(data_sent)

        '''
        Data comparison step
        data is structured and ready 
        just pass the same parser which 
        has comparator in it
        '''
        test_ids = ["test_sonata_messages_01"]
        result = {}
        for index in test_ids:
            data_sent = test_suite_sent_data[index]
            data_received = test_suite_parsed_data[index]
            result[index] = proc_data.compare_sent_received(parser=s_parser,
                                                            data_sent=data_sent,
                                                            data_received=data_received)

        for result in result[test_ids[0]]:
            for comparison in result:
                logger.error(comparison + ":==> " + str(result[comparison]))
            logger.error('\n')

        '''
        result = []
        while not received_q.empty():
            result.append(received_q.get())
            logging.debug("==>>>" + str(result))
        result.clear()
        '''
        sr.stop_sender(udp_snd_01_name)
        sr.stop_udp_server(udp_srv_name)
        return

if __name__ == "__main__":
     #test_this_server()
     #test_this_sender()
     #test_this_read_data()
     #test_this_read_and_parse()
     test_this_read_and_parse_and_json_gen()
     #test_this()
