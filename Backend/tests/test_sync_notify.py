from datetime import datetime, timezone

from app import notify_sync as ns
from app import scheduler as sch
from app.models import SyncRun


def test_recipients_uses_sync_notify_to_only(monkeypatch):
    monkeypatch.setattr(ns.config.settings, "SYNC_NOTIFY_TO", "c.c.sanchez@gmail.com")
    assert ns._recipients() == ["c.c.sanchez@gmail.com"]


def test_recipients_fallback_to_admins(monkeypatch):
    class _FakeQuery:
        def filter(self, *a, **k):
            return self

        def all(self):
            return [type("U", (), {"email": "admin@test.com"})()]

    class _FakeDB:
        def query(self, *a, **k):
            return _FakeQuery()

        def close(self):
            pass

    monkeypatch.setattr(ns, "SessionLocal", lambda: _FakeDB())
    monkeypatch.setattr(ns.config.settings, "SYNC_NOTIFY_TO", None)
    assert ns._recipients() == ["admin@test.com"]


def test_notify_skips_manual_and_nonfinal_runs(monkeypatch):
    db = ns.SessionLocal()
    try:
        run = SyncRun(sync_type="customers", status="completed", triggered_by="manual")
        db.add(run)
        db.commit()
        sent = []
        monkeypatch.setattr(ns, "_recipients", lambda: ["c.c.sanchez@gmail.com"])
        monkeypatch.setattr(ns, "_send_email", lambda to, subject, html: sent.append(to))
        ns.notify_sync_result(run.id)
    finally:
        db.close()
    assert sent == []


def test_notify_sends_on_scheduled_completed(monkeypatch):
    db = ns.SessionLocal()
    try:
        run = SyncRun(sync_type="customers", status="completed", triggered_by="scheduled",
                      processed=3, elapsed=1.5, started_at=datetime.now(timezone.utc),
                      finished_at=datetime.now(timezone.utc))
        db.add(run)
        db.commit()
        sent = []
        monkeypatch.setattr(ns, "_recipients", lambda: ["c.c.sanchez@gmail.com"])
        monkeypatch.setattr(ns, "_send_email", lambda to, subject, html: sent.append(to))
        ns.notify_sync_result(run.id)
    finally:
        db.close()
    assert sent == [["c.c.sanchez@gmail.com"]]


def test_send_email_uses_resend_api_and_bearer_auth(monkeypatch):
    class _Resp:
        status = 200

    monkeypatch.setattr(ns.config.settings, "RESEND_API_KEY", "re_test")
    demands = []
    monkeypatch.setattr(ns.urllib.request, "urlopen",
                        lambda *a, **k: demands.append(a[0]) or _Resp())
    ns._send_email(["c.c.sanchez@gmail.com"], "Asunto", "<p>Body</p>")
    req = demands[0]
    assert req.full_url == "https://api.resend.com/emails"
    assert req.get_header("Authorization") == "Bearer re_test"
    assert b"c.c.sanchez@gmail.com" in req.data


def test_send_email_noop_without_api_key(monkeypatch):
    monkeypatch.setattr(ns.config.settings, "RESEND_API_KEY", None)
    calls = []
    monkeypatch.setattr(ns.urllib.request, "urlopen", lambda req: calls.append(req))
    ns._send_email(["c.c.sanchez@gmail.com"], "Asunto", "<p>Body</p>")
    assert calls == []


def test_cron_trigger_timezone_is_buenos_aires():
    trigger = sch.cron_trigger()
    assert str(trigger.timezone) == "America/Argentina/Buenos_Aires"