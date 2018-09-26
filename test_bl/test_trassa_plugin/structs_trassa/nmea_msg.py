from test_bl.test_trassa_plugin.structs_trassa.nmeautils import nmea, nmea_utils
from test_bl.test_trassa_plugin.structs_trassa.nmeautils.types import talker
from test_bl.test_trassa_plugin.structs_trassa.nmeautils.types.proprietary import ais
from test_bl.test_trassa_plugin.structs_trassa.nmeautils.types.proprietary import aid

class NmeaMsg():
    def __init__(self):
        return

    def get_aix_txt(self):
        return str(talker.TXT('AI', 'TXT', ('1', '1', '21', 'External DGNSS in use')))

    def get_aix_alr(self):
        return str(talker.ALR('AI', 'ALR', ('1', '1', '01', 'V', 'V', 'Tx malfunction')))

    def get_pc_mst(self):
        timestamp = nmea_utils.timestamp('133930.40')
        return str(talker.MST('PC', 'MST', ('133930.40', 'V')))

    def get_pa_isd(self):
        return str(talker.ISD('PA', 'ISD', ('8989999', '001100', 'Vsl_cl_sgn', 'Vsl_name')))

    def get_pa_idd(self):

        return str(talker.IDD('PA', 'IDD', ('7776666', '89.5', 'N', '67.0', 'E', '67', '30.7', '32.5', '111430.07')))


    def get_p_ais_d_private(self):
        PAISD_obj=ais.AISD('AIS','AISD',('8989999',
                                           '001100',
                                           'Vsl_cl_sgn',
                                           'Vsl_name')
                           )
        PAISD_str = PAISD_obj.render()
        return PAISD_str

    def get_p_aid_d_private(self):
        PAIDD_OBJ = aid.AIDD('AID','AIDD',('7776666',
                                    '89.5',
                                    'N',
                                    '67.0',
                                    'E',
                                    '67',
                                    '30.7',
                                    '32.5',
                                    '111430.07')
                         )
        PAIDD_STR = PAIDD_OBJ.render()

        return PAIDD_STR

    def parse_paisd(self,
                    nmea_msg):
        paisd_obj = nmea.NMEASentence.parse(nmea_msg)



        return paisd_obj
def test_this():
    nmea_msg = NmeaMsg()
    test_nmea = {}

    # stuct for sending
    test_nmea['aitxt'] = nmea_msg.get_aix_txt()
    test_nmea['aialr'] = nmea_msg.get_aix_alr()
    test_nmea['pcmst'] = nmea_msg.get_pc_mst()



    # stuct for parsing
    #test_nmea['paidd'] = nmea_msg.get_pa_idd()
    test_nmea['paidd'] = nmea_msg.get_p_aid_d_private()

    #test_nmea['paisd'] = nmea_msg.get_pa_isd()
    test_nmea['paisd'] = nmea_msg.get_p_ais_d_private()
    paisd_parsed = nmea_msg.parse_paisd(test_nmea['paisd'])
    paisd_mmsi =   paisd_parsed.mmsi
    paisd_imo_num =   paisd_parsed.imo_num
    paisd_c_sign=   paisd_parsed.c_sign
    paisd_v_name=   paisd_parsed.v_name

    #test_nmea['paidd']='$PAIDD,1193046,3725.468,N,12209.80,W,101.9,34.5,41.0,061354.00*57'
    paidd_parsed = nmea_msg.parse_paisd(test_nmea['paidd'])
    paidd_mmsi = paidd_parsed.mmsi
    paidd_lon = paidd_parsed.lon
    paidd_hem_n_s =paidd_parsed.hem_n_s
    paidd_lat =paidd_parsed.lat
    paidd_hem_e_w =paidd_parsed.hem_e_w
    paidd_sog =paidd_parsed.sog
    paidd_hdg =paidd_parsed.hdg
    paidd_cog =paidd_parsed.cog
    paidd_tmstmp =paidd_parsed.tmstmp



    aitxt_parsed = nmea_msg.parse_paisd(test_nmea['aitxt'])
    sntns_total = aitxt_parsed.sntns_total
    sntns_order_num = aitxt_parsed.sntns_order_num
    stat_code = aitxt_parsed.stat_code
    stat_descr = aitxt_parsed.stat_descr

    aialr_parsed = nmea_msg.parse_paisd(test_nmea['aialr'])
    fail_time  = aialr_parsed.fail_time
    fail_code  = aialr_parsed.fail_code
    fail_stat  = aialr_parsed.fail_stat
    tct_stat   = aialr_parsed.tct_stat
    fail_descr = aialr_parsed.fail_descr


    pcmst_parsed = nmea_msg.parse_paisd(test_nmea['pcmst'])
    sntns_tmstmp = pcmst_parsed.sntns_tmstmp
    eq_state =  pcmst_parsed.eq_state

    for key in test_nmea.keys():
        print("mgs type: " + key + " message_nmea: " + test_nmea[key])

    return

if __name__=="__main__":
    test_this()



