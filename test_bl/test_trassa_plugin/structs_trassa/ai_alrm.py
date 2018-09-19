from test_bl.test_trassa_plugin.structs_trassa.nmeautils import nmea
from test_bl.test_trassa_plugin.structs_trassa.nmeautils.types import talker

class AiAlrm():
    def __init__(self):
        self.text_msg = talker.TXT('AI','TXT', ('1','1','21','External DGNSS in use'))
        print(str(self.text_msg))
        return

    def set_values_from_map(self):
        return

def test_this():
    ai_alr = AiAlrm()

if __name__=="__main__":
    test_this()



