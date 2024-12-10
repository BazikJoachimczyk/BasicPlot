from .create_objects import PIWNICE, OBJECTS


def CalculateAltitudes(ra: float, dec: float, time: list):
    star = SkyCoord(ra = ra, dec = dec)
    star_alt = []
    for time_point in time:
        star_altzaz = star.transform_to(AltAz(obstime = time_point, location = PIWNICE))
        star_alt.append(star_altzaz.alt)
    return star_alt