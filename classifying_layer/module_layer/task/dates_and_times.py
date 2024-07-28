from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import calendar

def get_dates_by_day_name(day_name, next=False):
    today = datetime.today()
    target_day = ['sunday', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'].index(day_name)
    current_day = today.weekday()
    if next:
        diff = (target_day - current_day + 7) % 7 + 7
    else:
        diff = (target_day - current_day + 7) % 7
    date = today + timedelta(days=diff)
    return date

def get_this_weeks_dates_by_day_names(day_names):
    today = datetime.today()
    dates = []
    for day in day_names:
        get_dates_by_day_name(day)
    return dates

def get_next_weeks_dates_by_day_names(day_names):
    today = datetime.today()
    dates = []
    for day in day_names:
        get_dates_by_day_name(day, next=True)
    return dates

def get_dates_for_today_and_or_tomorrow(rel_days):
    today = datetime.today()
    dates = []
    if 'today' in rel_days:
        dates.append(today)
    if 'tomorrow' in rel_days:
        dates.append(today + timedelta(days=1))
    return dates

def get_start_end_today_to_x_years(x):
    x_to_months = x * 12
    today = datetime.today()
    start = today
    end = (today + relativedelta(months=x_to_months)).replace(day=calendar.monthrange((today + relativedelta(months=x)).year, (today + relativedelta(months=x)).month)[1])
    return start, end

def get_next_month_start_end():
    today = datetime.today()
    first_day_next_month = (today.replace(day=1) + relativedelta(months=1))
    last_day_next_month = first_day_next_month.replace(day=calendar.monthrange(first_day_next_month.year, first_day_next_month.month)[1])
    return first_day_next_month, last_day_next_month

def get_start_end_today_to_x_months(x):
    today = datetime.today()
    start = today
    end = (today + relativedelta(months=x)).replace(day=calendar.monthrange((today + relativedelta(months=x)).year, (today + relativedelta(months=x)).month)[1])
    return start, end

def get_this_month_start_end():
    today = datetime.today()
    first_day_this_month = today.replace(day=1)
    last_day_this_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])
    return first_day_this_month, last_day_this_month

def get_date_by_month_and_num(month_name, num_day):
    today = datetime.today()
    month_number = list(calendar.month_name).index(month_name.capitalize())
    date = datetime(today.year, month_number, num_day)
    return date

def get_month_start_and_end_by_name(month_name):
    today = datetime.today()
    month_number = list(calendar.month_name).index(month_name.capitalize())
    if month_number < today.month:
        year = today.year + 1
    else:
        year = today.year
    first_day = datetime(year, month_number, 1)
    last_day = datetime(year, month_number, calendar.monthrange(year, month_number)[1])
    return first_day, last_day

def get_next_week_start_end():
    today = datetime.today()
    start = today + timedelta(days=(7 - today.weekday()))
    end = start + timedelta(days=6)
    return start, end

def get_start_end_today_to_x_weeks(x):
    today = datetime.today()
    start = today
    end = today + timedelta(weeks=x)
    return start, end

def get_this_week_start_end():
    today = datetime.today()
    start = today - timedelta(days=today.weekday())
    end = start + timedelta(days=6)
    return start, end

def get_next_weekend_start_end():
    today = datetime.today()
    start = today + timedelta((5 - today.weekday() + 7) % 7 + 7)
    end = start + timedelta(days=1)
    return start, end

def get_start_end_x_weekends(x):
    today = datetime.today()
    start = today + timedelta(weeks=x, days=(5 - today.weekday() + 7) % 7)
    end = start + timedelta(days=1)
    return start, end

def get_this_weekend_start_end():
    today = datetime.today()
    start = today + timedelta((5 - today.weekday() + 7) % 7)
    end = start + timedelta(days=1)
    return start, end

def get_start_end_today_to_x_days(x):
    today = datetime.today()
    start = today
    end = today + timedelta(days=x)
    return start, end

def get_time_now_to_x_hours(x):
    now = datetime.now()
    start = now
    end = now + timedelta(hours=x)
    return start, end

def get_time_from_num(num, am=False, pm=False):
    now = datetime.now()

    if am:
        time = datetime(hour=num)
    elif pm:
        num += 12
        time = datetime(hour=num)
    if now.hour > num:
        num += 12
    time = datetime(hour=num)
    return time

def get_time_now_to_eod():
    now = datetime.now()
    start = now
    end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
    return start, end

def get_time_now_to_x_minutes(x):
    now = datetime.now()
    start = now
    end = now + timedelta(minutes=x)
    return start, end

def switch_am_pm(now_am_pm):
    if 'AM' in now_am_pm:
        return ' PM'
    else:
        return ' AM'

def get_am_or_pm(now, hour, minute):
    norm_now = now.hour
    now_am_pm = ' AM' if now.hour < 12 else ' PM'
    
    if norm_now >= 12:
        norm_now -= 12

    if hour < norm_now:
        now_am_pm = switch_am_pm(now_am_pm)
    elif hour == norm_now and minute < now.minute:
        now_am_pm = switch_am_pm(now_am_pm)
    
    return now_am_pm

def get_time_from_spec(time_spec, am, pm):
    now = datetime.now()
    hour = int(time_spec.split(':')[0])
    minute = int(time_spec.split(':')[1])
    is_am = False
    if am:
        time_spec += ' AM'
        is_am = True
    elif pm:
        time_spec += ' PM'
    else:
        am_or_pm = get_am_or_pm(now, hour, minute)
        time_spec += am_or_pm
        if 'AM' in am_or_pm:
            is_am = True
    
    return datetime.strptime(time_spec, '%I:%M %p').time(), is_am
