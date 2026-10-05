from nbs_ruralscan.schema_tools.check_numbers import _nums


def test_space_grouped_thousands_are_joined():
    toks = _nums("Average annual rainfall 1 001 \u2013 1 500 mm 751 \u2013 1 000 mm")
    assert {"1001", "1500", "1000", "751"} <= toks


def test_split_tokens_are_kept():
    assert {"1", "001"} <= _nums("1 001 mm")


def test_decimals_and_separate_numbers_are_not_joined():
    toks = _nums("slope 5 - 50 m and 2.5 100")
    assert "550" not in toks
    assert "5100" not in toks


def test_locale_decimal_comma_and_thousands_dot():
    """es/fr/pt magnitudes: "29,8" is 29.8 and "5.047" may be 5047 (both readings kept)."""
    from nbs_ruralscan.schema_tools.check_numbers import _floats, _nums

    assert "29.8" in _nums("o rendimento aumentou 29,8 por cento")
    assert "5047" in _nums("millet 5.047 kg/ha")
    assert "5.047" in _nums("5.047 t/ha")  # the plain-decimal reading survives
    # a 3-digit thousands GROUP must not be read as a decimal comma
    assert _nums("area 1,637,600 ha") == {"1637600"}
    # an integral float magnitude matches a quote printing the bare integer
    assert not _floats(_nums(str(41.0))) - _floats(_nums("41 trees per hectare"))
