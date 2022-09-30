# -*- coding: utf-8 -*-
import datetime as dt


class CheckContext(object):
    """The properties of this class are made
    available as templated variables in the SQL interface.
    """
    def __init__(self, epoch, interval):
        self.epoch = int(epoch)
        self.timestamp = dt.datetime.utcfromtimestamp(epoch)
        self.interval = interval

    @property
    def ds(self):
        return self.timestamp.date()

    @property
    def tomorrow_ds(self):
        return self.ds + dt.timedelta(days=1)

    @property
    def yesterday_ds(self):
        return self.ds - dt.timedelta(days=1)

    @property
    def execution_date(self):
        return self.timestamp

    @property
    def next_execution_date(self):
        return self.timestamp + self.interval

    @property
    def prev_execution_date(self):
        return self.timestamp - self.interval

    def to_dict(self):
        return {
            'ds': self.ds,
            'tomorrow_ds': self.tomorrow_ds,
            'yesterday_ds': self.yesterday_ds,
            'execution_date': self.execution_date,
            'next_execution_date': self.next_execution_date,
            'prev_execution_date': self.prev_execution_date,
        }
