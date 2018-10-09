"""
This lib was designed to parse/generate nmea messages
with a standard in view.
To have a reminder of its guidelines here is an excerpt:

NMEA Encoding Conventions
-------------------------
Data is transmitted in serial async, 1 start-bit, 8 data-bits, 1 stop-bit, no parity.
1) Data-bits are in least-significant-bit order.
2) The standard specifies 4800 as the speed, but this is no longer common. The most-signifacant-bit is always zero.

Structure
     1  2    3                        4 5   6
     |  |    |                        | |   |
ex. $GPVTG,108.53,T,,M,0.04,N,0.07,K,A*31<CR><LF>

1) An NMEA sentence consists of a start delimiter(1), followed by a comma-separated sequence of fields ex.(3) till (4),
followed by the character * (ASCII 42), the checksum and an end-of-line marker.

2) The start delimiter is normally $ (ASCII 36) ex.(1). Packets of AIVDM/AIVDO data, which are otherwise formatted like NMEA, use !. Up to 4.00 these are the only permitted start characters [ANON].

3) The first field of a sentence ex (2) is called the "tag" and normally consists of a two-letter talker ID followed by a three-letter type code (ex. GP-talker id;  VTG-code).

4) Where a numeric |latitude| or |longitude| is given, the two digits immediately to the left of the decimal point are whole minutes,
to the right are decimals of minutes, and the remaining digits to the left of the whole minutes are whole degrees.

Eg. 4533.35 is 45 degrees and 33.35 minutes. ".35" of a minute is exactly 21 seconds.

Eg. 16708.033 is 167 degrees and 8.033 minutes. ".033" of a minute is about 2 seconds.

5) In NMEA 3.01 (and possibly some earlier versions), the character "^" (HEX 5E) is reserved as an introducer for two-character hex escapes using 0-9 and A-F, expressing an ISO 8859-1 (Latin-1) character [ANON].

6) The Checksum ex.(5) is mandatory, and the last field in a sentance. It is the 8-bit XOR of all characters in the sentance,
exclusing the "$", "I", or "*" characters; but including all "," and "^". It is encoded as two hexadecimal characters (0-9, A-F),
the most-significant-nibble being sent first.

7) Sentences are terminated by a <CR><LF> sequence ex.(7).

8) Maximum sentence length, including the $ and <CR><LF> is 82 bytes.

NB!
According to [UNMEA], the NMEA standard requires that a field (such as altitude, latitude, or longitude)
must be left empty when the GPS has no valid data for it. However, many receivers violate this. It’s common,
for example, to see latitude/longitude/altitude figures filled with zeros when the GPS has no valid data.

Talker IDs
----------
NMEA sentences do not identify the individual device that issued them;
the format was originally designed for shipboard multidrop networks on which it’s possible only to broadcast to all devices, not address a specific one.

NMEA sentences do, however, include a "talker ID" a two-character prefix that identifies the type of the transmitting unit.
By far the most common talker ID is "GP", identifying a generic GPS, but all of the following are well known:


Big list of talker IDs
-----------------------
AB Independent AIS Base Station
AD Dependent AIS Base Station
AG Autopilot - General
AP Autopilot - Magnetic
BN Bridge navigational watch alarm system
CC Computer - Programmed Calculator (obsolete)
CD Communications - Digital Selective Calling (DSC)
CM Computer - Memory Data (obsolete)
CS Communications - Satellite
CT Communications - Radio-Telephone (MF/HF)
CV Communications - Radio-Telephone (VHF)
CX Communications - Scanning Receiver
DE DECCA Navigation (obsolete)
DF Direction Finder
DU Duplex repeater station
EC Electronic Chart Display & Information System (ECDIS)
EP Emergency Position Indicating Beacon (EPIRB)
ER Engine Room Monitoring Systems
GP Global Positioning System (GPS)
HC Heading - Magnetic Compass
HE Heading - North Seeking Gyro
HN Heading - Non North Seeking Gyro
II Integrated Instrumentation
IN Integrated Navigation
LA Loran A (obsolete)
LC Loran C (obsolete)
MP Microwave Positioning System (obsolete)
NL Navigation light controller
OM OMEGA Navigation System (obsolete)
OS Distress Alarm System (obsolete)
RA RADAR and/or ARPA
SD Sounder, Depth
SN Electronic Positioning System, other/general
SS Sounder, Scanning
TI Turn Rate Indicator
TR TRANSIT Navigation System
U# # is a digit 0 … 9; User Configured
UP Microprocessor controller
VD Velocity Sensor, Doppler, other/general
DM Velocity Sensor, Speed Log, Water, Magnetic
VW Velocity Sensor, Speed Log, Water, Mechanical
WI Weather Instruments
YC Transducer - Temperature (obsolete)
YD Transducer - Displacement, Angular or Linear (obsolete)
YF Transducer - Frequency (obsolete)
YL Transducer - Level (obsolete)
YP Transducer - Pressure (obsolete)
YR Transducer - Flow Rate (obsolete)
YT Transducer - Tachometer (obsolete)
YV Transducer - Volume (obsolete)
YX Transducer
ZA Timekeeper - Atomic Clock
ZC Timekeeper - Chronometer
ZQ Timekeeper - Quartz
ZV Timekeeper - Radio Update, WWV or WWVH

TMVTD - Transas VTS / SML tracking system report
$TMVTD,DDMMYY,hhmmss.ss,a,xxxx,c—c,llll.llll,a,yyyyy.yyyy,a,x.x,a,x.x,a,a*hh<CR><LF>
‘TM’ indicates message generated by SML tracking system. ‘VTD’ is name of the message.
Transas is a mnanufacturer of proprietary ECDIS systems.

General Sentence Format
--------------------------
All data is transmitted in the form of sentences.
Only printable ASCII characters are allowed, plus CR (carriage return)
and LF (line feed). Each sentence starts with a "$" sign and ends with CRLF.
There are three basic kinds of sentences: talker sentences, proprietary sentences
and query sentences.
Talker Sentences
----------------
The general format for a talker sentence is:
$ttsss,d1,d2,....CRLF

The first two letters following the „$” are the talker identifier.
The next three characters (sss) are the sentence identifier, followed
by a number of data fields separated by commas, followed by an optional
checksum, and terminated by carriage return/line feed.
The data fields are uniquely defined for each sentence type.
Proprietary Sentences
---------------------
Proprietary sentences can either be output from the gps or used as input
to control information.
They always start with P which is followed by a 3 character manufactures
code and additional characters to define the sentence type.
"""
import operator
import re
from functools import reduce


class ParseError(ValueError):
	
	
	def __init__ (self, message, data):
		super(ParseError, self).__init__((message, data))


class SentenceTypeError(ParseError):
	pass


class ChecksumError(ParseError):
	pass


class NMEASentenceType(type):
	sentence_types = {}
	
	
	def __init__ (cls,
				  name,
				  bases,
				  dct):
		print("NMEASentenceType Init \n" + "cls" + str(type(cls)) + "\nname: " + name + "\nbases:" + str(
			bases) + "\ndct" + str(dct))
		type.__init__(cls,
					  name,
					  bases,
					  dct)
		base = bases[0]
		if base is object:
			return
		base.sentence_types[name] = cls
		cls.name_to_idx = dict((f[1], i) for i, f in enumerate(cls.fields))


# http://mikewatkins.ca/2008/11/29/python-2-and-3-metaclasses/
NMEASentenceBase = NMEASentenceType('NMEASentenceBase', (object,), {})


class NMEASentence(NMEASentenceBase):
	"""
	Base NMEA Sentence
	Parses and generates NMEA strings
	Examples:

	>>> s = NMEASentence.parse("$GPGGA,184353.07,1929.045,S,02410.506,E,1,04,2.6,100.00,M,-33.9,M,,0000*6D")
	>>> print(s)
	"""
	
	sentence_re = re.compile(r'''
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
	
	talker_re = \
		re.compile(r'^(?P<talker>\w{2})(?P<sentence>\w{3})$')
	query_re = \
		re.compile(r'^(?P<talker>\w{2})(?P<listener>\w{2})Q,(?P<sentence>\w{3})$')
	proprietary_re = \
		re.compile(r'^P(?P<manufacturer>\w{3})(?P<p_data_type>\w{1,})')
	
	name_to_idx = {}
	fields = ()
	
	
	@staticmethod
	def checksum (nmea_str):
		return reduce(operator.xor, map(ord, nmea_str), 0)
	
	
	@staticmethod
	def parse (line,
			   check = False):
		'''
		parse(line)

		Parses a string representing a NMEA 0183 sentence, and returns a
		NMEASentence object

		Raises ValueError if the string could not be parsed, or if the checksum
		did not match.
		'''
		match = NMEASentence.sentence_re.match(line)
		if not match:
			raise ParseError('could not parse data', line)
		
		# pylint: disable=bad-whitespace
		nmea_str = match.group('nmea_str')
		data_str = match.group('data')
		checksum = match.group('checksum')
		sentence_type = match.group('sentence_type').upper()
		data = data_str.split(',')
		
		if checksum:
			cs1 = int(checksum, 16)
			cs2 = NMEASentence.checksum(nmea_str)
			if cs1 != cs2:
				raise ChecksumError(
					'checksum does not match: %02X != %02X' % (cs1, cs2), data)
		elif check:
			raise ChecksumError(
				'strict checking requested but checksum missing', data)
		
		'''
		TEST whether the sentence is a proprietary sentence
		'''
		proprietary_match = NMEASentence.proprietary_re.match(sentence_type)
		'''
		TEST whether the sentence is query sentence
		'''
		query_match = NMEASentence.query_re.match(sentence_type)
		'''
		TEST whether the sentence is a talker sentence
		'''
		talker_match = NMEASentence.talker_re.match(sentence_type)
		
		'''
		Build object with accessible data fields 
		based on NMEA sentence type         
		'''
		if proprietary_match:
			manufacturer = proprietary_match.group('manufacturer')
			datatype = proprietary_match.group('p_data_type')
			# classname   = manufacturer + datatype
			if manufacturer == "CMS" and datatype == "T":
				datatype = manufacturer + datatype
			elif manufacturer == "EIS" and datatype == "T":
				datatype = manufacturer + datatype
			elif manufacturer == "AIS" and datatype == "D":
				datatype = manufacturer + datatype
			elif manufacturer == "AID" and datatype == "D":
				datatype = manufacturer + datatype
			
			cls = ProprietarySentence.sentence_types.get(manufacturer,
														 ProprietarySentence)
			return cls(manufacturer,
					   datatype,
					   data)
		
		elif query_match and not data_str:
			talker = query_match.group('talker')
			listener = query_match.group('listener')
			sentence = query_match.group('sentence')
			
			return QuerySentence(talker, listener, sentence)
		
		elif talker_match:
			talker = talker_match.group('talker')
			sentence = talker_match.group('sentence')
			cls = TalkerSentence.sentence_types.get(sentence)
			
			if not cls:
				# TODO instantiate base type instead of fail
				raise SentenceTypeError(
					'Unknown sentence type %s' % sentence_type, line)
			
			return cls(talker, sentence, data)
		
		raise ParseError(
			'could not parse sentence type: %r' % sentence_type, line)
	
	
	def __getattr__ (self, name):
		# pylint: disable=invalid-name
		t = type(self)
		try:
			i = t.name_to_idx[name]
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
	
	
	def __setattr__ (self, name, value):
		# pylint: disable=invalid-name
		t = type(self)
		if name not in t.name_to_idx:
			return object.__setattr__(self, name, value)
		
		i = t.name_to_idx[name]
		self.data[i] = str(value)
	
	
	def __repr__ (self):
		# pylint: disable=invalid-name
		r = []
		d = []
		t = type(self)
		for i, v in enumerate(self.data):
			if i >= len(t.fields):
				d.append(v)
				continue
			name = t.fields[i][1]
			r.append('%s=%r' % (name, getattr(self, name)))
		
		return '<%s(%s)%s>' % (
			type(self).__name__,
			', '.join(r),
			d and ' data=%r' % d or ''
		)
	
	
	def identifier (self):
		raise NotImplementedError
	
	
	def render (self,
				checksum = True,
				dollar = True,
				newline = True):
		
		ident = self.identifier()
		data = ','.join(self.data)
		res = ident + data
		if checksum:
			res += '*%02X' % NMEASentence.checksum(res)
		if dollar:
			res = '$' + res
		if newline:
			res += '\r\n'
		return res
	
	
	def __str__ (self):
		return self.render()


class TalkerSentence(NMEASentence):
	sentence_types = {}
	
	
	def __init__ (self,
				  talker,
				  sentence_type,
				  data):
		self.talker = talker
		self.sentence_type = sentence_type
		self.data = list(data)
	
	
	def identifier (self):
		return '%s%s,' % (self.talker, self.sentence_type)


class QuerySentence(NMEASentence):
	sentence_types = {}
	
	
	def __init__ (self, talker, listener, sentence_type):
		self.talker = talker
		self.listener = listener
		self.sentence_type = sentence_type
		self.data = []
	
	
	def identifier (self):
		return '%s%sQ,%s,' % (self.talker, self.listener, self.sentence_type)


class ProprietarySentence(NMEASentence):
	sentence_types = {}
	
	
	def __init__ (self,
				  manufacturer,
				  datatype,
				  data):
		
		self.manufacturer = manufacturer
		self.datatype = datatype
		self.data = list(data)
	
	
	def identifier (self):
		if (self.datatype == "EIST") or (self.datatype == "CMST") or (self.datatype == "AIDD") or (
				self.datatype == "AISD"):
			return 'P%s' % (self.datatype + ",")
		else:
			return 'P%s' % (self.manufacturer + self.datatype + ",")
