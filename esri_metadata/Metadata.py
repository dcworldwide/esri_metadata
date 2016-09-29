"""
Metadata class
"""
import os
import datetime
import tempfile
import copy

import xml.etree.ElementTree as ET


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
            for e in self.parentElementWrapper.element:
                if e.tag==self.name:
                    if self.element is not None:
                        raise Exception('Multiple elements found when expecting one')
                    self.element=e


    @property
    def is_missing(self):
        return self.is_bound and self.element is None


    def create(self):
        if not self.is_bound: raise Exception('Cannot create on unbound Element')
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


class AttributeWrapper(Wrapper):
    def bind(self,parentElementWrapper):
        super(AttributeWrapper,self).bind(parentElementWrapper)

    @property
    def is_missing(self):
        return self.is_bound and (self.parentElementWrapper.is_missing or self.name not in self.parentElementWrapper.element.keys())

    def create(self):
        if not self.is_bound: raise Exception('Cannot create on unbound Element')
        if self.is_missing:
            self.parentElementWrapper.create()
            self.parentElementWrapper.element.set(self.name,'')


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
        if not self.is_bound: raise Exception('Cannot create on unbound Element')
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


class Container(ElementWrapper):
    def __init__(self,children=None):
        self.mapping=self.get_children() if children is None else children
        for n,w in self.mapping.items():
            w.set_name(n)


    def get_children(self):
        return {}


    def __getattr__(self,name):
        """If a physical attribute doesn't exist, check in self.mapping and bind the instance."""
        w=self.mapping.get(name,None)
        if w is not None:
            w.set_name(name)
            w.bind(self)
            return w
        else:
            raise AttributeError('{} not found in {}'.format(name,self.name))


    def __delattr__(self,name):
        w=getattr(self,name)
        w.delete()


class SingleValue(object):
    def parse_value(self,v):
        raise NotImplemented()

    def format_value(self,v):
        raise NotImplemented()


class ScalarValue(ElementWrapper,SingleValue):
    @property
    def value(self):
        if self.element is None:
            return None
        elif len(self.element)>0:
            raise Exception('Greater than one child node for type: {}'.format(self.__class__.__name__))
        v=self.element.text
        return self.parse_value(v)

    @value.setter
    def value(self,v):
        self.create()
        self.element.text=self.format_value(v)
        # just remove any child elements in case, because this is supposed to be a scalar value
        for n in self.element:
            self.element.remove(n)


class StringValue(ScalarValue):
    def parse_value(self,v):
        return v

    def format_value(self,v):
        return unicode(v)


class IntegerValue(ScalarValue):
    def parse_value(self,v):
        return int(v)

    def format_value(self,v):
        return unicode(v)


class DateValue(ScalarValue):
    def parse_value(self,v):
        v=v.strip()
        return datetime.datetime.strptime(v,'%Y%m%d') if v else None

    def format_value(self,v):
        return datetime.datetime.strftime(v,'%Y%m%d')


class DateTimeValue(ScalarValue):
    def parse_value(self,v):
        v=v.strip()
        return datetime.datetime.strptime(v,'%Y-%m-%dT%H:%M:%S') if v else None

    def format_value(self,v):
        return datetime.datetime.strftime(v,'%Y-%m-%dT%H:%M:%S')


class AttributeScalarValue(AttributeWrapper,SingleValue):
    @property
    def value(self):
        return self.parse_value(self.parentElementWrapper.element.get(self.name))

    @value.setter
    def value(self,v):
        self.parentElementWrapper.create()
        e=self.parentElementWrapper.element.set(self.name,self.format_value(v))


class AttributeStringValue(AttributeScalarValue):
    def parse_value(self,v):
        return v
    def format_value(self,v):
        return unicode(v)



# ========================================
# Specific Classes
# ========================================
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


# ========================================
# Contact Classes
# ========================================
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


class PrcStep(Container):
    def get_children(self):
        return {
            'stepDesc':StringValue(),
            'stepProc':Contact(),
        }



# ========================================
# Constraints Classes
# ========================================
class Consts(Container):
    def get_children(self):
        return {
            'useLimit':List(StringValue),
        }

class RestrictCd(Container):
    def get_children(self):
        return {
            'RestrictCd':Container({'value':AttributeStringValue(),}),
        }

class LegConsts(Container):
    def get_children(self):
        return {
            'accessConsts':List(RestrictCd),
            'useConsts':List(RestrictCd),
            'useLimit':List(StringValue),
            'othConsts':List(StringValue),
        }

class SecConsts(Container):
    def get_children(self):
        return {
            'useLimit':List(StringValue),
            'userNote':StringValue(),
            'classSys':StringValue(),
            'handDesc':StringValue(),
            'class':Container({'ClasscationCd':Container({'value':AttributeStringValue(),}),}),
        }

class Const(Container):
    def get_children(self):
        return {
            'SecConsts':SecConsts(),
            'LegConsts':LegConsts(),
            'Consts':Consts(),
        }



# ========================================
# Base Metadata Class
# ========================================
class Metadata(Container):
    def __init__(self,datasetPath):
        self.datasetPath=datasetPath
        self.load(datasetPath)
        self.set_name('metadata')
        self.bind()
        super(Metadata,self).__init__()


    def get_children(self):
        return {
            'dataIdInfo':Container({
                'idAbs':StringValue(),
                'idCredit':StringValue(),
                'idPurp':StringValue(),
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
                'suppInfo':StringValue(),
                'resConst':List(Const),
            }),
            'dqInfo':Container({
                'dataLineage':Container({
                    'statement':StringValue(),
                    'prcStep':List(PrcStep),
                }),
            }),
            'Esri':Container({
                'ModDate':DateValue(),
                'scaleRange':Container({
                    'minScale':IntegerValue(),
                    'maxScale':IntegerValue(),
                }),
            }),
            'Binary':Container({
                'Thumbnail':Container({
                    'Data':StringValue(),
                }),
            }),
            'mdFileID':StringValue(),
            'mdConst':List(Const),
        }


    def load(self,path):
        if os.path.isfile(path):
            tmpPath=path
        else:
            with tempfile.NamedTemporaryFile(mode='w',suffix='.xml',delete=False) as fout:
                fout.write('<metadata />')
                tmpPath=fout.name
            import arcpy
            arcpy.MetadataImporter_conversion(path,tmpPath)
        self.load_from_xml(tmpPath)

    def load_from_xml(self,path):
        self.tree=ET.parse(path)


    def save(self,path=None):
        if path is None: path=self.datasetPath
        if os.path.isfile(path) or (os.path.isdir(os.path.dirname(path)) and path.endswith('.xml')):
            tmpPath=path
        else:
            with tempfile.NamedTemporaryFile(mode='w',suffix='.xml',delete=False) as fout:
                tmpPath=fout.name
        self.save_to_xml(tmpPath)
        if not os.path.isfile(path):
            import arcpy
            arcpy.MetadataImporter_conversion(tmpPath,path)

    def save_to_xml(self,path):
        self.tree.write(path)


    def bind(self):
        """Special case binding"""
        self.element=self.tree.getroot()
        self.parentElementWrapper=self
