from .. import AttributeWrapper


class AttributeScalarValue(AttributeWrapper):
    @property
    def value(self):
        return self.parse_value(self.parentElementWrapper.element.get(self.name))

    @value.setter
    def value(self,v):
        self.parentElementWrapper.create()
        e=self.parentElementWrapper.element.set(self.name,self.format_value(v))
