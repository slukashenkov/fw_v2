#!/usr/bin/env python

"""Functions to serialize/deserialize aisbinary messages.

Need to then wrap these functions with the outer AIS packet and then
convert the whole binary blob to a NMEA string.  Those functions are
not currently provided in this file.

serialize: python to ais binary
deserialize: ais binary to python

The generated code  uscg.py, aisbinary.py, and aisstring.py
which should be packaged with the resulting files.

A "Type 24" may be in part A or part B format;

According to the standard, parts A and B are expected to be broadcast in adjacent pairs;
in the real world they may (due to quirks in various aggregation methods)
be separated by other sentences or even interleaved with different Type 24 pairs;
decoders must cope with this.
The interpretation of some fields in Type B format changes depending on the range of
the Type B MMSI field.

160 bits for part A, 168 bits for part B.
According to the standard, both the A and B parts are supposed to be 168 bits.
However, in the wild, A parts are often transmitted with only 160 bits,
omitting the spare 7 bits at the end.
Implementers should be permissive about this.
[IALA] does not describe this message type; format information is thanks to Kurt Schwehr.

u	Unsigned integer
U   Unsigned integer with scale - renders as float, suffix is decimal places
i   Signed integer
I   Signed integer with scale - renders as float, suffix is decimal places
b   Boolean
e   Enumerated type (controlled vocabulary)
x   Spare or reserved bit
t   String (packed six-bit ASCII)
d   Data (uninterpreted binary)
a   Array boundary, numeric suffix is maximum array size.
    ^ before suffix means preceding fields is the length.
    Following fields are repeated to end of message

Field	    Len	    Description	        Member	    T	    Units
0-5	        6	    Message Type	    type	    u	    Constant: 24
6-7	        2	    Repeat Indicator	repeat	    u	    As in CNB
8-37	    30	    MMSI	            mmsi	    u	    9 digits
38-39	    2	    Part Number	        partno	    u	    0-1
40-159	    120	    Vessel Name	        shipname	t	    (Part A) 20 sixbit chars
160-167	    8	    Spare		                    x	    (Part A) Not used
40-47	    8	    Ship Type	        shiptype	e	    (Part B) See "Ship Types"
48-65	    18	    Vendor ID	        vendorid	t	    (Part B) 3 six-bit chars
66-69	    4	    Unit Model Code	    model	    u	    (Part B)
70-89	    20	    Serial Number	    serial	    u	    (Part B)
90-131	    42	    Call Sign	        callsign	t	    (Part B) As in Message Type 5
132-140	    9	    Dimension to Bow	to_bow	    u	    (Part B) Meters
141-149	    9	    Dimension to Stern	to_stern	u	    (Part B) Meters
150-155	    6	    Dimension to Port	to_port	    u	    (Part B) Meters
156-161	    6	    Dimension to
                    Starboard	to_starboard	    u	    (Part B) Meters
132-161	    30	    Mothership MMSI	mothership_mmsi	u	    (Part B) See below
162-167	    6	    Spare		                    x	    (Part B) Not used


"""
import sys
from decimal import Decimal
import unittest

from test_bl.test_trassa_plugin.structs_trassa.aisutils.BitVector import BitVector
from test_bl.test_trassa_plugin.structs_trassa.aisutils import aisstring
from test_bl.test_trassa_plugin.structs_trassa.aisutils import aisbinary
from test_bl.test_trassa_plugin.structs_trassa.aisutils import uscg


fieldList = (
    'MessageID',
    'RepeatIndicator',
    'UserID',
    'AISversion',
    'IMOnumber',
    'callsign',
    'name',
    'shipandcargo',
    'dimA',
    'dimB',
    'dimC',
    'dimD',
    'fixtype',
    'ETAmonth',
    'ETAday',
    'ETAhour',
    'ETAminute',
    'draught',
    'destination',
    'dte',
    'Spare',
)

def encode(type,
           params,
           validate=False):
    '''Create a shipdata binary message payload to pack into an AIS Msg shipdata.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 5 (field automatically set to "5")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - AISversion(uint): Compliant with what edition.  0 is the first edition.
      - IMOnumber(uint): vessel identification number (different than mmsi)
      - callsign(aisstr6): Ship radio call sign
      - name(aisstr6): Vessel name
      - shipandcargo(uint): what
      - dimA(uint): Distance from bow to reference position
      - dimB(uint): Distance from reference position to stern
      - dimC(uint): Distance from port side to reference position
      - dimD(uint): Distance from reference position to starboard side
      - fixtype(uint): Method used for positioning
      - ETAmonth(uint): Estimated time of arrival - month
      - ETAday(uint): Estimated time of arrival - day
      - ETAhour(uint): Estimated time of arrival - hour
      - ETAminute(uint): Estimated time of arrival - minutes
      - draught(udecimal): Maximum present static draught
      - destination(aisstr6): Where is the vessel going
      - dte(uint): Data terminal ready
      - Spare(uint): Reserved for definition by a regional authority. (field automatically set to "0")

    @param params: Dictionary of field names/values.  Throws a ValueError exception if required is missing
    @param validate: Set to true to cause checking to occur.  Runs slower.  FIX: not implemented.
    @rtype: BitVector
    @return: encoded binary message (for binary messages, this needs to be wrapped in a msg 8
    @note: The returned bits may not be 6 bit aligned.  It is up to you to pad out the bits.
    '''

    if type=="A":
        bvList = []
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=24),6))

        if 'RepeatIndicator' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['RepeatIndicator']),2))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0),2))

        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['MMSI']),30))

        #PartNumber = 0 for A
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0),2))
        #vesselName
        if 'name' in params:
            bvList.append(aisstring.encode(params['name'],120))
        else:
            bvList.append(aisstring.encode('@@@@@@@@@@@@@@@@@@@@',120))
        #Spare
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0),6))

        return aisbinary.joinBV(bvList)
    elif type == "B":
        bvList = []
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=24), 6))

        if 'RepeatIndicator' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['RepeatIndicator']), 2))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 2))

        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['MMSI']), 30))

        # PartNumber = 1 for B
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=1), 2))

        if 'shipandcargo' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['shipandcargo']), 8))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 8))

        if 'vendor_id' in params:
            bvList.append(aisstring.encode(params['vendor_id'], 18))
        else:
            bvList.append(aisstring.encode('@@@', 18))

        if 'unit_model' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['unit_model']),4))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 4))


        if 'serial_num' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['serial_num']), 20))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 20))



        if 'callsign' in params:
            bvList.append(aisstring.encode(params['callsign'], 42))
        else:
            bvList.append(aisstring.encode('@@@@@@@', 42))
        if 'dimA' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['dimA']), 9))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 9))
        if 'dimB' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['dimB']), 9))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 9))

        if 'dimC' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['dimC']), 6))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 6))

        if 'dimD' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['dimD']), 6))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 6))

        '''
        if 'mother_ship_mmsi' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['mother_ship_mmsi']), 30))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 4))
        '''

        #Spare
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 6))

        return aisbinary.joinBV(bvList)
    elif type == "aux":
        bvList = []
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=24), 6))

        if 'RepeatIndicator' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['RepeatIndicator']), 2))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 2))

        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['MMSI']), 30))

        # PartNumber = 1 for B
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=1), 2))

        if 'shipandcargo' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['shipandcargo']), 8))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 8))

        if 'vendor_id' in params:
            bvList.append(aisstring.encode(params['vendor_id'], 18))
        else:
            bvList.append(aisstring.encode('@@@', 18))

        if 'unit_model' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['unit_model']),4))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 4))


        if 'serial_num' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['serial_num']), 20))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 20))



        if 'callsign' in params:
            bvList.append(aisstring.encode(params['callsign'], 42))
        else:
            bvList.append(aisstring.encode('@@@@@@@', 42))

        if 'mother_ship_mmsi' in params:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=params['mother_ship_mmsi']), 30))
        else:
            bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 30))

        #Spare
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal=0), 6))

        return aisbinary.joinBV(bvList)

def decode(bv, validate=False):
    '''Unpack a shipdata message.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 5 (field automatically set to "5")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - AISversion(uint): Compliant with what edition.  0 is the first edition.
      - IMOnumber(uint): vessel identification number (different than mmsi)
      - callsign(aisstr6): Ship radio call sign
      - name(aisstr6): Vessel name
      - shipandcargo(uint): what
      - dimA(uint): Distance from bow to reference position
      - dimB(uint): Distance from reference position to stern
      - dimC(uint): Distance from port side to reference position
      - dimD(uint): Distance from reference position to starboard side
      - fixtype(uint): Method used for positioning
      - ETAmonth(uint): Estimated time of arrival - month
      - ETAday(uint): Estimated time of arrival - day
      - ETAhour(uint): Estimated time of arrival - hour
      - ETAminute(uint): Estimated time of arrival - minutes
      - draught(udecimal): Maximum present static draught
      - destination(aisstr6): Where is the vessel going
      - dte(uint): Data terminal ready
      - Spare(uint): Reserved for definition by a regional authority. (field automatically set to "0")
    @type bv: BitVector
    @param bv: Bits defining a message
    @param validate: Set to true to cause checking to occur.  Runs slower.  FIX: not implemented.
    @rtype: dict
    @return: params
    '''

    #Would be nice to check the bit count here..
    #if validate:
    #    assert (len(bv)==FIX: SOME NUMBER)
    r = {}
    r['MessageID']=5
    r['RepeatIndicator']=int(bv[6:8])
    r['UserID']=int(bv[8:38])
    r['AISversion']=int(bv[38:40])
    r['IMOnumber']=int(bv[40:70])
    r['callsign']=aisstring.decode(bv[70:112])
    r['name']=aisstring.decode(bv[112:232])
    r['shipandcargo']=int(bv[232:240])
    r['dimA']=int(bv[240:249])
    r['dimB']=int(bv[249:258])
    r['dimC']=int(bv[258:264])
    r['dimD']=int(bv[264:270])
    r['fixtype']=int(bv[270:274])
    r['ETAmonth']=int(bv[274:278])
    r['ETAday']=int(bv[278:283])
    r['ETAhour']=int(bv[283:288])
    r['ETAminute']=int(bv[288:294])
    r['draught']=Decimal(int(bv[294:302]))/Decimal('10')
    r['destination']=aisstring.decode(bv[302:422])
    r['dte']=int(bv[422:423])
    r['Spare']=0
    return r

def decodeMessageID(bv, validate=False):
    return 5

def decodeRepeatIndicator(bv, validate=False):
    return int(bv[6:8])

def decodeUserID(bv, validate=False):
    return int(bv[8:38])

def decodeAISversion(bv, validate=False):
    return int(bv[38:40])

def decodeIMOnumber(bv, validate=False):
    return int(bv[40:70])

def decodecallsign(bv, validate=False):
    return aisstring.decode(bv[70:112])

def decodename(bv, validate=False):
    return aisstring.decode(bv[112:232])

def decodeshipandcargo(bv, validate=False):
    return int(bv[232:240])

def decodedimA(bv, validate=False):
    return int(bv[240:249])

def decodedimB(bv, validate=False):
    return int(bv[249:258])

def decodedimC(bv, validate=False):
    return int(bv[258:264])

def decodedimD(bv, validate=False):
    return int(bv[264:270])

def decodefixtype(bv, validate=False):
    return int(bv[270:274])

def decodeETAmonth(bv, validate=False):
    return int(bv[274:278])

def decodeETAday(bv, validate=False):
    return int(bv[278:283])

def decodeETAhour(bv, validate=False):
    return int(bv[283:288])

def decodeETAminute(bv, validate=False):
    return int(bv[288:294])

def decodedraught(bv, validate=False):
    return Decimal(int(bv[294:302]))/Decimal('10')

def decodedestination(bv, validate=False):
    return aisstring.decode(bv[302:422])

def decodedte(bv, validate=False):
    return int(bv[422:423])

def decodeSpare(bv, validate=False):
    return 0


def printHtml(params, out=sys.stdout):
        out.write("<h3>shipdata</h3>\n")
        out.write("<table border=\"1\">\n")
        out.write("<tr bgcolor=\"orange\">\n")
        out.write("<th align=\"left\">Field Name</th>\n")
        out.write("<th align=\"left\">Type</th>\n")
        out.write("<th align=\"left\">Value</th>\n")
        out.write("<th align=\"left\">Value in Lookup Table</th>\n")
        out.write("<th align=\"left\">Units</th>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>MessageID</td>\n")
        out.write("<td>uint</td>\n")
        if 'MessageID' in params:
            out.write("    <td>"+str(params['MessageID'])+"</td>\n")
            out.write("    <td>"+str(params['MessageID'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>RepeatIndicator</td>\n")
        out.write("<td>uint</td>\n")
        if 'RepeatIndicator' in params:
            out.write("    <td>"+str(params['RepeatIndicator'])+"</td>\n")
            if str(params['RepeatIndicator']) in RepeatIndicatorDecodeLut:
                out.write("<td>"+RepeatIndicatorDecodeLut[str(params['RepeatIndicator'])]+"</td>")
            else:
                out.write("<td><i>Missing LUT entry</i></td>")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>UserID</td>\n")
        out.write("<td>uint</td>\n")
        if 'UserID' in params:
            out.write("    <td>"+str(params['UserID'])+"</td>\n")
            out.write("    <td>"+str(params['UserID'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>AISversion</td>\n")
        out.write("<td>uint</td>\n")
        if 'AISversion' in params:
            out.write("    <td>"+str(params['AISversion'])+"</td>\n")
            out.write("    <td>"+str(params['AISversion'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>IMOnumber</td>\n")
        out.write("<td>uint</td>\n")
        if 'IMOnumber' in params:
            out.write("    <td>"+str(params['IMOnumber'])+"</td>\n")
            out.write("    <td>"+str(params['IMOnumber'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>callsign</td>\n")
        out.write("<td>aisstr6</td>\n")
        if 'callsign' in params:
            out.write("    <td>"+str(params['callsign'])+"</td>\n")
            out.write("    <td>"+str(params['callsign'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>name</td>\n")
        out.write("<td>aisstr6</td>\n")
        if 'name' in params:
            out.write("    <td>"+str(params['name'])+"</td>\n")
            out.write("    <td>"+str(params['name'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>shipandcargo</td>\n")
        out.write("<td>uint</td>\n")
        if 'shipandcargo' in params:
            out.write("    <td>"+str(params['shipandcargo'])+"</td>\n")
            if str(params['shipandcargo']) in shipandcargoDecodeLut:
                out.write("<td>"+shipandcargoDecodeLut[str(params['shipandcargo'])]+"</td>")
            else:
                out.write("<td><i>Missing LUT entry</i></td>")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>dimA</td>\n")
        out.write("<td>uint</td>\n")
        if 'dimA' in params:
            out.write("    <td>"+str(params['dimA'])+"</td>\n")
            out.write("    <td>"+str(params['dimA'])+"</td>\n")
        out.write("<td>m</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>dimB</td>\n")
        out.write("<td>uint</td>\n")
        if 'dimB' in params:
            out.write("    <td>"+str(params['dimB'])+"</td>\n")
            out.write("    <td>"+str(params['dimB'])+"</td>\n")
        out.write("<td>m</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>dimC</td>\n")
        out.write("<td>uint</td>\n")
        if 'dimC' in params:
            out.write("    <td>"+str(params['dimC'])+"</td>\n")
            if str(params['dimC']) in dimCDecodeLut:
                out.write("<td>"+dimCDecodeLut[str(params['dimC'])]+"</td>")
            else:
                out.write("<td><i>Missing LUT entry</i></td>")
        out.write("<td>m</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>dimD</td>\n")
        out.write("<td>uint</td>\n")
        if 'dimD' in params:
            out.write("    <td>"+str(params['dimD'])+"</td>\n")
            if str(params['dimD']) in dimDDecodeLut:
                out.write("<td>"+dimDDecodeLut[str(params['dimD'])]+"</td>")
            else:
                out.write("<td><i>Missing LUT entry</i></td>")
        out.write("<td>m</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>fixtype</td>\n")
        out.write("<td>uint</td>\n")
        if 'fixtype' in params:
            out.write("    <td>"+str(params['fixtype'])+"</td>\n")
            if str(params['fixtype']) in fixtypeDecodeLut:
                out.write("<td>"+fixtypeDecodeLut[str(params['fixtype'])]+"</td>")
            else:
                out.write("<td><i>Missing LUT entry</i></td>")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>ETAmonth</td>\n")
        out.write("<td>uint</td>\n")
        if 'ETAmonth' in params:
            out.write("    <td>"+str(params['ETAmonth'])+"</td>\n")
            out.write("    <td>"+str(params['ETAmonth'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>ETAday</td>\n")
        out.write("<td>uint</td>\n")
        if 'ETAday' in params:
            out.write("    <td>"+str(params['ETAday'])+"</td>\n")
            out.write("    <td>"+str(params['ETAday'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>ETAhour</td>\n")
        out.write("<td>uint</td>\n")
        if 'ETAhour' in params:
            out.write("    <td>"+str(params['ETAhour'])+"</td>\n")
            out.write("    <td>"+str(params['ETAhour'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>ETAminute</td>\n")
        out.write("<td>uint</td>\n")
        if 'ETAminute' in params:
            out.write("    <td>"+str(params['ETAminute'])+"</td>\n")
            out.write("    <td>"+str(params['ETAminute'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>draught</td>\n")
        out.write("<td>udecimal</td>\n")
        if 'draught' in params:
            out.write("    <td>"+str(params['draught'])+"</td>\n")
            if str(params['draught']) in draughtDecodeLut:
                out.write("<td>"+draughtDecodeLut[str(params['draught'])]+"</td>")
            else:
                out.write("<td><i>Missing LUT entry</i></td>")
        out.write("<td>m</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>destination</td>\n")
        out.write("<td>aisstr6</td>\n")
        if 'destination' in params:
            out.write("    <td>"+str(params['destination'])+"</td>\n")
            out.write("    <td>"+str(params['destination'])+"</td>\n")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>dte</td>\n")
        out.write("<td>uint</td>\n")
        if 'dte' in params:
            out.write("    <td>"+str(params['dte'])+"</td>\n")
            if str(params['dte']) in dteDecodeLut:
                out.write("<td>"+dteDecodeLut[str(params['dte'])]+"</td>")
            else:
                out.write("<td><i>Missing LUT entry</i></td>")
        out.write("</tr>\n")
        out.write("\n")
        out.write("<tr>\n")
        out.write("<td>Spare</td>\n")
        out.write("<td>uint</td>\n")
        if 'Spare' in params:
            out.write("    <td>"+str(params['Spare'])+"</td>\n")
            out.write("    <td>"+str(params['Spare'])+"</td>\n")
        out.write("</tr>\n")
        out.write("</table>\n")

def printFields(params,
                out=sys.stdout,
                format='std',
                fieldList=None):
    '''Print a shipdata message to stdout.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 5 (field automatically set to "5")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - AISversion(uint): Compliant with what edition.  0 is the first edition.
      - IMOnumber(uint): vessel identification number (different than mmsi)
      - callsign(aisstr6): Ship radio call sign
      - name(aisstr6): Vessel name
      - shipandcargo(uint): what
      - dimA(uint): Distance from bow to reference position
      - dimB(uint): Distance from reference position to stern
      - dimC(uint): Distance from port side to reference position
      - dimD(uint): Distance from reference position to starboard side
      - fixtype(uint): Method used for positioning
      - ETAmonth(uint): Estimated time of arrival - month
      - ETAday(uint): Estimated time of arrival - day
      - ETAhour(uint): Estimated time of arrival - hour
      - ETAminute(uint): Estimated time of arrival - minutes
      - draught(udecimal): Maximum present static draught
      - destination(aisstr6): Where is the vessel going
      - dte(uint): Data terminal ready
      - Spare(uint): Reserved for definition by a regional authority. (field automatically set to "0")
    @param params: Dictionary of field names/values.
    @param out: File like object to write to.
    @rtype: stdout
    @return: text to out
    '''

    if 'std'==format:
        out.write("shipdata:\n")
        if 'MessageID' in params: out.write("    MessageID:        "+str(params['MessageID'])+"\n")
        if 'RepeatIndicator' in params: out.write("    RepeatIndicator:  "+str(params['RepeatIndicator'])+"\n")
        if 'UserID' in params: out.write("    UserID:           "+str(params['UserID'])+"\n")
        if 'AISversion' in params: out.write("    AISversion:       "+str(params['AISversion'])+"\n")
        if 'IMOnumber' in params: out.write("    IMOnumber:        "+str(params['IMOnumber'])+"\n")
        if 'callsign' in params: out.write("    callsign:         "+str(params['callsign'])+"\n")
        if 'name' in params: out.write("    name:             "+str(params['name'])+"\n")
        if 'shipandcargo' in params: out.write("    shipandcargo:     "+str(params['shipandcargo'])+"\n")
        if 'dimA' in params: out.write("    dimA:             "+str(params['dimA'])+"\n")
        if 'dimB' in params: out.write("    dimB:             "+str(params['dimB'])+"\n")
        if 'dimC' in params: out.write("    dimC:             "+str(params['dimC'])+"\n")
        if 'dimD' in params: out.write("    dimD:             "+str(params['dimD'])+"\n")
        if 'fixtype' in params: out.write("    fixtype:          "+str(params['fixtype'])+"\n")
        if 'ETAmonth' in params: out.write("    ETAmonth:         "+str(params['ETAmonth'])+"\n")
        if 'ETAday' in params: out.write("    ETAday:           "+str(params['ETAday'])+"\n")
        if 'ETAhour' in params: out.write("    ETAhour:          "+str(params['ETAhour'])+"\n")
        if 'ETAminute' in params: out.write("    ETAminute:        "+str(params['ETAminute'])+"\n")
        if 'draught' in params: out.write("    draught:          "+str(params['draught'])+"\n")
        if 'destination' in params: out.write("    destination:      "+str(params['destination'])+"\n")
        if 'dte' in params: out.write("    dte:              "+str(params['dte'])+"\n")
        if 'Spare' in params: out.write("    Spare:            "+str(params['Spare'])+"\n")
        elif 'csv'==format:
                if None == params.fieldList:
                           params.fieldList = fieldList
                needComma = False;
                for field in fieldList:
                        if needComma: out.write(',')
                        needComma = True
                        if field in params:
                                out.write(str(params[field]))
                        # else: leave it empty
                out.write("\n")
    elif 'html'==format:
        printHtml(params,out)
    else:
        print("ERROR: unknown format:",format)
        assert False
    return # Nothing to return

RepeatIndicatorEncodeLut = {
    'default':'0',
    'do not repeat any more':'3',
    } #RepeatIndicatorEncodeLut

RepeatIndicatorDecodeLut = {
    '0':'default',
    '3':'do not repeat any more',
    } # RepeatIndicatorEncodeLut

shipandcargoEncodeLut = {
    'Wing in ground (WIG), all ships of this type':'20',
    'Wing in ground (WIG), Hazardous catagory A':'21',
    'Wing in ground (WIG), Hazardous catagory B':'22',
    'Wing in ground (WIG), Hazardous catagory C':'23',
    'Wing in ground (WIG), Hazardous catagory D':'24',
    'Wing in ground (WIG), Reserved for future use':'25',
    'Wing in ground (WIG), Reserved for future use':'26',
    'Wing in ground (WIG), Reserved for future use':'27',
    'Wing in ground (WIG), Reserved for future use':'28',
    'Wing in ground (WIG), No additional information':'29',
    'fishing':'30',
    'towing':'31',
    'towing length exceeds 200m or breadth exceeds 25m':'32',
    'dredging or underwater ops':'33',
    'diving ops':'34',
    'military ops':'35',
    'sailing':'36',
    'pleasure craft':'37',
    'reserved':'38',
    'reserved':'39',
    'High speed craft (HSC), all ships of this type':'40',
    'High speed craft (HSC), Hazardous catagory A':'41',
    'High speed craft (HSC), Hazardous catagory B':'42',
    'High speed craft (HSC), Hazardous catagory C':'43',
    'High speed craft (HSC), Hazardous catagory D':'44',
    'High speed craft (HSC), Reserved for future use':'45',
    'High speed craft (HSC), Reserved for future use':'46',
    'High speed craft (HSC), Reserved for future use':'47',
    'High speed craft (HSC), Reserved for future use':'48',
    'High speed craft (HSC), No additional information':'49',
    'pilot vessel':'50',
    'search and rescue vessel':'51',
    'tug':'52',
    'port tender':'53',
    'anti-polution equipment':'54',
    'law enforcement':'55',
    'spare - local vessel':'56',
    'spare - local vessel':'57',
    'medical transport':'58',
    'ship according to RR Resolution No. 18':'59',
    'passenger, all ships of this type':'60',
    'passenger, Hazardous catagory A':'61',
    'passenger, Hazardous catagory B':'62',
    'passenger, Hazardous catagory C':'63',
    'passenger, Hazardous catagory D':'64',
    'passenger, Reserved for future use':'65',
    'passenger, Reserved for future use':'66',
    'passenger, Reserved for future use':'67',
    'passenger, Reserved for future use':'68',
    'passenger, No additional information':'69',
    'cargo, all ships of this type':'70',
    'cargo, Hazardous catagory A':'71',
    'cargo, Hazardous catagory B':'72',
    'cargo, Hazardous catagory C':'73',
    'cargo, Hazardous catagory D':'74',
    'cargo, Reserved for future use':'75',
    'cargo, Reserved for future use':'76',
    'cargo, Reserved for future use':'77',
    'cargo, Reserved for future use':'78',
    'cargo, No additional information':'79',
    'tanker, all ships of this type':'80',
    'tanker, Hazardous catagory A':'81',
    'tanker, Hazardous catagory B':'82',
    'tanker, Hazardous catagory C':'83',
    'tanker, Hazardous catagory D':'84',
    'tanker, Reserved for future use':'85',
    'tanker, Reserved for future use':'86',
    'tanker, Reserved for future use':'87',
    'tanker, Reserved for future use':'88',
    'tanker, No additional information':'89',
    'other type, all ships of this type':'90',
    'other type, Hazardous catagory A':'91',
    'other type, Hazardous catagory B':'92',
    'other type, Hazardous catagory C':'93',
    'other type, Hazardous catagory D':'94',
    'other type, Reserved for future use':'95',
    'other type, Reserved for future use':'96',
    'other type, Reserved for future use':'97',
    'other type, Reserved for future use':'98',
    'other type, No additional information':'99',
    } #shipandcargoEncodeLut

shipandcargoDecodeLut = {
    '20':'Wing in ground (WIG), all ships of this type',
    '21':'Wing in ground (WIG), Hazardous catagory A',
    '22':'Wing in ground (WIG), Hazardous catagory B',
    '23':'Wing in ground (WIG), Hazardous catagory C',
    '24':'Wing in ground (WIG), Hazardous catagory D',
    '25':'Wing in ground (WIG), Reserved for future use',
    '26':'Wing in ground (WIG), Reserved for future use',
    '27':'Wing in ground (WIG), Reserved for future use',
    '28':'Wing in ground (WIG), Reserved for future use',
    '29':'Wing in ground (WIG), No additional information',
    '30':'fishing',
    '31':'towing',
    '32':'towing length exceeds 200m or breadth exceeds 25m',
    '33':'dredging or underwater ops',
    '34':'diving ops',
    '35':'military ops',
    '36':'sailing',
    '37':'pleasure craft',
    '38':'reserved',
    '39':'reserved',
    '40':'High speed craft (HSC), all ships of this type',
    '41':'High speed craft (HSC), Hazardous catagory A',
    '42':'High speed craft (HSC), Hazardous catagory B',
    '43':'High speed craft (HSC), Hazardous catagory C',
    '44':'High speed craft (HSC), Hazardous catagory D',
    '45':'High speed craft (HSC), Reserved for future use',
    '46':'High speed craft (HSC), Reserved for future use',
    '47':'High speed craft (HSC), Reserved for future use',
    '48':'High speed craft (HSC), Reserved for future use',
    '49':'High speed craft (HSC), No additional information',
    '50':'pilot vessel',
    '51':'search and rescue vessel',
    '52':'tug',
    '53':'port tender',
    '54':'anti-polution equipment',
    '55':'law enforcement',
    '56':'spare - local vessel',
    '57':'spare - local vessel',
    '58':'medical transport',
    '59':'ship according to RR Resolution No. 18',
    '60':'passenger, all ships of this type',
    '61':'passenger, Hazardous catagory A',
    '62':'passenger, Hazardous catagory B',
    '63':'passenger, Hazardous catagory C',
    '64':'passenger, Hazardous catagory D',
    '65':'passenger, Reserved for future use',
    '66':'passenger, Reserved for future use',
    '67':'passenger, Reserved for future use',
    '68':'passenger, Reserved for future use',
    '69':'passenger, No additional information',
    '70':'cargo, all ships of this type',
    '71':'cargo, Hazardous catagory A',
    '72':'cargo, Hazardous catagory B',
    '73':'cargo, Hazardous catagory C',
    '74':'cargo, Hazardous catagory D',
    '75':'cargo, Reserved for future use',
    '76':'cargo, Reserved for future use',
    '77':'cargo, Reserved for future use',
    '78':'cargo, Reserved for future use',
    '79':'cargo, No additional information',
    '80':'tanker, all ships of this type',
    '81':'tanker, Hazardous catagory A',
    '82':'tanker, Hazardous catagory B',
    '83':'tanker, Hazardous catagory C',
    '84':'tanker, Hazardous catagory D',
    '85':'tanker, Reserved for future use',
    '86':'tanker, Reserved for future use',
    '87':'tanker, Reserved for future use',
    '88':'tanker, Reserved for future use',
    '89':'tanker, No additional information',
    '90':'other type, all ships of this type',
    '91':'other type, Hazardous catagory A',
    '92':'other type, Hazardous catagory B',
    '93':'other type, Hazardous catagory C',
    '94':'other type, Hazardous catagory D',
    '95':'other type, Reserved for future use',
    '96':'other type, Reserved for future use',
    '97':'other type, Reserved for future use',
    '98':'other type, Reserved for future use',
    '99':'other type, No additional information',
    } # shipandcargoEncodeLut

dimCEncodeLut = {
    '63 m or greater':'63',
    } #dimCEncodeLut

dimCDecodeLut = {
    '63':'63 m or greater',
    } # dimCEncodeLut

dimDEncodeLut = {
    '63 m or greater':'63',
    } #dimDEncodeLut

dimDDecodeLut = {
    '63':'63 m or greater',
    } # dimDEncodeLut

fixtypeEncodeLut = {
    'undefined':'0',
    'GPS':'1',
    'GLONASS':'2',
    'combined GPS/GLONASS':'3',
    'Loran-C':'4',
    'Chayka':'5',
    'integrated navigation system':'6',
    'surveyed':'7',
    } #fixtypeEncodeLut

fixtypeDecodeLut = {
    '0':'undefined',
    '1':'GPS',
    '2':'GLONASS',
    '3':'combined GPS/GLONASS',
    '4':'Loran-C',
    '5':'Chayka',
    '6':'integrated navigation system',
    '7':'surveyed',
    } # fixtypeEncodeLut

draughtEncodeLut = {
    '25.5 m or greater':'25.5',
    } #draughtEncodeLut

draughtDecodeLut = {
    '25.5':'25.5 m or greater',
    } # draughtEncodeLut

dteEncodeLut = {
    'available':'0',
    'not available':'1',
    } #dteEncodeLut

dteDecodeLut = {
    '0':'available',
    '1':'not available',
    } # dteEncodeLut


######################################################################
# UNIT TESTING
######################################################################
def testParams():
    '''Return a params file base on the testvalue tags.
    @rtype: dict
    @return: params based on testvalue tags
    '''
    params = {}
    params['MessageID'] = 5
    params['RepeatIndicator'] = 1
    params['UserID'] = 1193046
    params['AISversion'] = 0
    params['IMOnumber'] = 3210
    params['callsign'] = 'PIRATE1'
    params['name'] = 'BLACK PEARL@@@@@@@@@'
    params['shipandcargo'] = 55
    params['dimA'] = 10
    params['dimB'] = 11
    params['dimC'] = 12
    params['dimD'] = 13
    params['fixtype'] = 1
    params['ETAmonth'] = 2
    params['ETAday'] = 28
    params['ETAhour'] = 9
    params['ETAminute'] = 54
    params['draught'] = Decimal('21.1')
    params['destination'] = 'NOWHERE@@@@@@@@@@@@@'
    params['dte'] = 0
    params['Spare'] = 0

    return params

class Testshipdata(unittest.TestCase):
    '''Use testvalue tag text from each type to build test case the shipdata message'''
    def testEncodeDecode(self):

        params = testParams()
        bits   = encode(params)
        r      = decode(bits)

        # Check that each parameter came through ok.
        self.failUnlessEqual(r['MessageID'],params['MessageID'])
        self.failUnlessEqual(r['RepeatIndicator'],params['RepeatIndicator'])
        self.failUnlessEqual(r['UserID'],params['UserID'])
        self.failUnlessEqual(r['AISversion'],params['AISversion'])
        self.failUnlessEqual(r['IMOnumber'],params['IMOnumber'])
        self.failUnlessEqual(r['callsign'],params['callsign'])
        self.failUnlessEqual(r['name'],params['name'])
        self.failUnlessEqual(r['shipandcargo'],params['shipandcargo'])
        self.failUnlessEqual(r['dimA'],params['dimA'])
        self.failUnlessEqual(r['dimB'],params['dimB'])
        self.failUnlessEqual(r['dimC'],params['dimC'])
        self.failUnlessEqual(r['dimD'],params['dimD'])
        self.failUnlessEqual(r['fixtype'],params['fixtype'])
        self.failUnlessEqual(r['ETAmonth'],params['ETAmonth'])
        self.failUnlessEqual(r['ETAday'],params['ETAday'])
        self.failUnlessEqual(r['ETAhour'],params['ETAhour'])
        self.failUnlessEqual(r['ETAminute'],params['ETAminute'])
        self.failUnlessAlmostEqual(r['draught'],params['draught'],1)
        self.failUnlessEqual(r['destination'],params['destination'])
        self.failUnlessEqual(r['dte'],params['dte'])
        self.failUnlessEqual(r['Spare'],params['Spare'])

def addMsgOptions(parser):
    parser.add_option('-d','--decode',dest='doDecode',default=False,action='store_true',
                help='decode a "shipdata" AIS message')
    parser.add_option('-e','--encode',dest='doEncode',default=False,action='store_true',
                help='encode a "shipdata" AIS message')
    parser.add_option('--RepeatIndicator-field', dest='RepeatIndicatorField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--UserID-field', dest='UserIDField',metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--AISversion-field', dest='AISversionField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--IMOnumber-field', dest='IMOnumberField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--callsign-field', dest='callsignField',default='@@@@@@@',metavar='aisstr6',type='string'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--name-field', dest='nameField',default='@@@@@@@@@@@@@@@@@@@@',metavar='aisstr6',type='string'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--shipandcargo-field', dest='shipandcargoField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--dimA-field', dest='dimAField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--dimB-field', dest='dimBField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--dimC-field', dest='dimCField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--dimD-field', dest='dimDField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--fixtype-field', dest='fixtypeField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--ETAmonth-field', dest='ETAmonthField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--ETAday-field', dest='ETAdayField',default=0,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--ETAhour-field', dest='ETAhourField',default=24,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--ETAminute-field', dest='ETAminuteField',default=60,metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--draught-field', dest='draughtField',default=Decimal('0'),metavar='udecimal',type='string'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--destination-field', dest='destinationField',default='@@@@@@@@@@@@@@@@@@@@',metavar='aisstr6',type='string'
        ,help='Field parameter value [default: %default]')
    parser.add_option('--dte-field', dest='dteField',metavar='uint',type='int'
        ,help='Field parameter value [default: %default]')

def test_auth():
    from optparse import OptionParser
    parser = OptionParser(usage="%prog [options]")

    parser.add_option('--unit-test',dest='unittest',default=False,action='store_true',
        help='run the unit tests')
    parser.add_option('-v','--verbose',dest='verbose',default=False,action='store_true',
        help='Make the test output verbose')

    # FIX: remove nmea from binary messages.  No way to build the whole packet?
    # FIX: or build the surrounding msg 8 for a broadcast?
    typeChoices = ('binary','nmeapayload','nmea') # FIX: what about a USCG type message?
    parser.add_option('-t', '--type', choices=typeChoices, type='choice',
        dest='ioType', default='nmeapayload',
        help='What kind of string to write for encoding ('+', '.join(typeChoices)+') [default: %default]')


    outputChoices = ('std','html','csv','sql' )
    parser.add_option('-T', '--output-type', choices=outputChoices,
        type='choice', dest='outputType', default='std',
        help='What kind of string to output ('+', '.join(outputChoices)+') '
        '[default: %default]')

    parser.add_option('-o','--output',dest='outputFileName',default=None,
        help='Name of the python file to write [default: stdout]')

    parser.add_option('-f', '--fields', dest='fieldList', default=None,
        action='append', choices=fieldList,
        help='Which fields to include in the output.  Currently only for csv '
        'output [default: all]')

    parser.add_option('-p', '--print-csv-field-list', dest='printCsvfieldList',
        default=False,action='store_true',
        help='Print the field name for csv')

    parser.add_option('-c', '--sql-create', dest='sqlCreate', default=False,
        action='store_true',
        help='Print out an sql create command for the table.')

    parser.add_option('--latex-table', dest='latexDefinitionTable',
        default=False,action='store_true',
        help='Print a LaTeX table of the type')

    parser.add_option('--text-table', dest='textDefinitionTable', default=False,
        action='store_true',
        help='Print delimited table of the type (for Word table importing)')

    parser.add_option('--delimt-text-table', dest='delimTextDefinitionTable',
        default='    ',
        help='Delimiter for text table [default: \'%default\'] '
        '(for Word table importing)')

    dbChoices = ('sqlite','postgres')
    parser.add_option('-D', '--db-type', dest='dbType', default='postgres',
        choices=dbChoices,type='choice',
        help='What kind of database ('+', '.join(dbChoices)+') '
        '[default: %default]')

    addMsgOptions(parser)

    options, args = parser.parse_args()

    if options.unittest:
            sys.argv = [sys.argv[0]]
            if options.verbose: sys.argv.append('-v')
            unittest.main()

    outfile = sys.stdout
    if None!=options.outputFileName:
            outfile = open(options.outputFileName,'w')


    if options.doEncode:
        # Make sure all non required options are specified.
        if None==options.RepeatIndicatorField: parser.error("missing value for RepeatIndicatorField")
        if None==options.UserIDField: parser.error("missing value for UserIDField")
        if None==options.AISversionField: parser.error("missing value for AISversionField")
        if None==options.IMOnumberField: parser.error("missing value for IMOnumberField")
        if None==options.callsignField: parser.error("missing value for callsignField")
        if None==options.nameField: parser.error("missing value for nameField")
        if None==options.shipandcargoField: parser.error("missing value for shipandcargoField")
        if None==options.dimAField: parser.error("missing value for dimAField")
        if None==options.dimBField: parser.error("missing value for dimBField")
        if None==options.dimCField: parser.error("missing value for dimCField")
        if None==options.dimDField: parser.error("missing value for dimDField")
        if None==options.fixtypeField: parser.error("missing value for fixtypeField")
        if None==options.ETAmonthField: parser.error("missing value for ETAmonthField")
        if None==options.ETAdayField: parser.error("missing value for ETAdayField")
        if None==options.ETAhourField: parser.error("missing value for ETAhourField")
        if None==options.ETAminuteField: parser.error("missing value for ETAminuteField")
        if None==options.draughtField: parser.error("missing value for draughtField")
        if None==options.destinationField: parser.error("missing value for destinationField")
        if None==options.dteField: parser.error("missing value for dteField")
    msgDict = {
        'MessageID': '5',
        'RepeatIndicator': options.RepeatIndicatorField,
        'UserID': options.UserIDField,
        'AISversion': options.AISversionField,
        'IMOnumber': options.IMOnumberField,
        'callsign': options.callsignField,
        'name': options.nameField,
        'shipandcargo': options.shipandcargoField,
        'dimA': options.dimAField,
        'dimB': options.dimBField,
        'dimC': options.dimCField,
        'dimD': options.dimDField,
        'fixtype': options.fixtypeField,
        'ETAmonth': options.ETAmonthField,
        'ETAday': options.ETAdayField,
        'ETAhour': options.ETAhourField,
        'ETAminute': options.ETAminuteField,
        'draught': options.draughtField,
        'destination': options.destinationField,
        'dte': options.dteField,
        'Spare': '0',
    }

    bits = encode(msgDict)
    if 'binary' == options.io:
        print(str(bits))
    elif 'nmeapayload'==options.ioType:
        # FIX: figure out if this might be necessary at compile time
        bitLen=len(bits)
        if bitLen % 6 != 0:
            bits = bits + BitVector(size=(6 - (bitLen%6)))  # Pad out to multiple of 6
        print(aisbinary.bitvectoais6(bits)[0])

    # FIX: Do not emit this option for the binary message payloads.  Does not make sense.
    elif 'nmea' == options.ioType:
        nmea = uscg.create_nmea(bits)
        print(nmea)
    else:
        sys.exit('ERROR: unknown ioType.  Help!')


        if options.sqlCreate:
                sqlCreateStr(outfile,options.fieldList,dbType=options.dbType)

        if options.latexDefinitionTable:
                latexDefinitionTable(outfile)

        # For conversion to word tables
        if options.textDefinitionTable:
                textDefinitionTable(outfile,options.delimTextDefinitionTable)

        if options.printCsvfieldList:
                # Make a csv separated list of fields that will be displayed for csv
                if None == options.fieldList: options.fieldList = fieldList
                import StringIO
                buf = StringIO.StringIO()
                for field in options.fieldList:
                        buf.write(field+',')
                result = buf.getvalue()
                if result[-1] == ',': print(result[:-1])
                else: print(result)

        if options.doDecode:
                if len(args)==0: args = sys.stdin
                for msg in args:
                        bv = None

                        if msg[0] in ('$','!') and msg[3:6] in ('VDM','VDO'):
                                # Found nmea
                                # FIX: do checksum
                                bv = aisbinary.ais6tobitvec(msg.split(',')[5])
                        else: # either binary or nmeapayload... expect mostly nmeapayloads
                                # assumes that an all 0 and 1 string can not be a nmeapayload
                                binaryMsg=True
                                for c in msg:
                                        if c not in ('0','1'):
                                                binaryMsg=False
                                                break
                                if binaryMsg:
                                        bv = BitVector(bitstring=msg)
                                else: # nmeapayload
                                        bv = aisbinary.ais6tobitvec(msg)

                        printFields(decode(bv)
                                    ,out=outfile
                                    ,format=options.outputType
                                    ,fieldList=options.fieldList
                                    ,dbType=options.dbType
                                    )

def test_this():
    msg24_a = {}
    msg24_b = {}
    msg24_aux = {}
#-----------------------------------
    msg24_a['MessageID'] = 24
    msg24_a['RepeatIndicator'] = 1
    msg24_a['MMSI'] = 5678844

#-----------------------------------
    msg24_b['MessageID'] = 24
    msg24_b['RepeatIndicator'] = 1
    msg24_b['MMSI'] = 119304633
    msg24_b['shipandcargo'] = 55

    msg24_b['vendor_id'] = "VND"
    msg24_b['unit_model'] = 1
    msg24_b['serial_num'] = 2
    msg24_b['callsign'] = 'FGRTUSP'
    msg24_b['name'] = 'PTYDRPTYDRTFGRDTFGRD'

    msg24_b['dimA'] = 10
    msg24_b['dimB'] = 11
    msg24_b['dimC'] = 12
    msg24_b['dimD'] = 13

    msg24_b['mother_ship_mmsi'] = 0
    msg24_b['Spare'] = 0
# -----------------------------------
    msg24_aux['MessageID'] = 24
    msg24_aux['RepeatIndicator'] = 1
    msg24_aux['MMSI'] = 982031010
    msg24_aux['shipandcargo'] = 55

    msg24_aux['vendor_id'] = "VND"
    msg24_aux['unit_model'] = 1
    msg24_aux['serial_num'] = 2
    msg24_aux['callsign'] = 'FGRTUSP'
    msg24_aux['name'] = 'PTYDRPTYDRTFGRDTFGRD'

    msg24_aux['mother_ship_mmsi'] =12039567
    msg24_aux['Spare'] = 0
# -----------------------------------

    bits_a = encode(msg24_a,
                    type="A")
    bits_b = encode(msg24_b,
                    type="B")
    bits_aux = encode(msg24_aux,
                    type="aux")
    nmea_a = uscg.create_nmea(bits_a,
                            message_type=24,
                              aisChannel="A")
    nmea_b = uscg.create_nmea(bits_b,
                            message_type=24,
                              aisChannel="B")
    nmea_aux = uscg.create_nmea(bits_aux,
                                message_type=24,
                                aisChannel="B")
    return

############################################################
if __name__=='__main__':
    test_this()
