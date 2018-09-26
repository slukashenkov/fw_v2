from copy import deepcopy


class common_meta(type):

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

        return super(common_meta, cls_to_create).__new__(cls_to_create,
        name_of_the_cr_cls,
        bases,
        attr_dict)

    def init(cls_to_create,
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
        super(common_meta, cls_to_create).__init__(name_of_the_cr_cls,
        bases,
        attr_dict
        )

        cls_to_create.classes_fields[name_of_the_cr_cls] = name_of_the_cr_cls

class commonBaseCls(object, metaclass= common_meta):
    head=True
    created_classes={}
    classes_fields={}
    def __init__(self,
            cls,
            filelds):
        self.filelds = filelds
        name_sub=type(cls).__name__
        self.classes_fields[name_sub]=filelds
        self.created_classes[name_sub]=cls
        pass

class individTypeFields(commonBaseCls):
    head = False
    def __init__(self):
        self.fields={}
        self.fields['f1']='text 01'
        self.fields['f2'] = 'text 02'
        super().__init__(self,
                        self.fields)


class individTypeFields02(commonBaseCls):
    head = False
    def __init__(self):

        self.fields={}
        self.fields['f1_02']='text 01'
        self.fields['f2_02'] = 'text 02'
        super().__init__(self,
        self.fields)


if __name__=="__main__":

    in_fld = individTypeFields()
    in_fld = individTypeFields02()
    a=1
    #cbl=commonBaseCls()