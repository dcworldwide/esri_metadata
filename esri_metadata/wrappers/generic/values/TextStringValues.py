from . import TextScalarValue,TextContainer,StringValue


class TextStringValue(TextScalarValue,StringValue): pass


class TextStringValueContainer(TextContainer):
    CLASS=TextStringValue
