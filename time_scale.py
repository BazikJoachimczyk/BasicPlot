from astropy.time import Time, TimeDelta


def TimeScale12hrs():
    now = Time.now()                            # defaultowo pobiera UTC więc jest git
    delta_time = TimeDelta(60, format = 'sec')
    time_scale = []
    for i in range(720):                        # 60*12h
        now += delta_time
        time_scale.append(now)
    return time_scale


def GivenTimeScale(start: list, end:list):
    return None

