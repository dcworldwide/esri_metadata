from . import ScalarValue
from ...errors import InvalidValueError


class IntegerValue(ScalarValue):
    def parse_value(self,v):
        try:
            r=int(v)
        except ValueError as e:
            raise InvalidValueError('Invalid IntegerValue: {}'.format(v))
        return r

    def format_value(self,v):
        return unicode(v)
