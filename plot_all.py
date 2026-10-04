import calculate_visibility
import math
import numpy as np
from create_objects import PIWNICE
import matplotlib.pyplot as plt
from astropy.coordinates import SkyCoord
import astropy.units as u
from sun_events import BodyAlt

#add location as parameter

# (sun altitude limit, color) - bands overlap, so the sky gets darker with every twilight stage
TWILIGHT_BANDS = [(0, 'whitesmoke'), (-6, 'lightgray'), (-12, 'darkgray')]
PLOT_HEIGHT = 4             # inches, without the legend
LEGEND_MAX_COLUMNS = 6


def ContiguousSpans(times, mask):
    """Return (start, end) pairs for every contiguous run of True in mask."""
    spans = []
    start = None
    for i, flag in enumerate(mask):
        if flag and start is None:
            start = i
        elif not flag and start is not None:
            spans.append((times[start], times[i - 1]))
            start = None
    if start is not None:
        spans.append((times[start], times[len(mask) - 1]))
    return spans

def TwilightSpans(times, sun_altitudes):
    sun_altitudes = np.asarray(sun_altitudes)
    return [(color, ContiguousSpans(times, sun_altitudes <= limit)) for limit, color in TWILIGHT_BANDS]

def ShadeTwilight(ax, twilight_spans):
    for color, spans in twilight_spans:
        for start, end in spans:
            ax.axvspan(start, end, color = color, alpha = 0.5)

def MoonSeparations(obj, moon_coords):
    obj_coords = SkyCoord(ra = obj.ra * u.deg, dec = obj.dec * u.deg)
    # measure in the Moon's topocentric frame - converting the Moon to ICRS would move it to the barycentre
    return moon_coords.separation(obj_coords, origin_mismatch = "ignore").deg

def LabelMaximum(ax, times, values, label, ylim_top):
    max_idx = int(np.argmax(values))
    y = min(values[max_idx] + 2, ylim_top - 4)
    ax.text(times[max_idx], y, label, fontsize=12, color='black', ha='center')


def Plot(objects:list, timescale, moon_separation:bool = False):
    timescale_dt = timescale.datetime

    sun_altitudes = BodyAlt(timescale=timescale, location=PIWNICE, body = 'sun').altitudes
    moon = BodyAlt(timescale=timescale, location=PIWNICE, body = 'moon')
    twilight_spans = TwilightSpans(timescale_dt, sun_altitudes)

    # legend below the plots grows in rows instead of running off the sides of the figure
    legend_entries = len(objects) + 1
    legend_ncol = min(legend_entries, LEGEND_MAX_COLUMNS)
    legend_height = 0.25 * math.ceil(legend_entries / legend_ncol) + 0.3
    fig_height = PLOT_HEIGHT + legend_height

    fig, axes = plt.subplots(1, 2 if moon_separation else 1, figsize=(16, fig_height))
    if not moon_separation:
        axes = [axes]

    ax1 = axes[0]
    ax1.plot(timescale_dt, moon.altitudes, label='Moon Altitude', color='gray')
    ShadeTwilight(ax1, twilight_spans)
    ax1.axhline(y=25, color = 'black', linestyle = '--')
    for i, obj in enumerate(objects):
        altitudes = calculate_visibility.CalculateAltitudes(ra=obj.ra, dec=obj.dec, time=timescale)
        ax1.plot(timescale_dt, altitudes, label=f"{i + 1} - {obj.name}", color='black')
        LabelMaximum(ax1, timescale_dt, altitudes, str(i + 1), ylim_top=90)
    ax1.set_xlabel('UTC [month-day hour]')
    ax1.set_ylabel('Altitude [deg]')
    ax1.grid()
    ax1.set_ylim(0, 90)
    ax1.set_title('Altitude')


    if moon_separation:
        ax2 = axes[1]
        ShadeTwilight(ax2, twilight_spans)
        for i, obj in enumerate(objects):
            separations = MoonSeparations(obj, moon.coords)
            ax2.plot(timescale_dt, separations, color='black')
            LabelMaximum(ax2, timescale_dt, separations, str(i + 1), ylim_top=180)
        ax2.set_xlabel('UTC [month-day hour]')
        ax2.set_ylabel('Separation [deg]')
        ax2.grid()
        ax2.set_ylim(0, 180)
        ax2.set_title('Moon Separation')

    fig.legend(loc='lower center', bbox_to_anchor=(0.5, 0.1 / fig_height), fancybox=True, shadow=True, ncol=legend_ncol, fontsize=10)
    plt.subplots_adjust(bottom=(legend_height + 0.7) / fig_height)
    plt.show()
