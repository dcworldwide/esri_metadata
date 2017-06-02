import datetime
from pathlib2 import Path
import pytest

from esri_metadata import Metadata

DATA_DIR=Path.cwd()/'tests'/'data'


@pytest.fixture
def md(request):
    return Metadata(str(DATA_DIR/'invalid_data.xml'))


# tests
def test_invalid_date(md):
    with pytest.raises(Metadata.InvalidValueError): v=md.Esri.CreaDate.text.value

def test_invalid_time(md):
    with pytest.raises(Metadata.InvalidValueError): v=md.Esri.CreaTime.text.value

def test_invalid_datetime(md):
    with pytest.raises(Metadata.InvalidValueError): v=md.dataIdInfo.idCitation.date.pubDate.text.value

def test_invalid_int(md):
    with pytest.raises(Metadata.InvalidValueError): v=md.Esri.scaleRange.minScale.text.value

def test_invalid_single_element(md):
    with pytest.raises(Metadata.InvalidStructureError): v=md.dataIdInfo.idCredit
