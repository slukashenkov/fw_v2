#!/usr/bin/env python
"""Python functions to serialize/deserialize binary messages.

Need to then wrap these functions with the outer AIS packet and then
convert the whole binary blob to a NMEA string.  Those functions are
not currently provided in this file.

serialize: python to ais binary
deserialize: ais binary to python

The generated code uses translators.py, binary.py, and aisstring.py
which should be packaged with the resulting files.

"Types 1, 2 and 3: Position Report Class A
Type 1, 2 and 3 messages share a common reporting structure for navigational information; we’ll call it the Common Navigation Block (CNB).
This is the information most likely to be of interest for decoding software. Total of 168 bits, occupying one AIVDM sentence."

Common Navigation Block

Field	Len	        Description	                Member	        T	        Units
0-5	     6	        Message Type	            type	        u	        Constant: 1-3
43287	2	        Repeat Indicator	        repeat	        u	        Message repeat count
13728	30	        MMSI	                    mmsi	        u	        9 decimal digits
38-41	4	        Navigation Status	        status	        e	        See "Navigation Status"
42-49	8	        Rate of Turn (ROT)	        turn	        I3	        See below
50-59	10	        Speed Over Ground (SOG)	    speed	        U1	        See below
60-60	1	        Position Accuracy	        accuracy	    b	S       ee below
61-88	28	        Longitude	                lon	            I4	        Minutes/10000 (see below)
89-115	27	        Latitude	                lat	            I4	        Minutes/10000 (see below)
116-127	12	        Course Over Ground (COG)	course	        U1	        Relative to true north, to 0.1 degree precision
128-136	9	        True Heading (HDG)	        heading	        u	        0 to 359 degrees, 511 = not available.
137-142	6	        Time Stamp	                second	        u	        Second of UTC timestamp
143-144	2	        Maneuver Indicator	        maneuver	    e	        See "Maneuver Indicator"
145-147	3	        Spare		                                x	        Not used
148-148	1	        RAIM flag	                raim	        b	        See below
149-167	19	        Radio status	            radio	        u	        See below

Navigation Status
0	Under way using engine
1	At anchor
2	Not under command
3	Restricted manoeuverability
4	Constrained by her draught
5	Moored
6	Aground
7	Engaged in Fishing
8	Under way sailing
9	Reserved for future amendment of Navigational Status for HSC
10	Reserved for future amendment of Navigational Status for WIG
11	Reserved for future use
12	Reserved for future use
13	Reserved for future use
14	AIS-SART is active
15	Not defined (default)

"""
import sys
import unittest
from decimal import Decimal

from test_bl.test_trassa_plugin.structs_trassa.aisutils import aisbinary
from test_bl.test_trassa_plugin.structs_trassa.aisutils import uscg
from test_bl.test_trassa_plugin.structs_trassa.aisutils.BitVector import BitVector

# FIX: check to see if these will be needed
# Optimization of the true and false bit.
TrueBV = BitVector(bitstring = "1")
FalseBV = BitVector(bitstring = "0")

fieldList = (
    'MessageID',
    'RepeatIndicator',
    'UserID',
    'NavigationStatus',
    'ROT',
    'SOG',
    'PositionAccuracy',
    'longitude',
    'latitude',
    'COG',
    'TrueHeading',
    'TimeStamp',
    'RegionalReserved',
    'Spare',
    'RAIM',
    'state_syncstate',
    'state_slottimeout',
    'state_slotoffset',
)


def encode (params):
    """
    Create a position binary message payload to pack into an AIS Msg position.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 1 (field automatically set to "1")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - MMSI(uint): Unique ship identification number (MMSI)
      - NavigationStatus(uint): What is the vessel doing
      - ROT(int): RateOfTurn
      - SOG(udecimal): Speed over ground
      - PositionAccuracy(uint): Accuracy of positioning fixes
      - longitude(decimal): Location of the vessel  East West location
      - latitude(decimal): Location of the vessel  North South location
      - COG(udecimal): Course over ground
      - TrueHeading(uint): True heading (relative to true North)
      - TimeStamp(uint): UTC second when the report was generated
      - RegionalReserved(uint): Reserved for definition by a regional authority. (field automatically set to "0")
      - Spare(uint): Not used.  Should be set to zero. (field automatically set to "0")
      - RAIM(bool): Receiver autonomous integrity monitoring flag
      - state_syncstate(uint): Communications State - SOTDMA  Sycronization state
      - state_slottimeout(uint): Communications State - SOTDMA  Frames remaining until a new slot is selected
      - state_slotoffset(uint): Communications State - SOTDMA  In what slot will the next transmission occur. BROKEN

    @param params: Dictionary of field names/values.  Throws a ValueError exception if required is missing

    @rtype: BitVector
    @return: encoded binary message (for binary messages, this needs to be wrapped in a msg 8
    @note: The returned bits may not be 6 bit aligned.  It is up to you to pad out the bits.
    """
    
    bvList = []
    bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = 1), 6))
    
    if 'RepeatIndicator' in params:
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = params['RepeatIndicator']), 2))
    else:
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = 0), 2))
    
    bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = params['MMSI']), 30))
    
    if 'NavigationStatus' in params:
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = params['NavigationStatus']), 4))
    else:
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = 15), 4))
    
    if 'ROT' in params:
        bvList.append(aisbinary.bvFromSignedInt(params['ROT'], 8))
    else:
        bvList.append(aisbinary.bvFromSignedInt(-128, 8))
    
    if 'SOG' in params:
        bvList.append(
            aisbinary.setBitVectorSize(BitVector(intVal = int((Decimal(params['SOG']) * Decimal('10')))), 10))
    else:
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = int(1023)), 10))
    
    bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = params['PositionAccuracy']), 1))
    
    if 'longitude' in params:
        bvList.append(aisbinary.bvFromSignedInt(int(Decimal(params['longitude']) * Decimal('600000')), 28))
    else:
        bvList.append(aisbinary.bvFromSignedInt(108600000, 28))
    
    if 'latitude' in params:
        bvList.append(aisbinary.bvFromSignedInt(int(Decimal(params['latitude']) * Decimal('600000')), 27))
    else:
        bvList.append(aisbinary.bvFromSignedInt(54600000, 27))
    if 'COG' in params:
        bvList.append(
            aisbinary.setBitVectorSize(BitVector(intVal = int((Decimal(params['COG']) * Decimal('10')))), 12))
    else:
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = int(3600)), 12))
    if 'TrueHeading' in params:
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = params['TrueHeading']), 9))
    else:
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = 511), 9))
    if 'TimeStamp' in params:
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = params['TimeStamp']), 6))
    else:
        bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = 60), 6))
    
    bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = 0), 4))
    bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = 0), 1))
    
    if params["RAIM"]:
        bvList.append(TrueBV)
    else:
        bvList.append(FalseBV)
    
    bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = params['state_syncstate']), 2))
    bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = params['state_slottimeout']), 3))
    bvList.append(aisbinary.setBitVectorSize(BitVector(intVal = params['state_slotoffset']), 14))
    
    return aisbinary.joinBV(bvList)


def decode (bv, validate = False):
    """Unpack a position message.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 1 (field automatically set to "1")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - NavigationStatus(uint): What is the vessel doing
      - ROT(int): RateOfTurn
      - SOG(udecimal): Speed over ground
      - PositionAccuracy(uint): Accuracy of positioning fixes
      - longitude(decimal): Location of the vessel  East West location
      - latitude(decimal): Location of the vessel  North South location
      - COG(udecimal): Course over ground
      - TrueHeading(uint): True heading (relative to true North)
      - TimeStamp(uint): UTC second when the report was generated
      - RegionalReserved(uint): Reserved for definition by a regional authority. (field automatically set to "0")
      - Spare(uint): Not used.  Should be set to zero. (field automatically set to "0")
      - RAIM(bool): Receiver autonomous integrity monitoring flag
      - state_syncstate(uint): Communications State - SOTDMA  Sycronization state
      - state_slottimeout(uint): Communications State - SOTDMA  Frames remaining until a new slot is selected
      - state_slotoffset(uint): Communications State - SOTDMA  In what slot will the next transmission occur. BROKEN
    @type bv: BitVector
    @param bv: Bits defining a message
    @param validate: Set to true to cause checking to occur.  Runs slower.  FIX: not implemented.
    @rtype: dict
    @return: params
    """
    
    # Would be nice to check the bit count here..
    # if validate:
    #    assert (len(bv)==FIX: SOME NUMBER)
    r = {}
    r['MessageID'] = 1
    r['RepeatIndicator'] = int(bv[6:8])
    r['UserID'] = int(bv[8:38])
    r['NavigationStatus'] = int(bv[38:42])
    r['ROT'] = aisbinary.signedIntFromBV(bv[42:50])
    r['SOG'] = Decimal(int(bv[50:60])) / Decimal('10')
    r['PositionAccuracy'] = int(bv[60:61])
    r['longitude'] = Decimal(aisbinary.signedIntFromBV(bv[61:89])) / Decimal('600000')
    r['latitude'] = Decimal(aisbinary.signedIntFromBV(bv[89:116])) / Decimal('600000')
    r['COG'] = Decimal(int(bv[116:128])) / Decimal('10')
    r['TrueHeading'] = int(bv[128:137])
    r['TimeStamp'] = int(bv[137:143])
    r['RegionalReserved'] = 0
    r['Spare'] = 0
    r['RAIM'] = bool(int(bv[148:149]))
    r['state_syncstate'] = int(bv[149:151])
    r['state_slottimeout'] = int(bv[151:154])
    r['state_slotoffset'] = int(bv[154:168])
    return r


def decodeMessageID (bv, validate = False):
    return 1


def decodeRepeatIndicator (bv, validate = False):
    return int(bv[6:8])


def decodeUserID (bv, validate = False):
    return int(bv[8:38])


def decodeNavigationStatus (bv, validate = False):
    return int(bv[38:42])


def decodeROT (bv, validate = False):
    return aisbinary.signedIntFromBV(bv[42:50])


def decodeSOG (bv, validate = False):
    return Decimal(int(bv[50:60])) / Decimal('10')


def decodePositionAccuracy (bv, validate = False):
    return int(bv[60:61])


def decodelongitude (bv, validate = False):
    return Decimal(aisbinary.signedIntFromBV(bv[61:89])) / Decimal('600000')


def decodelatitude (bv, validate = False):
    return Decimal(aisbinary.signedIntFromBV(bv[89:116])) / Decimal('600000')


def decodeCOG (bv, validate = False):
    return Decimal(int(bv[116:128])) / Decimal('10')


def decodeTrueHeading (bv, validate = False):
    return int(bv[128:137])


def decodeTimeStamp (bv, validate = False):
    return int(bv[137:143])


def decodeRegionalReserved (bv, validate = False):
    return 0


def decodeSpare (bv, validate = False):
    return 0


def decodeRAIM (bv, validate = False):
    return bool(int(bv[148:149]))


def decodestate_syncstate (bv, validate = False):
    return int(bv[149:151])


def decodestate_slottimeout (bv, validate = False):
    return int(bv[151:154])


def decodestate_slotoffset (bv, validate = False):
    return int(bv[154:168])


def printHtml (params, out = sys.stdout):
    out.write("<h3>position</h3>\n")
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
        out.write("    <td>" + str(params['MessageID']) + "</td>\n")
        out.write("    <td>" + str(params['MessageID']) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>RepeatIndicator</td>\n")
    out.write("<td>uint</td>\n")
    if 'RepeatIndicator' in params:
        out.write("    <td>" + str(params['RepeatIndicator']) + "</td>\n")
        if str(params['RepeatIndicator']) in RepeatIndicatorDecodeLut:
            out.write("<td>" + RepeatIndicatorDecodeLut[str(params['RepeatIndicator'])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>UserID</td>\n")
    out.write("<td>uint</td>\n")
    if 'UserID' in params:
        out.write("    <td>" + str(params['UserID']) + "</td>\n")
        out.write("    <td>" + str(params['UserID']) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>NavigationStatus</td>\n")
    out.write("<td>uint</td>\n")
    if 'NavigationStatus' in params:
        out.write("    <td>" + str(params['NavigationStatus']) + "</td>\n")
        if str(params['NavigationStatus']) in NavigationStatusDecodeLut:
            out.write("<td>" + NavigationStatusDecodeLut[str(params['NavigationStatus'])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>ROT</td>\n")
    out.write("<td>int</td>\n")
    if 'ROT' in params:
        out.write("    <td>" + str(params['ROT']) + "</td>\n")
        out.write("    <td>" + str(params['ROT']) + "</td>\n")
    out.write("<td>4.733*sqrt(val) degrees/min</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>SOG</td>\n")
    out.write("<td>udecimal</td>\n")
    if 'SOG' in params:
        out.write("    <td>" + str(params['SOG']) + "</td>\n")
        if str(params['SOG']) in SOGDecodeLut:
            out.write("<td>" + SOGDecodeLut[str(params['SOG'])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("<td>knots</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>PositionAccuracy</td>\n")
    out.write("<td>uint</td>\n")
    if 'PositionAccuracy' in params:
        out.write("    <td>" + str(params['PositionAccuracy']) + "</td>\n")
        if str(params['PositionAccuracy']) in PositionAccuracyDecodeLut:
            out.write("<td>" + PositionAccuracyDecodeLut[str(params['PositionAccuracy'])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>longitude</td>\n")
    out.write("<td>decimal</td>\n")
    if 'longitude' in params:
        out.write("    <td>" + str(params['longitude']) + "</td>\n")
        out.write("    <td>" + str(params['longitude']) + "</td>\n")
    out.write("<td>degrees</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>latitude</td>\n")
    out.write("<td>decimal</td>\n")
    if 'latitude' in params:
        out.write("    <td>" + str(params['latitude']) + "</td>\n")
        out.write("    <td>" + str(params['latitude']) + "</td>\n")
    out.write("<td>degrees</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>COG</td>\n")
    out.write("<td>udecimal</td>\n")
    if 'COG' in params:
        out.write("    <td>" + str(params['COG']) + "</td>\n")
        out.write("    <td>" + str(params['COG']) + "</td>\n")
    out.write("<td>degrees</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>TrueHeading</td>\n")
    out.write("<td>uint</td>\n")
    if 'TrueHeading' in params:
        out.write("    <td>" + str(params['TrueHeading']) + "</td>\n")
        out.write("    <td>" + str(params['TrueHeading']) + "</td>\n")
    out.write("<td>degrees</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>TimeStamp</td>\n")
    out.write("<td>uint</td>\n")
    if 'TimeStamp' in params:
        out.write("    <td>" + str(params['TimeStamp']) + "</td>\n")
        if str(params['TimeStamp']) in TimeStampDecodeLut:
            out.write("<td>" + TimeStampDecodeLut[str(params['TimeStamp'])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("<td>seconds</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>RegionalReserved</td>\n")
    out.write("<td>uint</td>\n")
    if 'RegionalReserved' in params:
        out.write("    <td>" + str(params['RegionalReserved']) + "</td>\n")
        out.write("    <td>" + str(params['RegionalReserved']) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>Spare</td>\n")
    out.write("<td>uint</td>\n")
    if 'Spare' in params:
        out.write("    <td>" + str(params['Spare']) + "</td>\n")
        out.write("    <td>" + str(params['Spare']) + "</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>RAIM</td>\n")
    out.write("<td>bool</td>\n")
    if 'RAIM' in params:
        out.write("    <td>" + str(params['RAIM']) + "</td>\n")
        if str(params['RAIM']) in RAIMDecodeLut:
            out.write("<td>" + RAIMDecodeLut[str(params['RAIM'])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>state_syncstate</td>\n")
    out.write("<td>uint</td>\n")
    if 'state_syncstate' in params:
        out.write("    <td>" + str(params['state_syncstate']) + "</td>\n")
        if str(params['state_syncstate']) in state_syncstateDecodeLut:
            out.write("<td>" + state_syncstateDecodeLut[str(params['state_syncstate'])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>state_slottimeout</td>\n")
    out.write("<td>uint</td>\n")
    if 'state_slottimeout' in params:
        out.write("    <td>" + str(params['state_slottimeout']) + "</td>\n")
        if str(params['state_slottimeout']) in state_slottimeoutDecodeLut:
            out.write("<td>" + state_slottimeoutDecodeLut[str(params['state_slottimeout'])] + "</td>")
        else:
            out.write("<td><i>Missing LUT entry</i></td>")
    out.write("<td>frames</td>\n")
    out.write("</tr>\n")
    out.write("\n")
    out.write("<tr>\n")
    out.write("<td>state_slotoffset</td>\n")
    out.write("<td>uint</td>\n")
    if 'state_slotoffset' in params:
        out.write("    <td>" + str(params['state_slotoffset']) + "</td>\n")
        out.write("    <td>" + str(params['state_slotoffset']) + "</td>\n")
    out.write("</tr>\n")
    out.write("</table>\n")


def printKml (params, out = sys.stdout):
    """
    KML (Keyhole Markup Language) for Google Earth,
    but without the header/footer"""
    
    out.write("    <Placemark>\n")
    out.write("        <name>" + str(params['UserID']) + "</name>\n")
    out.write("        <description>\n")
    import io
    
    buf = io.StringIO()
    printHtml(params, buf)
    import cgi
    
    out.write(cgi.escape(buf.getvalue()))
    out.write("        </description>\n")
    out.write("        <styleUrl>#m_ylw-pushpin_copy0</styleUrl>\n")
    out.write("        <Point>\n")
    out.write("            <coordinates>")
    out.write(str(params['longitude']))
    out.write(',')
    out.write(str(params['latitude']))
    out.write(",0</coordinates>\n")
    out.write("        </Point>\n")
    out.write("    </Placemark>\n")


def printFields (params, out = sys.stdout, format = 'std', fieldList = None, dbType = 'postgres'):
    """Print a position message to stdout.

    Fields in params:
      - MessageID(uint): AIS message number.  Must be 1 (field automatically set to "1")
      - RepeatIndicator(uint): Indicated how many times a message has been repeated
      - UserID(uint): Unique ship identification number (MMSI)
      - NavigationStatus(uint): What is the vessel doing
      - ROT(int): RateOfTurn
      - SOG(udecimal): Speed over ground
      - PositionAccuracy(uint): Accuracy of positioning fixes
      - longitude(decimal): Location of the vessel  East West location
      - latitude(decimal): Location of the vessel  North South location
      - COG(udecimal): Course over ground
      - TrueHeading(uint): True heading (relative to true North)
      - TimeStamp(uint): UTC second when the report was generated
      - RegionalReserved(uint): Reserved for definition by a regional authority. (field automatically set to "0")
      - Spare(uint): Not used.  Should be set to zero. (field automatically set to "0")
      - RAIM(bool): Receiver autonomous integrity monitoring flag
      - state_syncstate(uint): Communications State - SOTDMA  Sycronization state
      - state_slottimeout(uint): Communications State - SOTDMA  Frames remaining until a new slot is selected
      - state_slotoffset(uint): Communications State - SOTDMA  In what slot will the next transmission occur. BROKEN
    @param params: Dictionary of field names/values.
    @param out: File like object to write to.
    @rtype: stdout
    @return: text to out
    """
    
    if 'std' == format:
        out.write("position:\n")
        if 'MessageID' in params:
            out.write("    MessageID:          " + str(params['MessageID']) + "\n")
        if 'RepeatIndicator' in params:
            out.write("    RepeatIndicator:    " + str(params['RepeatIndicator']) + "\n")
        if 'UserID' in params:
            out.write("    UserID:             " + str(params['UserID']) + "\n")
        if 'NavigationStatus' in params:
            out.write("    NavigationStatus:   " + str(params['NavigationStatus']) + "\n")
        if 'ROT' in params:
            out.write("    ROT:                " + str(params['ROT']) + "\n")
        if 'SOG' in params:
            out.write("    SOG:                " + str(params['SOG']) + "\n")
        if 'PositionAccuracy' in params:
            out.write("    PositionAccuracy:   " + str(params['PositionAccuracy']) + "\n")
        if 'longitude' in params:
            out.write("    longitude:          " + str(params['longitude']) + "\n")
        if 'latitude' in params:
            out.write("    latitude:           " + str(params['latitude']) + "\n")
        if 'COG' in params:
            out.write("    COG:                " + str(params['COG']) + "\n")
        if 'TrueHeading' in params:
            out.write("    TrueHeading:        " + str(params['TrueHeading']) + "\n")
        if 'TimeStamp' in params:
            out.write("    TimeStamp:          " + str(params['TimeStamp']) + "\n")
        if 'RegionalReserved' in params:
            out.write("    RegionalReserved:   " + str(params['RegionalReserved']) + "\n")
        if 'Spare' in params:
            out.write("    Spare:              " + str(params['Spare']) + "\n")
        if 'RAIM' in params:
            out.write("    RAIM:               " + str(params['RAIM']) + "\n")
        if 'state_syncstate' in params:
            out.write("    state_syncstate:    " + str(params['state_syncstate']) + "\n")
        if 'state_slottimeout' in params:
            out.write(
                "    state_slottimeout:  " + str(params['state_slottimeout']) + "\n")
        if 'state_slotoffset' in params:
            out.write("    state_slotoffset:   " + str(params['state_slotoffset']) + "\n")
        elif 'csv' == format:
            if None == params.fieldList:
                params.fieldList = fieldList
            needComma = False;
            for field in fieldList:
                if needComma:
                    out.write(',')
                needComma = True
                if field in params:
                    out.write(str(params[field]))
            # else: leave it empty
            out.write("\n")
    elif 'html' == format:
        printHtml(params, out)
    elif 'sql' == format:
        sqlInsertStr(params, out, dbType = dbType)
    elif 'kml' == format:
        printKml(params, out)
    elif 'kml-full' == format:
        out.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        out.write("<kml xmlns=\"http://earth.google.com/kml/2.1\">\n")
        out.write("<Document>\n")
        out.write("    <name>position</name>\n")
        printKml(params, out)
        out.write("</Document>\n")
        out.write("</kml>\n")
    else:
        print("ERROR: unknown format:", format)
        assert False
    
    return  # Nothing to return


RepeatIndicatorEncodeLut = {
    'default': '0',
    'do not repeat any more': '3',
}  # RepeatIndicatorEncodeLut

RepeatIndicatorDecodeLut = {
    '0': 'default',
    '3': 'do not repeat any more',
}  # RepeatIndicatorEncodeLut

NavigationStatusEncodeLut = {
    'under way using engine': '0',
    'at anchor': '1',
    'not under command': '2',
    'restricted maneuverability': '3',
    'constrained by her draught': '4',
    'moored': '5',
    'aground': '6',
    'engaged in fishing': '7',
    'under way sailing': '8',
    'reserved for future use (hazmat)': '9',
    'reserved for future use': '10',
    'reserved for future use': '11',
    'reserved for future use': '12',
    'reserved for future use': '13',
    'reserved for future use': '14',
    'not defined = default': '15',
}  # NavigationStatusEncodeLut

NavigationStatusDecodeLut = {
    '0': 'under way using engine',
    '1': 'at anchor',
    '2': 'not under command',
    '3': 'restricted maneuverability',
    '4': 'constrained by her draught',
    '5': 'moored',
    '6': 'aground',
    '7': 'engaged in fishing',
    '8': 'under way sailing',
    '9': 'reserved for future use (hazmat)',
    '10': 'reserved for future use',
    '11': 'reserved for future use',
    '12': 'reserved for future use',
    '13': 'reserved for future use',
    '14': 'reserved for future use',
    '15': 'not defined = default',
}  # NavigationStatusEncodeLut

SOGEncodeLut = {
    '102.2 knots or higher': '102.2',
}  # SOGEncodeLut

SOGDecodeLut = {
    '102.2': '102.2 knots or higher',
}  # SOGEncodeLut

PositionAccuracyEncodeLut = {
    'low (greater than 10 m)': '0',
    'high (less than 10 m)': '1',
}  # PositionAccuracyEncodeLut

PositionAccuracyDecodeLut = {
    '0': 'low (greater than 10 m)',
    '1': 'high (less than 10 m)',
}  # PositionAccuracyEncodeLut

TimeStampEncodeLut = {
    'not available/default': '60',
    'manual input': '61',
    'dead reckoning': '62',
    'inoperative': '63',
}  # TimeStampEncodeLut

TimeStampDecodeLut = {
    '60': 'not available/default',
    '61': 'manual input',
    '62': 'dead reckoning',
    '63': 'inoperative',
}  # TimeStampEncodeLut

RAIMEncodeLut = {
    'not in use': 'False',
    'in use': 'True',
}  # RAIMEncodeLut

RAIMDecodeLut = {
    'False': 'not in use',
    'True': 'in use',
}  # RAIMEncodeLut

state_syncstateEncodeLut = {
    'UTC direct': '0',
    'UTC indirect': '1',
    'synchronized to a base station': '2',
    'synchronized to another station': '3',
}  # state_syncstateEncodeLut

state_syncstateDecodeLut = {
    '0': 'UTC direct',
    '1': 'UTC indirect',
    '2': 'synchronized to a base station',
    '3': 'synchronized to another station',
}  # state_syncstateEncodeLut

state_slottimeoutEncodeLut = {
    'Last frame in this slot': '0',
    '1 frames left': '1',
    '2 frames left': '2',
    '3 frames left': '3',
    '4 frames left': '4',
    '5 frames left': '5',
    '6 frames left': '6',
    '7 frames left': '7',
}  # state_slottimeoutEncodeLut

state_slottimeoutDecodeLut = {
    '0': 'Last frame in this slot',
    '1': '1 frames left',
    '2': '2 frames left',
    '3': '3 frames left',
    '4': '4 frames left',
    '5': '5 frames left',
    '6': '6 frames left',
    '7': '7 frames left',
}  # state_slottimeoutEncodeLut


######################################################################
# UNIT TESTING
######################################################################
def testParams ():
    """Return a params file base on the testvalue tags.
    @rtype: dict
    @return: params based on testvalue tags
    """
    params = {}
    params['MessageID'] = 1
    params['RepeatIndicator'] = 1
    params['UserID'] = 1193046
    params['NavigationStatus'] = 3
    params['ROT'] = -2
    params['SOG'] = Decimal('101.9')
    params['PositionAccuracy'] = 1
    params['longitude'] = Decimal('-122.16328055555556')
    params['latitude'] = Decimal('37.424458333333334')
    params['COG'] = Decimal('34.5')
    params['TrueHeading'] = 41
    params['TimeStamp'] = 35
    params['RegionalReserved'] = 0
    params['Spare'] = 0
    params['RAIM'] = False
    params['state_syncstate'] = 2
    params['state_slottimeout'] = 0
    params['state_slotoffset'] = 1221
    
    return params


class Testposition(unittest.TestCase):
    """Use testvalue tag text from each type to build test case the position message"""
    
    
    def testEncodeDecode (self):
        params = testParams()
        bits = encode(params)
        r = decode(bits)
        
        # Check that each parameter came through ok.
        self.failUnlessEqual(r['MessageID'], params['MessageID'])
        self.failUnlessEqual(r['RepeatIndicator'], params['RepeatIndicator'])
        self.failUnlessEqual(r['UserID'], params['UserID'])
        self.failUnlessEqual(r['NavigationStatus'], params['NavigationStatus'])
        self.failUnlessEqual(r['ROT'], params['ROT'])
        self.failUnlessAlmostEqual(r['SOG'], params['SOG'], 1)
        self.failUnlessEqual(r['PositionAccuracy'], params['PositionAccuracy'])
        self.failUnlessAlmostEqual(r['longitude'], params['longitude'], 5)
        self.failUnlessAlmostEqual(r['latitude'], params['latitude'], 5)
        self.failUnlessAlmostEqual(r['COG'], params['COG'], 1)
        self.failUnlessEqual(r['TrueHeading'], params['TrueHeading'])
        self.failUnlessEqual(r['TimeStamp'], params['TimeStamp'])
        self.failUnlessEqual(r['RegionalReserved'], params['RegionalReserved'])
        self.failUnlessEqual(r['Spare'], params['Spare'])
        self.failUnlessEqual(r['RAIM'], params['RAIM'])
        self.failUnlessEqual(r['state_syncstate'], params['state_syncstate'])
        self.failUnlessEqual(r['state_slottimeout'], params['state_slottimeout'])
        self.failUnlessEqual(r['state_slotoffset'], params['state_slotoffset'])


def addMsgOptions (parser):
    parser.add_option('-d', '--decode', dest = 'doDecode', default = False, action = 'store_true',
                      help = 'decode a "position" AIS message')
    parser.add_option('-e', '--encode', dest = 'doEncode', default = False, action = 'store_true',
                      help = 'encode a "position" AIS message')
    parser.add_option('--RepeatIndicator-field', dest = 'RepeatIndicatorField', default = 0, metavar = 'uint',
                      type = 'int'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--UserID-field', dest = 'UserIDField', metavar = 'uint', type = 'int'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--NavigationStatus-field', dest = 'NavigationStatusField', default = 15, metavar = 'uint',
                      type = 'int'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--ROT-field', dest = 'ROTField', default = -128, metavar = 'int', type = 'int'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--SOG-field', dest = 'SOGField', default = Decimal('102.3'), metavar = 'udecimal',
                      type = 'string'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--PositionAccuracy-field', dest = 'PositionAccuracyField', metavar = 'uint', type = 'int'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--longitude-field', dest = 'longitudeField', default = Decimal('181'), metavar = 'decimal',
                      type = 'string'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--latitude-field', dest = 'latitudeField', default = Decimal('91'), metavar = 'decimal',
                      type = 'string'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--COG-field', dest = 'COGField', default = Decimal('360'), metavar = 'udecimal',
                      type = 'string'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--TrueHeading-field', dest = 'TrueHeadingField', default = 511, metavar = 'uint',
                      type = 'int'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--TimeStamp-field', dest = 'TimeStampField', default = 60, metavar = 'uint', type = 'int'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--RAIM-field', dest = 'RAIMField', metavar = 'bool', type = 'int'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--state_syncstate-field', dest = 'state_syncstateField', metavar = 'uint', type = 'int'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--state_slottimeout-field', dest = 'state_slottimeoutField', metavar = 'uint', type = 'int'
                      , help = 'Field parameter value [default: %default]')
    parser.add_option('--state_slotoffset-field', dest = 'state_slotoffsetField', metavar = 'uint', type = 'int'
                      , help = 'Field parameter value [default: %default]')


def test_author ():
    from optparse import OptionParser
    
    parser = OptionParser(usage = "%prog [options]")
    
    parser.add_option('--unit-test', dest = 'unittest', default = False, action = 'store_true',
                      help = 'run the unit tests')
    parser.add_option('-v', '--verbose', dest = 'verbose', default = False, action = 'store_true',
                      help = 'Make the test output verbose')
    
    # FIX: remove nmea from binary messages.  No way to build the whole packet?
    # FIX: or build the surrounding msg 8 for a broadcast?
    typeChoices = ('aisbinary', 'nmeapayload', 'nmea')  # FIX: what about a USCG type message?
    parser.add_option('-t', '--type', choices = typeChoices, type = 'choice',
                      dest = 'ioType', default = 'nmeapayload',
                      help = 'What kind of string to write for encoding (' + ', '.join(
                          typeChoices) + ') [default: %default]')
    
    outputChoices = ('std', 'html', 'csv', 'sql', 'kml', 'kml-full')
    parser.add_option('-T', '--output-type', choices = outputChoices,
                      type = 'choice', dest = 'outputType', default = 'std',
                      help = 'What kind of string to output (' + ', '.join(outputChoices) + ') '
                                                                                            '[default: %default]')
    
    parser.add_option('-o', '--output', dest = 'outputFileName', default = None,
                      help = 'Name of the python file to write [default: stdout]')
    
    parser.add_option('-f', '--fields', dest = 'fieldList', default = None,
                      action = 'append', choices = fieldList,
                      help = 'Which fields to include in the output.  Currently only for csv '
                             'output [default: all]')
    
    parser.add_option('-p', '--print-csv-field-list', dest = 'printCsvfieldList',
                      default = False, action = 'store_true',
                      help = 'Print the field name for csv')
    
    parser.add_option('-c', '--sql-create', dest = 'sqlCreate', default = False,
                      action = 'store_true',
                      help = 'Print out an sql create command for the table.')
    
    parser.add_option('--latex-table', dest = 'latexDefinitionTable',
                      default = False, action = 'store_true',
                      help = 'Print a LaTeX table of the type')
    
    parser.add_option('--text-table', dest = 'textDefinitionTable', default = False,
                      action = 'store_true',
                      help = 'Print delimited table of the type (for Word table importing)')
    
    parser.add_option('--delimt-text-table', dest = 'delimTextDefinitionTable',
                      default = '    ',
                      help = 'Delimiter for text table [default: \'%default\'] '
                             '(for Word table importing)')
    
    dbChoices = ('sqlite', 'postgres')
    parser.add_option('-D', '--db-type',
                      dest = 'dbType',
                      default = 'postgres',
                      choices = dbChoices, type = 'choice',
                      help = 'What kind of database (' + ', '.join(dbChoices) + ') '
                                                                                '[default: %default]')
    
    addMsgOptions(parser)
    
    (options, args) = parser.parse_args()
    success = True
    
    if not success:
        sys.exit('Something Failed')
    del success  # Hide success from epydoc
    
    if options.unittest:
        sys.argv = [sys.argv[0]]
        if options.verbose:
            sys.argv.append('-v')
        unittest.main()
    
    outfile = sys.stdout
    if None != options.outputFileName:
        outfile = open(options.outputFileName, 'w')
    
    if options.doEncode:
        # Make sure all non required options are specified.
        if None == options.RepeatIndicatorField:
            parser.error("missing value for RepeatIndicatorField")
        if None == options.UserIDField:
            parser.error("missing value for UserIDField")
        if None == options.NavigationStatusField:
            parser.error("missing value for NavigationStatusField")
        if None == options.ROTField:
            parser.error("missing value for ROTField")
        if None == options.SOGField:
            parser.error("missing value for SOGField")
        if None == options.PositionAccuracyField:
            parser.error("missing value for PositionAccuracyField")
        if None == options.longitudeField:
            parser.error("missing value for longitudeField")
        if None == options.latitudeField:
            parser.error("missing value for latitudeField")
        if None == options.COGField:
            parser.error("missing value for COGField")
        if None == options.TrueHeadingField:
            parser.error("missing value for TrueHeadingField")
        if None == options.TimeStampField:
            parser.error("missing value for TimeStampField")
        if None == options.RAIMField:
            parser.error("missing value for RAIMField")
        if None == options.state_syncstateField:
            parser.error("missing value for state_syncstateField")
        if None == options.state_slottimeoutField:
            parser.error("missing value for state_slottimeoutField")
        if None == options.state_slotoffsetField:
            parser.error("missing value for state_slotoffsetField")
    msgDict = {
        'MessageID': '1',
        'RepeatIndicator': options.RepeatIndicatorField,
        'UserID': options.UserIDField,
        'NavigationStatus': options.NavigationStatusField,
        'ROT': options.ROTField,
        'SOG': options.SOGField,
        'PositionAccuracy': options.PositionAccuracyField,
        'longitude': options.longitudeField,
        'latitude': options.latitudeField,
        'COG': options.COGField,
        'TrueHeading': options.TrueHeadingField,
        'TimeStamp': options.TimeStampField,
        'RegionalReserved': '0',
        'Spare': '0',
        'RAIM': options.RAIMField,
        'state_syncstate': options.state_syncstateField,
        'state_slottimeout': options.state_slottimeoutField,
        'state_slotoffset': options.state_slotoffsetField,
    }
    
    bits = encode(msgDict)
    
    if 'binary' == options.ioType:
        print(str(bits))
    elif 'nmeapayload' == options.ioType:
        # FIX: figure out if this might be necessary at compile time
        bitLen = len(bits)
        if bitLen % 6 != 0:
            bits = bits + BitVector(size = (6 - (bitLen % 6)))  # Pad out to multiple of 6
        print(aisbinary.bitvectoais6(bits)[0])
    
    # FIX: Do not emit this option for the binary message payloads.  Does not make sense.
    elif 'nmea' == options.ioType:
        nmea = uscg.create_nmea(bits)
        print(nmea)
    else:
        sys.exit('ERROR: unknown ioType.  Help!')
        
        if options.sqlCreate:
            sqlCreateStr(outfile, options.fieldList, dbType = options.dbType)
        
        if options.latexDefinitionTable:
            latexDefinitionTable(outfile)
        
        # For conversion to word tables
        if options.textDefinitionTable:
            textDefinitionTable(outfile, options.delimTextDefinitionTable)
        
        if options.printCsvfieldList:
            # Make a csv separated list of fields that will be displayed for csv
            if None == options.fieldList:
                options.fieldList = fieldList
            import io
            
            buf = io.StringIO()
            for field in options.fieldList:
                buf.write(field + ',')
            result = buf.getvalue()
            if result[-1] == ',':
                print(result[:-1])
            else:
                print(result)
        
        if options.doDecode:
            if len(args) == 0:
                args = sys.stdin
            for msg in args:
                bv = None
                
                if msg[0] in ('$', '!') and msg[3:6] in ('VDM', 'VDO'):
                    # Found nmea
                    # FIX: do checksum
                    bv = aisbinary.ais6tobitvec(msg.split(',')[5])
                else:  # either binary or nmeapayload... expect mostly nmeapayloads
                    # assumes that an all 0 and 1 string can not be a nmeapayload
                    binaryMsg = True
                    for c in msg:
                        if c not in ('0', '1'):
                            binaryMsg = False
                            break
                    if binaryMsg:
                        bv = BitVector(bitstring = msg)
                    else:  # nmeapayload
                        bv = aisbinary.ais6tobitvec(msg)
                
                printFields(decode(bv)
                            , out = outfile
                            , format = options.outputType
                            , fieldList = options.fieldList
                            , dbType = options.dbType
                            )
    
    return


def test_this ():
    '''
    msgDict = {
        'MessageID': '1',
        'RepeatIndicator': options.RepeatIndicatorField,
        'UserID': options.UserIDField,
        'NavigationStatus': options.NavigationStatusField,
        'ROT': options.ROTField,
        'SOG': options.SOGField,
        'PositionAccuracy': options.PositionAccuracyField,
        'longitude': options.longitudeField,
        'latitude': options.latitudeField,
        'COG': options.COGField,
        'TrueHeading': options.TrueHeadingField,
        'TimeStamp': options.TimeStampField,
        'RegionalReserved': '0',
        'Spare': '0',
        'RAIM': options.RAIMField,
        'state_syncstate': options.state_syncstateField,
        'state_slottimeout': options.state_slottimeoutField,
        'state_slotoffset': options.state_slotoffsetField,
    }
    '''
    msg01 = {}
    msg01['MessageID'] = 1
    msg01['RepeatIndicator'] = 1
    msg01['MMSI'] = 1193046
    msg01['NavigationStatus'] = 3
    msg01['ROT'] = -2
    msg01['SOG'] = Decimal('101.9')
    msg01['PositionAccuracy'] = 1
    msg01['longitude'] = Decimal('-122.16328055555556')
    msg01['latitude'] = Decimal('37.424458333333334')
    msg01['COG'] = Decimal('34.5')
    msg01['TrueHeading'] = 41
    msg01['TimeStamp'] = 35
    msg01['RegionalReserved'] = 0
    msg01['Spare'] = 0
    msg01['RAIM'] = False
    # This is SOTDMA communication state fields
    # 19 bites long in type 18
    # 1 field comes before for communication state
    # type choice
    msg01['state_syncstate'] = 2
    msg01['state_slottimeout'] = 0
    msg01['state_slotoffset'] = 1221
    
    bits = encode(msg01)
    nmea = uscg.create_nmea(bits,
                            message_type = 1)
    return


############################################################
if __name__ == '__main__':
    test_this()
