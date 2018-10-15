import unittest

from test_bl.test_bl_tools import var_utils
from test_bl.test_sonata_plugin.configs_sonata import sonata_suite_config
from test_bl.test_sonata_plugin.test_tools_sonata import sonata_nmea_msgs_content_process


@unittest.skip("SKIP CLASS BASED TEST 01 FOR NOW")
class SonataToNMEAConversionTestCase01(unittest.TestCase):
	
	
	@classmethod
	def setUpClass (self):
		"""
		SETUP COMMON PROPERTIES FOR ALL TESTS from BEGINNING TO THE END OF EXECUTION:
		1) INITIAL CONFIG
		2) UDP SERVER to listen for BL responses
		:return:
		"""
		'''
		Initial Setup for the test
		'''
		# self.conf = sonata_send_recieve_properties.SonataSendReceiveProperties()
		
		'''
		Proper setup from config files
		'''
		self.conf = sonata_suite_config.SonataSuiteConfig()
		
		'''
		Setup EVERYTHING that pertains to sending receiving (UDP Server/sender data and so on)
		'''
		self.sr = self.conf.sender_receiver
		curr_udp_srv = self.sr.udp_server_listen_on()
		self.conf.set_current_test("test_sonata_messages01")
		self.sr.load_test_messages()
		self.sr.set_udp_sender()
		
		# sr.curr_logger('Debug module send_receive_sonata ')
		self.curr_logger = self.conf.logging_tools.get_logger(__name__)
		self.tools = var_utils.Varutils()
		self.tools.build_test_banner(__name__,
									 self.conf.messages_type,
									 'starts',
									 self.curr_logger
									 )
	
	
	@classmethod
	def tearDownClass (self):
		self.sr.close_UDP_socket()
		self.sr.udp_server_stop_listen_on()
		self.tools.build_test_banner(__name__,
									 self.conf.messages_type,
									 'stops',
									 self.curr_logger
									 )
	
	
	def setUp (self):
		self.curr_logger.info('Test' + __name__ + 'setup routine. send recieve udp')
	
	
	def tearDown (self):
		self.curr_logger.info('Test' + __name__ + 'tearDown routine.')
		return
	
	
	@unittest.skip("SKIP CLASS BASED TEST 01 FOR NOW")
	def test_sonata_messages_id (self):
		"""
		:return:
		"""
		
		'''
		DO AN ACTION ASSUMED TO BE DONE BY EQUPMENT
		MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
		LISTENER HAS BEEN SETUP THEN AS WELL
		'''
		self.curr_logger.info("01 sonata message send send via udp")
		self.sr.udp_send_to()
		
		'''
		Actual messages being sent
		'''
		res01 = self.conf.msgs_to_send[0]
		self.curr_logger.info(res01)
		
		'''
		DATA used in messages
		'''
		res02 = self.conf.data_received[0]
		self.curr_logger.info(res02)
		res03 = self.conf.data_sent
		self.curr_logger.info(res03)
		
		'''
			CONTENT PROCESSING IS A STARTING POINT for 
			ALL DATA content MANIPULATIONS IN TEST.
			IT DOES:
				1) Parse RAW data received from BL (router out) 
				2) Possesses knowledge of data been sent initially
				3) Makes comparisons         
		'''
		snmea = sonata_nmea_msgs_content_process.SonataNmeaMsgsContentProcessing(self.conf.data_received,
																				 self.conf.data_sent)
		
		'''
		PARSE one of the received 
		messages into a structure 
		ready for comparison         
		'''
		snmea.packet_indx = 1
		snmea.parse_nmea()
		'''
		Non optimal way
		TOO FAR REMOVED FROM THE TEST
		comparison can be done inside
		enveloping class 
		for 
		CONTENT PROCESSING
		'''
		snmea.key_sent = "sonata_id"
		snmea.key_received = "label2"
		
		snmea.compare_fields()
		
		'''
		GET VALUES ONLY
		'''
		result01 = int(snmea.get_field_in())
		result02 = snmea.get_field_out()
		
		'''
			TODO:
			Comparison is should be as selective as possible  

		'''
		# snmea.compare_with
		
		self.curr_logger.debug("INIT_VAL sent to Sonata: --->>>" + res01)
		self.curr_logger.debug("RES_VAL Nmea from Sonata: --->>>" + res02)
		
		self.curr_logger.debug("Field --->>>" + str(snmea.key_sent) + "<<<--- sent to Sonata: --->>>" + str(result01))
		self.curr_logger.debug(
			"Field --->>>" + str(snmea.key_received) + " <<<---received in Nmea message from Sonata: --->>>" + str(
				result02))
		
		self.assertNotEqual(result01,
							result02)
	
	
	@unittest.skip("SKIP CLASS BASED TEST 02 FOR NOW")
	class SonataToNMEAConversionTestCase02(unittest.TestCase):
		
		
		@unittest.skip("SKIP CLASS BASED TEST 01 FOR NOW")
		def test_sonata_messages_longitude (self):
			"""
			:return:
			"""
			''' DO AN ACTION ASSUMED TO BE DONE BY EQUPMENT
				MESSAGES HAVE BEING FORMED DURING CONFIGURATION STAGE
				LISTENER HAS BEEN SETUP THEN AS WELL
			'''
			
			self.curr_logger.info("===============================================================================|")
			self.curr_logger.info("02 sonata message send send via udp")
			test_id = self.id()
			self.conf.set_current_test("test_sonata_messages02")
			# self.conf.load_test_messages()
			'''
			Setup UDP Server
			'''
			self.conf.reset_test_messages_received()
			
			self.sr.load_test_messages()
			self.sr.set_udp_sender()
			self.sr.udp_send_to()
			
			'''
			#Actual messages being sent
			'''
			
			res01 = self.conf.msgs_to_send[0]
			self.curr_logger.info(res01)
			
			'''
			#DATA used in messages
			'''
			
			res02 = self.conf.data_received[0]
			self.curr_logger.info(res02)
			res03 = self.conf.data_sent
			self.curr_logger.info(res03)
			
			'''
				#CONTENT PROCESSING IS A STARTING POINT for
				#ALL DATA content MANIPULATIONS IN TEST.
				#IT DOES:
					#1) Parse RAW data received from BL (router out)
					#2) Possesses knowledge of data been sent initially
					#3) Makes comparisons
			'''
			
			snmea = sonata_nmea_msgs_content_process.SonataNmeaMsgsContentProcessing(self.conf.data_received,
																					 self.conf.data_sent)
			
			'''
			#PARSE one of the received
			#messages into a structure
			#ready for comparison
			'''
			
			snmea.packet_indx = 0
			snmea.parse_nmea()
			
			'''
			#Non optimal way
			#TOO FAR REMOVED FROM THE TEST
			#comparison can be done inside
			#enveloping class
			#for
			#CONTENT PROCESSING
			'''
			
			snmea.key_sent = "sonata_id"
			snmea.key_received = "label2"
			
			snmea.compare_fields()
			'''
			'''
			# GET VALUES ONLY
			'''
			'''
			result01 = int(snmea.get_field_in())
			result02 = snmea.get_field_out()
			'''
			'''
			# TODO:
			# Comparison is should be as selective as possible
			'''
			# snmea.compare_with
			'''
			self.curr_logger.debug("INIT_VAL sent to Sonata: --->>>" + res01)
			self.curr_logger.debug("RES_VAL Nmea from Sonata: --->>>" + res02)
			
			self.curr_logger.debug("Field " + str(snmea.key_sent) + " sent to Sonata: --->>>" + str(result01))
			self.curr_logger.debug(
				"Field " + str(snmea.key_received) + "received in Nmea message from Sonata: --->>>" + str(result02))
			
			self.assertEqual(result01,
							 result02)


if __name__ == '__main__':
	# '''
	unittest.main()
# '''
