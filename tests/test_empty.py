from pathlib2 import Path
import pytest

from esri_metadata import Metadata

DATA_DIR=Path.cwd()/'tests'/'data'


@pytest.fixture
def md(request):
    return Metadata(str(DATA_DIR/'empty.xml'))


# tests
def test_missing_element(md):
    assert md.dataIdInfo.is_missing

def test_add_missing_element(md):
    md.dataIdInfo.idAbs.create()
    md.dataIdInfo.idAbs.value='Test'
    assert md.dataIdInfo.idAbs.value=='Test'
