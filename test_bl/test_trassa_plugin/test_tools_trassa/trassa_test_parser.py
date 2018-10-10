import enum
import logging
import os.path
import re

from test_bl.test_bl_tools.scan_logs import ScanLogs
from test_bl.test_trassa_plugin.structs_trassa import nmea_msg, astd_msg


class trassa_msg_types(enum.Enum):
	PAIDD = 1
	PAISD = 2
	AITXT = 3
	AIALR = 4
	PEIST = 5
	ASTD = 6


class trassa_test_types(enum.Enum):
	PASS = 1
	FAIL = 2
	NO_MSG_SENT = 3


class TrassaTestParser():
	
	
	def __init__ (self,
				  data_from = None,
				  data_to = None):
		"""
		:param data_from:
		:param data_to:
		"""
		self.range = [1, 2, 3, 4, 5, 6, 7, 8, 9]
		
		'''
		Search pattern is configured in json test data
		'''
		self.search_pttrn_keyword = "log_pttrn"
		
		'''
		LETS NOT DO ANYTHING WITHOUT PROPER LOGGER
		'''
		self.logger = logging.getLogger(__name__)
		'''
		ALL DATA TO PROCESS
		'''
		self.data_from = data_from
		self.data_to = data_to
		
		'''
		SPECIFIC PACKETS TO PROCESS
		'''
		self.packet_indx = None
		
		'''
		RESULTING STORAGE DATA STRUCTURES
		'''
		self.trassa_data_from = {}
		self.trassa_data_parsed_map = {}
		self.trassa_data_to = {}
		self.trassa_nmea_from_parsed = {}
		
		'''
		SPECIFIC VALUES TO COMPARE
		'''
		self.key_sent = None
		self.key_received = None
		'''
		regex-es for identification of
		incoming packets
		'''
		self.regex_dict = {}
		'''
		PAIDD msg
		$PAIDD,7776666,89.5,N,67.0,E,67,30.7,32.5,111430.07*63
		'''
		self.paidd_regex = re.compile(r'''
                                        ^.*PAIDD.*
                                        ''', re.X | re.IGNORECASE)
		self.regex_dict[trassa_msg_types.PAIDD] = self.paidd_regex
		
		'''
		PAISD msg
		$PAISD,8989999,001100,Vsl_cl_sgn,Vsl_name*5B
		'''
		self.paisd_regex = re.compile(r'''
                                      ^.*PAISD.*
                                      ''', re.X | re.IGNORECASE)
		self.regex_dict[trassa_msg_types.PAISD] = self.paisd_regex
		
		'''
		ASTD msg
		S.TRASSA.FE.KD1F
		'''
		self.astd_regex = re.compile(r'''
                                      .*TRASSA.FE.KD.*
                                      ''', re.X | re.IGNORECASE)
		self.regex_dict[trassa_msg_types.ASTD] = self.astd_regex
		
		'''
		AITXT msg
		$AITXT,1,1,21,External DGNSS in use*67
		'''
		self.aitxt_regex = re.compile(r'''
                                      ^.*AITXT.*
                                      ''', re.X | re.IGNORECASE)
		self.regex_dict[trassa_msg_types.AITXT] = self.aitxt_regex
		
		'''
		AIALR msg
		$AIALR,133930.40,01,V,V,Tx malfunction*35
		'''
		self.aialr_regex = re.compile(r'''
                                      ^.*AIALR.*
                                      ''', re.X | re.IGNORECASE)
		self.regex_dict[trassa_msg_types.AIALR] = self.aialr_regex
		
		'''
		PCMST msg
		'$PCMST,133930.40,V*2E'
		'''
		self.peist_regex = re.compile(r'''
                                      ^.*PEIST.*
                                      ''', re.X | re.IGNORECASE)
		self.regex_dict[trassa_msg_types.PEIST] = self.peist_regex
		
		self.logger.debug("TRASSA Parser is SET")
		
		'''
		Helper classes that do actual parsing
		'''
		self.nmea_msg_helper = nmea_msg.NmeaMsg()
		self.astd_msg_helper = astd_msg.AstdMsg()
	
	
	def parse_from (self):
		"""
		:return:
		"""
		self.trassa_data_parsed_map.clear()
		'''
		GET PARTICULAR MSG
		by index
		'''
		try:
			self.data_from[self.packet_indx]
		except IndexError:
			self.logger.info(
				"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			self.logger.info(
				"No RETURN packet FOUND at the index: " + str(self.packet_indx) + " IN THE DATA_FROM STRUCTURE")
			self.logger.info("BL/MUSSON CAN BE DOWN AT THE MOMENT")
			self.logger.info(
				"!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
			
			raise Exception("NO PACKETS GOTTEN FROM BL FOR PROCESSING. So IT SEEMS.")
		
		data_to_parse = self.data_from[self.packet_indx]
		
		'''NB! VERY IMPORTANT ADDITION'''
		'''BEFORE CONVERSION INTO DESIRED FORMAT from BIN'''
		data_to_parse = str(data_to_parse.decode())
		m_type = self.msg_type(data_to_parse)
		'''
		Get structures for different
		msg types
		'''
		if m_type == trassa_msg_types.PAIDD:
			'''
			PAIDD message as coded into JSON
			
			"MessageID": 1,
			"RepeatIndicator": 1,
			"MMSI": 1193046,
			"NavigationStatus": 3,
			"ROT": -2,
			"SOG": 101.9,
			"PositionAccuracy": 1,
			"longitude": -122.16328055555556,
			"latitude": 37.424458333333334,
			"COG": 34.5,
			"TrueHeading": 41,
			"TimeStamp": 35,
			"RegionalReserved": 0,
			"Spare": 0,
			"RAIM": false,
			"state_syncstate": 2,
			"state_slottimeout": 0,
			"state_slotoffset": 1221
			'''
			paidd_parsed = self.nmea_msg_helper.parse_nmea(nmea_msg = data_to_parse)
			self.trassa_data_parsed_map["MMSI"] = paidd_parsed.mmsi
			self.trassa_data_parsed_map["longitude"] = paidd_parsed.lon
			self.trassa_data_parsed_map["hem_n_s"] = paidd_parsed.hem_n_s
			self.trassa_data_parsed_map["latitude"] = paidd_parsed.lat
			self.trassa_data_parsed_map["hem_e_w"] = paidd_parsed.hem_e_w
			self.trassa_data_parsed_map["SOG"] = paidd_parsed.sog
			self.trassa_data_parsed_map["TrueHeading"] = paidd_parsed.hdg
			self.trassa_data_parsed_map["COG"] = paidd_parsed.cog
			self.trassa_data_parsed_map["TimeStamp"] = paidd_parsed.tmstmp
			return self.trassa_data_parsed_map
		
		elif m_type == trassa_msg_types.PAISD:
			'''
			type 5 fields:
			
			"MessageID": 5,
			"RepeatIndicator": 1,
			"MMSI": 1193046,
			"AISversion": 0,
			"IMOnumber": 3210,
			"callsign": "PIRATE1",
			"name": "SDRTYSDRTYSDRTYSDRTY",
			"shipandcargo": 21,
			"dimA": 10,
			"dimB": 11,
			"dimC": 12,
			"dimD": 13,
			"fixtype": 1,
			"ETAmonth": 2,
			"ETAday": 28,
			"ETAhour": 9,
			"ETAminute": 54,
			"draught": 21.1,
			"destination": "NOWHERE@@@@@@@@@@@@@",
			"dte": 0,
			"Spare": 0
			'''
			paisd_parsed = self.nmea_msg_helper.parse_nmea(nmea_msg = data_to_parse)
			self.trassa_data_parsed_map["MMSI"] = paisd_parsed.mmsi
			self.trassa_data_parsed_map["IMOnumber"] = paisd_parsed.imo_num
			self.trassa_data_parsed_map["callsign"] = paisd_parsed.c_sign
			self.trassa_data_parsed_map["name"] = paisd_parsed.v_name
			return self.trassa_data_parsed_map
		
		
		elif m_type == trassa_msg_types.AITXT:
			aixtxt_map = self.nmea_msg_helper.parse_nmea(data_to_parse)
			'''
			 = aitxt_parsed.sntns_total
			 = aitxt_parsed.sntns_order_num
			 = aitxt_parsed.stat_code
			 = aitxt_parsed.stat_descr
			'''
			self.trassa_data_parsed_map["sntns_total"] = aixtxt_map.sntns_total
			self.trassa_data_parsed_map["sntns_order_num"] = aixtxt_map.sntns_order_num
			self.trassa_data_parsed_map["stat_code"] = aixtxt_map.stat_code
			self.trassa_data_parsed_map["stat_descr"] = aixtxt_map.stat_descr
			
			return self.trassa_data_parsed_map
		
		elif m_type == trassa_msg_types.AIALR:
			aialr_map = self.nmea_msg_helper.parse_nmea(data_to_parse)
			'''
			fail_time = aialr_parsed.fail_time
			fail_code = aialr_parsed.fail_code
			fail_stat = aialr_parsed.fail_stat
			tct_stat = aialr_parsed.tct_stat
			fail_descr = aialr_parsed.fail_descr
			'''
			self.trassa_data_parsed_map["fail_time"] = aialr_map.fail_time
			self.trassa_data_parsed_map["fail_code"] = aialr_map.fail_code
			self.trassa_data_parsed_map["fail_stat"] = aialr_map.fail_stat
			self.trassa_data_parsed_map["tct_stat"] = aialr_map.tct_stat
			self.trassa_data_parsed_map["fail_descr"] = aialr_map.fail_descr
			
			return self.trassa_data_parsed_map
		
		elif m_type == trassa_msg_types.ASTD:
			astd_map = self.astd_msg_helper.parse_astd(data_to_parse)
			return astd_map
		
		elif m_type == trassa_msg_types.PEIST:
			peist_map = self.nmea_msg_helper.parse_nmea(data_to_parse)
			'''
			peist_timestamp = peist_parsed.time_stamp
			peist_ims_stat  = peist_parsed.ims_status
			'''
			self.trassa_data_parsed_map["time_stamp"] = peist_map.time_stamp
			self.trassa_data_parsed_map["ims_status"] = peist_map.ims_status
			
			return self.trassa_data_parsed_map
	
	
	def msg_type (self,
				  data_to_parse):
		msg_type = None
		for key in self.regex_dict:
			curr_regex = self.regex_dict[key]
			result = curr_regex.match(data_to_parse)
			if result:
				return key
	
	
	def compare_fields (self,
						msg_data_sent = None,
						msg_data_received = None,
						res_only = None):
		"""
		:param msg_data_sent: data gathered at the time when packet is formed
		:param msg_data_received: data gathered fro SUT in UDP server
		:return:
		"""
		self.res_only = res_only
		comparison_results = {}
		'''
		TRASSA deals with different kind of messages
		some of which do not assume sending anything for instance
		so we need to find out what type of message
		we are dealing with
		from sent
		'''
		msg_type = self.get_msg_type(msg_data_sent)
		'''
		TRASSA goes beyond "what is sent eq what is recent" check
		so test conditions have additions
		and anyway it is better to extract them beforehand
		'''
		
		if self.res_only == True:
			comp_cond = msg_data_sent[0]['test_conditions']
		else:
			comp_cond = msg_data_sent['test_conditions']
		
		if msg_type == trassa_msg_types.PEIST:
			test_type = self.get_test_type(msg_data_sent,
										   msg_data_received)
			
			if test_type == trassa_test_types.NO_MSG_SENT:
				comparison_results = self.__do_received_msg_check(rec_data = msg_data_received,
																  conditions = comp_cond)
			return comparison_results
		
		if msg_type == trassa_msg_types.PAIDD:
			if "pass" in msg_data_sent["test_conditions"].keys():
				'''
				Initialise what we will search on
				'''
				self.trassa_data_parsed_map = msg_data_received
				self.data_to = msg_data_sent["fields"]
				keys = msg_data_sent["test_conditions"]["pass"]
				for key in keys:
					comparison_results[key] = self.__do_comparison_paidd(key)
				return comparison_results
			if "fail" in msg_data_sent["test_conditions"].keys:
				return
		
		if msg_type == trassa_msg_types.PAISD:
			if "pass" in msg_data_sent["test_conditions"].keys():
				'''
				Initialise what we will search on
				'''
				self.trassa_data_parsed_map = msg_data_received
				self.data_to = msg_data_sent["fields"]
				keys = msg_data_sent["test_conditions"]["pass"]
				for key in keys:
					comparison_results[key] = self.__do_comparison_paisd(key)
				return comparison_results
			if "fail" in msg_data_sent["test_conditions"].keys:
				return
			
			return
		if (msg_type == trassa_msg_types.AITXT) or (msg_type == trassa_msg_types.AIALR):
			if "pass" in msg_data_sent["test_conditions"].keys():
				'''
				Initialise what we will search on
				'''
				self.trassa_data_parsed_map = msg_data_received
				self.data_to = msg_data_sent["fields"]
				keys = msg_data_sent["test_conditions"]["pass"]
				for key in keys:
					comparison_results[key] = self.__do_comparison_aitxt_alr(key)
				return comparison_results
			if "fail" in msg_data_sent["test_conditions"].keys:
				return
			return
		

		
		if msg_type == trassa_msg_types.ASTD:
			if "pass" in msg_data_sent["test_conditions"].keys():
				'''
				Initialise what we will search on
				'''
				self.trassa_data_parsed_map = msg_data_received
				self.data_to = msg_data_sent["fields"]
				keys = msg_data_sent["test_conditions"]["pass"]
				comparison_results = self.__do_comparison_astd(keys)
				return comparison_results
			if "fail" in msg_data_sent["test_conditions"].keys:
				return
			return
	
	
	def get_test_type (self,
					   msg_data_sent,
					   msg_data_received):
		
		if self.res_only == True:
			test_type = msg_data_sent[0]["test_conditions"]
		else:
			test_type = msg_data_sent["test_conditions"]
		
		if msg_data_received == None and "fail" in test_type.keys():
			return trassa_test_types.FAIL
		elif msg_data_received != None and "pass" in test_type.keys():
			return trassa_test_types.PASS
		elif msg_data_received != None and "no_msg_sent" in test_type.keys():
			return trassa_test_types.NO_MSG_SENT
	
	
	def get_msg_type (self,
					  msg_data_sent):
		if self.res_only == True:
			msg_type = msg_data_sent[0]['msg_type']
		else:
			msg_type = msg_data_sent['msg_type']
		
		if msg_type == 'aitxt':
			return trassa_msg_types.AITXT
		if msg_type == 'ais_type05' or msg_type == 'ais_type24a' or msg_type == 'ais_type24b':
			return trassa_msg_types.PAISD
		if msg_type == 'peist':
			return trassa_msg_types.PEIST
		if (msg_type == 'aitxt') or (msg_type == 'aialr'):
			return trassa_msg_types.AIALR
		if msg_type == 'ais_type01' or msg_type == 'ais_type18':
			return trassa_msg_types.PAIDD
		if msg_type == 'pcmst':
			return trassa_msg_types.ASTD
	
	
	def __do_log_parsing (self,
						  msg_data_sent,
						  path_to_log
						  ):
		'''For each element sent test for substring'''
		if os.path.exists(path_to_log):
			pattern_in = []
			try:
				if "fail" in msg_data_sent.keys():
					pattern_in.append(msg_data_sent[self.search_pttrn_keyword])
			except:
				raise Exception("Something is wrong with our assumption that we can iterate over sent messages list")
			
			try:
				for pattern in pattern_in:
					search_substr = ScanLogs(logs_location = path_to_log,
											 search_pttrn = pattern)
					result = search_substr.scan_logs()
					return result
			except:
				raise Exception("Something is wrong with our assumption that we formed a list of patterns")
			return
	
	
	def __do_comparison_aitxt_alr (self,
								   key):
		
		result = False
		if (key in self.data_to) and (key in self.trassa_data_parsed_map):
			field_sent = self.data_to[key]
			field_received = self.trassa_data_parsed_map[key]
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
	
	
	def __do_comparison_paidd (self,
							   key):
		'''
		PAIDD fields:
				("MMSI", "MMSI"),
				("Longitude", "lon"),
				("Hemisphere_sign_n_s", "hem_n_s"),
				("Latitude", "lat"),
				("Hemisphere_sign_e_w", "hem_e_w"),
				("Speed Over Ground(SOG)", "sog"),
				("True Heading(HDG)", "hdg"),
				("Course Over Ground(COG)", "cog"),
				("Timestamp", "tmstmp"),


		AIS 1,18 fields
			  "MessageID": 1,
			  "RepeatIndicator": 1,
			  "MMSI": 1193046,
			  "NavigationStatus": 3,
			  "ROT": -2,
			  "SOG": 101.9,
			  "PositionAccuracy": 1,
			  "longitude": -122.16328055555556,
			  "latitude": 37.424458333333334,
			  "COG": 34.5,
			  "TrueHeading": 41,
			  "TimeStamp": 35,
			  "RegionalReserved": 0,
			  "Spare": 0,
			  "RAIM": false,
			  "state_syncstate": 2,
			  "state_slottimeout": 0,
			  "state_slotoffset": 1221

			  "MMSI"
			  "longitude"
			  "latitude"
			  "SOG"
			  "COG"
			  "TrueHeading"
		:param key: field for comparison
		:return:
		'''
		'''
		  "MMSI"
		  "longitude"
		  "latitude"
		  "SOG"
		  "COG"
		  "TrueHeading"
		'''
		result = False
		if "MMSI" == key and ((key in self.data_to) and (key in self.trassa_data_parsed_map)):
			field_sent = self.data_to[key]
			field_received = int(self.trassa_data_parsed_map[key])
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
		
		if "longitude" == key and ((key in self.data_to) and (key in self.trassa_data_parsed_map)):
			field_sent = self.data_to[key]
			field_received = float(self.trassa_data_parsed_map[key])
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
		
		if "latitude" == key and ((key in self.data_to) and (key in self.trassa_data_parsed_map)):
			field_sent = self.data_to[key]
			field_received = float(self.trassa_data_parsed_map[key])
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
		
		if "SOG" == key and ((key in self.data_to) and (key in self.trassa_data_parsed_map)):
			field_sent = self.data_to[key]
			field_received = float(self.trassa_data_parsed_map[key])
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
		
		if "COG" == key and ((key in self.data_to) and (key in self.trassa_data_parsed_map)):
			field_sent = self.data_to[key]
			field_received = float(self.trassa_data_parsed_map[key])
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
		
		if "TrueHeading" == key and ((key in self.data_to) and (key in self.trassa_data_parsed_map)):
			field_sent = float(self.data_to[key])
			field_received = float(self.trassa_data_parsed_map[key])
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
	
	
	def __do_comparison_paisd (self,
							   key):
		'''
		PAISD Fields
			("MMSI", "mmsi"),
			("IMO Number", "imo_num"),
			("Call Sign", "c_sign"),
			("Vessel Name", "v_name"),

		AIS 5 fields
		  "res_ptrn": "^.*PAISD.*",
		  "fields":{
		  "MessageID": 5,
		  "RepeatIndicator": 1,
		  "MMSI": 1193046,
		  "AISversion": 0,
		  "IMOnumber": 3210,
		  "callsign": "PIRATE1",
		  "name": "SDRTYSDRTYSDRTYSDRTY",
		  "shipandcargo": 21,
		  "dimA": 10,
		  "dimB": 11,
		  "dimC": 12,
		  "dimD": 13,
		  "fixtype": 1,
		  "ETAmonth": 2,
		  "ETAday": 28,
		  "ETAhour": 9,
		  "ETAminute": 54,
		  "draught": 21.1,
		  "destination": "NOWHERE@@@@@@@@@@@@@",
		  "dte": 0,
		  "Spare": 0

	  :param key:
	  :return:
	  '''
		
		result = False
		if "MMSI" == key and ((key in self.data_to) and (key in self.trassa_data_parsed_map)):
			field_sent = self.data_to[key]
			field_received = int(self.trassa_data_parsed_map[key])
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
		
		if "name" == key and ((key in self.data_to) and (key in self.trassa_data_parsed_map)):
			field_sent = self.data_to[key]
			field_received = str(self.trassa_data_parsed_map[key])
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
		
		if "callsign" == key and ((key in self.data_to) and (key in self.trassa_data_parsed_map)):
			field_sent = self.data_to[key]
			field_received = str(self.trassa_data_parsed_map[key])
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
		
		if "IMOnumber" == key and ((key in self.data_to) and (key in self.trassa_data_parsed_map)):
			field_sent = self.data_to[key]
			field_received = int(self.trassa_data_parsed_map[key])
			try:
				assert field_sent == field_received, "Fields ARE NOT equal"
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " was successful")
				return (result, field_sent, field_received)
			except:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " in field named: " + key + " FAILED MISERABLY")
				return (result, field_sent, field_received)
	
	
	def __do_comparison_astd (self,
							  key):
		'''
		PAIDD fields:
		("MMSI", "MMSI"),
		("Longitude", "lon"),
		("Hemisphere_sign_n_s", "hem_n_s"),
		("Latitude", "lat"),
		("Hemisphere_sign_e_w", "hem_e_w"),
		("Speed Over Ground(SOG)", "sog"),
		("True Heading(HDG)", "hdg"),
		("Course Over Ground(COG)", "cog"),
		("Timestamp", "tmstmp"),


		AIS 1,18 fields
		  "MessageID": 1,
		  "RepeatIndicator": 1,
		  "MMSI": 1193046,
		  "NavigationStatus": 3,
		  "ROT": -2,
		  "SOG": 101.9,
		  "PositionAccuracy": 1,
		  "longitude": -122.16328055555556,
		  "latitude": 37.424458333333334,
		  "COG": 34.5,
		  "TrueHeading": 41,
		  "TimeStamp": 35,
		  "RegionalReserved": 0,
		  "Spare": 0,
		  "RAIM": false,
		  "state_syncstate": 2,
		  "state_slottimeout": 0,
		  "state_slotoffset": 1221

		  "MMSI"
		  "longitude"
		  "latitude"
		  "SOG"
		  "COG"
		  "TrueHeading"
		:param key:
		:return:
		'''
		'''
		  "MMSI"
		  "longitude"
		  "latitude"
		  "SOG"
		  "COG"
		  "TrueHeading"
		'''
		result = False
		keys_sent = self.data_to.keys()
		keys_rec = self.trassa_data_parsed_map.keys()
		
		if ("eq_state" in keys_sent) and ("trassa_status" in keys_rec):
			field_sent = str(self.data_to["eq_state"])
			field_received = str(self.trassa_data_parsed_map["trassa_status"])
			
			if (field_sent == "V" and field_received == "F") or (field_sent == "A" and field_received == "G"):
				result = True
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + "was successful")
				return (result, field_sent, field_received)
			else:
				self.logger.debug("Comparison of " + str(field_sent) + " and " + str(
					field_received) + " FAILED MISERABLY")
				return (result, field_sent, field_received)
	
	
	def __do_received_msg_check (self,
								 rec_data,
								 conditions):
		if not rec_data:
			raise Exception("Received data dataset is empty. KD is not on MOST likely!")
		
		if "no_msg_sent" in conditions.keys():
			send_period = conditions["no_msg_sent"][0]["time_stamp"]
			flag = conditions["no_msg_sent"][1]["ims_status"]
			result = {}
			message_type = "peist"
			
			if rec_data:
				t_stamp_01 = rec_data[1]["time_stamp"]
				t_stamp_02 = rec_data[2]["time_stamp"]
				msg_01_sec = int(t_stamp_01[-4])
				msg_02_sec = int(t_stamp_02[-4])
				
				comp = msg_02_sec - msg_01_sec
				res_flag = rec_data[1]["ims_status"]
				
				if comp == send_period and res_flag == flag:
					result[message_type] = (True, comp, res_flag)
					return result
				else:
					result[message_type] = (False, comp, res_flag)
					return result
	
	
	def parse_log_auto (self,
						msg_data_sent,
						path_to_log):
		
		return
