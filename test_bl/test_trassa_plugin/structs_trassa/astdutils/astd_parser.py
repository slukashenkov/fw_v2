import re
from copy import deepcopy


class astd_meta(type):
    def __new__(cls_to_create,
                name_of_the_cr_cls,
                bases,
                attr_dict
                ):
        print('-----------------------------------')
        print("inside meta")
        print( "Allocating memory for class")
        print(name_of_the_cr_cls)
        print(bases)
        print(attr_dict)

        return super(astd_meta, cls_to_create).__new__(cls_to_create,
                                                        name_of_the_cr_cls,
                                                        bases,
                                                        attr_dict)

    def __init__(cls_to_create,
                name_of_the_cr_cls,
                bases,
                attr_dict
                ):
        print('-----------------------------------')
        print("inside meta")
        print("Initializing class")
        print(name_of_the_cr_cls)
        print(bases)
        print(attr_dict)
        super(astd_meta, cls_to_create).__init__(name_of_the_cr_cls,
                                                 bases,
                                                 attr_dict
                                                 )
        cls_to_create.created_classes[name_of_the_cr_cls] = name_of_the_cr_cls
        if 'fields' in attr_dict.keys():
            cls_to_create.classes_fields[name_of_the_cr_cls] = dict((f[1], i) for i, f in enumerate(attr_dict['fields']))

class astd_msgs(object,
                metaclass= astd_meta):
    created_classes={}
    classes_fields={}

    def __init__(self,
                sub_cls = None,
                fields  = None):

        if sub_cls is not None and fields is not None:
            name_sub = type(sub_cls).__name__
            self.created_classes[name_sub]=sub_cls
            self.classes_fields[name_sub] = dict((f[1], i) for i, f in enumerate(sub_cls.fields))

        return

    #@staticmethod
    def parse(self,
              line):

        parsed_data={}

        if type(line) is str:
            astd_fields = line.split('.')
        else:
            raise Exception("Message is not a string")

        message_type=str(astd_fields[1]).lower()
        r_msg_type = re.compile(message_type)

        if message_type in self.created_classes.keys():
            num_of_fields_reg = len(self.classes_fields[message_type]) - 1
            num_of_fields_res = len(astd_fields)
            if num_of_fields_reg == num_of_fields_res:

                for fld_name in self.classes_fields[message_type]:
                    idx = self.classes_fields[message_type][fld_name]
                    parsed_data[fld_name]=astd_fields[idx]

            return parsed_data
        else:
            raise Exception("Message type subclass is not named as deviceId in ASTD message as it MUST")


    def __getattr__(self,
                    name):
        #pylint: disable=invalid-name
        t = type(self)
        try:
            i = t.classes_fields[name]
        except KeyError:
            raise AttributeError(name)
        f = t.fields[i]
        if i < len(self.data):
            v = self.data[i]
        else:
            v = ''
        if len(f) >= 3:
            if v == '':
                return None
            try:
                return f[2](v)
            except:
                return v
        else:
            return v

    def __setattr__(self, name, value):
        #pylint: disable=invalid-name
        t = type(self)
        if name not in t.classes_fields:
            return object.__setattr__(self, name, value)

        i = t.name_to_idx[name]
        self.data[i] = str(value)

class trassa(astd_msgs):
    """
    trassa ASTD message example: S.TRASSA.FE.KD1G
    """
    fields= (
            ('signal_type', 'signal_type'),
            ('device_id', 'device_id'),
            ('network_type', 'network_type'),
            ('kd_id', 'kd_id'),
            ('payload', 'trassa_status'),
        )

class other(astd_msgs):

    fields=(
            ('signal_type', 'other'),
            ('device_id', 'device_id'),
            ('network_type','network_type'),
            ('kd_id', 'kd_id' ),
            ('payload', 'other_msg'),
        )

def test_this():
    astd_msg_g  = 'S.TRASSA.FE.KD1G'
    astd_msg_f  = 'S.TRASSA.FE.KD1F'
    trassa_astd_msgs = astd_msgs()
    trassa_astd_msgs.parse(astd_msg_f)

if __name__=="__main__":
    test_this()

