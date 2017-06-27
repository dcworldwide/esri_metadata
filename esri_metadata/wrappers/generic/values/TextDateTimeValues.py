from . import TextScalarValue,TextContainer,DateValue,TimeValue,DateTimeValue


class TextDateValue(TextScalarValue,DateValue): pass
class TextTimeValue(TextScalarValue,TimeValue): pass
class TextDateTimeValue(TextScalarValue,DateTimeValue): pass


class TextDateValueContainer(TextContainer):
    CLASS=TextDateValue

class TextTimeValueContainer(TextContainer):
    CLASS=TextTimeValue

class TextDateTimeValueContainer(TextContainer):
    CLASS=TextDateTimeValue
