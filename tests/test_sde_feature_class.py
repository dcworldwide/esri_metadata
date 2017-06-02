import datetime
from pathlib2 import Path
import pytest

from esri_metadata import Metadata

DATA_DIR=Path.cwd()/'tests'/'data'


@pytest.fixture
def md(request):
    return Metadata(str(DATA_DIR/'connection.sde'/'Metadata_Test'))


# tests
def test_load(md):
    assert md.dataIdInfo.idCitation.resTitle.text.value=='Title'


def test_read(md):
    assert md.dataIdInfo.idAbs.text.value.find('Description')!=-1
    assert md.dataIdInfo.idCitation.resTitle.text.value=='Title'
    assert md.dataIdInfo.idCitation.date.pubDate.text.value==datetime.datetime(2016,9,1)
    assert md.dataIdInfo.idPoC.rpIndName.text.value=='Points of Contact1 Name'
    assert md.dataIdInfo.idPoC.role.RoleCd.value.value=='007'
    assert md.dataIdInfo.idCitation.citRespParty[0].rpCntInfo.cntAddress.addressType.value=='postal'
    assert md.dataIdInfo.idCitation.citRespParty[0].rpCntInfo.cntPhone.voiceNum[0].text.value=='07 1234 5678'


def test_save(md):
    assert md.dataIdInfo.idCitation.resTitle.text.value=='Title'
    md.dataIdInfo.idCitation.resTitle.text.value='New Title'
    md.save(md.datasetPath)

    md=Metadata(md.datasetPath)
    assert md.dataIdInfo.idCitation.resTitle.text.value=='New Title'
    md.dataIdInfo.idCitation.resTitle.text.value='Title'
    md.save(md.datasetPath)
