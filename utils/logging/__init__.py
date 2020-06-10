# -*- coding: utf-8 -*-
import functools
import inspect
import logging
import os


def with_line_number():
    """Add the line number of the called function.
    """
    def the_decorator(func):
        @functools.wraps(func)
        def func_wrapper(self, *args, **kwargs):
            caller = inspect.getframeinfo(inspect.stack()[1][0])
            if 'extra' not in kwargs:
                kwargs['extra'] = {}
            basename = os.path.basename(caller.filename)
            kwargs['extra'].update({
                'basename': basename,
                'linenum': caller.lineno,
            })
            return func(self, *args, **kwargs)
        return func_wrapper
    return the_decorator


class WithFieldsAdapter(logging.LoggerAdapter):
    """Append some metadata to each subsequent logging call.
    """
    def process(self, msg, kwargs):
        b = ''
        if self.extra:
            b = ' '.join(['(%s: %s)' % (k, v) for k, v in self.extra.items() if v])
        return ('%s %s' % (b, msg)).strip(), kwargs


class Logger(object):
    """Custom logger definition.
    """
    def __init__(self, name, extra=None):
        self.name = name
        self._root = logging.getLogger(self.name)
        self._extra = extra or {}
        self._log = WithFieldsAdapter(self._root, self._extra)

    @with_line_number()
    def debug(self, *args, **kwargs):
        self._log.debug(*args, **kwargs)

    @with_line_number()
    def info(self, *args, **kwargs):
        self._log.info(*args, **kwargs)

    @with_line_number()
    def warning(self, *args, **kwargs):
        self._log.warning(*args, **kwargs)

    @with_line_number()
    def error(self, *args, **kwargs):
        self._log.error(*args, **kwargs)

    @with_line_number()
    def exception(self, *args, **kwargs):
        self._log.exception(*args, **kwargs)

    def set_level(self, level):
        self._log.setLevel(level)

    def with_fields(self, **metadata_dict):
        """Append some metadata to each subsequent logging call.
        """
        extra = self._extra.copy()
        extra.update(metadata_dict)
        self._log = WithFieldsAdapter(self._root, extra)


def task_logger(name):
    """Decorator to provide custom task logger.
    """
    def the_decorator(func):
        @functools.wraps(func)
        def func_wrapper(self, *args, **kwargs):
            extra = {'c_task': self.request.id}
            self.log = Logger('%s.%s' % (name, func.__name__), extra)
            try:
                return func(self, *args, **kwargs)
            except Exception as e:
                self.log.exception(str(e))
                raise
        return func_wrapper
    return the_decorator
