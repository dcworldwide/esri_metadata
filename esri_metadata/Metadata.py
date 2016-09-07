"""
Metadata class
"""
import os
import datetime

from xml.dom import minidom
from xml.dom import Node


class Wrapper(object):
    def set_name(self,name):
        self.name=name

    @property
    def is_bound(self):
        return self.parentElementWrapper is not None

    def bind(self,parentElementWrapper):
        self.parentElementWrapper=parentElementWrapper



class ElementWrapper(Wrapper):
    def bind(self,parentElementWrapper):
        super(ElementWrapper,self).bind(parentElementWrapper)
        self.element=None
        if not self.parentElementWrapper.is_missing:
            for e in self.parentElementWrapper.element.childNodes:
                if e.nodeType==Node.ELEMENT_NODE and e.localName==self.name:
                    if self.element is not None:
                        raise Exception('Multiple elements found when expecting one')
                    self.element=e


    def create(self):
        if not self.is_bound: raise Exception('Cannot create on unbound Element')
        if self.is_missing:
            self.parentElementWrapper.create()
            e=self.parentElementWrapper.element.ownerDocument.createElement(self.name)
            self.parentElementWrapper.element.appendChild(e)
            self.element=e


    @property
    def is_missing(self):
        return self.is_bound and self.element is None


class AttributeWrapper(Wrapper):
    def bind(self,parentElementWrapper):
        super(AttributeWrapper,self).bind(parentElementWrapper)
        if not self.parentElementWrapper.is_missing:
            self.attribute=self.parentElementWrapper.element.getAttributeNode(self.name)


class List(Wrapper):
    def __init__(self,itemType):
        self.itemType=itemType

    def bind(self,parentElementWrapper):
        super(List,self).bind(parentElementWrapper)
        self.elements=[]
        if not self.parentElementWrapper.is_missing:
            for e in self.parentElementWrapper.element.childNodes:
                if e.nodeType==Node.ELEMENT_NODE and e.localName==self.name:
                    self.elements.append(e)

    def __getitem__(self,i):
        e=self.elements[i]
        ew=self.itemType()
        ew.set_name(self.name)
        ew.parentElementWrapper=self
        ew.element=e
        return ew


class Container(ElementWrapper):
    def __init__(self,children=None):
        self.mapping=self.get_children() if children is None else children
        for n,w in self.mapping.items():
            w.set_name(n)

    def get_children(self):
        return {}

    def __getattr__(self,name):
        """If a physical attribute doesn't exist, check in self.mapping and bind the instance.
        """
        w=self.mapping.get(name,None)
        if w:
            w.set_name(name)
            w.bind(self)
            return w
        raise AttributeError('{} not found in {}'.format(name,self.name))



class SingleValue(object):
    def parse_value(self,v):
        raise NotImplemented()

    def format_value(self,v):
        raise NotImplemented()


class ScalarValue(ElementWrapper,SingleValue):
    @property
    def value(self):
        if self.element is None or len(self.element.childNodes)==0:
            return None
        elif len(self.element.childNodes)>1:
            raise Exception('Greater than one child node for type: {}'.format(self.__class__.__name__))
        v=self.element.childNodes[0]
        return self.parse_value(v.data)

    @value.setter
    def value(self,v):
        # self.parentElementWrapper.create()
        e=self.element.ownerDocument.createTextNode(self.format_value(v))
        for n in self.element.childNodes:
            self.element.removeChild(n)
            n.unlink()
        self.element.appendChild(e)


class StringValue(ScalarValue):
    def parse_value(self,v):
        return v

    def format_value(self,v):
        return str(v)


class DateTimeValue(ScalarValue):
    def parse_value(self,v):
        v=v.strip()
        return datetime.datetime.strptime(v,'%Y-%m-%dT%H:%M:%S') if v else None

    def format_value(self,v):
        return datetime.datetime.strftime(v,'%Y-%m-%dT%H:%M:%S')


class AttributeScalarValue(AttributeWrapper,SingleValue):
    @property
    def value(self):
        return self.parse_value(self.attribute.value)

class AttributeStringValue(AttributeScalarValue):
    def parse_value(self,v):
        return v
    def format_value(self,v):
        return str(v)



class Keywords(Container):
    def get_children(self):
        return {
            'keyword':List(StringValue),
            'thesaName':Container({'resTitle':StringValue(),}),
        }

class TpCat(Container):
    def get_children(self):
        return {
            'TopicCatCd':Container({'value':AttributeStringValue(),}),
        }

class Contact(Container):
    def get_children(self):
        return {
            'displayName':StringValue(),# similar to rpIndName but not always populated
            'rpIndName':StringValue(),
            'rpOrgName':StringValue(),
            'rpPosName':StringValue(),
            'role':Container({'RoleCd':Container({'value':AttributeStringValue(),}),}),
            'rpCntInfo':Container({
                'cntAddress':Container({
                    'eMailAdd':StringValue(),
                    'addressType':AttributeStringValue(),
                    'delPoint':StringValue(),
                    'city':StringValue(),
                    'state':StringValue(),
                    'postCode':StringValue(),
                    'country':StringValue(),
                }),
                'cntPhone':Container({
                    'voiceNum':StringValue(),
                    'faxNum':StringValue(),
                }),
            }),
        }



class Metadata(Container):
    def __init__(self,datasetPath):
        if os.path.isfile(datasetPath):
            self.load_from_xml(datasetPath)
        self.set_name('metadata')
        self.bind()
        super(Metadata,self).__init__()


    def get_children(self):
        return {
            'dataIdInfo':Container({
                'idAbs':StringValue(),
                'idCitation':Container({
                    'resTitle':StringValue(),
                    'resAltTitle':StringValue(),
                    'citRespParty':List(Contact),
                    'date':Container({'pubDate':DateTimeValue(),}),
                }),
                'idPoC':Contact(),
                'themeKeys':List(Keywords),
                'placeKeys':List(Keywords),
                'searchKeys':List(Keywords),
                'tpCat':List(TpCat),
            }),
        }


    def load_from_xml(self,path):
        self.doc=minidom.parse(path)


    def bind(self):
        """Special case binding"""
        self.element=self.doc.documentElement
        self.parentElementWrapper=self


