# PCMST/PAIDD and probably other transas ais

from ... import nmea


class AID(nmea.ProprietarySentence):
    sentence_types = {}

    def __new__(_cls,
                manufacturer,
                datatype,
                data):
        name = datatype
        cls = _cls.sentence_types.get(name, _cls)
        return super(AID, cls).__new__(cls)

    def __init__(self,
                 manufacturer,
                 datatype,
                 data):
        self.sentence_type =  datatype
        super(AID, self).__init__(manufacturer,
                                  datatype,
                                  data)


class AIDD(AID):
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

