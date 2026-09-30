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
