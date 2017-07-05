from . import TextScalarValue,TextContainer,DecimalValue


class TextDecimalValue(TextScalarValue,DecimalValue): pass


class TextDecimalValueContainer(TextContainer):
    CLASS=TextDecimalValue
