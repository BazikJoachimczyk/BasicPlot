import astropy.units as u
from astropy.coordinates import SkyCoord, get_body
import matplotlib.pyplot as plt

def PlotMoonSeparation(objects:list, timescale: list):
    moon_coords = []
    for time_point in timescale:
        moon_point = get_body('moon', time_point)
        moon_point_icrs = moon_point.transform_to('icrs')
        moon_coords.append(moon_point_icrs)
    timescale = [t.datetime for t in timescale]
    plt.figure(figsize=(9,9))
    for obj in objects:
        separations = []
        obj_coords = SkyCoord(ra=obj.ra*u.deg, dec=obj.dec*u.deg)
        for moon_point in moon_coords:
            separation = obj_coords.separation(moon_point)
            separations.append(separation.deg)
        plt.plot(timescale, separations, label = obj.name)
    plt.xlabel('UTC [month-day hour]')
    plt.ylabel('Separation [deg]')
    plt.grid()
    plt.legend()
    plt.show()

    
