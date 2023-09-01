import datetime
import re
from apscheduler.schedulers.background import BackgroundScheduler

def add_interval_schedule(type='interval', **kwargs):

    if (type == 'interval'):
        params = {}
        for k, v in kwargs.items():
            if k not in ('year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second', 'start_date', 'end_date'):
                pass
            else:
                params[k] = v
        print(params)