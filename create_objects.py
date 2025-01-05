from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz


PIWNICE = EarthLocation(lat = 53.0975*u.deg, lon = 18.5625*u.deg, height = 80*u.m)

# zakładam, że dostaję plik tekstowy, gdzie:
# nazwa_obiektu ra dec w formie dziesiętnej stopni na ten moment
# co gdy deklinacja ma +-?

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
            elements = line.split()
            obj = Object(elements[0], elements[1], elements[2])
            obj.FillSkycoords()
            objects.append(obj)
    return objects

# zakładam, że zwraca: listę obiektów OBJECTS, współrzędne obserwatorium PIWNICE