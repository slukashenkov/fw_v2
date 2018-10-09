# PCMST/PAIDD and probably other transas ais

from ... import nmea


class CMS(nmea.ProprietarySentence):
	sentence_types = {}
	
	
	def __new__ (_cls,
				 manufacturer,
				 datatype,
				 data):
		name = datatype
		cls = _cls.sentence_types.get(name, _cls)
		return super(CMS, cls).__new__(cls)
	
	
	def __init__ (self,
				  manufacturer,
				  datatype,
				  data):
		self.sentence_type = datatype
		super(CMS, self).__init__(manufacturer,
								  datatype,
								  data)


class CMST(CMS):
	""" PCMST - Proprietary "T" equipment status
		 """
	fields = (
		("Sentences Timestamp", "sntns_tmstmp"),
		("Eqipment state", "eq_state"),
	)
