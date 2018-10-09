# PCMST/PAIDD and probably other transas ais

from ... import nmea


class EIS(nmea.ProprietarySentence):
	sentence_types = {}
	
	
	def __new__ (_cls,
				 manufacturer,
				 datatype,
				 data):
		name = datatype
		name_create_nmea = datatype
		cls = _cls.sentence_types.get(name, _cls)
		return super(EIS, cls).__new__(cls)
	
	
	def __init__ (self,
				  manufacturer,
				  datatype,
				  data):
		self.sentence_type = datatype
		super(EIS, self).__init__(manufacturer,
								  datatype,
								  data)


class EIST(EIS):
	"""PEIST - proprietary keep alive msg
	"""
	fields = (
		("time_stamp", "time_stamp"),
		("ims_status", "ims_status"),
	)
