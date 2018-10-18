# from binascii import a2b_qp
import copy
import logging

from test_bl.test_trassa_plugin.structs_trassa import ais_msg
from test_bl.test_trassa_plugin.structs_trassa.nmea_msg import NmeaMsg


class TrassaMsg():
    
    
    def __init__ (self):
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
        self.ais_msgs = ais_msg.AisMsg()
        self.nmea_msgs = NmeaMsg()
        
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
    
    
    def set_values_from_json_map (self,
                                  test_data):
        """
        First things first.
        Hygiene.
        Cleanup.
        :return:
        """
        self.reset_fields()
        '''
        Trassa message types
        '''
        
        '''
        Find out test conditions
        '''
        test_type_dict = test_data["test_conditions"]
        if "pass" in test_type_dict.keys():
            test_type = "pass"
        elif "fail" in test_type_dict.keys():
            test_type = "fail"
        elif "no_msg_sent" in test_type_dict.keys():
            test_type = "no_msg_sent"
        
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
            # stuct for sending
            msg01 = {}
            msg01['MessageID'] = test_data['fields']['MessageID']
            msg01['RepeatIndicator'] = test_data['fields']['RepeatIndicator']
            msg01['MMSI'] = test_data['fields']['MMSI']
            msg01['NavigationStatus'] = test_data['fields']['NavigationStatus']
            msg01['ROT'] = test_data['fields']['ROT']
            msg01['SOG'] = test_data['fields']['SOG']
            msg01['PositionAccuracy'] = test_data['fields']['PositionAccuracy']
            msg01['longitude'] = test_data['fields']['longitude']
            msg01['latitude'] = test_data['fields']['latitude']
            msg01['COG'] = test_data['fields']['COG']
            msg01['TrueHeading'] = test_data['fields']['TrueHeading']
            msg01['TimeStamp'] = test_data['fields']['TimeStamp']
            msg01['RegionalReserved'] = test_data['fields']['RegionalReserved']
            msg01['Spare'] = test_data['fields']['Spare']
            msg01['RAIM'] = test_data['fields']['RAIM']
            # This is SOTDMA communication state fields
            # 19 bites long in type 18
            # 1 field comes before for communication state
            # type choice
            msg01['state_syncstate'] = test_data['fields']['state_syncstate']
            msg01['state_slottimeout'] = test_data['fields']['state_slottimeout']
            msg01['state_slotoffset'] = test_data['fields']['state_slotoffset']
            
            test_msg = self.ais_msgs.get_type_1(msg01)
            t_data = copy.deepcopy(test_data)
            return (test_msg,
                    t_data,
                    test_type)
        
        elif "ais_type05" == message_type_str:
            # stuct for sending
            msg05 = {}
            msg05['MessageID'] = test_data['fields']['MessageID']
            msg05['RepeatIndicator'] = test_data['fields']['RepeatIndicator']
            msg05['MMSI'] = test_data['fields']['MMSI']
            msg05['AISversion'] = test_data['fields']['AISversion']
            msg05['IMOnumber'] = test_data['fields']['IMOnumber']
            msg05['callsign'] = test_data['fields']['callsign']
            msg05['name'] = test_data['fields']['name']
            msg05['shipandcargo'] = test_data['fields']['shipandcargo']
            msg05['dimA'] = test_data['fields']['dimA']
            msg05['dimB'] = test_data['fields']['dimB']
            msg05['dimC'] = test_data['fields']['dimC']
            msg05['dimD'] = test_data['fields']['dimD']
            msg05['fixtype'] = test_data['fields']['fixtype']
            msg05['ETAmonth'] = test_data['fields']['ETAmonth']
            msg05['ETAday'] = test_data['fields']['ETAday']
            msg05['ETAhour'] = test_data['fields']['ETAhour']
            msg05['ETAminute'] = test_data['fields']['ETAminute']
            msg05['draught'] = test_data['fields']['draught']
            msg05['destination'] = test_data['fields']['destination']
            msg05['dte'] = test_data['fields']['dte']
            msg05['Spare'] = test_data['fields']['Spare']
            
            test_msg = self.ais_msgs.get_type_5(msg05)
            t_data = copy.deepcopy(test_data)
            return (test_msg,
                    t_data,
                    test_type)
        
        elif "ais_type18" == message_type_str:
            msg18 = {}
            msg18['MessageID'] = test_data['fields']['MessageID']
            msg18['RepeatIndicator'] = test_data['fields']['RepeatIndicator']
            msg18['MMSI'] = test_data['fields']['MMSI']
            msg18['SOG'] = test_data['fields']['SOG']
            msg18['PositionAccuracy'] = test_data['fields']['PositionAccuracy']
            msg18['longitude'] = test_data['fields']['longitude']
            msg18['latitude'] = test_data['fields']['latitude']
            msg18['COG'] = test_data['fields']['COG']
            msg18['TrueHeading'] = test_data['fields']['TrueHeading']
            msg18['TimeStamp'] = test_data['fields']['TimeStamp']
            msg18['Spare'] = test_data['fields']['Spare']
            msg18['cs_unit'] = test_data['fields']['cs_unit']
            msg18['display_flag'] = test_data['fields']['display_flag']
            msg18['dsc_flag'] = test_data['fields']['dsc_flag']
            msg18['band_flag'] = test_data['fields']['band_flag']
            msg18['msg22_flag'] = test_data['fields']['msg22_flag']
            msg18['mode_flag'] = test_data['fields']['mode_flag']
            msg18['RAIM'] = test_data['fields']['RAIM']
            # CommStateSelector 0 = SOTDMA
            ##CommStateSelector 1 = ITDMA
            msg18['CommStateSelector'] = test_data['fields']['CommStateSelector']
            # This state is ought to be filled
            # in full according tospecs
            #
            # This field can be SOTDMA or ITDMA communication state
            # 20 bites long
            # msg18['CommState'] = 0
            # What follows is SOTDMA communication state
            msg18['state_syncstate'] = test_data['fields']['state_syncstate']
            msg18['state_slottimeout'] = test_data['fields']['state_slottimeout']
            msg18['state_slotoffset'] = test_data['fields']['state_slotoffset']
            
            test_msg = self.ais_msgs.get_type_18(msg18)
            t_data = copy.deepcopy(test_data)
            return (test_msg,
                    t_data,
                    test_type)
        
        elif "ais_type24a" == message_type_str:
            msg24_a = {}
            msg24_a['MessageID'] = test_data['fields']['MessageID']
            msg24_a['RepeatIndicator'] = test_data['fields']['RepeatIndicator']
            msg24_a['MMSI'] = test_data['fields']['MMSI']
            
            test_msg = self.ais_msgs.get_type_24(type = "A",
                                                 msg24 = msg24_a)
            t_data = copy.deepcopy(test_data)
            return (test_msg,
                    t_data,
                    test_type)
        
        elif "ais_type24b" == message_type_str:
            msg24_b = {}
            msg24_b['MessageID'] = test_data['fields']['MessageID']
            msg24_b['RepeatIndicator'] = test_data['fields']['RepeatIndicator']
            msg24_b['MMSI'] = test_data['fields']['MMSI']
            msg24_b['shipandcargo'] = test_data['fields']['shipandcargo']
            
            msg24_b['vendor_id'] = test_data['fields']['vendor_id']
            msg24_b['unit_model'] = test_data['fields']['unit_model']
            msg24_b['serial_num'] = test_data['fields']['serial_num']
            msg24_b['callsign'] = test_data['fields']['callsign']
            msg24_b['name'] = test_data['fields']['name']
            
            msg24_b['dimA'] = test_data['fields']['dimA']
            msg24_b['dimB'] = test_data['fields']['dimB']
            msg24_b['dimC'] = test_data['fields']['dimC']
            msg24_b['dimD'] = test_data['fields']['dimD']
            msg24_b['Spare'] = test_data['fields']['Spare']
            
            test_msg = self.ais_msgs.get_type_24(type = "B",
                                                 msg24 = msg24_b)
            t_data = copy.deepcopy(test_data)
            return (test_msg,
                    t_data,
                    test_type)
        
        elif "aitxt" == message_type_str:
            msg_aitxt = (test_data['fields']['sntns_total'],
                         test_data['fields']['sntns_order_num'],
                         test_data['fields']['stat_code'],
                         test_data['fields']['stat_descr'])
            
            test_msg = self.nmea_msgs.get_ai(type = 'TXT',
                                             ai_flds = msg_aitxt)
            t_data = copy.deepcopy(test_data)
            return (test_msg,
                    t_data,
                    test_type)
        elif "aialr" == message_type_str:
            
            msg_aialr = (test_data['fields']['fail_time'],
                         test_data['fields']['fail_code'],
                         test_data['fields']['fail_stat'],
                         test_data['fields']['tct_stat'],
                         test_data['fields']['fail_descr'])
            
            test_msg = self.nmea_msgs.get_ai(type = 'ALR',
                                             ai_flds = msg_aialr)
            t_data = copy.deepcopy(test_data)
            return (test_msg,
                    t_data,
                    test_type)
        
        elif "pcmst" == message_type_str:
            
            msg_pcmst = (test_data['fields']['sntns_tmstmp'],
                         test_data['fields']['eq_state'])
            test_msg = self.nmea_msgs.get_pc_mst(mst_flds = msg_pcmst)
            t_data = copy.deepcopy(test_data)
            return (test_msg,
                    t_data,
                    test_type)
        elif "peist" == message_type_str:
            msg_peist = (test_data['fields']['time_stamp'],
                         test_data['fields']['ims_status']
                         )
            test_msg = self.nmea_msgs.get_p_eis_t_private(peist_fields = msg_peist)
            
            t_data = copy.deepcopy(test_data)
            return (test_msg,
                    t_data,
                    test_type)
        return
    
    
    def reset_fields (self):
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
