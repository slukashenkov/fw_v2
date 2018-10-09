# PCMST/PAIDD and probably other transas ais

from ... import nmea


class AIS(nmea.ProprietarySentence):
	sentence_types = {}
	
	
	def __new__ (_cls,
				 manufacturer,
				 datatype,
				 data):
		name = datatype
		cls = _cls.sentence_types.get(name,
									  _cls)
		
		return super(AIS, cls).__new__(cls)
	
	
	def __init__ (self,
				  manufacturer,
				  datatype,
				  data):
		self.sentence_type = datatype
		super(AIS, self).__init__(manufacturer,
								  datatype,
								  data)


class AISD(AIS):
	"""PAISD - AIS data for FOR CUSTOM equipment

		data comes from into
		$PAISD
		from
		--------------------
		AIVDM type 5 or 24
		from fields
		--------------------
		AIVDM to PAISD mapping:

		AIVDM Field: MMSI
		AIVDM Field:  IMO Number
		AIVDM Field: Call Sign
		AIVDM Field: Vessel Name
	"""
	fields = (
		("MMSI", "mmsi"),
		("IMO Number", "imo_num"),
		("Call Sign", "c_sign"),
		("Vessel Name", "v_name"),
	)
