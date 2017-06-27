from . import TextScalarValue,TextContainer,IntegerValue


class TextIntegerValue(TextScalarValue,IntegerValue): pass


class TextIntegerValueContainer(TextContainer):
    CLASS=TextIntegerValue
