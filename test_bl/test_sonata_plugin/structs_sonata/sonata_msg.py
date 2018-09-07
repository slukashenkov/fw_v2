from binascii import a2b_qp
from bitstring import BitArray
#from binascii import a2b_qp
import copy, logging

from test_bl.test_sonata_plugin.configs_sonata import sonata_send_recieve_properties
from test_bl.test_bl_tools import read_test_data
from test_bl.test_bl_tools.logging_tools import  LoggingTools

class SonataMsg:
    def __init__(self):

        """
        Since this is a specific message
        for SONATA module testing
        The expectation is to get configuration from
        module specific configuration class during initialisation
        of a message - one message only.

        Atomic values are expected to be stored in whatever storage
        is chosen for the tests
        meaning
        one message = one set of values

        :param SonataSendReceiveProperties:
        """
        '''
        LETS NOT DO ANYTHING WITHOUT PROPER LOGGER
        '''
        self.logger = logging.getLogger(__name__)

        '''
         Sonata message fields
         '''
        self.mtype      = None  # тип сообщения: 00 - нав.данные, 01 - текст Ж
        self.sonata_id  = None  # id
        self.lat        = None  # lattitude
        self.lon        = None  # longitude
        self.vel        = None  # velocity
        self.course     = None  # course
        self.state      = None  # A(ctual), N(orth), E(ast)
        self.tail       = None  # Датчики и каналы управления игнорируются плагином.
        self.signal_lvl = None  # signal level still need to be present in order to be properly processed by BL

        '''
        Constructed messages
        '''
        self.sonata_msg          = None
        self.sonata_data_chsumed = None
        '''
        Message data 
        '''
        self.fields_data = {}
        '''
        MAP to store message fields` data
        and message to be sent
        '''
        self.mapped_fields = {}


    def set_sonata_values_map(self):
        '''
        Read those field values from file
        '''
        read_data=read_test_data.ReadData(self.path_to_test_data)
        read_data.read_file_to_map()
        self.mapped_fields=read_data.final_map
        self.set_values_from_map()
        return

    def set_values_from_map(self):
        '''
        Sonata message fields
        '''
        if "mtype" in self.mapped_fields:
            mtype_str=self.mapped_fields.pop('mtype')
            self.mtype = BitArray(bin=str(mtype_str))  # тип сообщения: 00 - нав.данные, 01 - текст Ж

            '''
            SET the VALUES FOR FURTHER 
            COMPARISON RIGHT HERE SINCE 
            the 
            WE HAVE TARGET STUCTURE AVAILABLE 
            '''
            self.data_for_comparison['mtype'] =self.mtype.int

        if "sonata_id" in self.mapped_fields:
            sonata_id_str = self.mapped_fields.pop('sonata_id')
            self.sonata_id = BitArray(bin=sonata_id_str)  # id

            self.data_for_comparison['sonata_id'] = self.sonata_id.int

        if "lat" in self.mapped_fields:
            lat_str = self.mapped_fields.pop('lat')
            self.lat = BitArray(bin=lat_str)  # lattitude
            '''
            TODO: Maybe 4 fields for lattitude are better. NOT just ONE
            '''
            #self.lat = BitArray(bin=''.join(('1011001', '0111011', '0111011', '1001')))  # 89,59,59,9
            self.data_for_comparison['lat'] = self.lat.int

        if "lon" in self.mapped_fields:
            lon_str=self.mapped_fields.pop('lon')
            self.lon = BitArray(bin=lon_str)  # longitude
            '''
            TODO: Maybe 4 fields for longitude are better. NOT just ONE
            '''
            #self.lon = BitArray(bin="".join(('10110011', '0111011', '0111011', '1001')))  # 179,59,59,9
            self.data_for_comparison['lon'] = self.lon.int

        if "vel" in self.mapped_fields:
            vel_str = self.mapped_fields.pop('vel')
            self.vel = BitArray(bin=vel_str)  # velocity

            '''
            TODO: Maybe 2 fields for velocity are better. NOT just ONE
            '''
            #self.vel = BitArray(bin=''.join(('111', '1100011')))  # velocity
            self.data_for_comparison['vel'] = self.vel.int

        if "course" in self.mapped_fields:
            course_str = self.mapped_fields.pop('course')
            self.course = BitArray(bin=course_str)  # course
            #self.course = BitArray(bin=''.join(('11', '0111011')))  # course
            self.data_for_comparison['course'] = self.course.int

        if "state" in self.mapped_fields:
            state_str = self.mapped_fields.pop('state')
            self.state = BitArray(bin=state_str)  # A(ctual), N(orth), E(ast)
            self.data_for_comparison['state'] = self.state.int

        if "tail" in self.mapped_fields:
            tail_int = int(self.mapped_fields.pop('tail'))
            self.tail = BitArray(tail_int)  # Датчики и каналы управления игнорируются плагином.
            self.data_for_comparison['tail'] = self.tail.int

        if "signal_lvl" in self.mapped_fields:
            signal_lvl_str = self.mapped_fields.pop('signal_lvl')
            self.signal_lvl = BitArray(bin=signal_lvl_str)
            self.data_for_comparison['signal_lvl'] = self.signal_lvl.int
        '''
        Individual fields combined into a whole SONATA message
        First: converted into HEX
        Second: checksummed and prepended with $ 
        '''
        self.sonata_data = self.mtype + self.sonata_id + self.lat + self.lon + self.vel + self.course + self.state + self.tail + self.signal_lvl
        self.sonata_msg = self.sonata_data.hex.upper()
        self.sonata_data_chsumed = '$' + self.add_checksum(self.sonata_msg)

        self.logger.debug(": " + self.sonata_msg + " <- Sonata message composed from stored values: ")
        self.logger.debug(": " + self.sonata_data_chsumed + " <- Sonata message composed from stored values: ")

        return

    def set_values_from_json_map(self,
                                 test_data):
        """
        First things first.
        Hygiene.
        Cleanup.
        :return:
        """
        self.reset_fields()
        '''
        Sonata message fields
        '''
        if "mtype" in test_data:
            '''
            SET the VALUES FOR FURTHER 
            COMPARISON RIGHT HERE SINCE 
            the 
            WE HAVE TARGET STUCTURE AVAILABLE 
            '''
            self.fields_data['mtype'] = test_data.pop('mtype')

            '''
            Attempts to find a way to form bin 
            number of the size appropriate for Sonata
            messages
            '''
            #mtype_bin = bin(self.fields_data.get("mtype"))
            #mtype_barr = BitArray(mtype_bin)

            #field_length = BitArray(bin='0b00')
            #field_length = BitArray()
            #field_length.append(mtype_barr)
            #self.mtype = BitArray(field_length)  # тип сообщения: 00 - нав.данные, 01 - текст Ж
            #self.mtype = BitArray(bin=str(mtype_str))

            '''Form the proper string for mtype'''
            # mtype_str = format(self.fields_data.get("mtype"),'b')
            mtype_str = '{0:02b}'.format(self.fields_data.get("mtype"))
            self.mtype = BitArray(bin=mtype_str) # тип сообщения: 00 - нав.данные, 01 - текст Ж


        if "sonata_id" in test_data:
            '''
            SET the VALUES FOR FURTHER 
            COMPARISON RIGHT HERE SINCE 
            the 
            WE HAVE TARGET STRUCTURE AVAILABLE 
            '''
            self.fields_data['sonata_id'] = test_data.pop('sonata_id')

            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #sonata_id_bin = bin(self.fields_data.get('sonata_id'))
            #mtype_barr = BitArray(sonata_id_bin)

            #field_length = BitArray(bin='0b000000000000')
            #field_length = BitArray()
            #field_length.append(mtype_barr)
            #self.sonata_id = BitArray(field_length)  # sonata_id

            '''Form the proper string for sonata_id'''
            #self.sonata_id = BitArray(bin=str(sonata_id_str))
            #sonata_id_str = format(self.fields_data.get('sonata_id'), 'b')
            sonata_id_str = '{0:012b}'.format(self.fields_data.get('sonata_id'), 'b')
            self.sonata_id = BitArray(bin=sonata_id_str)


        if "lat" in test_data:
            '''
            SET the VALUES FOR FURTHER 
            COMPARISON RIGHT HERE SINCE 
            the 
            WE HAVE TARGET STUCTURE AVAILABLE 
            '''
            self.fields_data['lat'] = test_data.pop('lat')
            '''
            TODO: Maybe 4 fields for lattitude are better. NOT just ONE
            DONE
            '''
            '''SET degrees'''
            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #lat_deg = BitArray(bin='0b0000000')
            #lat_deg = BitArray()
            #lat_deg_bin = bin(self.fields_data.get("lat").get("deg"))
            #deg_barr_int = self.fields_data.get("lat").get("deg")
            #lat_deg_barr_int = BitArray(int=deg_barr_int, length=8)
            #lat_deg_barr = BitArray(lat_deg_bin)
            #lat_deg.append(lat_deg_barr)


            '''THIS STRING FORMATION SHOULD WORK Fingers crossed'''
            # lat_deg_str = format(self.fields_data.get("lat").get("deg"), 'b')
            lat_deg_str = '{0:07b}'.format(self.fields_data.get("lat").get("deg"))
            self.lat_deg = BitArray(bin=lat_deg_str)



            '''SET minutes'''
            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #lat_min = BitArray(bin='0b0000000')
            #lat_min = BitArray()
            #lat_min_bin = bin(self.fields_data.get("lat").get("min"))

            #lat_min_barr_int = BitArray(int=int(self.fields_data.get("lat").get("min")), length=8)
            #lat_min_barr = BitArray(lat_min_bin)
            #lat_min.append(lat_min_barr)

            '''THIS STRING FORMATION SHOULD WORK Fingers crossed'''
            #lat_min_str = format(self.fields_data.get("lat").get("min"), 'b')
            lat_min_str = '{0:07b}'.format(self.fields_data.get("lat").get("min"))
            self.lat_min = BitArray(bin=lat_min_str)

            '''Set seconds'''
            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #lat_sec = BitArray(bin='0b0000000')
            #lat_sec = BitArray()
            #lat_sec_bin = bin(self.fields_data.get("lat").get("sec"))
            #lat_sec_str = format(self.fields_data.get("lat").get("sec"), 'b')
            #lat_sec_barr = BitArray(lat_sec_bin)
            #lat_sec.append(lat_sec_barr)

            '''THIS STRING FORMATION SHOULD WORK Fingers crossed'''
            # lat_sec_str = format(self.fields_data.get("lat").get("sec"), 'b')
            lat_sec_str = '{0:07b}'.format(self.fields_data.get("lat").get("sec"))
            self.lat_sec = BitArray(bin=lat_sec_str)


            '''Set tens of seconds'''
            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #lat_tens_sec = BitArray(bin='0b0000')
            #lat_tens_sec = BitArray()
            #lat_tens_sec_bin = bin(self.fields_data.get("lat").get("tens_sec"))
            #lat_tens_sec_str = format(self.fields_data.get("lat").get("tens_sec"), 'b')
            #lat_tens_sec_barr = BitArray(lat_tens_sec_bin)
            #lat_tens_sec.append(lat_tens_sec_barr)

            '''THIS STRING FORMATION SHOULD WORK Fingers crossed'''
            # lat_tens_sec_str = format(self.fields_data.get("lat").get("tens_sec"), 'b')
            lat_tens_sec_str = '{0:04b}'.format(self.fields_data.get("lat").get("tens_sec"))
            self.lat_tens_sec = BitArray(bin=lat_tens_sec_str)

            '''Set full value'''
            #self.lat = BitArray()

            #self.lat.append(lat_deg)
            #self.lat.append(lat_min)
            #self.lat.append(lat_sec)
            #self.lat.append(lat_tens_sec)

            self.lat = self.lat_deg+self.lat_min+self.lat_sec+self.lat_tens_sec


        if "lon" in test_data:
            '''
            SET the VALUES FOR FURTHER 
            COMPARISON RIGHT HERE SINCE 
            the 
            WE HAVE TARGET STUCTURE AVAILABLE 
            '''
            self.fields_data['lon'] = test_data.pop('lon')

            '''
            TODO: Maybe 4 fields for lattitude are better. NOT just ONE
            DONE
            '''
            '''SET degrees'''
            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #lon_deg = BitArray(bin='0b0000000')
            #lon_deg = BitArray()
            #lon_deg_bin = bin(self.fields_data.get("lon").get("deg"))
            #lon_deg_str = format(self.fields_data.get("lon").get("deg"), 'b')
            #lon_deg_barr = BitArray(lon_deg_bin)
            #lon_deg.append(lon_deg_barr)


            '''THIS STRING FORMATION SHOULD WORK Fingers crossed'''
            # lon_deg_str = format(self.fields_data.get("lon").get("deg"), 'b')
            lon_deg_str = '{0:08b}'.format(self.fields_data.get("lon").get("deg"))
            self.lon_deg = BitArray(bin=lon_deg_str)

            '''Set minutes'''
            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #lon_min = BitArray(bin='0b0000000')
            #lon_min = BitArray()
            #lon_min_bin = bin(self.fields_data.get("lon").get("min"))
            #lon_min_str = format(self.fields_data.get("lon").get("min"), 'b')
            #lon_min_barr = BitArray(lon_min_bin)
            #lon_min.append(lon_min_barr)

            '''THIS STRING FORMATION SHOULD WORK Fingers crossed'''
            # lon_min_str = format(self.fields_data.get("lon").get("min"), 'b')
            lon_min_str = '{0:07b}'.format(self.fields_data.get("lon").get("min"))
            self.lon_min = BitArray(bin=lon_min_str)

            '''Set seconds'''
            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #lat_sec = BitArray(bin='0b0000000')
            #lon_sec = BitArray()
            #lon_sec_bin = bin(self.fields_data.get("lon").get("sec"))
            #lon_sec_str = format(self.fields_data.get("lon").get("sec"), 'b')
            #lon_sec_barr = BitArray(lon_sec_bin)
            #lon_sec.append(lon_sec_barr)

            '''THIS STRING FORMATION SHOULD WORK Fingers crossed'''
            # lon_sec_str = format(self.fields_data.get("lon").get("sec"), 'b')
            lon_sec_str = '{0:07b}'.format(self.fields_data.get("lon").get("sec"))
            self.lon_sec = BitArray(bin=lon_sec_str)


            '''Set tens of seconds'''
            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #lat_tens_sec = BitArray(bin='0b0000')
            #lon_tens_sec = BitArray()
            #lon_tens_sec_bin = bin(self.fields_data.get("lon").get("tens_sec"))
            #lon_tens_sec_str = format(self.fields_data.get("lon").get("tens_sec"), 'b')
            #lon_tens_sec_barr = BitArray(lon_tens_sec_bin)
            #lon_tens_sec.append(lon_tens_sec_barr)

            '''THIS STRING FORMATION SHOULD WORK Fingers crossed'''
            # lon_tens_sec_str = format(self.fields_data.get("lon").get("tens_sec"), 'b')
            lon_tens_sec_str = '{0:04b}'.format(self.fields_data.get("lon").get("tens_sec"))
            self.lon_tens_sec = BitArray(bin=lon_tens_sec_str)


            '''Set full value'''
            #self.lon = BitArray()
            #self.lon.append(lat_deg)
            #self.lon.append(lat_min)
            #self.lon.append(lat_sec)
            #self.lon.append(lat_tens_sec)

            self.lon = self.lon_deg+self.lon_min+self.lon_sec+self.lon_tens_sec


        if "vel" in test_data:
            '''
            SET the VALUES FOR FURTHER 
            COMPARISON RIGHT HERE SINCE 
            the 
            WE HAVE TARGET STUCTURE AVAILABLE 
            '''
            self.fields_data['vel'] = test_data.pop('vel')

            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #vel_hkm_h_bin = bin(self.fields_data.get('vel').get("hkm_h"))
            #vel_hkm_h_str = format(self.fields_data.get('vel').get("hkm_h"), 'b')
            #vel_hkm_h_barr = BitArray(vel_hkm_h_bin)

            #vel_km_h_bin = bin(self.fields_data.get('vel').get("km_h"))
            #vel_km_h_str = format(self.fields_data.get('vel').get("km_h"), 'b')
            #vel_km_h_barr = BitArray(vel_km_h_bin)

            '''SET hkm_h'''
            '''THIS STRING FORMATION SHOULD WORK Fingers crossed'''
            # vel_hkm_h_str = format(self.fields_data.get('vel').get("hkm_h"), 'b')
            vel_hkm_h_str = '{0:03b}'.format(self.fields_data.get('vel').get("hkm_h"))
            self.vel_hkm_h = BitArray(bin=vel_hkm_h_str)

            '''SET km_h'''
            '''THIS STRING FORMATION SHOULD WORK Fingers crossed'''
            # vel_km_h_str = format(self.fields_data.get('vel').get("km_h"), 'b')
            vel_km_h_str = '{0:07b}'.format(self.fields_data.get('vel').get("km_h"))
            self.vel_km_h = BitArray(bin=vel_km_h_str)

            # field_length = BitArray(bin='0b000000000000')
            #field_length = BitArray()
            #field_length.append(vel_barr)
            #self.vel = BitArray(field_length)  # sonata_id

            '''Set full value'''
            self.vel = self.vel_hkm_h+self.vel_km_h



        if "course" in test_data:
            '''
            SET the VALUES FOR FURTHER 
            COMPARISON RIGHT HERE SINCE 
            the 
            WE HAVE TARGET STUCTURE AVAILABLE 
            '''
            self.fields_data['course'] = test_data.pop('course')
            '''
            TODO: Maybe 4 fields for lattitude are better. NOT just ONE
            DONE
            '''
            '''SET course'''
            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #course_deg = BitArray(bin='0b0000000')
            #course_deg = BitArray()
            #course_deg_bin = bin(self.fields_data.get("course").get("deg"))
            #course_deg_str = format(self.fields_data.get('course').get("deg"), 'b')
            #course_deg_barr = BitArray(course_deg_bin)
            #course_deg.append(course_deg_barr)

            #course_tens_deg = BitArray()
            #course_tens_deg_bin = bin(self.fields_data.get("course").get("tens_deg"))
            #course_tens_deg_str = format(self.fields_data.get('course').get("tens_deg"), 'b')
            #course_tens_deg_barr = BitArray(course_tens_deg_bin)
            #course_tens_deg.append(course_tens_deg_barr)
            # self.course = BitArray()
            # self.course.append(course_deg)
            # self.course.append(course_tens_deg)

            '''SET course_deg'''
            # course_deg_str = format(self.fields_data.get('course').get("deg"), 'b')
            course_deg_str = '{0:02b}'.format(self.fields_data.get('course').get("deg"))
            self.course_deg = BitArray(bin=course_deg_str)

            '''SET course_tens_deg'''
            # course_tens_deg_str = format(self.fields_data.get('course').get("tens_deg"), 'b')
            course_tens_deg_str = '{0:07b}'.format(self.fields_data.get('course').get("tens_deg"))
            self.course_tens_deg = BitArray(bin=course_tens_deg_str)

            '''Set full value'''
            self.course = self.course_deg + self.course_tens_deg


        if "state" in test_data:
            '''
            SET the VALUES FOR FURTHER 
            COMPARISON RIGHT HERE SINCE 
            the 
            WE HAVE TARGET STUCTURE AVAILABLE 
            '''
            self.fields_data['state'] = test_data.pop('state')

            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #state_str = format(self.fields_data.get("state"),'b')
            #state_bin = bin(self.fields_data.get("state"))
            #state_barr = BitArray(mtype_bin)
            #field_length = BitArray(bin='0b00')
            #field_length = BitArray()
            #field_length.append(state_barr)
            #self.state = BitArray(field_length)  # тип сообщения: 00 - нав.данные, 01 - текст Ж


            '''SET state'''
            # state_str = format(self.fields_data.get("state"),'b')
            state_str = '{0:03b}'.format(self.fields_data.get("state"))


            '''Set full value'''
            self.state = BitArray(bin=state_str)  # A(ctual), N(orth), E(ast)


        if "tail" in test_data:
            '''
            SET the VALUES FOR FURTHER 
            COMPARISON RIGHT HERE SINCE 
            the 
            WE HAVE TARGET STUCTURE AVAILABLE 
            '''
            self.fields_data['tail'] = test_data.pop('tail')

            tail_int = self.fields_data.get("tail")
            self.tail = BitArray(tail_int)  # Датчики и каналы управления игнорируются плагином. = bin(self.fields_data.get("state"))


        if "signal_lvl" in test_data:
            '''
            SET the VALUES FOR FURTHER 
            COMPARISON RIGHT HERE SINCE 
            the 
            WE HAVE TARGET STUCTURE AVAILABLE 
            '''
            self.fields_data['signal_lvl'] = test_data.pop('signal_lvl')

            '''Attempts to find a way to form bin number of the size appropriate for Sonata'''
            #signal_lvl_str = format(self.fields_data.get("signal_lvl"),'b')
            #signal_lvl_bin = bin(self.fields_data.get("signal_lvl"))
            #signal_lvl_barr = BitArray(mtype_bin)

            #field_length = BitArray(bin='0b00')
            #field_length = BitArray()
            #field_length.append(signal_lvl_barr)
            #self.signal_lvl = BitArray(field_length)  # тип сообщения: 00 - нав.данные, 01 - текст Ж
            #self.signal_lvl = BitArray(bin=signal_lvl_str)

            '''SET signal_lvl'''
            # signal_lvl_str = format(self.fields_data.get("signal_lvl"),'b')
            signal_lvl_str = '{0:04b}'.format(self.fields_data.get("signal_lvl"))


            '''Set full value'''
            self.signal_lvl = BitArray(bin=signal_lvl_str)



        '''|---------------------------------------------------------------------------------------------------------'''
        '''
        Individual fields combined into a whole SONATA message
        First: converted into HEX
        Second: checksummed and prepended with $ 
        '''
        #sonata_data = self.mtype + self.sonata_id + self.lat + self.lon + self.vel + self.course + self.state + self.tail + self.signal_lvl
        #self.sonata_msg = sonata_data.hex.upper()
        #self.sonata_data_chsumed = '$' + self.add_checksum(self.sonata_msg)

        #self.logger.debug(": " + self.sonata_msg + " <- Sonata message composed from stored values: ")
        #self.logger.debug(": " + self.sonata_data_chsumed + " <- Sonata message composed from stored values: ")

        '''
        Individual fields combined into a whole SONATA message
        First: converted into HEX
        Second: checksummed and prepended with $ 
        '''

        '''
        However there are exceptions
        designed for negative testing 
        '''
        if "fail" in test_data and (test_data['fail'] == 'bad_chsum'):

            '''Store search pattern and test message type (positive/negative)'''
            self.fields_data['fail'] = test_data.pop('fail')
            self.fields_data['log_pttrn'] = test_data.pop('log_pttrn')

            self.logger.debug(
                "============================================================================================")

            self.sonata_data = self.mtype + self.sonata_id + self.lat + self.lon + self.vel + self.course + self.state + self.tail + self.signal_lvl
            self.sonata_msg = self.sonata_data.hex.upper()

            self.logger.debug("============================================================================================")
            self.logger.debug(": " + self.sonata_msg + " <- Sonata message composed from stored values: ")

            self.sonata_data_chsumed = '$' + self.add_checksum_wrong(self.sonata_msg)
            self.logger.debug(": " + self.sonata_data_chsumed + " <- Sonata message WAS checksumed INCORRECTLY: ")
            self.sonata_data_chsumed = ''.join([self.sonata_data_chsumed, '\n\n'])
            self.logger.debug(": " + self.sonata_data_chsumed + " <- Sonata message WAS NOT WAS checksumed INCORRECTLY but TAILED ")
            self.logger.debug("============================================================================================")

            test_data_combined = (self.sonata_data_chsumed, copy.deepcopy(self.fields_data), "fail")
            return test_data_combined

        if "fail" in test_data and (test_data['fail'] == 'no_$'):

            '''Store search pattern right away'''
            self.fields_data['fail'] = test_data.pop('fail')
            self.fields_data['log_pttrn'] = test_data.pop('log_pttrn')


            self.logger.debug(
                "============================================================================================")

            self.sonata_data = self.mtype + self.sonata_id + self.lat + self.lon + self.vel + self.course + self.state + self.tail + self.signal_lvl
            self.sonata_msg = self.sonata_data.hex.upper()
            self.logger.debug(": " + self.sonata_msg + " <- Sonata message composed from stored values: ")
            self.sonata_data_chsumed = '#' + self.add_checksum(self.sonata_msg)
            self.logger.debug(": " + self.sonata_data_chsumed + " <- Sonata message checksumed but no $: ")
            self.sonata_data_chsumed = ''.join([self.sonata_data_chsumed, '\n\n'])

            self.logger.debug(
                "============================================================================================")

            test_data_combined = (self.sonata_data_chsumed, copy.deepcopy(self.fields_data),"fail")
            return test_data_combined

        if "fail" in test_data and (test_data['fail'] == 'no_tail'):

            '''Store search pattern right away'''

            self.fields_data['fail'] = test_data.pop('fail')
            self.fields_data['log_pttrn'] = test_data.pop('log_pttrn')


            self.logger.debug("============================================================================================")

            self.sonata_data = self.mtype + self.sonata_id + self.lat + self.lon + self.vel + self.course + self.state + self.tail + self.signal_lvl
            self.sonata_msg = self.sonata_data.hex.upper()
            self.logger.debug(": " + self.sonata_msg + " <- Sonata message composed from stored values: ")
            self.sonata_data_chsumed = '$' + self.add_checksum(self.sonata_msg)
            self.logger.debug(": " + self.sonata_data_chsumed + " <- Sonata message checksumed: but no TAIL ")

            self.logger.debug("============================================================================================")

            test_data_combined = (self.sonata_data_chsumed, copy.deepcopy(self.fields_data),"fail")
            return test_data_combined

        else:
            '''Store search keys for values that ought to match'''
            self.fields_data['pass'] = test_data.pop('pass')


            self.logger.debug("============================================================================================")

            self.sonata_data = self.mtype + self.sonata_id + self.lat + self.lon + self.vel + self.course + self.state + self.tail + self.signal_lvl
            self.sonata_msg = self.sonata_data.hex.upper()
            self.logger.debug(": " + self.sonata_msg + " <- Sonata message composed from stored values: ")
            self.sonata_data_chsumed = '$' + self.add_checksum(self.sonata_msg)
            self.logger.debug(": " + self.sonata_data_chsumed + " <- Sonata message checksumed: ")
            self.sonata_data_chsumed = ''.join([self.sonata_data_chsumed, '\n\n'])
            self.logger.debug(": " + self.sonata_data_chsumed + " <- Sonata message checksumed and TAILED")

            self.logger.debug("============================================================================================")
            test_data_combined = (self.sonata_data_chsumed, copy.deepcopy(self.fields_data),"pass")
            return test_data_combined

    '''
    |------------------------------------------------------------------------------------------------------------------|
    '''

    # checksum calculation
    # execute on
    # bs_data

    def add_checksum(self,
                    sonata_msg_in):
        """
        Calculate and append checksum to formed message
        """
        return sonata_msg_in + self.checksum(BitArray(a2b_qp(sonata_msg_in)))


    def add_checksum_wrong(self,
                           sonata_msg_in):
        message = BitArray(a2b_qp(sonata_msg_in)).reverse()
        """
        Calculate and append checksum to formed message
        """
        return sonata_msg_in + self.checksum_wrong(BitArray(a2b_qp(sonata_msg_in)))
        #return sonata_msg_in + self.checksum(message)

    def checksum(self,
                 bitarray):
        """
        Calculate sonata checksum
        """

        total = sum((octet.int for octet in bitarray.cut(8)))
        return BitArray(hex(total))[-8:].hex.upper()

    def checksum_wrong(self,
                 bitarray):
        """
        Calculate sonata checksum
        """
        bitarray.reverse()
        total = sum((octet.int for octet in bitarray.cut(8)))
        return BitArray(hex(total))[-8:].hex.upper()

    def reset_fields(self):
        '''
        Sonata message fields
        '''
        self.mtype = None  # тип сообщения: 00 - нав.данные, 01 - текст Ж
        self.sonata_id = None  # id
        self.lat = None  # lattitude
        self.lon = None  # longitude
        self.vel = None  # velocity
        self.course = None  # course
        self.state = None  # A(ctual), N(orth), E(ast)
        self.tail = None  # Датчики и каналы управления игнорируются плагином.
        self.signal_lvl = None  # signal level still need to be present in order to be properly processed by BL

        self.sonata_msg = None
        self.sonata_data_chsumed = None

        return

    def get_msg(self):
        return self.sonata_data_chsumed

    def get_msg_data(self):
        return

    def set_example_sonata_values(self):
        '''
        Sonata
        message
        fields for debug purposes only
        these values are guarantied to be valid
        and useful if the only thing we acre about is a that message is formed and cabn be sent
        '''
        self.mtype = BitArray(bin='11')  # тип сообщения: 00 - нав.данные, 01 - текст Ж
        self.sonata_id = BitArray(bin='000000000011')  # id
        self.lat = BitArray(bin=''.join(('1011001', '0111011', '0111011', '1001')))  # 89,59,59,9
        self.lon = BitArray(bin="".join(('10110011','0111011', '0111011', '1001')))  # 179,59,59,9
        self.vel = BitArray(bin=''.join(('111', '1100011')))  # 7,99
        self.course = BitArray(bin=''.join(('11', '0111011')))  # 3,59
        self.state = BitArray(bin='001')  # A(ctual), N(orth), E(ast)
        self.tail = BitArray(17)  # Датчики и каналы управления игнорируются плагином.
        self.signal_lvl=BitArray(bin='1111')

        '''
        Individual
        fields
        combined
        into
        a
        whole
        message
        '''
        self.sonata_data = self.mtype + self.sonata_id + self.lat + self.lon + self.vel + self.course + self.state + self.tail + self.signal_lvl
        self.sonata_msg = self.sonata_data.hex.upper()
        #self.sonata_data_chsumed=self.add_checksum(self.sonata_msg)

        self.sonata_data_chsumed = '$'+ self.add_checksum(self.sonata_msg)

        self.logger.debug(": " + self.sonata_msg + " <- Current handmade Sonata message: ")
        self.logger.debug(": " + self.sonata_data_chsumed + " <- handmade Sonata message with checksum added: ")
        return

def test_this():
     return


if __name__ == '__main__':
    test_this()