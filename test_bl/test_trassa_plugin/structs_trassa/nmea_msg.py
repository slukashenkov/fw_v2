from test_bl.test_trassa_plugin.structs_trassa.nmeautils import nmea
from test_bl.test_trassa_plugin.structs_trassa.nmeautils.types import talker

class NmeaMsg():
    def __init__(self):
        return

    def get_aix_txt(self):
        return str(talker.TXT('AI', 'TXT', ('1', '1', '21', 'External DGNSS in use')))

    def get_aix_alr(self):
        return str(talker.ALR('AI', 'ALR', ('1', '1', '01', 'V', 'V', 'Tx malfunction')))
    def get_pc_mst(self):
        return str(talker.ALR('PC', 'MST', ('095530.09', 'A')))

    def get_pa_isd(self):
        return str(talker.ISD('PA', 'ISD', ('8989999', '001100', 'Vsl_cl_sgn', 'Vsl_name')))

    def get_pa_idd(self):
        return str(talker.IDD('PA', 'IDD', ('7776666', '89.5', 'N', '67.0', 'E', '67', '30.7', '32.5', '111430.07')))

def test_this():
    nmea_msg = NmeaMsg()
    test_nmea = {}

    # stuct for sending
    test_nmea['aitxt'] = nmea_msg.get_aix_txt()
    test_nmea['aialr'] = nmea_msg.get_aix_alr()
    test_nmea['pcmst'] = nmea_msg.get_pc_mst()

    # For parsing
    test_nmea['paisd'] = nmea_msg.get_pa_isd()
    test_nmea['paidd'] = nmea_msg.get_pa_idd()

    for key in test_nmea.keys():
        print("mgs type: " + key + " message_nmea: " + test_nmea[key])
    return

if __name__=="__main__":
    test_this()



