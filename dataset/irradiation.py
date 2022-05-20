import json

from typing import Dict


def load_data(filename: str) -> Dict:
    """Returns a dictionary containing the average irradiation hour by hour
    organized by month, day and hour loaded from the specified file.

    For example, the average irradiation of 23 April at 10 AM is data[4][23][10]"""

    def str2datetime(s):
        date_, time_ = s.split(':')
        hour, minutes = int(time_[:2]), int(time_[2:])
        year, month, day = int(date_[:4]), int(date_[4:6]), int(date_[6:10])
        return year, month, day, hour, minutes

    data = json.load(open(filename, 'r'))
    values = dict()
    for d in data['outputs']['hourly']:
        _, month, day, _, _ = str2datetime(d['time'])
        if not month in values: values[month] = dict()
        if not day in values[month]: values[month][day] = list()
        values[month][day].append(d['G(i)'])
    return values


def load_months_avg(filename: str) -> Dict:
    """Returns a dictionary that contains for each month the average of the
    average irradiation of each hour of the day loaded from the specified file."""

    def month_avg(month_data):
        ret = []
        for hour in range(24):
            acc = 0
            for day in month_data:
                acc += month_data[day][hour]
            ret.append(acc / len(month_data))
        return ret

    data = load_data(filename)

    avg = dict()
    for month in data:
        avg[month] = month_avg(data[month])

    return avg
