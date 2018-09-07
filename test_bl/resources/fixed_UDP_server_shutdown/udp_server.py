import socketserver
import multiprocessing
import logging

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
        self.banner(server_name='<------------------ Handle udp payload -----------------> \n' + 'UDP SERVER PayLoad HANDLER',
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
class UdpServer(socketserver.ThreadingUDPServer):

    #def __init__(self, server_address, handler_class=UdpPayloadHandler, data_in=received_data):
    def __init__(self,
                 server_address=None,
                 handler_class=None,
                 data_in=None,
                 curr_log_tools=None,
                 conf_in = None
                 ):

        if conf_in != None:
            self.conf = conf_in
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

class UdpServerProc(socketserver.UDPServer, multiprocessing.Process):

    #def __init__(self, server_address, handler_class=UdpPayloadHandler, data_in=received_data):
    def __init__(self,
                 server_address=None,
                 handler_class=None,
                 data_in=None,
                 curr_log_tools=None,
                 conf_in = None
                 ):

        if conf_in != None:
            self.conf = conf_in
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
                               ending='starts',
                               logging_level='INFO',
                               logger=self.logger
                               )
        return

    def run(self):
        self.serve_forever
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
    #'''
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

        self.udp_server_banner(server_name='python_UDP_SERVER',
                               server_ip=self.ip_address,
                               server_port=self.port,
                               ending='STOPS to SERVE FOREVER',
                               logging_level='INFO',
                               logger=self.logger
                               )
        self.server_close()
        return
    #'''

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

def test_threaded_srv():
    import threading
    from test_bl.test_bl_tools import logging_tools, udp_server, udp_sender

    '''
    TO BECOME properly initialised
    Server needs logger
    '''
    # conf = sonata_send_recieve_properties.SonataSendReceiveProperties()
    conf = sonata_suite_config.SonataSuiteConfig()

    lt = conf.logging_tools
    '''
    Server needs iterable to store data_from in
    '''
    data_in = []

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

    address = ('10.11.10.12', 55557)
    # address = ('localhost', 0)  # let the kernel give us a port
    server = udp_server.UdpServer(address,
                                  UdpPayloadHandler,
                                  data_in,
                                  lt,
                                  conf
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


def test_proc_srv():
    import socketserver
    import multiprocessing
    import logging

    from test_bl.test_bl_tools import logging_tools
    from test_bl.test_sonata_plugin.configs_sonata import sonata_suite_config, sonata_send_recieve_properties
    from test_bl.test_bl_tools import var_utils
    from test_bl.test_bl_tools import logging_tools, udp_server, udp_sender

    '''
    TO BECOME properly initialised
    Server needs logger
    '''
    # conf = sonata_send_recieve_properties.SonataSendReceiveProperties()
    conf = sonata_suite_config.SonataSuiteConfig()

    lt = conf.logging_tools
    '''
    Server needs iterable to store data_from in
    '''
    data_in = []

    '''
    Server needs listening prefs
    '''
    address = ('10.11.10.12', 55557)
    # address = ('localhost', 0)  # let the kernel give us a port
    server = udp_server.UdpServerProc(address,
                                  UdpPayloadHandler,
                                  data_in,
                                  lt,
                                  conf
                                  )
    server.start()

    return

def test_this():
    #test_proc_srv()
    test_threaded_srv()

if __name__ == '__main__':
    test_this()