from . import ScalarValue


class StringValue(ScalarValue):
    def parse_value(self,v):
        return v

    def format_value(self,v):
        return unicode(v)
