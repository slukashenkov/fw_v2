# PCMST/PAIDD and probably other transas ais

from ... import nmea


class AIS(nmea.ProprietarySentence):
    sentence_types = {}

    def __new__(_cls, manufacturer, data):
        name = manufacturer
        cls = _cls.sentence_types.get(name, _cls)
        return super(AIS, cls).__new__(cls)

    def __init__(self, manufacturer, data):
        self.sentence_type = manufacturer
        super(AIS, self).__init__(manufacturer, data)


class CMST(AIS):
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

class AIDD(AIS):
    """PAIDD - AIS data for FOR CUSTOM eqipment

        data comes from into
        $PAIDD
        from
        --------------------
        AIVDM type 1 or 18
        from fields
        --------------------
        AIVDM to PAIDD mapping

        AIVDM Field: MMSI
        AIVDM Field: Longitude

            Hemisphere_sign_n_s -> Calculated

        AIVDM Field: Latitude

            Hemisphere_sign_e_w -> Calculated

        AIVDM Field: Speed Over Ground(SOG)
        AIVDM Field: True Heading(HDG)
        AIVDM Field: Course Over Ground(COG)

            timestamp -> Calculated
    """
    fields = (
        ("MMSI", "mmsi"),
        ("Longitude", "lon"),
        ("Hemisphere_sign_n_s", "hem_n_s"),
        ("Latitude", "lat"),
        ("Hemisphere_sign_e_w", "hem_e_w"),
        ("Speed Over Ground(SOG)", "sog"),
        ("True Heading(HDG)", "hdg"),
        ("Course Over Ground(COG)", "cog"),
        ("Timestamp", "tmstmp"),
    )
