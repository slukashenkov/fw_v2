import logging, copy
from test_bl.test_sonata_plugin.configs_sonata import sonata_send_recieve_properties, sonata_suite_config
from test_bl.test_sonata_plugin.test_tools_sonata import sonata_test_parser

class SonataNmeaMsgsContentProcessing:
    def __init__(self,
                 conf=None,
                 data_from=None,
                 data_to=None,
                 data_to_list=None
                 ):

        """
        :param data_from:
        :param data_to:
        """
        '''
        LETS NOT DO ANYTHING WITHOUT PROPER LOGGER
        '''
        if conf == None:
            raise Exception("Test suite config is not provived. \n CAN NOT LOG ANYTHING HERE!")

        else:
            '''
            SetUp logger
            '''
            self.conf = conf
            self.logger = self.conf.logging_tools.get_logger(__name__)

        '''
        SETUP DATA to work on
        '''
        '''
        These are individual packets for comparison
        '''
        self.data_from = data_from
        self.data_to = data_to


        '''
        If there are more packets to be sent let them be in a list 
        '''
        self.data_to_list = data_to_list

        '''
        SETUP PROCESSED DATA 
        Storage  
        '''
        self.data_parsed = None

        '''
        PACKET PROCESSING INSTRUCTIONS
        only index FOR DEMO
        TO DO: clean-up 
        '''
        self.packet_indx = None

        '''
        Keys for comparisons 
        '''
        self.key_sent       = None
        self.key_received   = None

        '''
        TEMP debug  
        Thing!!!
        TODO: here should be processing 
        for all values in all iterables holding
        messages
        playing part in the particular test.
        Both outgoing and incoming.
        '''

        '''
        Initialize parser with data
        to parse
        '''
        self.nmea_parser=sonata_test_parser.SonataTestParser(conf           = self.conf,
                                                             data_from      = self.data_from,
                                                             data_to        = self.data_to
                                                            )

        '''List of parsed maps for bulk parsing'''
        self.nmea_parsed_list = []
        return


    def parse_nmea(self):
        #self.curr_msg = self.data_from[0]
        #self.nmea_parser.data_from = self.curr_msg
        self.nmea_parser.packet_indx = self.packet_indx
        self.data_parsed = self.nmea_parser.parse_from()
        return

    def parse_nmea_auto(self):
        i=0
        while i < self.conf.data_sent_list.__len__():
            self.packet_indx = i
            i = i + 1
            self.parse_nmea()
            self.nmea_parsed_list.append(copy.deepcopy(self.nmea_parser.sonata_nmea_parsed_map))
        return


    def compare_fields_auto(self):
        pass_keys = []
        indx=0
        result = {}
        results_list = []

        while indx < self.conf.data_sent_list.__len__():

            msg=self.conf.data_sent_list[indx]
            if msg["pass"] != "":

                pass_keys = msg["pass"]
                self.nmea_parser.data_to = self.conf.data_sent_list[indx]
                self.nmea_parser.sonata_nmea_parsed_map = self.nmea_parsed_list[indx]
                indx = indx + 1

                for key in pass_keys:

                    self.key_sent = key
                    self.key_received = key

                    if key == "sonata_id":
                        res_sonata_id = self.nmea_parser.compare_fields(sonata_id=key)
                        result[key]=res_sonata_id

                    elif  key == "lat":
                        res_lat = self.nmea_parser.compare_fields(lat=key)
                        result[key] = res_lat

                    elif key == "lon":
                        res_lon = self.nmea_parser.compare_fields(lon=key)
                        result[key] = res_lon

                    elif key == "vel":
                        res_vel = self.nmea_parser.compare_fields(vel=key)
                        result[key] = res_vel

                    elif key == "course":
                        res_course = self.nmea_parser.compare_fields(course=key)
                        result[key] = res_course

                    elif key == "vel_knots":
                        res_vel_knots = self.nmea_parser.compare_fields(vel_knots=key)
                        result[key] = res_vel_knots

                results_list.append(copy.deepcopy(result))

        return results_list

    def get_field_in(self):
        return self.data_parsed[self.key_received]

    def get_field_out(self):
        return self.data_to[self.key_sent]