from . import Wrapper
from ..errors import UnboundElementError


class AttributeWrapper(Wrapper):
    def bind(self,parentElementWrapper):
        super(AttributeWrapper,self).bind(parentElementWrapper)


    @property
    def is_present(self):
        return self.is_bound and self.parentElementWrapper.is_present and self.name in self.parentElementWrapper.element.keys()

    @property
    def is_missing(self):
        return not self.is_present


    def create(self):
        if not self.is_bound: raise UnboundElementError('Cannot create on unbound Element')
        if self.is_missing:
            self.parentElementWrapper.create()
            self.parentElementWrapper.element.set(self.name,'')
