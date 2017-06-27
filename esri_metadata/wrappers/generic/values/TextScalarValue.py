from .. import TextWrapper
from ...errors import InvalidStructureError


class TextScalarValue(TextWrapper):# TODO: also ScalarValue here?
    @property
    def value(self):
        if self.parentElementWrapper.is_missing:
            return None
        elif len(self.parentElementWrapper.element)>0:
            raise InvalidStructureError('Greater than one child node for type: {}'.format(self.__class__.__name__))
        v=self.parentElementWrapper.element.text
        return self.parse_value(v)

    @value.setter
    def value(self,v):
        self.parentElementWrapper.create()
        e=self.parentElementWrapper.element
        e.text=self.format_value(v)
        # just remove any child elements in case, because this is supposed to be a scalar value
        for n in e:
            e.remove(n)
