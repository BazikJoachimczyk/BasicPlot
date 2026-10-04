from astropy.time import Time
from astropy.coordinates import AltAz, EarthLocation, get_body


class BodyAlt():
    def __init__(self, timescale:Time, location:EarthLocation, body:str):
        self.body = body
        self.timescale = timescale
        self.location = location
        self.coords = get_body(self.body, time=self.timescale, location=self.location)
        self.altitudes = self.calculate_altitudes()

    def calculate_altitudes(self):
        body_altaz = self.coords.transform_to(AltAz(obstime=self.timescale, location=self.location))
        return body_altaz.alt.degree
