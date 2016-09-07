import datetime
from pathlib2 import Path
import pytest

from esri_metadata import Metadata

DATA_DIR=Path.cwd()/'tests'/'data'


@pytest.fixture
def md(request):
    return Metadata(str(DATA_DIR/'full_labelled.xml'))


# tests
def test_load(md):
    assert md.dataIdInfo.idCitation.resTitle.value=='Title'


def test_read(md):
    assert md.dataIdInfo.idAbs.value.find('Description')!=-1
    assert md.dataIdInfo.idCitation.resTitle.value=='Title'
    assert md.dataIdInfo.idCitation.date.pubDate.value==datetime.datetime(2016,9,1)
    assert md.dataIdInfo.idPoC.rpIndName.value=='Points of Contact1 Name'
    assert md.dataIdInfo.idPoC.role.RoleCd.value.value=='007'
    assert md.dataIdInfo.idCitation.citRespParty[0].rpCntInfo.cntAddress.addressType.value=='postal'
    assert md.dataIdInfo.idCitation.citRespParty[0].rpCntInfo.cntPhone.voiceNum.value=='07 1234 5678'

def test_missing_element(md):
    assert md.dataIdInfo.idPoC.rpCntInfo.cntAddress.is_missing


def test_list(md):
    assert md.dataIdInfo.tpCat[0].TopicCatCd.value.value=='008'
    assert md.dataIdInfo.searchKeys[0].keyword[0].value=='Tags'


def test_separate_instances(md):
    # make sure the different contacts are fully creating children wrappers from scratch
    firstContactNameWrapper=md.dataIdInfo.idPoC.rpIndName
    assert firstContactNameWrapper.value=='Points of Contact1 Name'
    assert md.dataIdInfo.idCitation.citRespParty[0].rpIndName.value=='Contact1 Name'
    assert firstContactNameWrapper.value=='Points of Contact1 Name'

def test_change_value(md):
    md.dataIdInfo.idAbs.value='Test'
    assert md.dataIdInfo.idAbs.value=='Test'
