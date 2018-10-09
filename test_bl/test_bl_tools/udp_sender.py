import logging
import multiprocessing
import socket
import sys
from logging.handlers import TimedRotatingFileHandler
from time import sleep

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "UDP_SENDER_PROC.log"


class UdpSender:
	
	
	def __init__ (self ,
				  msg_iterator = None ,
				  logging_tools = None ,
				  ip_to = "127.0.0.1" ,
				  port_to = "55555" ,
				  evnt_msg_sent = None
				  ):
		"""
		:param msg_iterator:
		:param logging_tools:
		:param ip_to:
		:param port_to:
		:param evnt_msg_sent:
		"""
		
		self.sock = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
		self.msg_iterator = msg_iterator
		self.ip_to = ip_to
		self.port_to = port_to
		
		'''Lack of set event should not block anything'''
		if evnt_msg_sent != None:
			self.evnt_msg_sent = evnt_msg_sent
		
		'''Set logger'''
		if logging_tools != None:
			self.curr_logger = logging_tools.get_logger(__name__)
		else:
			self.curr_logger = logging.getLogger(__name__)
	
	
	def send_udp (self):
		for msg in self.msg_iterator:
			self.sock.sendto(str.encode(msg) ,
							 (self.ip_to ,
							  self.port_to)
							 )
			if self.msg_sent_evnt != None:
				self.msg_sent_evnt.set()
			self.curr_logger.debug("Sent to: " + self.ip_to + ":" + str(self.port_to) + " message: " + msg)
			sleep(self.delay)
		return
	
	
	def close_socket (self):
		self.sock.close()
		return


class UdpSenderProcess(multiprocessing.Process):
	
	
	def __init__ (self ,
				  ip_to = "10.11.10.12" ,
				  port_to = "55555" ,
				  event_msg_send = None ,
				  msgs_queue = None ,
				  msg_sent_status_queue = None
				  ):
		
		"""
		:param ip_to:           address where udp packet will be sent
		:param port_to:         port where udp packet will be sent
		:param event_msg_send:  event that triggers popping paket from the queue and sending it
		:param event_msg_sent:  event signalling any interested external party that message has been sent
		:param msgs_queue:      the queue of the actual messages that have to be sent
		None in queue is a poison pill which will force the sender process`s exit
		"""
		'''Utility functions'''
		
		
		def get_console_handler ():
			console_handler = logging.StreamHandler(sys.stdout)
			console_handler.setFormatter(FORMATTER)
			return console_handler
		
		
		def get_null_handler ():
			console_handler = logging.NullHandler()
			console_handler.setFormatter(FORMATTER)
			return console_handler
		
		
		def get_file_handler (self):
			file_handler = TimedRotatingFileHandler(LOG_FILE , when = 'midnight')
			file_handler.setFormatter(FORMATTER)
			return file_handler
		
		
		def get_logger (logger_name):
			logger = logging.getLogger(logger_name)
			logger.setLevel(logging.DEBUG)  # better to have too much log than not enough
			logger.addHandler(get_null_handler)
			# logger.addHandler(get_file_handler())
			# with this pattern, it's rarely necessary to propagate the error up to parent
			logger.propagate = True
			return logger
		
		
		'''setup'''
		multiprocessing.Process.__init__(self)
		self.sock = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
		self.ip_to = ip_to
		self.port_to = int(port_to)
		# self.logger = get_logger(logger_name=__name__)
		
		self.event_msg_send = event_msg_send
		self.msgs_queue = msgs_queue
		self.msg_sent_status_queue = msg_sent_status_queue
	
	
	def run (self):
		cnt = 0
		while True:
			self.event_msg_send.wait()
			next_task = self.msgs_queue.get()
			
			if next_task != None:
				print("is about to send msg: " + next_task + str(self.ip_to) + ":" + str(self.port_to) + "\n")
			# self.logger.debug("is about to send msg: " + next_task + "\n")
			else:
				print("POISON PILL!!!!\n")
			# self.logger.debug("POISON PILL!!!!\n")
			# Poison pill
			if next_task is None:
				print("Killed by POISON PILL")
				# self.logger.debug("Killed by POISON PILL")
				exit(0)
			else:
				print("sending msg: " + next_task + " to:" + str(self.ip_to) + ":" + str(self.port_to) + "\n")
				# self.logger.debug("sending msg: " + next_task + "\n")
				encoded = str.encode(next_task)
				self.sock.sendto(encoded , (self.ip_to ,
											self.port_to))
				'''
				self.sock.sendto(str.encode(str(next_task)),
								 (self.ip_to,
								  self.port_to))
				'''
				self.event_msg_send.clear()
				self.msg_sent_status_queue.put("done")
			cnt = cnt + 1
