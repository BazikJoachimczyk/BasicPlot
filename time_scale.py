from astropy.time import Time, TimeDelta


def TimeScale12hrs():
    now = Time.now()                            # defaultowo pobiera UTC więc jest git
    delta_time = TimeDelta(60, format = 'sec')
    time_scale = []
    for i in range(720):                        # 60*12h
        now += delta_time
        time_scale.append(now)
    return time_scale

def TimeScaleForTheNight():
    now = Time.now()
    current_hour = now.datetime.hour
    delta_time = TimeDelta(5, format = 'min')
    time_scale = []
    print('current hour', current_hour)
    if current_hour < 7:
        one_day = TimeDelta(1, format = 'day')
        yesterday = now - one_day
        yesterday_datetime = yesterday.to_datetime()
        yesterday_datetime.replace(hour = 18, minute = 0, second = 0, microsecond = 0)
        print("yesterday_datetime", yesterday_datetime)
        start = Time(yesterday_datetime)
    else:
        today_datetime = now.to_datetime()
        today_datetime.replace(hour = 18, minute = 0, second = 0, microsecond = 0)
        start = Time(today_datetime)
    print(start)
    time_scale.append(start)
    for _ in range(720):
        start += delta_time
        time_scale.append(start)
    return time_scale

def GivenTimeScale(start: list, end:list):
    return None

