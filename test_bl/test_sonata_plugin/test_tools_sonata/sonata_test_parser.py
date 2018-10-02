import logging, math
import os.path
from test_bl.test_bl_tools.logging_tools import LoggingTools
from test_bl.test_bl_tools.scan_logs import ScanLogs

class SonataTestParser:
    def __init__(self,
                 conf           = None,
                 data_from      = None,
                 data_to        = None
                 ):
        """
        :param data_from:
        :param data_to:
        """
        self.range = [1, 2, 3, 4, 5, 6, 7, 8, 9]

        '''
        Search pattern is configured in json test data
        '''
        self.search_pttrn_keyword = "log_pttrn"

        '''
        LETS NOT DO ANYTHING WITHOUT PROPER LOGGER
        '''
        self.logger = logging.getLogger(__name__)
        if conf != None :
            self.conf = conf
        self.logger.debug("Sonata PARSER`s SETUP is finished")


        '''
        ALL DATA TO PROCESS
        '''
        self.data_from = data_from
        self.data_to = data_to

        '''
        SPECIFIC PACKETS TO PROCESS
        '''
        self.packet_indx = None

        '''
        RESULTING STORAGE DATA STRUCTURES
        '''
        self.sonata_nmea_from = {}
        self.sonata_nmea_parsed_map = {}
        self.sonata_nmea_to = {}
        self.sonata_nmea_from_parsed = {}
        return

        '''
        SPECIFIC VALUES TO COMPARE
        '''
        self.key_sent = None
        self.key_received = None

        self.logger.debug("Sonata Parser is SET")

    def parse_from(self):
        """
        :return:
        """
        '''
        GET PARTICULAR PAKET
        by index
        '''
        try:
            self.data_from[self.packet_indx]
        except IndexError:
            self.logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            self.logger.info("No RETURN packet FOUND at the index: "+ str(self.packet_indx) + " IN THE DATA_FROM STRUCTURE")
            self.logger.info("BL/MUSSON CAN BE DOWN AT THE MOMENT")
            self.logger.info("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

            raise Exception("NO PACKETS GOTTEN FROM BL FOR PROCESSING. So IT SEEMS.")

        data_to_parse = self.data_from[self.packet_indx]

        #print("!!!!!!!@@@@@" + str(data_to_parse))
        '''NB! VERY IMPORTANT ADDITION'''
        '''BEFORE CONVERSION INTO DESIRED '''
        data_to_parse = str(data_to_parse)
        #print("!!!!!!!@@@@@" + data_to_parse)

        ind_values=data_to_parse.split(",")

        indx = 0
        lat = {}
        lon = {}
        vel = {}
        course = {}
        data_from = {}
        data_from["lat"] = lat
        data_from["lon"] = lon
        data_from["vel"] = vel
        data_from["course"] = course

        for val in ind_values:
            if val:
                label = "label" + str(indx)
                self.sonata_nmea_from[label] = val
                if indx == 2:
                    data_from["sonata_id"] = val
                    indx += 1
                    continue
                if indx == 6:
                    course["deg"] = val
                    course["tens_deg"] = val
                    indx += 1
                    continue
                if indx == 10:
                    data_from["vel_knots"] = val
                    indx += 1
                    continue
                if indx == 14:
                    vel["hkm_h"] = val
                    vel["km_h"] = val
                    indx += 1
                    continue
                if indx == 18:
                    lat["deg"] = val
                    lat["min"] = val
                    lat["sec"] = val
                    lat["tens_sec"] = val
                    indx += 1
                    continue
                if indx == 26:
                    lon["deg"] = val
                    lon["min"] = val
                    lon["sec"] = val
                    lon["tens_sec"] = val
                    indx += 1
                    continue

            indx += 1

        self.sonata_nmea_parsed_map = data_from
        return self.sonata_nmea_parsed_map


    def compare_fields_old(self,
                        sonata_id   =   None,
                        lat         =   None,
                        lon         =   None,
                        vel         =   None,
                        vel_knots   =   None,
                        course      =   None
                        ):
        result = False

        if sonata_id != None and  ((sonata_id in self.data_to) and (sonata_id in self.sonata_nmea_parsed_map)):
            field_sent = self.data_to[sonata_id]
            field_received = int(self.sonata_nmea_parsed_map[sonata_id])
            try:
                assert field_sent == field_received, "Fields ARE NOT equal"
                result = True
                self.logger.critical("Comparison of "+ str(field_sent)  +" and " + str(field_received) + " in field named: "+ " was successful")
                return result
            except:
                self.logger.debug("Comparison of " + str(field_sent) + " and " + str(field_received) + " in field named: " + sonata_id + " FAILED MISERABLY")
                return result

        if lat != None and  ((lat in self.data_to) and (lat in self.sonata_nmea_parsed_map)):
            field_sent = self.data_to[lat]
            field_sent_str = str(field_sent["deg"]) + str(field_sent["min"]) + str(field_sent["sec"])+"." + str(field_sent["tens_sec"])
            field_received=self.sonata_nmea_parsed_map[lat]["deg"]
            try:
                assert field_sent_str==field_received, "Fields ARE NOT equal"
                result = True
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + " was successful")
                return result
            except:
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + lat + " FAILED MISERABLY")
                return result

        if lon != None and  ((lon in self.data_to) and (lon in self.sonata_nmea_parsed_map)):
            field_sent = self.data_to[lon]
            field_sent_str = str(field_sent["deg"])+str(field_sent["min"])+str(field_sent["sec"])+"."+str(field_sent["tens_sec"])
            field_received=self.sonata_nmea_parsed_map[lon]

            field_received = self.sonata_nmea_parsed_map[lon]["deg"]
            try:
                assert field_sent_str == field_received, "Fields ARE NOT equal"
                result = True
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received+ " in field named: " + lon + " was successful")
                return result
            except:
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + lon + " FAILED MISERABLY")
                return result

        if vel != None and  ((vel in self.data_to) and (vel in self.sonata_nmea_parsed_map)):
            field_sent = self.data_to[vel]
            '''
            if (field_sent["hkm_h"] or field_sent["km_h"]) in self.range:
                field_sent_hkm_h_str = str(0) + str(field_sent["hkm_h"])
                field_sent_km_h_str = str(0) + str(field_sent["km_h"])
                field_sent_str = field_sent_hkm_h_str + field_sent_km_h_str
            else:
                field_sent_str = str(field_sent["hkm_h"]) + str(field_sent["km_h"])
            '''
            field_sent_str = str(field_sent["hkm_h"]) + str(field_sent["km_h"])
            field_received=self.sonata_nmea_parsed_map[vel]["hkm_h"]
            try:
                assert field_sent_str == field_received, "Fields ARE NOT equal"
                result = True
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + vel + " was successful")
                return result
            except:
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + vel + " FAILED MISERABLY")
                return result


        if course != None and  ((course in self.data_to) and (course in self.sonata_nmea_parsed_map)):
            field_sent = self.data_to[course]
            field_sent_str = str(field_sent["deg"]) + str(field_sent["tens_deg"])

            field_received=self.sonata_nmea_parsed_map[course]["deg"]
            try:
                assert field_sent_str == field_received, "Fields ARE NOT equal"
                result = True
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received+ " in field named: " + course + " was successful")
                return result
            except:
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + course +" FAILED MISERABLY")
                return result

        if vel_knots != None and vel_knots in self.sonata_nmea_parsed_map:
            field_sent = self.data_to["vel"]
            field_sent_str_hkm_h = str(field_sent["hkm_h"])
            field_sent_str_hkm_h = float(field_sent_str_hkm_h)*100
            field_sent_str_km_h = str(field_sent["km_h"])
            field_sent_str_km_h = float(field_sent_str_km_h)

            field_sent_calc = field_sent_str_hkm_h + field_sent_str_km_h
            field_sent_calc = field_sent_calc / 1.852
            field_sent_calc = round(field_sent_calc)
            field_sent_str = str(field_sent_calc)

            field_received = self.sonata_nmea_parsed_map[vel_knots]
            field_received = float(field_received)
            field_received = round(field_received)
            try:
                #assert field_sent_str == field_received, "Fields ARE NOT equal"
                assert str(field_sent_calc) == str(field_received), "Fields ARE NOT equal"
                result = True
                self.logger.debug("Comparison of " + str(field_sent) + " " + field_sent_str + " " + str(field_sent_calc)+ " and " + str(field_received) + " in field named: " + vel_knots + " was successful")
                return result
            except:
                self.logger.debug("Comparison of " +str(field_sent) + " " + field_sent_str +" " + str(field_sent_calc) + " and " + str(field_received) + " in field named: " + vel_knots + " FAILED MISERABLY")
                return result

        self.logger.info("Comparison of WAS NOT TRIGGERED FOR ANY CONDITION.Something is OFF")
        return result

    def compare_fields(self,
                       msg_data_sent,
                       msg_data_received = None):
        """
        :param msg_data_sent: data gathered at the time when packet is formed
        :param msg_data_received: data gathered fro SUT in UDP server
        :return:
        """
        comparison_results = {}
        if msg_data_received == None and "fail" in msg_data_sent.keys():
            pattern_to_search = msg_data_sent["fail"]
            self.parse_log(pattern_to_search)
            return comparison_results
        elif msg_data_received != None and "pass" in msg_data_sent.keys():
            self.sonata_nmea_parsed_map = msg_data_received
            self.data_to = msg_data_sent
            keys = msg_data_sent["pass"]
            for key in keys:
                comparison_results[key] = self.__do_comparison(key)
            return comparison_results


    def __do_comparison(self,
                        key):
        result = False
        if "sonata_id" == key and  ((key in self.data_to) and (key in self.sonata_nmea_parsed_map)):
            field_sent = self.data_to[key]
            field_received = int(self.sonata_nmea_parsed_map[key])
            try:
                assert field_sent == field_received, "Fields ARE NOT equal"
                result = True
                self.logger.debug("Comparison of "+ str(field_sent)  +" and " + str(field_received) + " in field named: "+ key+ " was successful")
                return (result, field_sent, field_received)
            except:
                self.logger.debug("Comparison of " + str(field_sent) + " and " + str(field_received) + " in field named: " + key + " FAILED MISERABLY")
                return (result, field_sent, field_received)

        if "lat" == key and  ((key in self.data_to) and (key in self.sonata_nmea_parsed_map)):
            field_sent = self.data_to[key]
            deg      = field_sent["deg"]
            if deg < 10:
                deg = str("0"+str(deg))
            else:
                deg = str(deg)

            min      = field_sent["min"]
            if min < 10:
                min = str("0" + str(min))
            else:
                min = str(min)

            sec      = field_sent["sec"]
            if sec < 10:
                sec = str("0" + str(sec))
            else:
                sec = str(sec)

            tens_sec = field_sent["tens_sec"]
            tens_sec = str(tens_sec)

            field_sent_str = str(deg + min + sec +"." + tens_sec)
            field_received=self.sonata_nmea_parsed_map[key]["deg"]

            try:
                assert field_sent_str==field_received, "Fields ARE NOT equal"
                result = True
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + key +" was successful")
                return (result, field_sent, field_sent_str, field_received)
            except:
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + key + " FAILED MISERABLY")
                return (result, field_sent, field_sent_str, field_received)

        if "lon" == key and  ((key in self.data_to) and (key in self.sonata_nmea_parsed_map)):
            field_sent = self.data_to[key]
            field_received = self.sonata_nmea_parsed_map[key]
            field_received = self.sonata_nmea_parsed_map[key]["deg"]

            deg = field_sent["deg"]
            if deg == 0:
                deg = str("000")
            elif deg < 10 and deg != 0:
                deg = str("00" + str(deg))
            elif deg == 10 and deg != 0:
                deg = str("0" + str(deg))
            elif deg <= 99 and deg != 0:
                deg = str("0" + str(deg))
            else:
                deg = str(deg)

            min = field_sent["min"]
            if min == 0:
                min = str("00")
            elif min < 10 and min != 0:
                min = str("0" + str(min))
            else:
                min = str(min)

            sec = field_sent["sec"]
            if sec == 0:
                sec = str("00")
            elif sec < 10 and sec != 0:
                sec = str("0" + str(sec))

            else:
                sec = str(sec)

            tens_sec = field_sent["tens_sec"]
            tens_sec = str(tens_sec)

            field_sent_str = str(deg + min + sec +"." + tens_sec)

            try:
                assert field_sent_str == field_received, "Fields ARE NOT equal"
                result = True
                self.logger.info("Comparison of " + field_sent_str + " and " + field_received+ " in field named: " + key + " was successful")
                return (result, field_sent, field_sent_str, field_received)
            except:
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + key + " FAILED MISERABLY")
                return (result, field_sent, field_sent_str, field_received)

        if "vel" == key and  ((key in self.data_to) and (key in self.sonata_nmea_parsed_map)):
            field_sent = self.data_to[key]
            '''
            if (field_sent["hkm_h"] or field_sent["km_h"]) in self.range:
                field_sent_hkm_h_str = str(0) + str(field_sent["hkm_h"])
                field_sent_km_h_str = str(0) + str(field_sent["km_h"])
                field_sent_str = field_sent_hkm_h_str + field_sent_km_h_str
            else:
                field_sent_str = str(field_sent["hkm_h"]) + str(field_sent["km_h"])
            '''
            hkm_h_int = field_sent["hkm_h"]
            if hkm_h_int == 0:
                hkm_h = str("")
            else:
                hkm_h = str(hkm_h_int)

            km_h = field_sent["km_h"]
            if km_h >= 100:
                hkm_h_int = hkm_h_int + 1
                hkm_h = str(hkm_h_int)
                km_h = km_h - 100
                if km_h < 10:
                    km_h = str("0"+str(km_h))
                else:
                    km_h = str(km_h)
            elif km_h <10 and hkm_h == "":
                km_h = str(km_h)
            elif km_h < 10:
                km_h = str("0"+str(km_h))
            else:
                km_h = str(km_h)
            field_sent_str = str(hkm_h + km_h)
            field_received=self.sonata_nmea_parsed_map[key]["hkm_h"]
            try:
                assert field_sent_str == field_received, "Fields ARE NOT equal"
                result = True
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + key + " was successful")
                return (result, field_sent,field_sent_str, field_received)
            except:
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + key + " FAILED MISERABLY")
                return (result, field_sent, field_sent_str, field_received)


        if "course" == key and  ((key in self.data_to) and (key in self.sonata_nmea_parsed_map)):
            field_sent = self.data_to[key]
            deg_int      = field_sent["deg"]
            if deg_int == 0:
                deg = str("")
            else:
                deg = str(deg_int)

            tens_deg = field_sent["tens_deg"]
            if tens_deg < 10 and deg =="":
                tens_deg = str(tens_deg)
            elif tens_deg < 10:
                tens_deg = str("0" + str(tens_deg))
            elif tens_deg >= 100:
                if deg == "":
                    tens_deg = str(tens_deg)
                elif deg in range(1,9):
                    tens_deg = str("0" + str(tens_deg))
                else:
                    deg = int(deg) + 1
                    deg = str(deg)
                    tens_deg = tens_deg - 100
                    if tens_deg < 10:
                        tens_deg = str("0" + str(tens_deg))
                    elif tens_deg == 0:
                        tens_deg = str("0" + "0")
                    else:
                        tens_deg = str(tens_deg)
            else:
                tens_deg = str(tens_deg)

            field_sent_str = str(deg + tens_deg)
            field_received=self.sonata_nmea_parsed_map[key]["deg"]

            try:
                assert field_sent_str == field_received, "Fields ARE NOT equal"
                result = True
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received+ " in field named: " + key + " was successful")
                return (result, field_sent, field_sent_str, field_received)
            except Exception:
                self.logger.debug("Comparison of " + field_sent_str + " and " + field_received + " in field named: " + key +" FAILED MISERABLY")
                return (result, field_sent, field_sent_str, field_received)


        if "vel_knots" == key and key in self.sonata_nmea_parsed_map:
            '''received data'''
            field_received = self.sonata_nmea_parsed_map[key]
            field_received_int = float(field_received)
            try:
                field_received_full,field_received_frac = field_received.split('.')
                field_received = field_received_full
            except Exception:
                pass


            #field_received_int = float(field_received)
            #field_received_int = format(field_received_int, '.0f')
            #field_received_int = round(field_received_int)
            #field_received = str(field_received_int)


            '''sent data'''
            field_sent = self.data_to["vel"]
            hkm_h_int = field_sent["hkm_h"]
            km_h_int  = field_sent["km_h"]
            hkm_h_int = float(hkm_h_int)*100
            field_sent_calc = hkm_h_int + km_h_int
            field_sent_calc = field_sent_calc / 1.852
            field_sent_str = str(field_sent_calc)


            try:
                field_sent_full, field_sent_frac = field_sent_str.split(".")
                field_sent_str = field_sent_full
            except Exception:
                field_sent_str = field_sent_str

            '''Difference in rounding and calculations compensation'''
            diff = int(field_received) - int(field_sent_str)
            if diff >= 1:
                field_sent_calc = round(field_sent_calc)
                field_sent_str = str(field_sent_calc)

            #field_sent_calc_repr = format(field_sent_calc, '.0f')
            #field_sent_calc = round(field_sent_calc, 1)
            #field_sent_calc = round(field_sent_calc)
            #field_sent_str = str(field_sent_calc)

            '''
            field_sent_str_hkm_h = str(field_sent["hkm_h"])
            field_sent_str_hkm_h = float(field_sent_str_hkm_h)*100
            field_sent_str_km_h = str(field_sent["km_h"])
            field_sent_str_km_h = float(field_sent_str_km_h)

            field_sent_calc = field_sent_str_hkm_h + field_sent_str_km_h
            field_sent_calc = field_sent_calc / 1.852
            field_sent_calc = round(field_sent_calc)
            field_sent_str = str(field_sent_calc)
            '''

            try:
                assert field_sent_str == field_received, "Fields ARE NOT equal"
                result = True
                self.logger.debug("Comparison of " + str(field_sent) + " " + " and " + str(field_received) + " in field named: " + key + " was successful")
                return (result, field_sent, field_sent_str, field_received )
            except:
                self.logger.debug("Comparison of " +str(field_sent) + " " + " and " + str(field_received) + " in field named: " + key + " FAILED MISERABLY")
                return (result, field_sent,field_sent_str, field_received)

        self.logger.info("Comparison of WAS NOT TRIGGERED FOR ANY CONDITION.Something is OFF")
        raise Exception("Comparison of WAS NOT TRIGGERED FOR ANY CONDITION.Something is OFF")
        return result


    def parse_log(self,
                  path_to_log,
                  pattern_in =None):
        if pattern_in != None:
            if os.path.exists(path_to_log):
                log_location = path_to_log
                search_substr = ScanLogs(logs_location=path_to_log,
                                         search_pttrn=pattern_in)
                result = search_substr.scan_logs(pattern_in)
        else:
            raise Exception ("NO PATTERN TO SEARCH FOR")
        return result

    def parse_log_auto(self,
                       msg_data_sent,
                       path_to_log
                       ):
        '''For each element sent test for substring'''
        if os.path.exists(path_to_log):
            pattern_in = []
            try:
                if "fail" in msg_data_sent.keys():
                    pattern_in.append(msg_data_sent[self.search_pttrn_keyword])
            except:
                raise Exception("Something is wrong with our assumption that we can iterate over sent messages list")

            try:
                for pattern in pattern_in:
                    search_substr = ScanLogs(logs_location=path_to_log,
                                              search_pttrn =pattern)
                    result = search_substr.scan_logs()
                    return result
            except:
                raise Exception("Something is wrong with our assumption that we formed a list of patterns")
            return