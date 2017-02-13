import datetime
from pathlib2 import Path
import pytest

from esri_metadata import Metadata

DATA_DIR=Path.cwd()/'tests'/'data'


@pytest.fixture
def md(request):
    return Metadata(str(DATA_DIR/'full_labelled.xml'))

@pytest.fixture
def temp_path(request):
    return str(DATA_DIR/'temp.xml')


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
    assert md.dataIdInfo.idCitation.citRespParty[0].rpCntInfo.cntAddress.eMailAdd[0].value=='Contact1 Email'
    assert md.dataIdInfo.idCitation.citRespParty[0].rpCntInfo.cntPhone.voiceNum[0].value=='07 1234 5678'


def test_missing_element(md):
    assert md.dataIdInfo.idCitation.citRespParty[0].rpCntInfo.is_bound
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


def test_change_value(md,temp_path):
    md.dataIdInfo.idCitation.resTitle.value='Test'
    assert md.dataIdInfo.idCitation.resTitle.value=='Test'
    md.save(temp_path)

    md=Metadata(temp_path)
    assert md.dataIdInfo.idCitation.resTitle.value=='Test'


def test_delete_list_item(md,temp_path):
    # make sure it's there, do the delete and make sure it's gone
    assert md.dataIdInfo.tpCat[1].TopicCatCd.value.value=='015'
    del md.dataIdInfo.tpCat[1]
    assert len(md.dataIdInfo.tpCat)==1
    md.save(temp_path)

    # reload the file and make sure it's still gone (ie. that it was persisted)
    md=Metadata(temp_path)
    assert len(md.dataIdInfo.tpCat)==1


def test_delete_container(md,temp_path):
    # make sure it's there, do the delete and make sure it's gone
    assert md.dataIdInfo.idCitation.resTitle.value=='Title'
    del md.dataIdInfo.idCitation.resTitle
    assert md.dataIdInfo.idCitation.resTitle.element is None
    assert md.dataIdInfo.idCitation.resTitle.is_missing
    md.save(temp_path)

    # reload the file and make sure it's still gone (ie. that it was persisted)
    md=Metadata(temp_path)
    assert md.dataIdInfo.idCitation.resTitle.is_missing


def test_append_container_to_list(md):
    md.dataIdInfo.idCitation.citRespParty.append(md.dataIdInfo.idPoC)
    assert md.dataIdInfo.idCitation.citRespParty[2].rpIndName.value=='Points of Contact1 Name'


def test_append_container_to_list_invalid_type(md):
    with pytest.raises(TypeError):
        md.dataIdInfo.idCitation.citRespParty.append(md.dataIdInfo)


def test_set_container(md,temp_path):
    c=md.dataIdInfo.idCitation.citRespParty[1]
    md.dataIdInfo.idPoC.set(c)
    assert md.dataIdInfo.idPoC.rpIndName.value=='Contact2 Name'
    md.save(temp_path)

    # reload the file and make sure it's still gone (ie. that it was persisted)
    md=Metadata(temp_path)
    assert md.dataIdInfo.idPoC.rpIndName.value=='Contact2 Name'
