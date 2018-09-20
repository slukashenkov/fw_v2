from test_bl.test_trassa_plugin.structs_trassa.nmeautils import nmea
from test_bl.test_trassa_plugin.structs_trassa.nmeautils.types import talker

class AiAlrm():
    def __init__(self):
        test_nmea = {}
        #stuct for sending
        test_nmea['aitxt'] = str(talker.TXT('AI','TXT', ('1','1','21','External DGNSS in use')))
        test_nmea['aialr'] = str(talker.ALR('AI','ALR', ('1','1','01','V','V','Tx malfunction')))
        test_nmea['pcmst'] = str(talker.ALR('PC','MST', ('095530.09','A')))

        #For parsing
        test_nmea['paisd'] = str(talker.ISD('PA', 'ISD', ('8989999', '001100', 'Vsl_cl_sgn', 'Vsl_name')))
        test_nmea['paidd'] = str(talker.IDD('PA', 'IDD', ('7776666', '89.5', 'N', '67.0','E', '67', '30.7','32.5','111430.07')))

        for key in test_nmea.keys():
            print("mgs type: "+key+" message_nmea: "+test_nmea[key])
        return

    def set_values_from_map(self):
        return

def test_this():
    ai_alr = AiAlrm()

if __name__=="__main__":
    test_this()



