from create_objects import PIWNICE
import astropy.units as u
import json 
from astropy.coordinates import SkyCoord, AltAz, EarthLocation, Angle


def CalculateAltitudes(ra: float, dec: float, time: list, observatory = PIWNICE):
    star = SkyCoord(ra = ra*u.deg, dec = dec*u.deg)
    star_alt = []
    for time_point in time:
        star_altzaz = star.transform_to(AltAz(obstime = time_point, location = observatory))
        star_alt.append(star_altzaz.alt.degree)
    return star_alt

def UIAltitudes(ra_str:str, dec_str:str, time:list, lat_str:str, lon_str:str):
    lat = Angle(lat_str, unit=u.deg)
    lon = Angle(lon_str, unit=u.deg)
    ra = Angle(ra_str, unit=u.deg)
    dec = Angle(dec_str, unit=u.deg)
    observatory = EarthLocation(lat=lat, lon=lon)
    star = SkyCoord(ra = ra, dec = dec)
    star_altaz = [star.transform_to(AltAz(obstime = time_point, location = observatory)) for time_point in time]
    star_alts = [star.alt.degree for star in star_altaz]
    json_time = [time_point.isot.split('T')[1][:8] for time_point in time]
    output = { 
        "time": json_time,
        "altitude": star_alts
        }
    json_output = json.dumps(output)
    print(json_output)
    return json_output