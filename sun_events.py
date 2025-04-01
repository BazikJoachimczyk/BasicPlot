from astropy.time import Time
from create_objects import PIWNICE
from astropy.coordinates import AltAz, get_body
import numpy as np


class BodyAlt():
    def __init__(self, timescale:list, location:PIWNICE, body:str):
        self.body = body
        self.timescale = timescale
        self.location = location
        self.altitudes = self.calculate_altitudes()

    def calculate_altitudes(self):
        body_altaz = [get_body(self.body, time=timepoint).transform_to(AltAz(obstime=timepoint, location=self.location)) for timepoint in self.timescale ]
        return [alt.alt.degree for alt in body_altaz]
