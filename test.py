import datetime

def get_last_whole_week(today=None, epoch=False):
    # a date object
    date_today = today or datetime.date.today()


    # By default day 0 is Monday. Sunday is 6.
    dow_today = date_today.weekday()

    if dow_today == 6:
        days_ago_saturday = 1
    else:
        # If day between 0-5, to get last saturday, we need to go to day 0 (Monday), then two more days.
        days_ago_saturday = dow_today + 2
    # Make a timedelta object so we can do date arithmetic.
    delta_saturday = datetime.timedelta(days=days_ago_saturday)
    # saturday is now a date object representing last saturday
    saturday = date_today - delta_saturday
    # timedelta object representing '6 days'...
    delta_prevsunday = datetime.timedelta(days=6)
    # Making a date object. Subtract the 6 days from saturday to get "the Sunday before that".
    prev_sunday = saturday - delta_prevsunday

    # we need to return a range starting with midnight on a Sunday, and ending w/ 23:59:59 on the
    # following Saturday... optionally in epoch format.

    if epoch:
        # saturday is date obj = 'midnight saturday'. We want the last second of the day, not the first.
        saturday_epoch = time.mktime(saturday.timetuple()) + 86399
        prev_sunday_epoch = time.mktime(prev_sunday.timetuple())
        last_week = (prev_sunday_epoch, saturday_epoch)
    else:
        saturday_str = saturday.strftime('%Y-%m-%d')
        prev_sunday_str = prev_sunday.strftime('%Y-%m-%d')
        last_week = (prev_sunday_str, saturday_str)
    return last_week