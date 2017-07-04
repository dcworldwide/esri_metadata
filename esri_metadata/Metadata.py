"""
Metadata class
"""
import os
import tempfile

import xml.etree.ElementTree as ET

from .wrappers.errors import *
from .wrappers.generic import *
from .wrappers.generic.values import *


# ========================================
# Specific Classes
# ========================================
class DateTriple(Container):
    def get_children(self):
        return {
            'pubDate':TextDateTimeValueContainer(),
            'createDate':TextDateTimeValueContainer(),
            'reviseDate':TextDateTimeValueContainer(),
        }


class Keywords(Container):
    def get_children(self):
        return {
            'keyword':List(TextStringValueContainer),
            'thesaName':List(ThesaName),
        }

class ThesaName(Container):
    def get_children(self):
        return {
            'resTitle':TextStringValueContainer(),
            'resAltTitle':TextStringValueContainer(),
            'collTitle':TextStringValueContainer(),
            'isbn':TextStringValueContainer(),
            'issn':TextStringValueContainer(),
            'date':DateTriple(),
            'otherCitDet':TextStringValueContainer(),
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
            'displayName':TextStringValueContainer(), # similar to rpIndName but not always populated
            'rpIndName':TextStringValueContainer(),
            'rpOrgName':TextStringValueContainer(),
            'rpPosName':TextStringValueContainer(),
            'role':Container({'RoleCd':Container({'value':AttributeStringValue(),}),}),
            'rpCntInfo':Container({
                'cntAddress':Container({
                    'eMailAdd':List(TextStringValueContainer),
                    'addressType':AttributeStringValue(),
                    'delPoint':TextStringValueContainer(),
                    'city':TextStringValueContainer(),
                    'state':TextStringValueContainer(),
                    'postCode':TextStringValueContainer(),
                    'country':TextStringValueContainer(),
                }),
                'cntPhone':Container({
                    'voiceNum':List(TextStringValueContainer),
                    'faxNum':List(TextStringValueContainer),
                }),
            }),
        }


class PrcStep(Container):
    def get_children(self):
        return {
            'stepDesc':TextStringValueContainer(),
            'stepProc':Contact(),
        }



# ========================================
# Constraints Classes
# ========================================
class Consts(Container):
    def get_children(self):
        return {
            'useLimit':List(TextStringValueContainer),
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
            'useLimit':List(TextStringValueContainer),
            'othConsts':List(TextStringValueContainer),
        }

class SecConsts(Container):
    def get_children(self):
        return {
            'useLimit':List(TextStringValueContainer),
            'userNote':TextStringValueContainer(),
            'classSys':TextStringValueContainer(),
            'handDesc':TextStringValueContainer(),
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
            'identCode':TextStringValueContainer(),
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
            'measDesc':TextStringValueContainer(),
            'evalMethDesc':TextStringValueContainer(),
            'measResult':Container({'ConResult':Container({'conExpl':TextStringValueContainer()})}),
        }


class AxisDimension(Container):
    def get_children(self):
        return {
            'type':AttributeStringValue(), # 001=Row-y, 002=Column-x
            'dimSize':TextIntegerValueContainer(),
            'dimResol':Container({'value':Container({'uom':AttributeStringValue(),'text':TextIntegerValue(),}),}),
        }


class GridSpatRep(Container):
    def get_children(self):
        return {
            'numDims':TextIntegerValueContainer(),
            'axisDimension':List(AxisDimension),
            'tranParaAv':TextBooleanTitleCaseValueContainer(),
        }

class Georect(Container):
    def get_children(self):
        # this is different to GridSpatRep in some of the fields that haven't been fleshed out here
        return {
            'numDims':TextIntegerValueContainer(),
            'axisDimension':List(AxisDimension),
            'tranParaAv':TextBooleanTitleCaseValueContainer(),
        }


class SpatRepInfo(Container):
    def get_children(self):
        return {
            'GridSpatRep':GridSpatRep(),
            'VectSpatRep':Container({}),
            'Georect':Georect(),
        }



# Fields
class Detailed(Container):
    def get_children(self):
        return {
            'Name':AttributeStringValue(),
            'enttyp':Container({
                'enttypl':TextStringValueContainer(),
                'enttypt':TextStringValueContainer(),
                'enttypc':TextStringValueContainer(),
            }),
            'attr':List(Attr),
        }

class Attr(Container):
    def get_children(self):
        return {
            'attrlabl':TextStringValueContainer(),
            'attrdomv':List(Attrdomv),
        }

class Attrdomv(Container):
    def get_children(self):
        return {
            'edom':List(Edom),
            'udom':TextStringValueContainer(),
            'rdom':Container({
                'rdommin':TextStringValueContainer(),
                'rdommax':TextStringValueContainer(),
            }),
            'codesetd':Container({
                'codesetn':TextStringValueContainer(),
                'codesets':TextStringValueContainer(),
            }),
        }

class Edom(Container):
    def get_children(self):
        return {
            'edomv':TextStringValueContainer(),
            'edomvd':TextStringValueContainer(),
            'edomvds':TextStringValueContainer(),
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
                'idAbs':TextStringValueContainer(),
                'idCredit':TextStringValueContainer(),
                'idPurp':TextStringValueContainer(),
                'idCitation':Container({
                    'resTitle':TextStringValueContainer(),
                    'resAltTitle':TextStringValueContainer(),
                    'citRespParty':List(Contact),
                    'date':DateTriple(),
                }),
                'idPoC':Contact(),
                'themeKeys':List(Keywords),
                'placeKeys':List(Keywords),
                'searchKeys':List(Keywords),
                'tpCat':List(TpCat),
                'suppInfo':TextStringValueContainer(),
                'resConst':List(Const),
                'aggrInfo':List(AggrInfo),
                'spatRpType':List(SpatRpType),
                'resMaint':Container({
                    'maintCont':List(Contact),
                }),
            }),
            'dqInfo':Container({
                'dataLineage':Container({
                    'statement':TextStringValueContainer(),
                    'prcStep':List(PrcStep),
                }),
                'report':List(Report),
            }),
            'eainfo':Container({
                'detailed':List(Detailed),
            }),
            'spatRepInfo':List(SpatRepInfo),
            'Esri':Container({
                'CreaDate':TextDateValueContainer(),
                'CreaTime':TextTimeValueContainer(),
                'ModDate':TextDateValueContainer(),
                'ModTime':TextTimeValueContainer(),
                'SyncDate':TextDateValueContainer(),
                'scaleRange':Container({
                    'minScale':TextIntegerValueContainer(),
                    'maxScale':TextIntegerValueContainer(),
                }),
            }),
            'Binary':Container({
                'Thumbnail':Container({
                    'Data':TextStringValueContainer(),
                }),
            }),
            'mdFileID':TextStringValueContainer(),
            'mdConst':List(Const),
            'mdDateSt':TextDateValueContainer(), # Metadata Details -> Last Update
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
