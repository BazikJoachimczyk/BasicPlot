from .calculate_visibility import CalculateAltitudes
from .create_objects import PIWNICE, BuildObjectsList
import matplotlib.pyplot as plt
from astropy.coordinates import get_moon

def Plot(objects:list, timescale:list):
    moon_alts = []
    for time_point in timescale:
        moon_altaz = get_moon(time_point).transform_to(AltAz(obstime = time_point, location = PIWNICE))
        moon_alts.append(moon_altaz.alt)
    plt.figure(figsize=(9,9))
    plt.plot(timescale, moon_alts, label = 'Moon', color = 'gray')
    for obj in objects:
        altitudes = CalculateAltitudes(ra = obj.ra, dec = obj.dec, time = timescale)
        plt.plot(timescale, altitudes, color = 'black', label = obj.name)
    plt.grid()
    plt.legend()
    plt.ylim(25,90)
    plt.show()
    





