import socketserver
import socket
import logging
import multiprocessing

from test_bl.test_bl_tools import logging_tools
from test_bl.test_sonata_plugin.configs_sonata import sonata_suite_config, sonata_send_recieve_properties
from test_bl.test_bl_tools import var_utils



class UdpPayloadHandler(socketserver.BaseRequestHandler):

    def __init__(self,
                 request,
                 client_address,
                 server_in):

        self.logger = server_in.logger
        self.server_in = server_in

        self.banner = server_in.udp_server_banner
        self.banner(server_name='UDP SERVER PayLoad HANDLER',
                                    server_ip=self.server_in.ip_address,
                                    server_port=self.server_in.port,
                                    ending='SETS ITSELF UP in __init__',
                                    logging_level=self.server_in.local_log_level,
                                    logger=self.logger
                                    )
        self.data_in_store = server_in.data_in

        socketserver.BaseRequestHandler.__init__(self,
                                                 request,
                                                 client_address,
                                                 server_in)
        return

    '''What the ... is this'''
    '''
    def set_data_storage(self,
                         struct_in,
                         type):
        if type:
            self.store_data_list=struct_in
        else:
            self.store_data_map=struct_in
    '''
    def setup(self):
        return socketserver.BaseRequestHandler.setup(self)

    def handle(self):
        '''
        Here the attribute assigned on the UDP server creation
        is used to store recieved messages from KD
        for further processing in The actual test
        :return:
        '''
        #self.server.conf.data_received_lock.acquire()
        #self.logger.debug('<------------------ Handle udp payload ----------------->')
        #messages = self.server.data_in
        self.banner(
            server_name='<------------------ Handle udp payload -----------------> \n' + 'UDP SERVER PayLoad HANDLER',
            server_ip=self.server_in.ip_address,
            server_port=self.server_in.port,
            ending='works with: ' + str(self.request) + 'before it is appended to the storage struct: ' + str(self.data_in_store) + 'as' + str(self.request[0]) ,
            logging_level=self.server_in.local_log_level,
            logger=self.logger
            )

        data = str(self.request[0])
        self.data_in_store.append(data)
        #self.server.conf.data_received_lock.release()
        self.banner(server_name='<------------------ Handle udp payload -----------------> ' + 'UDP SERVER PayLoad HANDLER',
                       server_ip=self.server_in.ip_address,
                        server_port=self.server_in.port,
                        ending=' starts to handle: ' + data + ' and append it to storage struct: ' + str(self.data_in_store),
                        logging_level=self.server_in.local_log_level,
                        logger=self.logger
                        )

        return

    def finish(self):
      #  self.logger.debug('finish')
        return socketserver.BaseRequestHandler.finish(self)


#class UdpServer(socketserver.ThreadingUDPServer):
class UdpServer(socketserver.UDPServer):

    #def __init__(self, server_address, handler_class=UdpPayloadHandler, data_in=received_data):
    def __init__(self,
                 server_address,
                 handler_class,
                 data_in,
                 curr_log_tools=logging_tools.LoggingTools,
                 conf = None
                 ):


        if conf != None:
            self.conf = conf
        self.logger=curr_log_tools.get_logger(__name__)
        self.local_log_level = 'INFO'
        self.udp_server_banner = var_utils.Varutils().build_srv_banner
        self.ip_address = server_address[0]
        self.port = server_address[1]

        self.allow_reuse_address = True
        socketserver.UDPServer.__init__(self,
                                        server_address,
                                        handler_class)

        self.data_in=data_in
        self.stop_serve_forever = True
        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=server_address[0],
                               server_port=server_address[1],
                               ending='starts in a PROCESS',
                               logging_level='INFO',
                               logger=self.logger
                               )
        proc_name = multiprocessing.current_process().name
        proc_pid = multiprocessing.current_process().pid
        self.logger.info("Curr_proc_name: " +proc_name + "Curr_proc_pid: " + proc_pid)
        self.serve_forever()
        return

    def server_activate(self):
        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=self.ip_address,
                               server_port=self.port,
                               ending='activates in A PROCESS',
                               logging_level='DEBUG',
                               logger=self.logger
                               )
        self.stop_serve_forever = True
        self.serve_forever()
        return

    def serve_forever(self):
        proc_name = multiprocessing.current_process().name
        proc_pid = multiprocessing.current_process().pid
        self.logger.info("Curr_proc_name: " + proc_name + "Curr_proc_pid: " + proc_pid)

        while self.stop_serve_forever:

            self.handle_request()
            self.udp_server_banner(server_name='python_UDP_SERVER',
                                   server_ip=self.ip_address,
                                   server_port=self.port,
                                   ending='is serving forever',
                                   logging_level='INFO',
                                   logger=self.logger
                                   )

        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=self.ip_address,
                               server_port=self.port,
                               ending='STOPS to SERVE FOREVER',
                               logging_level='INFO',
                               logger=self.logger
                               )
        self.server_close()
        return

    def handle_request(self):
        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=self.ip_address,
                               server_port=self.port,
                               ending='calls handle_request',
                               logging_level='DEBUG',
                               logger=self.logger
                               )

        return socketserver.UDPServer.handle_request(self)

    def verify_request(self, request, client_address):
        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=self.ip_address,
                               server_port=self.port,
                               ending='calls verify_request '  + str(request) + ' from: ' + str(client_address),
                               logging_level='INFO',
                               logger=self.logger
                               )

        self.logger.debug('UDP Server calls verify_request(%s, %s)', request, client_address)
        return socketserver.UDPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=self.ip_address,
                               server_port=self.port,
                               ending='calls verify_request '  + str(request) + ' from: ' + str(client_address),
                               logging_level='INFO',
                               logger=self.logger
                               )

        self.logger.debug('UDP Server calls process_request(%s, %s)', request, client_address)
        return socketserver.UDPServer.process_request(self,
                                                      request,
                                                      client_address)

    def server_close(self):
        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=self.ip_address,
                               server_port=self.port,
                               ending='calls server_close',
                               logging_level=self.local_log_level,
                               logger=self.logger
                               )
        return socketserver.UDPServer.server_close(self)

    def finish_request(self, request, client_address):
        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=self.ip_address,
                               server_port=self.port,
                               ending='calls finish_request '  + str(request) + ' from: ' + str(client_address),
                               logging_level='INFO',
                               logger=self.logger
                               )
        self.logger.debug('finish_request(%s, %s)', request, client_address)
        return socketserver.UDPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        self.logger.debug('close_request(%s)', request_address)
        return socketserver.UDPServer.close_request(self, request_address)
    '''--------------------------------------------------------------------------------------------------------------'''

class ProcessUdpListener(multiprocessing.Process):
        def __init__(self,
                     data_in = None):
            multiprocessing.Process.__init__(self)
            self.data = data_in
            #self.port = 6666
            #self.address = "10.11.10.12"
            self.address = ('10.11.10.12', 6667)

        def run(self):
            self.startServer()
            return

        def startServer(self):
            udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #address = ('', self.port)
            udpSocket.bind(self.address)
            while 1:
                data, client = udpSocket.recvfrom(1024)
                #print( self.data +'>>>'+ data.strip())
                self.data.put(data)
                udpSocket.sendto(bytes(4), client)
            return

def test_this():
    import threading

    import socketserver
    import logging
    import multiprocessing ,time

    from test_bl.test_bl_tools import logging_tools
    from test_bl.test_sonata_plugin.configs_sonata import sonata_suite_config, sonata_send_recieve_properties
    from test_bl.test_bl_tools import var_utils

    from test_bl.test_bl_tools import logging_tools, udp_server, udp_sender

    for i in range(1,3):
        time.sleep(20)
        '''
        Do a self created udp server
        '''
        q = multiprocessing.Queue()
        p_udp = ProcessUdpListener(q)
        p_udp.start()
        p_udp.terminate()


        #while True:
         #   print(q.get())

        '''
        TO BECOME properly initialised
        Server needs logger
        '''
        conf = sonata_send_recieve_properties.SonataSendReceiveProperties()
        #conf = sonata_suite_config.SonataSuiteConfig()


        lt = conf.logging_tools
        '''
        Server needs iterable to store data_from in
        '''
        data_in = []

        '''
        Server needs listening prefs
        '''
        address = ('10.11.10.12', 6666)
        #address = ('localhost', 0)  # let the kernel give us a port
        '''
        server = udp_server.UdpServer(address,
                                      udp_server.UdpPayloadHandler,
                                     data_in,
                                      lt,
                                      conf
                                      )
        ip, port = server.server_address  # find out what port we were given
        '''
        '''
        t = threading.Thread(target=server.serve_forever)
        t.setDaemon(True)  # don't hang on exit
        t.start()
        t.join
        '''
        '''
        p = multiprocessing.Process(target=udp_server.UdpServer,
                                    args=(address,
                                            UdpPayloadHandler,
                                            data_in,
                                            lt,
                                            conf
                                      ),
                                    name="udp_server"
                                    )
        p.daemon=True
        p.start()
        pid = p.pid
        '''
        '''
        Pure debug 
        '''
        #logger = logging.getLogger('External call to logger'+ 'pid: '+ str(p.pid))
        #logger.info('Server on %s:%s', ip, port)

        '''
        Stop UDP server
        '''
        #t.stop_serve_forever = False  # don't hang on exit



    return
if __name__ == '__main__':
    test_this()