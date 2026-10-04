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
PLOT_WIDTH = 14             # inches
PLOT_HEIGHT = 5             # inches, without the legend
LEGEND_MAX_COLUMNS = 4
# 8 colours that stay distinguishable also for colour-blind readers; with more targets the
# line style changes, so every target up to 32 gets its own colour + style combination
TARGET_COLORS = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
TARGET_LINESTYLES = ['-', '--', ':', '-.']


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


def TargetStyle(index:int):
    """Colour and line style of the index-th target (0-based)."""
    color = TARGET_COLORS[index % len(TARGET_COLORS)]
    linestyle = TARGET_LINESTYLES[(index // len(TARGET_COLORS)) % len(TARGET_LINESTYLES)]
    return color, linestyle

def LegendLabel(number:int, obj, mean_moon_separation:float):
    return f"{number} - {obj.name} ({mean_moon_separation:.0f} deg)"


def Plot(objects:list, timescale):
    timescale_dt = timescale.datetime

    sun_altitudes = BodyAlt(timescale=timescale, location=PIWNICE, body = 'sun').altitudes
    moon = BodyAlt(timescale=timescale, location=PIWNICE, body = 'moon')
    twilight_spans = TwilightSpans(timescale_dt, sun_altitudes)

    # legend below the plot grows in rows instead of running off the sides of the figure
    legend_entries = len(objects) + 1
    legend_ncol = min(legend_entries, LEGEND_MAX_COLUMNS)
    legend_height = 0.2 * math.ceil(legend_entries / legend_ncol) + 0.2
    fig_height = PLOT_HEIGHT + legend_height

    fig, ax = plt.subplots(figsize=(PLOT_WIDTH, fig_height))
    ax.plot(timescale_dt, moon.altitudes, label='Moon Altitude', color='gray')
    ShadeTwilight(ax, twilight_spans)
    ax.axhline(y=25, color = 'black', linestyle = '--')
    for i, obj in enumerate(objects):
        altitudes = calculate_visibility.CalculateAltitudes(ra=obj.ra, dec=obj.dec, time=timescale)
        # separation changes only by a few degrees during the night, so the mean is enough
        mean_separation = float(np.mean(MoonSeparations(obj, moon.coords)))
        color, linestyle = TargetStyle(i)
        ax.plot(timescale_dt, altitudes, label=LegendLabel(i + 1, obj, mean_separation),
                color=color, linestyle=linestyle, linewidth=2)
        LabelMaximum(ax, timescale_dt, altitudes, str(i + 1), ylim_top=90)
    ax.set_xlabel('UTC [month-day hour]')
    ax.set_ylabel('Altitude [deg]')
    ax.grid()
    ax.set_ylim(0, 90)
    ax.set_title('Altitude (mean Moon separation in brackets)')

    fig.legend(loc='lower center', bbox_to_anchor=(0.5, 0.1 / fig_height), fancybox=True, shadow=True, ncol=legend_ncol, fontsize=10)
    plt.subplots_adjust(bottom=(legend_height + 0.6) / fig_height)
    plt.show()
