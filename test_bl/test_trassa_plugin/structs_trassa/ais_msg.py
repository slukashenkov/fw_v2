from decimal import Decimal

from test_bl.test_trassa_plugin.structs_trassa.aisutils import uscg
from test_bl.test_trassa_plugin.structs_trassa.aisutils.types import ais_msg_1, ais_msg_18, ais_msg_24, ais_msg_5


class AisMsg():
    
    
    def __init__ (self):
        return
    
    
    def get_type_1 (self,
                    msg01):
        
        bits = ais_msg_1.encode(msg01)
        nmea = uscg.create_nmea(bits,
                                message_type = 1)
        return nmea
    
    
    def get_type_18 (self,
                     msg18):
        bits = ais_msg_18.encode(msg18)
        nmea = uscg.create_nmea(bits,
                                message_type = 18)
        return nmea
    
    
    def get_type_5 (self,
                    msg05):
        
        bits = ais_msg_5.encode(msg05)
        nmea = list(uscg.create_nmea(bits,
                                     message_type = 5))
        
        return nmea
    
    
    def get_type_24 (self,
                     type,  # Can be B and aux. A and B should be tested aux was done just in case
                     msg24
                     ):
        
        if type == 'A':
            bits_a = ais_msg_24.encode(type = "A",
                                       params = msg24)
            nmea_a = uscg.create_nmea(bits_a,
                                      message_type = 24,
                                      aisChannel = "A")
            return nmea_a
        elif type == 'B':
            bits_b = ais_msg_24.encode(type = "B",
                                       params = msg24
                                       )
            nmea_b = uscg.create_nmea(bits_b,
                                      message_type = 24,
                                      aisChannel = "B")
            return nmea_b
        elif type == 'aux':
            bits_aux = ais_msg_24.encode(type = "aux",
                                         params = msg24)
            nmea_aux = uscg.create_nmea(bits_aux,
                                        message_type = 24,
                                        aisChannel = "B")
            return nmea_aux


def test_this ():
    ais_msg = AisMsg()
    test_ais = {}
    
    # stuct for sending
    msg01 = {}
    msg01['MessageID'] = 1
    msg01['RepeatIndicator'] = 1
    msg01['MMSI'] = 1193046
    msg01['NavigationStatus'] = 3
    msg01['ROT'] = -2
    msg01['SOG'] = Decimal('101.9')
    msg01['PositionAccuracy'] = 1
    msg01['longitude'] = Decimal('-122.16328055555556')
    msg01['latitude'] = Decimal('37.424458333333334')
    msg01['COG'] = Decimal('34.5')
    msg01['TrueHeading'] = 41
    msg01['TimeStamp'] = 35
    msg01['RegionalReserved'] = 0
    msg01['Spare'] = 0
    msg01['RAIM'] = False
    # This is SOTDMA communication state fields
    # 19 bites long in type 18
    # 1 field comes before for communication state
    # type choice
    msg01['state_syncstate'] = 2
    msg01['state_slottimeout'] = 0
    msg01['state_slotoffset'] = 1221
    
    test_ais['type_1'] = ais_msg.get_type_1(msg01)
    
    # stuct for sending
    msg05 = {}
    msg05['MessageID'] = 5
    msg05['RepeatIndicator'] = 1
    msg05['MMSI'] = 1193046
    msg05['AISversion'] = 0
    msg05['IMOnumber'] = 3210
    msg05['callsign'] = 'PIRATE1'
    msg05['name'] = 'SDRTYSDRTYSDRTYSDRTY'
    msg05['shipandcargo'] = 21
    msg05['dimA'] = 10
    msg05['dimB'] = 11
    msg05['dimC'] = 12
    msg05['dimD'] = 13
    msg05['fixtype'] = 1
    msg05['ETAmonth'] = 2
    msg05['ETAday'] = 28
    msg05['ETAhour'] = 9
    msg05['ETAminute'] = 54
    msg05['draught'] = Decimal('21.1')
    msg05['destination'] = 'NOWHERE@@@@@@@@@@@@@'
    msg05['dte'] = 0
    msg05['Spare'] = 0
    
    test_ais['type_5'] = ais_msg.get_type_5(msg05)
    
    # stuct for sending
    msg18 = {}
    msg18['MessageID'] = 18
    msg18['RepeatIndicator'] = 1
    msg18['MMSI'] = 1193046
    msg18['SOG'] = Decimal('101.9')
    msg18['PositionAccuracy'] = 1
    msg18['longitude'] = Decimal('-122.16328055555556')
    msg18['latitude'] = Decimal('37.424458333333334')
    msg18['COG'] = Decimal('34.5')
    msg18['TrueHeading'] = 41
    msg18['TimeStamp'] = 35
    msg18['Spare'] = 0
    msg18['cs_unit'] = False
    msg18['display_flag'] = False
    msg18['dsc_flag'] = False
    msg18['band_flag'] = False
    msg18['msg22_flag'] = False
    msg18['mode_flag'] = False
    msg18['RAIM'] = False
    # CommStateSelector 0 = SOTDMA
    ##CommStateSelector 1 = ITDMA
    msg18['CommStateSelector'] = 0
    # This state is ought to be filled
    # in full according tospecs
    #
    # This field can be SOTDMA or ITDMA communication state
    # 20 bites long
    # msg18['CommState'] = 0
    # What follows is SOTDMA communication state
    msg18['state_syncstate'] = 2
    msg18['state_slottimeout'] = 0
    msg18['state_slotoffset'] = 1221
    
    test_ais['type_18'] = ais_msg.get_type_18(msg18)
    
    # stuct for sending
    # -----------------------------------
    msg24_a = {}
    msg24_a['MessageID'] = 24
    msg24_a['RepeatIndicator'] = 1
    msg24_a['MMSI'] = 5678844
    
    # -----------------------------------
    test_ais['type_24_a'] = ais_msg.get_type_24(type = "A",
                                                msg_24 = msg24_a)
    
    # stuct for sending
    # -----------------------------------
    msg24_b = {}
    msg24_b['MessageID'] = 24
    msg24_b['RepeatIndicator'] = 1
    msg24_b['MMSI'] = 119304633
    msg24_b['shipandcargo'] = 55
    
    msg24_b['vendor_id'] = "VND"
    msg24_b['unit_model'] = 1
    msg24_b['serial_num'] = 2
    msg24_b['callsign'] = 'FGRTUSP'
    msg24_b['name'] = 'PTYDRPTYDRTFGRDTFGRD'
    
    msg24_b['dimA'] = 10
    msg24_b['dimB'] = 11
    msg24_b['dimC'] = 12
    msg24_b['dimD'] = 13
    
    # msg24_b['mother_ship_mmsi'] = 0
    msg24_b['Spare'] = 0
    # -----------------------------------
    test_ais['type24_b'] = ais_msg.get_type_24(type = "B",
                                               msg_24 = msg24_b
                                               )
    
    # stuct for sending
    msg24_aux = {}
    
    msg24_aux['MessageID'] = 24
    msg24_aux['RepeatIndicator'] = 1
    msg24_aux['MMSI'] = 982031010
    msg24_aux['shipandcargo'] = 55
    msg24_aux['vendor_id'] = "VND"
    msg24_aux['unit_model'] = 1
    msg24_aux['serial_num'] = 2
    msg24_aux['callsign'] = 'FGRTUSP'
    msg24_aux['name'] = 'PTYDRPTYDRTFGRDTFGRD'
    
    msg24_aux['mother_ship_mmsi'] = 12039567
    msg24_aux['Spare'] = 0
    test_ais['type24_aux'] = ais_msg.get_type_24(msg_24 = msg24_aux,
                                                 type = "aux")
    
    for key in test_ais.keys():
        print("mgs type: " + key + " message_nmea: " + str(test_ais[key]))
    return


if __name__ == "__main__":
    test_this()
