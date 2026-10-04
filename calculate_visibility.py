from create_objects import PIWNICE
import astropy.units as u
import json
from astropy.coordinates import SkyCoord, AltAz, EarthLocation, Angle


def CalculateAltitudes(ra: float, dec: float, time, observatory = PIWNICE):
    star = SkyCoord(ra = ra*u.deg, dec = dec*u.deg)
    return star.transform_to(AltAz(obstime = time, location = observatory)).alt.degree

def UIAltitudes(ra_str:str, dec_str:str, time, lat_str:str, lon_str:str):
    lat = Angle(lat_str, unit=u.deg)
    lon = Angle(lon_str, unit=u.deg)
    ra = Angle(ra_str, unit=u.hourangle)
    dec = Angle(dec_str, unit=u.deg)
    observatory = EarthLocation(lat=lat, lon=lon)
    star = SkyCoord(ra = ra, dec = dec)
    star_alts = star.transform_to(AltAz(obstime = time, location = observatory)).alt.degree
    json_time = [isot.split('T')[1][:8] for isot in time.isot]
    output = {
        "time": json_time,
        "altitude": star_alts.tolist()
        }
    json_output = json.dumps(output)
    print(json_output)
    return json_output
