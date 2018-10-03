import logging, math, re, enum
import os.path

from test_bl.test_bl_tools.scan_logs import ScanLogs
from test_bl.test_trassa_plugin.structs_trassa import nmea_msg, ais_msg, astd_msg

class trassa_msg_types(enum.Enum):
                        PAIDD = 1
                        PAISD = 2
                        AITXT = 3
                        AIALR = 4
                        PEIST = 5
                        ASTD  = 6

class TrassaTestParser():

    def __init__(self,
                 data_from = None,
                 data_to   = None):
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
        self.regex_dict ={}
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
                                      ''',re.X | re.IGNORECASE)
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
                                      ''',re.X | re.IGNORECASE)
        self.regex_dict[trassa_msg_types.AIALR] = self.aialr_regex

        '''
        PCMST msg
        '$PCMST,133930.40,V*2E'
        '''
        self.peist_regex = re.compile(r'''
                                      ^.*PEIST.*
                                      ''',re.X | re.IGNORECASE)
        self.regex_dict[trassa_msg_types.PEIST] = self.peist_regex

        self.logger.debug("TRASSA Parser is SET")

        '''
        Helper classes that do actual parsing 
        '''
        self.nmea_msg_helper = nmea_msg.NmeaMsg()
        self.astd_msg_helper = astd_msg.AstdMsg()

    def parse_from(self):
        """
        :return:
        """
        self.trassa_data_parsed_map.clear()
        '''
        GET PARTICULAR PAKET
        by index
        '''
        try:
            self.data_from[self.packet_indx]
        except IndexError:
            self.logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.logger.info("No RETURN packet FOUND at the index: "+ str(self.packet_indx) + " IN THE DATA_FROM STRUCTURE")
            self.logger.info("BL/MUSSON CAN BE DOWN AT THE MOMENT")
            self.logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            raise Exception("NO PACKETS GOTTEN FROM BL FOR PROCESSING. So IT SEEMS.")

        data_to_parse = self.data_from[self.packet_indx]

        '''NB! VERY IMPORTANT ADDITION'''
        '''BEFORE CONVERSION INTO DESIRED '''
        data_to_parse = str(data_to_parse.decode())
        m_type = self.msg_type(data_to_parse)
        '''
        Get structures for different
        msg types  
        '''
        if m_type == trassa_msg_types.PAIDD:
            '''
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
            paidd_parsed = self.nmea_msg_helper.parse_nmea(nmea_msg=data_to_parse)
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

        elif m_type  == trassa_msg_types.PAISD:
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
            paisd_parsed = self.nmea_msg_helper.parse_nmea(nmea_msg=data_to_parse)
            self.trassa_data_parsed_map["MMSI"] = paisd_parsed.mmsi
            self.trassa_data_parsed_map["IMOnumber"] = paisd_parsed.imo_num
            self.trassa_data_parsed_map["callsign"] = paisd_parsed.c_sign
            self.trassa_data_parsed_map["name"] = paisd_parsed.v_name
            return self.trassa_data_parsed_map

        elif m_type  == trassa_msg_types.PEIST:
            peist_map = self.nmea_msg_helper.parse_nmea(data_to_parse)

            return self.trassa_data_parsed_map

        elif m_type  == trassa_msg_types.AITXT:
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

        elif m_type  == trassa_msg_types.AIALR:
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


    def msg_type(self,
                 data_to_parse):
        msg_type = None
        for key in self.regex_dict:
            curr_regex = self.regex_dict[key]
            result = curr_regex.match(data_to_parse)
            if result:
                 return key

    def compare_fields(self,
                       msg_data_sent,
                       msg_data_received=None):
        """
        :param msg_data_sent: data gathered at the time when packet is formed
        :param msg_data_received: data gathered fro SUT in UDP server
        :return:
        """
        comparison_results = {}
        if msg_data_received == None and "fail" in msg_data_sent.keys():
            pattern_to_search = msg_data_sent["fail"]
            self.parse_log(pattern_to_search)
            return comparison_results
        elif msg_data_received != None and "pass" in msg_data_sent.keys():
            self.trassa_data_parsed_map = msg_data_received
            self.data_to = msg_data_sent
            keys = msg_data_sent["pass"]
            for key in keys:
                comparison_results[key] = self.__do_comparison(key)
            return comparison_results