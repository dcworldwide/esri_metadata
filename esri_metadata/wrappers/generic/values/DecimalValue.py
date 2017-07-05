from decimal import Decimal

from . import ScalarValue
from ...errors import InvalidValueError


class DecimalValue(ScalarValue):
    def parse_value(self,v):
        try:
            r=Decimal(v)
        except ValueError as e:
            raise InvalidValueError('Invalid DecimalValue: {}'.format(v))
        return r

    def format_value(self,v):
        return unicode(v)
