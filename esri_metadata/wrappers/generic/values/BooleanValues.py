from . import ScalarValue
from ...errors import InvalidValueError


class BooleanValueBaseClass(ScalarValue):
    CHOICES=[]

    def parse_value(self,v):
        if v not in self.CHOICES:
            raise InvalidValueError('Invalid BooleanValue: {}'.format(v))
        return self.CHOICES[1]==v

    def format_value(self,v):
        return self.CHOICES[1] if v else self.CHOICES[0]


class BooleanTitleCaseValue(BooleanValueBaseClass):
    CHOICES=['False','True']
