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
        cls_to_create.classes_fields[name_of_the_cr_cls] = name_of_the_cr_cls

class astd_msgs(object, metaclass= astd_meta):
    head=True
    created_classes={}
    classes_fields={}

    def __init__(self,
                sub_cls,
                filelds):

        self.filelds = filelds
        name_sub=type(sub_cls).__name__

        self.created_classes[name_sub]=sub_cls
        self.classes_fields[name_sub] = dict((f[1], i) for i, f in enumerate(sub_cls.fields))
        pass

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

class trassa_astd_fields(astd_msgs):
    """
    trassa ASTD message example: S.TRASSA.FE.KD1G
    """
    head = False
    def __init__(self):

        self.fields= (
            ('signal_type', 'signal_type'),
            ('device_id', 'device_id'),
            ('network_type', 'network_type'),
            ('kd_id', 'kd_id'),
            ('payload', 'trassa_status'),
        )

        super().__init__(self,
                         self.fields)



class other_astd_fields(astd_msgs):
    head = False
    def __init__(self
                    ):

        self.fields=(
            ('signal_type', 'signal_type'),
            ('device_id', 'device_id'),
            ('network_type','network_type'),
            ('kd_id', 'kd_id' ),
            ('payload', 'other_msg'),
        )
        self.srch_patterns = {}
        message_re = re.compile(r'''
               # start of string, optional whitespace, optional '$'
               ^\s*\$?

               # message (from '$' or start to checksum or end, non-inclusve)
               (?P<nmea_str>
                   # sentence type identifier
                   (?P<sentence_type>

                       # proprietary sentence
                       (P\w{3,},)|

                       # query sentence, ie: 'CCGPQ,GGA'
                       # NOTE: this should have no data
                       (\w{2}\w{2}Q,\w{3})|

                       # taker sentence, ie: 'GPGGA'
                       (\w{2}\w{3})
                   ),    
                   # rest of message
                   (?P<data>[^*]*)

               )
               # checksum: *HH
               (?:[*](?P<checksum>[A-F0-9]{2}))?

               # optional trailing whitespace
               \s*[\r\n]*$
               ''', re.X | re.IGNORECASE)

        self.srch_patterns['message_lvl'] = message_re

        super().__init__(self,
                        self.fields)


if __name__=="__main__":

    in_fld = trassa_astd_fields()
    in_fld = other_astd_fields()
    a=1
    #cbl=commonBaseCls()
