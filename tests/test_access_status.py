"""Tests for the Unpaywall access-status verifier (issue #53) — no real network."""

import io
import json

from nbs_ruralscan.schema_tools import access_status


def _fake_urlopen(payload):
    def _open(url, timeout=0):
        return io.BytesIO(json.dumps(payload).encode())

    return _open


def test_lookup_maps_oa_and_license(monkeypatch):
    monkeypatch.setattr(
        access_status.urllib.request,
        "urlopen",
        _fake_urlopen(
            {
                "is_oa": True,
                "oa_status": "gold",
                "best_oa_location": {"license": "cc-by"},
            }
        ),
    )
    r = access_status.lookup("10.3390/x")
    assert r == {
        "access_status": "open_access",
        "license": "cc-by",
        "oa_status": "gold",
    }


def test_lookup_paywalled_has_no_license(monkeypatch):
    monkeypatch.setattr(
        access_status.urllib.request,
        "urlopen",
        _fake_urlopen(
            {"is_oa": False, "oa_status": "closed", "best_oa_location": None}
        ),
    )
    r = access_status.lookup("10.1016/x")
    assert r["access_status"] == "paywalled"
    assert r["license"] == ""


def test_lookup_blank_doi_is_none():
    assert access_status.lookup("") is None


def test_network_failure_returns_none(monkeypatch):
    def _boom(url, timeout=0):
        raise OSError("no network")

    monkeypatch.setattr(access_status.urllib.request, "urlopen", _boom)
    assert access_status.lookup("10.1/x") is None
