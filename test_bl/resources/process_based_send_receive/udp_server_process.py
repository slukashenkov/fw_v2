import multiprocessing
import socket
import socketserver

from test_bl.test_bl_tools import logging_tools
from test_bl.test_bl_tools import var_utils


class UdpPayloadHandler(socketserver.BaseRequestHandler):
	
	
	def __init__ (self,
				  request,
				  client_address,
				  server_in):
		self.logger = server_in.logger
		self.server_in = server_in
		
		self.banner = server_in.udp_server_banner
		self.banner(server_name = 'UDP SERVER PayLoad HANDLER',
					server_ip = self.server_in.ip_address,
					server_port = self.server_in.port,
					ending = 'SETS ITSELF UP in __init__',
					logging_level = self.server_in.local_log_level,
					logger = self.logger
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
	
	
	def setup (self):
		return socketserver.BaseRequestHandler.setup(self)
	
	
	def handle (self):
		'''
		Here the attribute assigned on the UDP server creation
		is used to store recieved messages from KD
		for further processing in The actual test
		:return:
		'''
		# self.server.conf.data_received_lock.acquire()
		# self.logger.debug('<------------------ Handle udp payload ----------------->')
		# messages = self.server.data_in
		self.banner(
			server_name = '<------------------ Handle udp payload -----------------> \n' + 'UDP SERVER PayLoad HANDLER',
			server_ip = self.server_in.ip_address,
			server_port = self.server_in.port,
			ending = 'works with: ' + str(self.request) + 'before it is appended to the storage struct: ' + str(
				self.data_in_store) + 'as' + str(self.request[0]),
			logging_level = self.server_in.local_log_level,
			logger = self.logger
		)
		
		data = str(self.request[0])
		self.data_in_store.append(data)
		# self.server.conf.data_received_lock.release()
		self.banner(
			server_name = '<------------------ Handle udp payload -----------------> ' + 'UDP SERVER PayLoad HANDLER',
			server_ip = self.server_in.ip_address,
			server_port = self.server_in.port,
			ending = ' starts to handle: ' + data + ' and append it to storage struct: ' + str(self.data_in_store),
			logging_level = self.server_in.local_log_level,
			logger = self.logger
		)
		
		return
	
	
	def finish (self):
		#  self.logger.debug('finish')
		return socketserver.BaseRequestHandler.finish(self)


# class UdpServer(socketserver.ThreadingUDPServer):
class UdpServer(socketserver.ThreadingUDPServer, socketserver.ThreadingMixIn):
	
	
	# def __init__(self, server_address, handler_class=UdpPayloadHandler, data_in=received_data):
	def __init__ (self,
				  server_address,
				  handler_class,
				  data_in,
				  curr_log_tools = logging_tools.LoggingTools,
				  conf = None
				  ):
		
		if conf != None:
			self.conf = conf
		self.logger = curr_log_tools.get_logger(__name__)
		self.local_log_level = 'INFO'
		self.udp_server_banner = var_utils.Varutils().build_srv_banner
		self.ip_address = server_address[0]
		self.port = server_address[1]
		
		self.allow_reuse_address = True
		socketserver.UDPServer.__init__(self,
										server_address,
										handler_class)
		
		self.data_in = data_in
		self.stop_serve_forever = True
		self.udp_server_banner(server_name = 'python_UDP_SERVER',
							   server_ip = server_address[0],
							   server_port = server_address[1],
							   ending = 'starts in a PROCESS',
							   logging_level = 'INFO',
							   logger = self.logger
							   )
		proc_name = multiprocessing.current_process().name
		proc_pid = multiprocessing.current_process().pid
		self.logger.info("Curr_proc_name: " + proc_name + "Curr_proc_pid: " + proc_pid)
		self.serve_forever()
		return
	
	
	def server_activate (self):
		self.udp_server_banner(server_name = 'python_UDP_SERVER',
							   server_ip = self.ip_address,
							   server_port = self.port,
							   ending = 'activates in A PROCESS',
							   logging_level = 'DEBUG',
							   logger = self.logger
							   )
		self.stop_serve_forever = True
		self.serve_forever()
		return
	
	
	def serve_forever (self):
		proc_name = multiprocessing.current_process().name
		proc_pid = multiprocessing.current_process().pid
		self.logger.info("Curr_proc_name: " + proc_name + "Curr_proc_pid: " + proc_pid)
		
		while self.stop_serve_forever:
			self.handle_request()
			self.udp_server_banner(server_name = 'python_UDP_SERVER',
								   server_ip = self.ip_address,
								   server_port = self.port,
								   ending = 'is serving forever',
								   logging_level = 'INFO',
								   logger = self.logger
								   )
		
		self.udp_server_banner(server_name = 'python_UDP_SERVER',
							   server_ip = self.ip_address,
							   server_port = self.port,
							   ending = 'STOPS to SERVE FOREVER',
							   logging_level = 'INFO',
							   logger = self.logger
							   )
		self.server_close()
		return
	
	
	def handle_request (self):
		self.udp_server_banner(server_name = 'python_UDP_SERVER',
							   server_ip = self.ip_address,
							   server_port = self.port,
							   ending = 'calls handle_request',
							   logging_level = 'DEBUG',
							   logger = self.logger
							   )
		
		return socketserver.UDPServer.handle_request(self)
	
	
	def verify_request (self, request, client_address):
		self.udp_server_banner(server_name = 'python_UDP_SERVER',
							   server_ip = self.ip_address,
							   server_port = self.port,
							   ending = 'calls verify_request ' + str(request) + ' from: ' + str(client_address),
							   logging_level = 'INFO',
							   logger = self.logger
							   )
		
		self.logger.debug('UDP Server calls verify_request(%s, %s)', request, client_address)
		return socketserver.UDPServer.verify_request(self, request, client_address)
	
	
	def process_request (self, request, client_address):
		self.udp_server_banner(server_name = 'python_UDP_SERVER',
							   server_ip = self.ip_address,
							   server_port = self.port,
							   ending = 'calls verify_request ' + str(request) + ' from: ' + str(client_address),
							   logging_level = 'INFO',
							   logger = self.logger
							   )
		
		self.logger.debug('UDP Server calls process_request(%s, %s)', request, client_address)
		return socketserver.UDPServer.process_request(self,
													  request,
													  client_address)
	
	
	def server_close (self):
		self.udp_server_banner(server_name = 'python_UDP_SERVER',
							   server_ip = self.ip_address,
							   server_port = self.port,
							   ending = 'calls server_close',
							   logging_level = self.local_log_level,
							   logger = self.logger
							   )
		return socketserver.UDPServer.server_close(self)
	
	
	def finish_request (self, request, client_address):
		self.udp_server_banner(server_name = 'python_UDP_SERVER',
							   server_ip = self.ip_address,
							   server_port = self.port,
							   ending = 'calls finish_request ' + str(request) + ' from: ' + str(client_address),
							   logging_level = 'INFO',
							   logger = self.logger
							   )
		self.logger.debug('finish_request(%s, %s)', request, client_address)
		return socketserver.UDPServer.finish_request(self, request, client_address)
	
	
	def close_request (self, request_address):
		self.logger.debug('close_request(%s)', request_address)
		return socketserver.UDPServer.close_request(self, request_address)
	
	
	'''--------------------------------------------------------------------------------------------------------------'''


class UdpListenerProcess(multiprocessing.Process):
	
	
	def __init__ (self,
				  ip_on = "10.11.10.12",
				  port_on = 55555,
				  sync_event = None,
				  result_queue = None,
				  logger_in = None
				  ):
		multiprocessing.Process.__init__(self)
		self.result_queue = result_queue
		self.sync_event = sync_event
		self.port = port_on
		self.ip = ip_on
		self.address = (self.ip, self.port)
	
	
	def run (self):
		self.startServer()
		return
	
	
	def startServer (self):
		udpSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		# address = ('', self.port)
		udpSocket.bind(self.address)
		while 1:
			data, client = udpSocket.recvfrom(1024)
			print(str(data) + '<<<<==Received')
			self.result_queue.put(data)
			# udpSocket.sendto(bytes(4), client)
			self.sync_event.set()
			print(self.sync_event)
		return


class PayloadProcessor(multiprocessing.Process):
	
	
	def __init__ (self,
				  sync_event = None,
				  result_queue = None,
				  logger_in = None
				  ):
		multiprocessing.Process.__init__(self)
		self.result_queue = result_queue
		self.sync_event = sync_event
	
	
	def run (self):
		while 1:
			print("Waiting for event")
			self.sync_event.wait()
			res = self.result_queue.get()
			print(str(res) + '<<<<== Received from Q')
		
		return


def test_this ():
	import multiprocessing
	
	from test_bl.test_bl_tools import udp_sender
	
	# for i in range(1,3):
	# time.sleep(20)
	'''
	Do a self created udp server
	'''
	q_messages = multiprocessing.Queue()
	q_sent_res = multiprocessing.Queue()
	q_res_messages = multiprocessing.Queue()
	
	sync_sent = multiprocessing.Event()
	sync_res = multiprocessing.Event()
	
	p_udp_listen = UdpListenerProcess(result_queue = q_res_messages,
									  sync_event = sync_res)
	
	p_udp_send = udp_sender.UdpSenderProcess(sync_event = sync_sent,
											 msgs_queue = q_messages,
											 result_queue = q_sent_res
											 )
	
	date_handler = PayloadProcessor(result_queue = q_res_messages,
									sync_event = sync_res
									)
	# date_handler.start()
	p_udp_send.start()
	p_udp_listen.start()
	
	q_messages.put(1)
	q_messages.put(2)
	q_messages.put(3)
	q_messages.put(None)
	
	sync_sent.wait
	cnt_reslt = q_sent_res.get(block = True)
	p_udp_send.terminate()
	
	res = []
	cnt_res = 1
	while 1:
		sync_res.wait()
		q = q_res_messages.get()
		
		if cnt_res == cnt_reslt:
			res.append(q)
			p_udp_listen.terminate()
			break
		else:
			res.append(q)
			cnt_res = cnt_res + 1
	
	return


if __name__ == '__main__':
	test_this()
