from mimesis.schema import Field, Schema
from mimesis import Generic
import json

class SonataJsonDataGen():
    def __init__(self,
                 gen_file_dir = 'C:\\data\\kronshtadt\\QA\\BL\\AutomationFrameworkDesign\\bl_frame_work\\test_bl\\test_sonata_plugin\\resources_sonata\\sonata_test_data_gen.json',
                 gen_file_name = 'sonata_gen_data.json',
                 num_of_msgs = 3,
                 seq_num_tcase = 1,
                 test_case_name="test",
                 test_case_msg_id="message"
                 ):

        self.gen_file_dir = gen_file_dir

        if  test_case_name!=None and test_case_msg_id!=None:
                self.test_case_name=test_case_name
                self.test_case_msg_id=test_case_msg_id
        else:
            raise Exception("test case or test message name or both is not provided")

        self.g_provider = Generic('en')

        self.generate_sonata_json(num_of_msgs = num_of_msgs)




    def generate_sonata_json(self,
                             num_of_msgs = 3,
                             seq_num_tcase = 1):

        gt=json_gen_tools(
                            test_case_name = self.test_case_name,
                            test_case_msg_id = self.test_case_msg_id
                        )
        a=1

        sonata_msg_json = lambda: {
                                 lambda: gt.build_test_case_id(
                                                seq_num_tcase
                                                ),

                                lambda:gt.build_test_msg_id(
                                                num_of_msgs),


        }


        self.sonata_schema = Schema(schema=gt.build_sonata_obj())
        sonata_obj = self.sonata_schema.create(iterations=num_of_msgs)
        msgs_lngth = sonata_obj.__len__()
        msg_dict = {}
        for i in sonata_obj:

            name = gt.build_test_msg_id(msgs_lngth)
            msgs_lngth = msgs_lngth - 1
            msg_dict[name] = i


        t_case_dict = {}
        tcase_name = gt.build_test_case_id(seq_num_tcase)
        t_case_dict[tcase_name]  = msg_dict
        sonata_json = json.dumps(t_case_dict)

        with open(self.gen_file_dir, "w") as write_file:
            json.dump(t_case_dict, write_file)

        return t_case_dict

    def generate_msgs_set(self):
        return

    def generate_tcase_set(self):
        return

class json_gen_tools():

    def __init__(self,
                 test_case_name = None,
                 test_case_msg_id = None
                 ):

        if test_case_name != None and test_case_msg_id != None:
            self.test_case_name=test_case_name
            self.test_case_msg_id = test_case_msg_id
        else:
            raise Exception("test case or test message name or both is not provided")

    def build_test_msg_id(self,
                          seq_num=None):
        if seq_num != None:

            if seq_num <= 9:
                id = self.test_case_msg_id + "_0" +  str(seq_num)
            else:
                id = self.test_case_msg_id + "_" + str(seq_num)

        return id

    def build_test_case_id(self,
                          t_suite_num = None):

        if t_suite_num != None:
            if t_suite_num <=9:
                id = self.test_case_name + "_0" + str(t_suite_num)
            else:
                id = self.test_case_name + "_" + str(t_suite_num)
        return id

    def build_sonata_obj(self):
        _ = Field('en')
        sonata_msg_obj = lambda: {"pass": ["sonata_id", "lat", "lon", "vel", "course", "vel_knots" ],
                                    "mtype": _('numbers.between', minimum=0,
                                                                    maximum=3),

                                    "sonata_id": _('numbers.between', minimum=0,
                                                                        maximum=4095),
                                    "lat": {
                                        "deg": _('numbers.between', minimum=0,
                                                                        maximum=127),
                                        "min": _('numbers.between', minimum=0,
                                                                        maximum=127),
                                        "sec": _('numbers.between', minimum=0,
                                                                        maximum=127),
                                        "tens_sec": _('numbers.between', minimum=0,
                                                                            maximum=15)
                                    },

                                    "lon": {
                                        "deg": _('numbers.between', minimum=0,
                                                                        maximum=255),
                                        "min": _('numbers.between', minimum=0,
                                                                        maximum=127),
                                        "sec": _('numbers.between', minimum=0,
                                                                        maximum=127),
                                        "tens_sec": _('numbers.between', minimum=0,
                                                                            maximum=15)
                                    },

                                    "vel": {"hkm_h": _('numbers.between', minimum=0,
                                                                            maximum=7),
                                            "km_h": _('numbers.between', minimum=0,
                                                                            maximum=127)
                                            },

                                    "course": {
                                        "deg": _('numbers.between', minimum=0,
                                                                    maximum=3),
                                        "tens_deg": _('numbers.between', minimum=0,
                                                                            maximum=127)
                                    },

                                    "state": _('numbers.between', minimum=1,
                                                                    maximum=7),
                                    "tail": _('numbers.between', minimum=17,
                                                                    maximum=17),
                                    "signal_lvl": _('numbers.between', minimum=15,
                                                                        maximum=15)
                                }

        return sonata_msg_obj


def test_this():
    import os
    from mimesis.schema import Field, Schema
    from test_bl.test_bl_tools.read_test_data import ReadData

    module_abs_path = os.path.abspath(os.path.dirname(__file__))
    # path_to_data = "..\\test_sonata_plugin\\resources_sonata\\sonata_test_data.json"
    path_to_data = "..\\..\\test_sonata_plugin\\resources_sonata\\sonata_test_data_gen500.json"
    #path_to_data = "..\\..\\test_sonata_plugin\\resources_sonata\\sonata_test_data_gen_over_500.json"
    path_to_data = os.path.join(module_abs_path, path_to_data)



    s_json_gen = SonataJsonDataGen( gen_file_dir = path_to_data,
                                    num_of_msgs = 100,
                                    test_case_name="test_sonata_messages",
                                    test_case_msg_id="msgSonata")

    '''
    rd=ReadData()
    rd.data_location_map = s_json_gen.gen_file_dir
    rd.read_json_to_map()
    '''


if __name__ == '__main__':
    test_this()