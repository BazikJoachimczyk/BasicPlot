import numpy as np
import astropy.units as u
from astropy.time import Time, TimeDelta

NIGHT_START_HOUR = 16                           # UTC
NIGHT_END_HOUR = 7                              # UTC, next day
STEP_MINUTES = 1


def _minute_grid(start: Time, minutes: int):
    return start + np.arange(0, minutes + 1, STEP_MINUTES) * u.min


def TimeScale12hrs(now: Time = None):
    if now is None:
        now = Time.now()                        # defaultowo pobiera UTC więc jest git
    return _minute_grid(now + 1 * u.min, 12 * 60 - 1)

def TimeScaleForTheNight(now: Time = None):
    if now is None:
        now = Time.now()
    now_datetime = now.to_datetime()
    if now_datetime.hour < NIGHT_END_HOUR:      # still last night
        now_datetime = (now - TimeDelta(1, format = 'jd')).to_datetime()
    start = Time(now_datetime.replace(hour = NIGHT_START_HOUR, minute = 0, second = 0, microsecond = 0))
    night_minutes = (24 - NIGHT_START_HOUR + NIGHT_END_HOUR) * 60
    return _minute_grid(start, night_minutes)
