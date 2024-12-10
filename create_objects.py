from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation

PIWNICE = EarthLocation(lat = 53*u.deg, lon = 18*u.deg, height = 70*u.m)
OBJECTS = None

path = r"C:\Users\Bazik\Desktop\lista_obiektów.txt"

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

OBJECTS = []
with open(path, 'r') as file:
    for line in file:
        elements = line.split()
        obj = Object(elements[0], elements[1], elements[2])
        obj.FillSkycoords()
        OBJECTS.append(obj)


# zakładam, że zwraca: listę obiektów OBJECTS, współrzędne obserwatorium PIWNICE