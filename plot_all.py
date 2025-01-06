import calculate_visibility
from create_objects import PIWNICE
import matplotlib.pyplot as plt
from astropy.coordinates import get_body, AltAz

def Plot(objects:list, timescale:list):
    moon_alts = []
    for time_point in timescale:
        moon_altaz = get_body('moon', time_point).transform_to(AltAz(obstime = time_point, location = PIWNICE))
        moon_alts.append(moon_altaz.alt.degree)
    timescale = [t.datetime for t in timescale]
    plt.figure(figsize=(9,9))
    plt.plot(timescale, moon_alts, label = 'Moon', color = 'gray')
    for obj in objects:
        altitudes = calculate_visibility.CalculateAltitudes(ra = obj.ra, dec = obj.dec, time = timescale)
        plt.plot(timescale, altitudes, label = obj.name)
    plt.xlabel('UTC [month-day hour]')
    plt.ylabel('Altitude [deg]')
    plt.grid()
    plt.legend()
    plt.ylim(25,90)
    plt.show()
    





