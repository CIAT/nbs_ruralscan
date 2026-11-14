import io
from unittest.mock import Mock

import pytest

from nbs_ruralscan.schema_tools import evidence_authority, review_server, submit_review


def test_old_server_and_submit_refuse_before_reading_payload(tmp_path, monkeypatch):
    (tmp_path / ".ciat-evidence-readonly").write_text("retired")
    monkeypatch.setattr(review_server, "ROOT", tmp_path)
    handler = Mock(rfile=io.BytesIO(b"unread"))
    for route in ("/api/decision", "/api/challenge", "/api/apply", "/api/submit"):
        handler.path = route
        review_server.Handler.do_POST(handler)
        assert handler._json.call_args.args[0] == 410
        assert handler.rfile.tell() == 0
    with pytest.raises(ValueError, match="RuralScan/evidence"):
        submit_review.ship("reviewer", root=tmp_path)
    assert not evidence_authority.retired(tmp_path / "disposable")
