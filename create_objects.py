from astropy import units as u
from astropy.coordinates import SkyCoord, EarthLocation


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
    # line format: <name> <ra deg> <dec deg>; name may contain spaces, '#' starts a comment
    objects = []
    with open(path, 'r') as file:
        for line_no, line in enumerate(file, start = 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            elements = line.rsplit(maxsplit = 2)
            if len(elements) != 3:
                raise ValueError(f"{path}:{line_no}: expected '<name> <ra> <dec>', got '{line}'")
            obj = Object(elements[0], elements[1], elements[2])
            obj.FillSkycoords()
            objects.append(obj)
    return objects
