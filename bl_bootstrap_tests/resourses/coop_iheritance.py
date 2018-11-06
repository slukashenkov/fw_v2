class c_1:
    def __new__(cls,
                arg1=None,
                arg2=None):
        
        cls=super().__new__(cls)
        cls.arg01 = arg1
        cls.arg02 = arg2
        
        return cls
    
    def __init__(self):
        pass
        
    def p_name(self):
        print("root class c_1")
        

class c_2(c_1):
    def p_name(self):
        print("1 level class c_2")
        super(c_2, self).p_name()
        
class c_3(c_1):
    def p_name (self):
        print("1 level class c_3")
        super(c_3, self).p_name()

class c_4(c_3, c_2):
    def __new__(cls):
        
        cls=super().__new__(cls, arg1=77, arg2=55)
        cls.arg04 = 78
        return cls
        
    def __init__(self):
        self.arg03 = 9
        pass
    
    def p_name (self):
        print("2nd level class c_4")
        super(c_4, self).p_name()
        
'''
basic inheritance
features
'''

class base_cls:
    def base_f1(self):
        self.__name_mngl=99
        print("Work done in base class")

class base_offspring01(base_cls):
    def off_01_f1(self):
        print("Work done in offspring 01 class")

if __name__ == "__main__":
    c4 = c_4()
    c4.p_name()
    print(c_4.__mro__)
    
    '''
    Testing basic inheritance features
    '''
    
    off01 = base_offspring01()
    off01.base_f1()
    off01.off_01_f1()