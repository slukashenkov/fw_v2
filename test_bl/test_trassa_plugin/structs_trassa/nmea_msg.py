from test_bl.test_trassa_plugin.structs_trassa.nmeautils import nmea, nmea_utils
from test_bl.test_trassa_plugin.structs_trassa.nmeautils.types import talker
from test_bl.test_trassa_plugin.structs_trassa.nmeautils.types.proprietary import ais, aid, eis, cms


class NmeaMsg():
    def __init__(self):
        return

    def get_ai(self,
               type,  #can be TXT or ALR
               ai_flds):
        if type == "TXT":
            aitxt_obj = talker.TXT('AI', 'TXT', ai_flds)
            ai_txt_str = aitxt_obj.render()
            return ai_txt_str
        elif type =="ALR":
            aialr_obj = talker.ALR('AI', 'ALR', ai_flds)
            ai_alr_str = aialr_obj.render()
            return ai_alr_str

    def get_aix_alr(self):
        #return str(talker.TXT('AI', 'TXT', ('1', '1', '21', 'External DGNSS in use')))
        return str(talker.ALR('AI', 'ALR', ('133930.40', '01', 'V', 'V', 'Tx malfunction')))


    def get_pc_mst(self,
                   mst_flds):
        #str(talker.MST('PC', 'MST', ('133930.40', 'V')))
        pcmst_obj = cms.CMS('CMS', 'CMST', mst_flds)
        pcmst_str = pcmst_obj.render()
        return pcmst_str

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

    def get_p_eis_t_private(self,
                            peist_fields):
        PEIST_OBJ = eis.EIST('EIS','EIST', peist_fields)

        PEIST_STR = PEIST_OBJ.render()
        return PEIST_STR

    def parse_nmea(self,
                   nmea_msg):
        paisd_obj = nmea.NMEASentence.parse(nmea_msg)
        return paisd_obj

def test_this():
    nmea_msg = NmeaMsg()
    test_nmea = {}

    #STRUCTURES for sending
    aitxt_msg = ('1', '1', '21', 'External DGNSS in use')
    test_nmea['aitxt'] = nmea_msg.get_ai(type ='TXT',
                                         ai_flds = aitxt_msg)
    aitxt_parsed = nmea_msg.parse_nmea(test_nmea['aitxt'])
    sntns_total = aitxt_parsed.sntns_total
    sntns_order_num = aitxt_parsed.sntns_order_num
    stat_code = aitxt_parsed.stat_code
    stat_descr = aitxt_parsed.stat_descr

    # stuct for sending
    aialr_msg = ('133930.40', '01', 'V', 'V', 'Tx malfunction')
    test_nmea['aialr'] = nmea_msg.get_ai(type ='ALR',
                                               ai_flds = aialr_msg)

    aialr_parsed = nmea_msg.parse_nmea(test_nmea['aialr'])
    fail_time  = aialr_parsed.fail_time
    fail_code  = aialr_parsed.fail_code
    fail_stat  = aialr_parsed.fail_stat
    tct_stat   = aialr_parsed.tct_stat
    fail_descr = aialr_parsed.fail_descr

    # stuct for sending
    pcmst_msg = ('133930.40', 'V')
    test_nmea['pcmst'] = nmea_msg.get_pc_mst(mst_flds=pcmst_msg)
    pcmst_parsed        =nmea_msg.parse_nmea(test_nmea['pcmst'])
    pcmst_sntns_tmstmp  = pcmst_parsed.sntns_tmstmp
    pcmst_eq_state      = pcmst_parsed.eq_state



    # STRUCTURES for parsing
    # test creation and conversion into
    #
    # PEIST IMS keepelive msg
    msg_flds = ('142418.00','A')
    test_nmea['peist'] = nmea_msg.get_p_eis_t_private(peist_fields=msg_flds)
    peist_parsed = nmea_msg.parse_nmea(test_nmea['peist'])
    peist_timestamp = peist_parsed.time_stamp
    peist_ims_stat  = peist_parsed.ims_status


    #test_nmea['paisd'] = nmea_msg.get_pa_isd()
    test_nmea['paisd'] = nmea_msg.get_p_ais_d_private()
    paisd_parsed = nmea_msg.parse_nmea(test_nmea['paisd'])
    paisd_mmsi =   paisd_parsed.mmsi
    paisd_imo_num =   paisd_parsed.imo_num
    paisd_c_sign=   paisd_parsed.c_sign
    paisd_v_name=   paisd_parsed.v_name

    #test_nmea['paidd'] = nmea_msg.get_pa_idd()
    test_nmea['paidd'] = nmea_msg.get_p_aid_d_private()
    #test_nmea['paidd']='$PAIDD,1193046,3725.468,N,12209.80,W,101.9,34.5,41.0,061354.00*57'
    paidd_parsed = nmea_msg.parse_nmea(test_nmea['paidd'])
    paidd_mmsi = paidd_parsed.mmsi
    paidd_lon = paidd_parsed.lon
    paidd_hem_n_s =paidd_parsed.hem_n_s
    paidd_lat =paidd_parsed.lat
    paidd_hem_e_w =paidd_parsed.hem_e_w
    paidd_sog =paidd_parsed.sog
    paidd_hdg =paidd_parsed.hdg
    paidd_cog =paidd_parsed.cog
    paidd_tmstmp =paidd_parsed.tmstmp



    '''
    TEST PCMST parsing
    '''
    pcmst_parsed = nmea_msg.parse_nmea(test_nmea['pcmst'])
    sntns_tmstmp = pcmst_parsed.sntns_tmstmp
    eq_state =  pcmst_parsed.eq_state

    for key in test_nmea.keys():
        print("mgs type: " + key + " message_nmea: " + test_nmea[key])

    return

if __name__=="__main__":
    test_this()



