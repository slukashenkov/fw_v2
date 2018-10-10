import copy
import logging


class ProcessReceivedData:
	
	
	def __init__ (self,
				  data_from = None,
				  conf = None
				  ):
		"""
		:param data_from:
		:param data_to:
		"""
		
		'''
		LETS NOT DO ANYTHING WITHOUT PROPER LOGGER
		'''
		'''
		Logger with the name __name__
		should be setup from config
		before this object is created and available
		beforehand
		'''
		self.logger = logging.getLogger(__name__)
		
		if conf == None:
			'''
			SETUP DATA to work on
			'''
			'''
			List of packets for comparison
			'''
			self.data_from = data_from
			'''
			SETUP PROCESSED DATA
			Storage
			'''
			self.data_parsed = []
		else:
			'''
			SetUp logger  in case there is config class used
			'''
			self.conf = conf
			self.logger = logging.getLogger(__name__)
			return
	
	
	def parse_received_data (self,
							 parser,
							 received_data):
		self.data_parsed.clear()
		parser.data_from = received_data
		try:
			for indx in range(len(received_data)):
				parser.packet_indx = indx
				self.data_parsed.append(copy.deepcopy(parser.parse_from()))
				self.logger.debug("<<== received data parsed ==>>")
			return self.data_parsed
		except:
			raise Exception("Something wrong with the received data array")
	
	
	def parse_received_packet (self,
							   parser,
							   packet):
		self.data_parsed.clear()
		parser.packet_to_parse = [packet]
		try:
			for indx in range(len(parser.packet_to_parse)):
				parser.packet_indx = indx
				self.data_parsed.append(copy.deepcopy(parser.parse_from()))
			return self.data_parsed
		except:
			raise Exception("Something wrong with the array of received data ")
	
	
	def parse_sut_log (self,
					   parser,
					   path_to_sut_log,
					   data_sent
					   ):
		self.data_parsed.clear()
		for msg_data in data_sent:
			data_parsed = parser.parse_log_auto(msg_data_sent = msg_data,
												path_to_log = path_to_sut_log)
			self.data_parsed.append(data_parsed)
		return self.data_parsed
	
	
	def compare_sent_received (self,
							   parser,
							   data_sent,
							   data_received):
		"""
		:param parser:          package specific parser
		:param data_sent:       list of data been sent
		:param data_received:   list of data been received
		:return:
		"""
		data_compared = []
		result = []
		'''
		len() check is for cases when we expect the number of messages sent == to the number received
		'''
		if len(data_sent) == len(data_received):
			num_of_elem = len(data_sent)
			proc_elem = 0
			
			result = copy.deepcopy(
				[parser.compare_fields(msg_data_sent, msg_data_received) for msg_data_sent, msg_data_received in
				 zip(data_sent, data_received)])
		
		else:
			result = parser.compare_fields(msg_data_sent = data_sent,
										   msg_data_received = data_received,
										   res_only = True)
		return result
	
	
	'''
	Initial compare function
	TODO: delete?
	'''
	
	
	def compare (self,
				 parser,
				 test_conditions_key,
				 data_sent,
				 data_received
				 ):
		pass_keys = []
		indx = 0
		result = {}
		results_list = []
		while indx < len(data_sent):
			msg = data_sent[indx]
			
			if test_conditions_key in msg.keys():
				pass_keys.append(msg[test_conditions_key])
				
				parser.data_to = self.conf.data_sent_list[indx]
				self.nmea_parser.sonata_nmea_parsed_map = self.nmea_parsed_list[indx]
				indx = indx + 1
				
				for key in pass_keys:
					self.key_sent = key
					self.key_received = key
					
					if key == "sonata_id":
						res_sonata_id = self.nmea_parser.compare_fields(sonata_id = key)
						result[key] = res_sonata_id
					
					elif key == "lat":
						res_lat = self.nmea_parser.compare_fields(lat = key)
						result[key] = res_lat
					
					elif key == "lon":
						res_lon = self.nmea_parser.compare_fields(lon = key)
						result[key] = res_lon
					
					elif key == "vel":
						res_vel = self.nmea_parser.compare_fields(vel = key)
						result[key] = res_vel
					
					elif key == "course":
						res_course = self.nmea_parser.compare_fields(course = key)
						result[key] = res_course
					
					elif key == "vel_knots":
						res_vel_knots = self.nmea_parser.compare_fields(vel_knots = key)
						result[key] = res_vel_knots
		
		results_list.append(copy.deepcopy(result))
		self.logger.debug("<<== send/receive comparison is done ==>>")
		return results_list
