import socket
import threading, multiprocessing
from time import sleep
import logging

class UdpSender:
    '''
    TODO: Synchronisation problems - DONE
    DONE: It was actually cleanup of the data_from to be sent
    when tests are run in parallel (or just several tests at once from UNITTEST)
    '''
    '''
    A REMINDER FOR NO REASON
    
    while 1:
    n_msg =[1,2,3]
    self.curr_logger.info('Start sending messages to KD')
    for i in n_msg:

        if self.conf.quit_flag:
            self.curr_logger.debug('Quit sending messages to' + self.conf.toInfo)
            return
        if self.conf.pause_flag:
            self.curr_logger.debug('Pause sending messages to' + self.conf.toInfo)
            while self.conf.pause_flag and not self.conf.quit_flag:
                sleep(0.5)
            if self.conf.quit_flag:
                continue
            else:
                self.curr_logger.debug('Continue')


    for n in range(0, self.conf.num_msgs_to_send):
        msg = next(iterator)
        self.sock.sendto(str.encode(msg),
                        (self.conf.ip_to,
                        self.conf.port_to)
                        )
        sleep(1)
        self.curr_logger.debug('Message SENT to KD'+ msg)
    '''
    '''
        TODO: LeftOVERS from initial script. Need to decide whether there is any need in this.             
    '''
    '''
         for i in range(self.conf.delay):
            if self.conf.quit_flag or self.conf.pause_flag:
                break;
            sleep(1)
    '''
    def __init__(self,
                 msg_iterator,
                 delay=1,
                 logging_tools=None,
                 ip_to="127.0.0.1",
                 port_to="55555"
                 ):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.msg_iterator=msg_iterator
        self.delay = delay
        self.ip_to = ip_to
        self.port_to = port_to

        '''Set logger'''
        if logging_tools !=None:
            self.curr_logger=logging_tools.get_logger(__name__)


    def send_udp(self):

        for msg in self.msg_iterator:

            self.sock.sendto(str.encode(msg),
                            (self.ip_to,
                            self.port_to)
                            )
            self.curr_logger.debug("Sent to: "+ self.ip_to + ":"+ str(self.port_to)+" message: " + msg)
            sleep(self.delay)
        return

    def close_socket(self):
        self.sock.close()
        return

class UdpSenderProcess(multiprocessing.Process):
        def __init__(self,
                     ip_to="10.11.10.12",
                     port_to="55555",
                     sync_event=None,
                     msgs_queue=None,
                     result_queue=None,
                     logger_in=None):
            multiprocessing.Process.__init__(self)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.ip_to = ip_to
            self.port_to = int(port_to)
            self.sync_event = sync_event
            self.msgs_queue = msgs_queue
            self.result_queue = result_queue

        def run(self):
            #self.sync_event.wait()
            proc_name = self.name
            cntr = 0
            while True:
                next_task = self.msgs_queue.get()
                sleep(3)
                # Poison pill
                if next_task is None:
                    #print '%s: Exiting' % proc_name
                    #self.msgs_queue.task_done()
                    self.result_queue.put(cntr)
                    self.sync_event = True
                    break
                #print '%s: %s' % (proc_name, next_task)

                self.sock.sendto(str.encode(str(next_task)),
                                 (self.ip_to,
                                  self.port_to)
                                 )
                #answer = next_task()
                #self.task_queue.task_done()
                cntr = cntr+1

            return



