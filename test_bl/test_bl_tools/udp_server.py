import socketserver
import logging

from test_bl.test_bl_tools import logging_tools
#from test_bl.test_sonata_plugin.configs_sonata import sonata_suite_config, sonata_send_recieve_properties
from test_bl.test_bl_tools import var_utils


class UdpPayloadHandler(socketserver.BaseRequestHandler):

    def __init__(self,
                 request,
                 client_address,
                 server_in):
        self.server_in = server_in
        self.data_in_store = server_in.data_in_queue
        self.data_in_status = server_in.status_queue
        self.logger = server_in.logger
        self.banner = server_in.udp_server_banner
        if self.server_in.res_filter != None:
            self.res_filter = server_in.res_filter
        else:
            self.res_filter = None
        self.banner(server_name='UDP SERVER PayLoad HANDLER',
                                    server_ip=self.server_in.ip_address,
                                    server_port=self.server_in.port,
                                    ending='SETS ITSELF UP in __init__',
                                    logger=self.logger
                                    )
        socketserver.BaseRequestHandler.__init__(self,
                                                 request,
                                                 client_address,
                                                 server_in)

        return

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
            server_name='<------------------ Handle udp payload -----------------> ' + 'UDP SERVER PayLoad HANDLER',
            server_ip=self.server_in.ip_address,
            server_port=self.server_in.port,
            ending='works with: ' + str(self.request) + 'before it is appended to the storage struct: ' + str(self.data_in_store) + 'as' + str(self.request[0]) ,
            logger=self.logger
            )


        '''TODO deal with datatype when reading from the RESEIVE Q'''
        #data = str(self.request[0])
        data = self.request[0]
        if self.res_filter != None:
            data_str = str(data)
            match = self.res_filter.match(data_str)
            if match:
                self.logger("$$$$$$$$$$$$$$$$regex MATCHED $$$$$$$$$$$$$ ")
                self.logger(data_str)
                self.logger("$$$$$$$$$$$$$$$$regex MATCHED $$$$$$$$$$$$$ ")
                self.data_in_store.put(data)
                self.data_in_status.put("received")
        else:
            self.data_in_store.put(data)
            self.data_in_status.put("received")


        if self.server.msg_res_event != None:
            self.server.msg_res_event.set()
        #self.server.conf.data_received_lock.release()
        self.banner(server_name='<------------------ Handle udp payload -----------------> ' + 'UDP SERVER PayLoad HANDLER',
                       server_ip=self.server_in.ip_address,
                        server_port=self.server_in.port,
                        ending=' starts to handle: ' + str(data) + ' and append it to storage struct: ' + str(self.data_in_store),
                        logger=self.logger
                        )

        return

    def finish(self):
      #  self.logger.debug('finish')
        return socketserver.BaseRequestHandler.finish(self)


class UdpServer(socketserver.ThreadingUDPServer):
    def __init__(self,
                 server_address = None,
                 handler_class  = None,
                 data_in_queue  = None,
                 status_queue   = None,
                 conf_in        = None,
                 msg_res_event  = None,
                 res_filter = None
                 ):
        """

        :param server_address:
        :param handler_class:
        :param data_in_queue:
        :param status_queue:
        :param conf_in:
        :param msg_res_event:
        """
        '''
        LETS NOT DO ANYTHING WITHOUT PROPER LOGGER
        '''
        self.res_filter=res_filter
        self.logger = logging.getLogger(__name__)

        self.name=None
        if conf_in != None:
            self.conf = conf_in
        self.udp_server_banner = var_utils.Varutils().build_srv_banner
        self.ip_address = server_address[0]
        self.port = server_address[1]
        self.msg_res_event = msg_res_event

        self.allow_reuse_address = True
        socketserver.UDPServer.__init__(self,
                                        server_address,
                                        handler_class)
        self.data_in_queue = data_in_queue
        self.status_queue  = status_queue
        self.stop_serve_forever = True
        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=server_address[0],
                               server_port=server_address[1],
                               ending='init',
                               logging_level='INFO',
                               logger=self.logger
                               )
        return

    def server_activate(self):
        return

    def stop_server(self):
        self.stop_serve_forever = False
        self.serve_forever()

    def serve_forever(self):
        while self.stop_serve_forever:
            self.handle_request()
            self.udp_server_banner(server_name='python_UDP_SERVER',
                                   server_ip=self.ip_address,
                                   server_port=self.port,
                                   ending='is serving forever',
                                   logging_level='INFO',
                                   logger=self.logger
                                   )
        else:
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
        return socketserver.UDPServer.handle_request(self)

    def verify_request(self, request, client_address):
        return socketserver.UDPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        return socketserver.UDPServer.process_request(self,
                                                      request,
                                                      client_address)

    def server_close(self):
        return socketserver.UDPServer.server_close(self)

    def finish_request(self, request, client_address):
        return socketserver.UDPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        return socketserver.UDPServer.close_request(self, request_address)
    '''--------------------------------------------------------------------------------------------------------------'''


class UdpServerProc(socketserver.ThreadingUDPServer):


    def __init__(self,
                 server_address=None,
                 handler_class=None,
                 data_in=None,
                 curr_log_tools=None,
                 conf_in = None,
                 msg_res_event = None
                 ):

        if conf_in != None:
            self.conf = conf_in
        self.logger=curr_log_tools.get_logger(__name__)
        self.udp_server_banner = var_utils.Varutils().build_srv_banner
        self.ip_address = server_address[0]
        self.port = server_address[1]
        self.msg_res_event = msg_res_event

        self.allow_reuse_address = True
        socketserver.UDPServer.__init__(self,
                                        server_address,
                                        handler_class)
        self.data_in=data_in
        self.stop_serve_forever = True
        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=server_address[0],
                               server_port=server_address[1],
                               ending='starts',
                               logging_level='INFO',
                               logger=self.logger
                               )
        return

    def server_activate(self):
        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=self.ip_address,
                               server_port=self.port,
                               ending='activates',
                               logging_level='DEBUG',
                               logger=self.logger
                               )
        return

    def stop_server(self):
        self.stop_serve_forever = False
        self.serve_forever()

    def serve_forever(self):
        while self.stop_serve_forever:
            self.handle_request()
            self.udp_server_banner(server_name='python_UDP_SERVER',
                                   server_ip=self.ip_address,
                                   server_port=self.port,
                                   ending='is serving forever',
                                   logging_level='INFO',
                                   logger=self.logger
                                   )
        else:
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


def test_this():
    import threading
    from test_bl.test_bl_tools import logging_tools, udp_server, udp_sender
    from test_bl.test_sonata_plugin.configs_sonata import sonata_suite_config

    '''
    TO BECOME properly initialised
    Server needs logger
    '''
    #conf = sonata_send_recieve_properties.SonataSendReceiveProperties()
    conf = sonata_suite_config.SonataSuiteConfig()


    lt = conf.logging_tools
    '''
    Server needs iterable to store data_from in
    '''
    data_in = []

    '''
    Server needs listening prefs
    '''
    address = ('10.11.10.12', 55556)
    #address = ('localhost', 0)  # let the kernel give us a port
    server = udp_server.UdpServer(address,
                                  UdpPayloadHandler,
                                  data_in,
                                  lt,
                                  conf
                                  )
    ip, port = server.server_address  # find out what port we were given

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True)  # don't hang on exit
    t.start()
    t.join

    '''
    Pure debug 
    '''
    logger = logging.getLogger('External call to logger')
    logger.info('Server on %s:%s', ip, port)

    '''
    Stop UDP server
    '''
    t.stop_serve_forever = False  # don't hang on exit

    return

def test_threaded_srv():
    import threading
    from test_bl.test_bl_tools import logging_tools, udp_server, udp_sender
    from test_bl.test_bl_tools import logging_tools, udp_server, udp_sender
    from test_bl.test_sonata_plugin.configs_sonata import sonata_suite_config

    '''
    TO BECOME properly initialised
    Server needs logger
    '''
    # conf = sonata_send_recieve_properties.SonataSendReceiveProperties()
    conf = sonata_suite_config.SonataSuiteConfig()

    lt = conf.logging_tools


    '''
    Server needs listening prefs
    '''


    server02 = conf.sender_receiver.udp_server
    #ip, port = server.server_address  # find out what port we were given
    ip02, port02 = server02.server_address

    #server02.serve_forever()
    t01 = threading.Thread(target=server02.serve_forever)
    t01.setDaemon(True)  # don't hang on exit
    t01.start()
    t01.join

    server02.stop_serve_forever = False

    '''
    Server needs iterable to store data_from in
    '''
    data_in = []

    '''Naturally server neeeds an adddress and a port'''
    address = ('10.11.10.12', 55557)

    # address = ('localhost', 0)  # let the kernel give us a port

    '''
    server_address  = None,
    handler_class   = None,
    data_in         = None,
    curr_log_tools  = None,
    conf_in         = None,
    msg_res_event   = None
    '''

    server = udp_server.UdpServer(server_address    = address,
                                  handler_class     = UdpPayloadHandler,
                                  data_in           = data_in,
                                  curr_log_tools    = lt,
                                  conf_in           = None,
                                  msg_res_event     = None
                                  )

    t = threading.Thread(target=server.serve_forever)
    t.setDaemon(True)  # don't hang on exit
    t.start()
    t.join


    #server.RequestHandlerClass.srv_shutdown = True

    #server.serve_forever()

    '''
    Stop UDP server.
    NB! When attempt is made to use flag.
    It is not checked until the moment when the new service request comes in
    '''
    #server.stop_serve_forever = False  # don't hang on exit

    '''Regular procedure is a shutdown method call. It sets flag checked authomatically'''

    server02.stop_server()
    server.stop_server()

    return

if __name__ == '__main__':
    #test_this()
    test_threaded_srv()