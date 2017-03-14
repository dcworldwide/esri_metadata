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
    with pytest.raises(Metadata.InvalidValueError): v=md.Esri.CreaDate.value

def test_invalid_time(md):
    with pytest.raises(Metadata.InvalidValueError): v=md.Esri.CreaTime.value

def test_invalid_datetime(md):
    with pytest.raises(Metadata.InvalidValueError): v=md.dataIdInfo.idCitation.date.pubDate.value

def test_invalid_int(md):
    with pytest.raises(Metadata.InvalidValueError): v=md.Esri.scaleRange.minScale.value
