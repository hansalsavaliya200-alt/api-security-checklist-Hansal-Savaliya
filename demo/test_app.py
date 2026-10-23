"""Automated checks for the demo API. Run: python -m unittest -v test_app.py"""
import unittest
import uuid
from unittest import mock

import app as demo


class ApiSecurityTests(unittest.TestCase):
    def setUp(self):
        demo.reset_rate_limits()
        self.c = demo.app.test_client()

    # helpers ---------------------------------------------------------------
    def login(self, user):
        r = self.c.post("/api/v1/login", json={"username": user, "password": f"demo-password-{user}"})
        self.assertEqual(r.status_code, 200)
        return {"Authorization": f"Bearer {r.get_json()['access_token']}"}

    def make_note(self, headers, title="t"):
        r = self.c.post("/api/v1/notes", json={"title": title, "body": "b"}, headers=headers)
        self.assertEqual(r.status_code, 201)
        return r.get_json()["id"]

    # authentication ----------------------------------------------------------
    def test_frontend_and_assets_are_served_with_csp(self):
        page = self.c.get("/")
        self.assertEqual(page.status_code, 200)
        self.assertIn("API Security Console", page.get_data(as_text=True))
        self.assertIn("script-src 'self'", page.headers["Content-Security-Policy"])

        for asset in ("app.js", "styles.css"):
            response = self.c.get(f"/static/{asset}")
            self.assertEqual(response.status_code, 200)

    def test_health_endpoint_is_200(self):
        r = self.c.get("/api/v1/health")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["status"], "ok")

    def test_profile_endpoint_returns_current_user(self):
        h = self.login("alice")
        r = self.c.get("/api/v1/me", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["username"], "alice")
        self.assertTrue(r.get_json()["id"].startswith("u-"))

    def test_no_token_is_401(self):
        r = self.c.get("/api/v1/notes")
        self.assertEqual(r.status_code, 401)
        self.assertEqual(r.headers.get("WWW-Authenticate"), "Bearer")

    def test_tampered_token_is_401(self):
        r = self.c.get("/api/v1/notes", headers={"Authorization": "Bearer abc.def.ghi"})
        self.assertEqual(r.status_code, 401)

    def test_wrong_password_and_unknown_user_same_response(self):
        a = self.c.post("/api/v1/login", json={"username": "alice", "password": "wrong"})
        b = self.c.post("/api/v1/login", json={"username": "nobody", "password": "wrong"})
        self.assertEqual(a.status_code, 401)
        self.assertEqual(a.get_json()["error"]["message"], b.get_json()["error"]["message"])

    # object-level authorisation ----------------------------------------------
    def test_cannot_read_or_delete_other_users_note(self):
        alice, bob = self.login("alice"), self.login("bob")
        nid = self.make_note(alice)
        self.assertEqual(self.c.get(f"/api/v1/notes/{nid}", headers=bob).status_code, 404)
        self.assertEqual(self.c.delete(f"/api/v1/notes/{nid}", headers=bob).status_code, 404)
        self.assertEqual(self.c.get(f"/api/v1/notes/{nid}", headers=alice).status_code, 200)

    def test_missing_and_foreign_notes_look_identical(self):
        alice, bob = self.login("alice"), self.login("bob")
        nid = self.make_note(alice)
        foreign = self.c.get(f"/api/v1/notes/{nid}", headers=bob)
        missing = self.c.get(f"/api/v1/notes/{uuid.uuid4()}", headers=bob)
        self.assertEqual(foreign.status_code, missing.status_code)
        self.assertEqual(foreign.get_json()["error"]["message"], missing.get_json()["error"]["message"])

    def test_list_only_returns_own_notes(self):
        alice, bob = self.login("alice"), self.login("bob")
        self.make_note(alice, "alice-only")
        titles = [n["title"] for n in self.c.get("/api/v1/notes", headers=bob).get_json()["items"]]
        self.assertNotIn("alice-only", titles)

    def test_can_update_own_note(self):
        h = self.login("alice")
        nid = self.make_note(h, "original")
        r = self.c.put(f"/api/v1/notes/{nid}", json={"title": "updated", "body": "new body"}, headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()["title"], "updated")
        self.assertEqual(r.get_json()["body"], "new body")

    def test_cannot_update_other_users_note(self):
        alice, bob = self.login("alice"), self.login("bob")
        nid = self.make_note(alice)
        r = self.c.put(f"/api/v1/notes/{nid}", json={"title": "hacked", "body": "nope"}, headers=bob)
        self.assertEqual(r.status_code, 404)

    # input validation ----------------------------------------------------------
    def test_validation_rejects_bad_input(self):
        h = self.login("alice")
        bad_payloads = [
            {}, {"title": ""}, {"title": 123}, {"title": "x" * 101},
            {"title": "ok", "body": "y" * 1001},
            {"title": "ok", "owner_id": "u-1002"},      # mass-assignment attempt
            {"title": "ok", "is_admin": True},
        ]
        for p in bad_payloads:
            r = self.c.post("/api/v1/notes", json=p, headers=h)
            self.assertEqual(r.status_code, 400, p)

    def test_wrong_content_type_is_415(self):
        h = self.login("alice")
        r = self.c.post("/api/v1/notes", data="title=x", headers=h,
                        content_type="application/x-www-form-urlencoded")
        self.assertEqual(r.status_code, 415)

    def test_oversized_body_is_413(self):
        h = self.login("alice")
        r = self.c.post("/api/v1/notes", data="{" + ' ' * 20000 + "}", headers=h,
                        content_type="application/json")
        self.assertEqual(r.status_code, 413)

    def test_malformed_id_is_404_not_500(self):
        h = self.login("alice")
        self.assertEqual(self.c.get("/api/v1/notes/not-a-uuid", headers=h).status_code, 404)

    # output shaping ---------------------------------------------------------------
    def test_internal_fields_never_returned(self):
        h = self.login("alice")
        nid = self.make_note(h)
        body = self.c.get(f"/api/v1/notes/{nid}", headers=h).get_json()
        self.assertEqual(set(body), {"id", "title", "body", "created_at"})

    # rate limiting ------------------------------------------------------------------
    def test_login_rate_limit(self):
        codes = [self.c.post("/api/v1/login", json={"username": "alice", "password": "x"}).status_code
                 for _ in range(7)]
        self.assertEqual(codes[:5], [401] * 5)
        self.assertEqual(codes[5], 429)

    def test_rate_limit_cannot_be_bypassed_with_spoofed_forwarded_header(self):
        for attempt in range(5):
            response = self.c.post(
                "/api/v1/login",
                json={"username": "alice", "password": "x"},
                headers={"X-Forwarded-For": f"198.51.100.{attempt + 1}"},
            )
            self.assertEqual(response.status_code, 401)

        blocked = self.c.post(
            "/api/v1/login",
            json={"username": "alice", "password": "x"},
            headers={"X-Forwarded-For": "198.51.100.6"},
        )
        self.assertEqual(blocked.status_code, 429)

    def test_429_has_retry_after(self):
        for _ in range(5):
            self.c.post("/api/v1/login", json={"username": "alice", "password": "x"})
        r = self.c.post("/api/v1/login", json={"username": "alice", "password": "x"})
        self.assertEqual(r.status_code, 429)
        self.assertIn("Retry-After", r.headers)

    def test_rate_limit_headers_are_exposed(self):
        r = self.c.get("/api/v1/health")
        self.assertIn("X-RateLimit-Limit", r.headers)
        self.assertIn("X-RateLimit-Remaining", r.headers)
        self.assertIn("X-RateLimit-Reset", r.headers)

    # error handling ------------------------------------------------------------------
    def test_errors_are_generic_and_carry_request_id(self):
        r = self.c.get("/api/v1/does-not-exist")
        self.assertEqual(r.status_code, 404)
        err = r.get_json()["error"]
        self.assertTrue(err["request_id"])
        self.assertNotIn("Traceback", r.get_data(as_text=True))

    def test_unexpected_exception_hides_details(self):
        h = self.login("alice")
        nid = self.make_note(h)
        with mock.patch.object(demo, "public_note",
                               side_effect=RuntimeError("secret internal detail")):
            r = self.c.get(f"/api/v1/notes/{nid}", headers=h)
        self.assertEqual(r.status_code, 500)
        self.assertEqual(r.get_json()["error"]["message"], "Something went wrong.")
        self.assertNotIn("secret internal detail", r.get_data(as_text=True))

    # headers / versioning ---------------------------------------------------------
    def test_security_headers_present(self):
        r = self.c.get("/api/v1/notes")
        self.assertEqual(r.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(r.headers["X-Frame-Options"], "DENY")
        self.assertEqual(r.headers["Referrer-Policy"], "no-referrer")
        self.assertEqual(r.headers["Cache-Control"], "no-store")
        self.assertIn("Strict-Transport-Security", r.headers)
        self.assertIn("X-Request-ID", r.headers)

    def test_deprecated_version_signals_sunset(self):
        h = self.login("alice")
        r = self.c.get("/api/v0/notes", headers=h)
        self.assertEqual(r.status_code, 200)
        self.assertIn("Deprecation", r.headers)
        self.assertIn("Sunset", r.headers)
        self.assertIn("successor-version", r.headers["Link"])
        self.assertNotIn("Deprecation", self.c.get("/api/v1/notes", headers=h).headers)

    # logging ------------------------------------------------------------------------
    def test_logs_do_not_contain_secrets(self):
        with self.assertLogs("demo-api", level="INFO") as cm:
            r = self.c.post("/api/v1/login", json={"username": "alice", "password": "demo-password-alice"})
            token = r.get_json()["access_token"]
            self.c.get("/api/v1/notes", headers={"Authorization": f"Bearer {token}"})
        joined = "\n".join(cm.output)
        self.assertNotIn("demo-password-alice", joined)
        self.assertNotIn(token, joined)


if __name__ == "__main__":
    unittest.main()
