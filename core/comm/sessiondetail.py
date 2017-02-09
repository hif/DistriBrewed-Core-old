class SessionDetail:
    SECONDS = 1
    MINUTES = 60
    HOURS = 60*MINUTES
    DAYS = 24*HOURS
    HOLD_TIME_UNITS = (
        (SECONDS, 'Seconds'),
        (MINUTES, 'Minutes'),
        (HOURS, 'Hours'),
        (DAYS, 'Days')
    )
    id = 0
    session = 0
    index = 0
    name = ""
    worker_type = ""
    target = ""
    hold_time = 1
    time_unit_seconds = MINUTES
    notes = ""
    done = False