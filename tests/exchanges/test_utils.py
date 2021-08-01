import pytest

from src.exchanges.utils import format_timestamp


def test_format_timestamp():
    assert format_timestamp(1556636400)                  == "2019-05-01T00:00:00+09:00"
    assert format_timestamp("1556636400")                == "2019-05-01T00:00:00+09:00"
    assert format_timestamp(1556636400.00)               == "2019-05-01T00:00:00+09:00"
    assert format_timestamp("1556636400.00")             == "2019-05-01T00:00:00+09:00"
    assert format_timestamp("2019-05-01T00:00:00+09:00") == "2019-05-01T00:00:00+09:00"
    assert format_timestamp("2019-04-30T15:00:00Z")      == "2019-05-01T00:00:00+09:00"
    assert format_timestamp("2019-05-01T00:00:00")       == "2019-05-01T00:00:00+09:00"
    assert format_timestamp("2019-05-01T00:00:00.000")   == "2019-05-01T00:00:00+09:00"

    with pytest.raises(ValueError):
        format_timestamp("2019@05@01T00:00:00")
        format_timestamp("2019-05-01T0:0:0")

    with pytest.raises(TypeError):
        format_timestamp(-1)
        format_timestamp(None)
