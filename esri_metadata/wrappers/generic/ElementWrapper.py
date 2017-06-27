import copy

from . import Wrapper
from ..errors import InvalidStructureError,UnboundElementError


class ElementWrapper(Wrapper):
    def bind(self,parentElementWrapper):
        super(ElementWrapper,self).bind(parentElementWrapper)
        self.element=None
        if not self.parentElementWrapper.is_missing:
            for e in self.parentElementWrapper.element:
                if e.tag==self.name:
                    if self.element is not None:
                        raise InvalidStructureError('Multiple elements found when expecting one')
                    self.element=e


    @property
    def is_missing(self):
        return not self.is_present

    @property
    def is_present(self):
        return self.is_bound and self.element is not None


    def create(self):
        if not self.is_bound: raise UnboundElementError('Cannot create on unbound Element')
        if self.is_missing:
            self.parentElementWrapper.create()
            e=ET.SubElement(self.parentElementWrapper.element,self.name)
            self.element=e


    def set(self,elementWrapper):
        parentNode=self.parentElementWrapper.element
        self.delete()
        e=copy.deepcopy(elementWrapper.element)
        e.tag=self.name
        parentNode.append(e)
        self.element=e


    def delete(self):
        self.parentElementWrapper.element.remove(self.element)
        self.element=None
