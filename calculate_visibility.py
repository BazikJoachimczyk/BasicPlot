from create_objects import PIWNICE
import astropy.units as u
from astropy.coordinates import SkyCoord, AltAz

def CalculateAltitudes(ra: float, dec: float, time: list):
    star = SkyCoord(ra = ra*u.deg, dec = dec*u.deg)
    star_alt = []
    for time_point in time:
        star_altzaz = star.transform_to(AltAz(obstime = time_point, location = PIWNICE))
        star_alt.append(star_altzaz.alt.degree)
    return star_alt