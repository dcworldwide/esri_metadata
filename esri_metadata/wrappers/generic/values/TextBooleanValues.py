from . import TextScalarValue,TextContainer,BooleanTitleCaseValue


class TextBooleanTitleCaseValue(TextScalarValue,BooleanTitleCaseValue): pass


class TextBooleanTitleCaseValueContainer(TextContainer):
    CLASS=TextBooleanTitleCaseValue
