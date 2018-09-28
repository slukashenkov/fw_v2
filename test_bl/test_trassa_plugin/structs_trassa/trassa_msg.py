from binascii import a2b_qp
from bitstring import BitArray
#from binascii import a2b_qp
import copy, logging

from test_bl.test_sonata_plugin.configs_sonata import sonata_send_recieve_properties
from test_bl.test_bl_tools import read_test_data
from test_bl.test_bl_tools.logging_tools import  LoggingTools


class TrassaMsg():
    def __init__(self):
        """
        Trassa msg class covers not a msg
        but a set of messages that used in tests.
        It should be able to define what type of the
        message comes from the test data storage
        and
        form a "sendable message" and store data for futher comparison
        where applicable

        :param SonataSendReceiveProperties:
        """
        '''
        LETS NOT DO ANYTHING WITHOUT PROPER LOGGER
        '''
        self.logger = logging.getLogger(__name__)

        '''
        TRASSA message types
        '''
        nmea    = None
        ais_01  = None
        ais_05  = None
        ais_18  = None
        ais_24_a = None
        ais_24_b = None
        aialr   = None
        '''
        Message data 
        '''
        self.fields_data = {}
        '''
        MAP to store message fields` data
        and message to be sent
        '''
        self.mapped_fields = {}
        return

    def set_values_from_json_map(self,
                                 test_data):
        """
        First things first.
        Hygiene.
        Cleanup.
        :return:
        """
        self.reset_fields()
        '''
        Sonata message fields
        '''

        '''
        Find out test conditions
        '''
        test_type = test_data["test_conditions"]
        if "pass" in test_type.keys():
            test_type="pass"
        else:
            test_type="fail"

        '''
        Find out what kind of message 
        from the required list
        should be formed        
        '''
        message_type_str = test_data["msg_type"]

        '''
        TODO:
        Lets look for substrings in the type
        so naming is flexible  
        '''
        if "ais_type01" == message_type_str:
            test_data = [1,2,3]
            test_msg = "Ps,d,d,d,d"
            return (test_msg,test_data,test_type)
        elif "ais_type05" == message_type_str:
            test_data = [1, 2, 3]
            test_msg = "Ps,d,d,d,d"
            return (test_msg,test_data, test_type)
        elif "ais_type18" == message_type_str:
            test_data = [1, 2, 3]
            test_msg = "Ps,d,d,d,d"
            return (test_msg,test_data, test_type)
        elif "ais_type24a" == message_type_str:
            test_data = [1, 2, 3]
            test_msg = "Ps,d,d,d,d"
            return (test_msg,test_data, test_type)
        elif "ais_type24b" == message_type_str:
            test_data = [1, 2, 3]
            test_msg = "Ps,d,d,d,d"
            return (test_msg,test_data, test_type)
        elif "aitxt" == message_type_str:
            test_data = [1, 2, 3]
            test_msg = "Ps,d,d,d,d"
            return (test_msg,test_data, test_type)
        elif "aialr" == message_type_str:
            test_data = [1, 2, 3]
            test_msg = "Ps,d,d,d,d"
            return (test_msg,test_data, test_type)
        elif "pcmst" == message_type_str:
            test_data = [1, 2, 3]
            test_msg = "Ps,d,d,d,d"
        return (test_msg, test_data, test_type)




        return

    def reset_fields(self):
        """
        Sonata message fields
        """
        nmea = None
        ais_01 = None
        ais_05 = None
        ais_18 = None
        ais_24_a = None
        ais_24_b = None

        return
