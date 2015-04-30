from unittest import TestCase

from spidermon.stats import Stats
from spidermon import settings
from .options import MonitorOptions, MonitorOptionsMetaclass


class Monitor(TestCase):
    __metaclass__ = MonitorOptionsMetaclass

    def __init__(self, methodName='runTest', name=None):
        super(Monitor, self).__init__(methodName)
        self._name = name
        self._data = None
        self._parent = None
        self._init_method()

    @property
    def name(self):
        return ':'.join([self.monitor_name, self.method_name])

    @property
    def full_name(self):
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        parts.append(self.name)
        return '/'.join(parts)

    @property
    def level(self):
        return self.method_level or \
               self.monitor_level or \
               self.parent_level or \
               settings.DEFAULT_MONITOR_LEVEL

    @property
    def order(self):
        return self.method.options.order

    @property
    def monitor_name(self):
        return self._name or \
               self.options.name or \
               self.__class__.__name__

    @property
    def monitor_full_name(self):
        parts = []
        if self.parent and self.parent.full_name:
            parts.append(self.parent.full_name)
        parts.append(self.monitor_name)
        return '/'.join(parts)

    @property
    def monitor_description(self):
        return self.options.description or \
               self.__class__.__doc__ or \
               settings.DEFAULT_DESCRIPTION

    @property
    def monitor_level(self):
        return self.options.level

    @property
    def method(self):
        return getattr(self, self._testMethodName)

    @property
    def method_name(self):
        return self.method.options.name or \
               self._testMethodName

    @property
    def method_description(self):
        return self.method.options.description or \
               self.method.__func__.__doc__ or \
               settings.DEFAULT_DESCRIPTION

    @property
    def method_level(self):
        return self.method.options.level

    @property
    def parent(self):
        return self._parent

    @property
    def parent_level(self):
        return self.parent.level

    def set_parent(self, parent):
        self._parent = parent

    def init_data(self, **data):
        self._data = data

    def debug_tree(self, level=0):
        return level*'\t' + repr(self) + '\n'

    def _init_method(self):
        MonitorOptions.add_or_create(self.method.__func__)

    def __repr__(self):
        return '<MONITOR:(%s) at %s>' % (self.name, hex(id(self)))

    def __str__(self):
        return self.name


class StatsMonitor(Monitor):
    def __init__(self, methodName='runTest', name=None):
        super(StatsMonitor, self).__init__(methodName, name)
        self.stats = Stats()

    def init_data(self, **data):
        super(StatsMonitor, self).init_data(**data)
        stats = data.get('stats')
        if stats:
            self.stats = Stats(stats)


class JobMonitor(StatsMonitor):
    def __init__(self, methodName='runTest', name=None):
        super(JobMonitor, self).__init__(methodName, name)
        self.job = {}

    def init_data(self, **data):
        super(StatsMonitor, self).init_data(**data)
        self.job = data.get('job')
