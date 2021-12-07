import pytest

from api import gb_extract as gbe


def test_decrement_adm():
    assert gbe.decrement_adm("ADM3") == "ADM2"
    assert gbe.decrement_adm("ADM2") == "ADM1"
    assert gbe.decrement_adm("ADM1") == "ADM0"
    with pytest.raises(KeyError):
        assert gbe.decrement_adm("ADM0")
    with pytest.raises(KeyError):
        assert gbe.decrement_adm("ADM4")
