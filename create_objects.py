from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz


PIWNICE = EarthLocation(lat = 53.0975*u.deg, lon = 18.5625*u.deg, height = 80*u.m)

class Object:
    def __init__(self, name, ra, dec):
        self.name = str(name)
        self.ra = float(ra)
        self.dec = float(dec)
        self.skycoords = 0

    def FillSkycoords(self):
        self.skycoords = SkyCoord(ra = self.ra*u.deg, dec = self.dec*u.deg)

def BuildObjectsList(path):
    objects = []
    with open(path, 'r') as file:
        for line in file:
            print(line)
            elements = line.split()
            obj = Object(elements[0], elements[1], elements[2])
            obj.FillSkycoords()
            objects.append(obj)
    return objects

