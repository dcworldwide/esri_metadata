import datetime

from . import ScalarValue
from ...errors import InvalidValueError


class DateTimeValueBaseClass(ScalarValue):
    FORMAT=''

    def parse_value(self,v):
        try:
            r=datetime.datetime.strptime(v.strip(),self.FORMAT) if v else None
        except ValueError as e:
            raise InvalidValueError('Invalid {}: {}'.format(self.__class__.__name__,v))
        return r

    def format_value(self,v):
        return datetime.datetime.strftime(v,self.FORMAT)


class DateValue(DateTimeValueBaseClass):
    FORMAT='%Y%m%d'

class TimeValue(DateTimeValueBaseClass):
    FORMAT='%H%M%S'

class DateTimeValue(DateTimeValueBaseClass):
    FORMAT='%Y-%m-%dT%H:%M:%S'
