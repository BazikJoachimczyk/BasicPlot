import calculate_visibility
import numpy as np
from create_objects import PIWNICE
import matplotlib.pyplot as plt
from astropy.coordinates import get_body, AltAz, SkyCoord
import astropy.units as u
from sun_events import BodyAlt

#add location as parameter


def Plot(objects:list, timescale:list, moon_separation:bool = False):
    timescale_dt = [t.datetime for t in timescale]

    sun_altitudes = np.array(BodyAlt(timescale=timescale, location=PIWNICE, body = 'sun').altitudes)
    moon_altitudes = np.array(BodyAlt(timescale=timescale, location=PIWNICE, body = 'moon').altitudes) 

    moon_coords = [] if moon_separation else None
    for time_point in timescale:
        if moon_separation:
            moon_icrs = get_body('moon', time_point).transform_to('icrs')
            moon_coords.append(moon_icrs)

    range06_idx = (np.array(sun_altitudes) <= 0 ) & (np.array(sun_altitudes) > -6)
    range612_idx = (np.array(sun_altitudes) <= -6 ) & (np.array(sun_altitudes) > -12) 
    rangebelow12_idx = (np.array(sun_altitudes) < -12)

    sun06_times = np.array(timescale_dt)[range06_idx]
    sun612_times = np.array(timescale_dt)[range612_idx]
    sunbelow12_times = np.array(timescale_dt)[rangebelow12_idx]

    fig, axes = plt.subplots(1, 2 if moon_separation else 1, figsize=(14, 7))#, constrained_layout=True)
    plt.tight_layout(rect=[0, 0.1, 1, 1])
    if not moon_separation:
        axes = [axes]

    ax1 = axes[0]
    ax1.plot(timescale_dt, moon_altitudes, label='Moon Altitude', color='gray')
    ax1.axvspan(sun06_times[0], sun06_times[-1], color = 'whitesmoke', alpha = 0.5)
    ax1.axvspan(sun612_times[0], sun612_times[-1], color = 'lightgray', alpha = 0.5)
    ax1.axvspan(sunbelow12_times[0], sunbelow12_times[-1], color = 'darkgray', alpha = 0.5)
    ax1.axhline(y=25, color = 'black', linestyle = '--')
    for i in range(len(objects)):
        altitudes = calculate_visibility.CalculateAltitudes(ra=objects[i].ra, dec=objects[i].dec, time=timescale)
        max_alt = max(altitudes)
        max_alt_index = altitudes.index(max_alt)
        max_time = timescale_dt[max_alt_index]
        ax1.plot(timescale_dt, altitudes, label=f"{i + 1} - {objects[i].name}", color='black')
        ax1.text(max_time, max_alt + 2, str(i + 1), fontsize=12, color='black', ha='center')
    ax1.set_xlabel('UTC [month-day hour]')
    ax1.set_ylabel('Altitude [deg]')
    ax1.grid()
    ax1.set_ylim(0, 90)
    ax1.set_title('Altitude')    


    if moon_separation:
            ax2 = axes[1]
            for i in range(len(objects)):
                separations = []
                obj_coords = SkyCoord(ra=objects[i].ra * u.deg, dec=objects[i].dec * u.deg)
                for moon_point in moon_coords:
                    separation = obj_coords.separation(moon_point)
                    separations.append(separation.deg)
                ax2.axvspan(sun06_times[0], sun06_times[-1], color = 'whitesmoke', alpha = 0.5)
                ax2.axvspan(sun612_times[0], sun612_times[-1], color = 'lightgray', alpha = 0.5)
                ax2.axvspan(sunbelow12_times[0], sunbelow12_times[-1], color = 'darkgray', alpha = 0.5)
                ax2.plot(timescale_dt, separations, color='black')
                max_sep = max(separations)
                max_idx = separations.index(max_sep)
                max_time = timescale_dt[max_idx]
                ax2.text(max_time, max_sep + 2, str(i + 1), fontsize=12, color='black', ha='center')
            ax2.set_xlabel('UTC [month-day hour]')
            ax2.set_ylabel('Separation [deg]')
            ax2.grid()
            ax2.set_ylim(0, 180)
            ax2.set_title('Moon Separation')

    fig.legend(loc='lower center', bbox_to_anchor=(0.5, 0.05), fancybox=True, shadow=True, ncol=len(objects) // 2 + 1, fontsize=10)
    plt.subplots_adjust(bottom=0.3)  
    plt.show()



