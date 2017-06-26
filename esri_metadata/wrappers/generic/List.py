import copy

from . import Wrapper
from ..errors import UnboundElementError


class List(Wrapper):
    def __init__(self,itemType):
        self.itemType=itemType

    def bind(self,parentElementWrapper):
        super(List,self).bind(parentElementWrapper)
        self.elements=[]
        if not self.parentElementWrapper.is_missing:
            for e in self.parentElementWrapper.element:
                if e.tag==self.name:
                    self.elements.append(e)


    @property
    def is_present(self):
        return self.is_bound and len(self)>0

    @property
    def is_missing(self):
        return not self.is_present


    def __len__(self):
        return len(self.elements)

    def __getitem__(self,i):
        e=self.elements[i]
        ew=self.itemType()
        ew.set_name(self.name)
        ew.parentElementWrapper=self
        ew.element=e
        return ew

    def __delitem__(self,i):
        e=self.elements[i]
        self.parentElementWrapper.element.remove(e)
        del self.elements[i]

    def __iter__(self):
        for i in range(0,len(self.elements)):
            yield self.__getitem__(i)

    def append(self,elementWrapper=None):
        if not self.is_bound: raise UnboundElementError('Cannot create on unbound Element')
        if self.parentElementWrapper.is_missing: self.parentElementWrapper.create()
        if elementWrapper is not None:
            if not isinstance(elementWrapper,self.itemType): raise TypeError('Cannot assign {} where {} is expected'.format(elementWrapper.__class__.__name__,self.itemType.__name__))
            e=copy.deepcopy(elementWrapper.element)
            # set the name of the element (it might have been called something else where it came from)
            e.tag=self.name
            self.parentElementWrapper.element.append(e)
        else:
            e=ET.SubElement(self.parentElementWrapper.element,self.name)
        self.elements.append(e)
        return self[len(self.elements)-1]
