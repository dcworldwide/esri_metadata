"""
Metadata class
"""
import os
import datetime
import tempfile
import copy

import xml.etree.ElementTree as ET


class InvalidValueError(ValueError):
    """Raised when trying to parse a value that is invalid."""
    pass

class InvalidStructureError(Exception):
    """Raised when the XML doesn't match what is expected."""
    pass

class UnboundElementError(Exception):
    """Raised when a Wrapper instance is being used in a way that it needs to be bound to an XML object but it is not."""
    pass


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


class TextWrapper(Wrapper):
    def bind(self,parentElementWrapper):
        super(TextWrapper,self).bind(parentElementWrapper)

    @property
    def is_missing(self):
        return self.is_bound and self.parentElementWrapper.is_missing

    def create(self):
        if not self.is_bound: raise UnboundElementError('Cannot create on unbound Element')
        if self.is_missing:
            self.parentElementWrapper.create()


class AttributeWrapper(Wrapper):
    def bind(self,parentElementWrapper):
        super(AttributeWrapper,self).bind(parentElementWrapper)

    @property
    def is_missing(self):
        return self.is_bound and (self.parentElementWrapper.is_missing or self.name not in self.parentElementWrapper.element.keys())

    def create(self):
        if not self.is_bound: raise UnboundElementError('Cannot create on unbound Element')
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


    @property
    def is_missing(self):
        return not self.is_present

    @property
    def is_present(self):
        return self.is_bound and len(self)>0


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


class ScalarValue(TextWrapper,SingleValue):
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


class StringValue(ScalarValue):
    def parse_value(self,v):
        return v

    def format_value(self,v):
        return unicode(v)

class StringValueContainer(Container):
    def get_children(self):
        return {'text':StringValue()}


class IntegerValue(ScalarValue):
    def parse_value(self,v):
        try:
            r=int(v)
        except ValueError as e:
            raise InvalidValueError('Invalid IntegerValue: {}'.format(v))
        return r

    def format_value(self,v):
        return unicode(v)


class ChoiceValue(ScalarValue):
    def get_choices(self):
        raise NotImplemented()

    def parse_value(self,v):
        if v not in self.get_choices():
            raise InvalidValueError('Invalid ChoiceValue: {}'.format(v))
        return v

    def format_value(self,v):
        if v not in self.get_choices():
            raise InvalidValueError('Invalid ChoiceValue: {}'.format(v))
        return unicode(v)


class BooleanValueBaseClass(ScalarValue):
    CHOICES=[]

    def parse_value(self,v):
        if v not in self.CHOICES:
            raise InvalidValueError('Invalid ChoiceValue: {}'.format(v))
        return self.CHOICES[1]==v

    def format_value(self,v):
        return self.CHOICES[1] if v else self.CHOICES[0]

class BooleanValueTitleCase(BooleanValueBaseClass):
    CHOICES=['False','True']


class DateTimeValueBaseClass(ScalarValue):
    FORMAT=''

    def parse_value(self,v):
        try:
            r=datetime.datetime.strptime(v.strip(),self.FORMAT) if v else None
        except ValueError as e:
            raise InvalidValueError('Invalid {}: {}'.format(self.__class__.__name__,v))
        return r

    def format_value(self,v):
        return datetime.datetime.strftime(v,self.FORMAT)


class DateValue(DateTimeValueBaseClass):
    FORMAT='%Y%m%d'

class TimeValue(DateTimeValueBaseClass):
    FORMAT='%H%M%S'

class DateTimeValue(DateTimeValueBaseClass):
    FORMAT='%Y-%m-%dT%H:%M:%S'


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
class DateTriple(Container):
    def get_children(self):
        return {
            'pubDate':Container({'text':DateTimeValue(),}),
            'createDate':Container({'text':DateTimeValue(),}),
            'reviseDate':Container({'text':DateTimeValue(),}),
        }


class Keywords(Container):
    def get_children(self):
        return {
            'keyword':List(StringValueContainer),
            'thesaName':List(ThesaName),
        }

class ThesaName(Container):
    def get_children(self):
        return {
            'resTitle':StringValueContainer(),
            'resAltTitle':StringValueContainer(),
            'collTitle':StringValueContainer(),
            'isbn':StringValueContainer(),
            'issn':StringValueContainer(),
            'date':DateTriple(),
            'otherCitDet':StringValueContainer(),
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
            'displayName':StringValueContainer(), # similar to rpIndName but not always populated
            'rpIndName':StringValueContainer(),
            'rpOrgName':StringValueContainer(),
            'rpPosName':StringValueContainer(),
            'role':Container({'RoleCd':Container({'value':AttributeStringValue(),}),}),
            'rpCntInfo':Container({
                'cntAddress':Container({
                    'eMailAdd':List(StringValueContainer),
                    'addressType':AttributeStringValue(),
                    'delPoint':StringValueContainer(),
                    'city':StringValueContainer(),
                    'state':StringValueContainer(),
                    'postCode':StringValueContainer(),
                    'country':StringValueContainer(),
                }),
                'cntPhone':Container({
                    'voiceNum':List(StringValueContainer),
                    'faxNum':List(StringValueContainer),
                }),
            }),
        }


class PrcStep(Container):
    def get_children(self):
        return {
            'stepDesc':StringValueContainer(),
            'stepProc':Contact(),
        }



# ========================================
# Constraints Classes
# ========================================
class Consts(Container):
    def get_children(self):
        return {
            'useLimit':List(StringValueContainer),
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
            'useLimit':List(StringValueContainer),
            'othConsts':List(StringValueContainer),
        }

class SecConsts(Container):
    def get_children(self):
        return {
            'useLimit':List(StringValueContainer),
            'userNote':StringValueContainer(),
            'classSys':StringValueContainer(),
            'handDesc':StringValueContainer(),
            'class':Container({'ClasscationCd':Container({'value':AttributeStringValue(),}),}),
        }

class Const(Container):
    def get_children(self):
        return {
            'SecConsts':SecConsts(),
            'LegConsts':LegConsts(),
            'Consts':Consts(),
        }





class AggrInfo(Container):
    def get_children(self):
        return {
            'aggrDSIdent':AggrDsIdent(),
            'assocType':Container({'AscTypeCd':Container({'value':AttributeStringValue(),}),}), # value: 004=Source
        }

class AggrDsIdent(Container):
    def get_children(self):
        return {
            'identCode':StringValueContainer(),
        }


class SpatRpType(Container):
    def get_children(self):
        return {
            'SpatRepTypCd':Container({'value':AttributeStringValue(),}), # value: 001=Vector, 002=Grid
        }

class Report(Container):
    def get_children(self):
        return {
            'type':AttributeStringValue(), # DQNonQuanAttAcc: Quan or Qual?
            'dimension':AttributeStringValue(),
            'measDesc':StringValueContainer(),
            'evalMethDesc':StringValueContainer(),
            'measResult':Container({'ConResult':Container({'conExpl':StringValueContainer()})}),
        }


class AxisDimension(Container):
    def get_children(self):
        return {
            'type':AttributeStringValue(), # 001=Row-y, 002=Column-x
            'dimSize':Container({'text':IntegerValue(),}),
            'dimResol':Container({'value':Container({'uom':AttributeStringValue(),'text':IntegerValue(),}),}),
        }


class GridSpatRep(Container):
    def get_children(self):
        return {
            'numDims':Container({'text':IntegerValue(),}),
            'axisDimension':List(AxisDimension),
            'tranParaAv':Container({'text':BooleanValueTitleCase(),}),
        }

class Georect(Container):
    def get_children(self):
        # this is different to GridSpatRep in some of the fields that haven't been fleshed out here
        return {
            'numDims':Container({'text':IntegerValue(),}),
            'axisDimension':List(AxisDimension),
            'tranParaAv':Container({'text':BooleanValueTitleCase(),}),
        }


class SpatRepInfo(Container):
    def get_children(self):
        return {
            'GridSpatRep':GridSpatRep(),
            'VectSpatRep':Container({}),
            'Georect':Georect(),
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
                'idAbs':StringValueContainer(),
                'idCredit':StringValueContainer(),
                'idPurp':StringValueContainer(),
                'idCitation':Container({
                    'resTitle':StringValueContainer(),
                    'resAltTitle':StringValueContainer(),
                    'citRespParty':List(Contact),
                    'date':DateTriple(),
                }),
                'idPoC':Contact(),
                'themeKeys':List(Keywords),
                'placeKeys':List(Keywords),
                'searchKeys':List(Keywords),
                'tpCat':List(TpCat),
                'suppInfo':StringValueContainer(),
                'resConst':List(Const),
                'aggrInfo':List(AggrInfo),
                'spatRpType':List(SpatRpType),
                'resMaint':Container({
                    'maintCont':List(Contact),
                }),
            }),
            'dqInfo':Container({
                'dataLineage':Container({
                    'statement':StringValueContainer(),
                    'prcStep':List(PrcStep),
                }),
                'report':List(Report),
            }),
            'spatRepInfo':List(SpatRepInfo),
            'Esri':Container({
                'CreaDate':Container({'text':DateValue(),}),
                'CreaTime':Container({'text':TimeValue(),}),
                'ModDate':Container({'text':DateValue(),}),
                'ModTime':Container({'text':TimeValue(),}),
                'SyncDate':Container({'text':DateValue(),}),
                'scaleRange':Container({
                    'minScale':Container({'text':IntegerValue(),}),
                    'maxScale':Container({'text':IntegerValue(),}),
                }),
            }),
            'Binary':Container({
                'Thumbnail':Container({
                    'Data':StringValueContainer(),
                }),
            }),
            'mdFileID':StringValueContainer(),
            'mdConst':List(Const),
            'mdDateSt':Container({'text':DateValue(),}), # Metadata Details -> Last Update
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
        root=self.tree.getroot()
        self.element=root if root.tag==self.name else None
        self.parentElementWrapper=self


    # add references to exceptions here for easier error handling in client code
    InvalidValueError=InvalidValueError
    InvalidStructureError=InvalidStructureError
    UnboundElementError=UnboundElementError
