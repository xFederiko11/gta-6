"""Offline regression tests for the GitHub Pages negative-path CDN smoke test.

Simulate GitHub Pages results without network access or publishing the site.
The built artifact is separately verified by public_release_gate.py.
"""
from contextlib import redirect_stdout, nullcontext
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from types import SimpleNamespace
import io
import os
import unittest
import urllib.request


class LivePrivatePathChecks(unittest.TestCase):
    def block(self):
        workflow = Path(".github/workflows/deploy-site.yml").read_text(encoding="utf-8")
        marker = "          # Verify that the live CDN does not serve operational artifacts."
        ending = "          home=urllib.request.urlopen(base+'?public-nav=1'"
        start = workflow.index(marker)
        end = workflow.index(ending, start)
        raw = workflow[start:end]
        result = "\n".join(line[10:] for line in raw.splitlines()) + "\n"
        compile(result, "<private-path-gate>", "exec")
        return result

    def run_fake(self, handler):
        output = io.StringIO()
        env = {
            "urllib": urllib,
            "time": SimpleNamespace(sleep=lambda _: None),
            "base": "https://xfederiko11.github.io/gta-6/",
        }
        with (patch("urllib.request.urlopen", side_effect=handler) as request,
              patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": ""}),
              redirect_stdout(output)):
            exec(self.block(), env)
        return env, output.getvalue(), request.call_count

    @staticmethod
    def http_error(request, code):
        return HTTPError(request.full_url, code, "test-response", None, None)

    def test_private_404_is_confirmed_not_guessed(self):
        def handler(request, timeout):
            raise self.http_error(request, 404)
        env, stdout, count = self.run_fake(handler)
        self.assertEqual(env["unverified_private"], [])
        self.assertEqual(stdout.count("PUBLIC_PRIVATE_PATH_404_OK"), 12)
        self.assertEqual(count, 12)

    def test_persistent_503_is_explicitly_unverified_not_404(self):
        def handler(request, timeout):
            raise self.http_error(request, 503 if "/crescita-x/" in request.full_url else 404)
        env, stdout, count = self.run_fake(handler)
        self.assertEqual(env["unverified_private"], [("crescita-x/", 503)])
        self.assertIn("PUBLIC_PRIVATE_CDN_DEGRADED 1", stdout)
        self.assertIn("NOT a verified 404", stdout)
        self.assertEqual(stdout.count("PUBLIC_PRIVATE_PATH_404_OK"), 11)
        self.assertEqual(count, 17)

    def test_public_private_path_fails_immediately_even_after_prior_503(self):
        responses = iter((503, 200))
        def handler(request, timeout):
            code = next(responses)
            if code == 200:
                return nullcontext(SimpleNamespace(status=200))
            raise self.http_error(request, code)
        with self.assertRaisesRegex(AssertionError, "Internal artifact is public: crescita-x"):
            self.run_fake(handler)

    def test_any_http_200_is_not_accepted_as_a_safe_private_path(self):
        def handler(request, timeout):
            return nullcontext(SimpleNamespace(status=200))
        with self.assertRaisesRegex(AssertionError, "Internal artifact is public: crescita-x"):
            self.run_fake(handler)

    def test_unexpected_403_is_not_reported_as_404_or_503(self):
        def handler(request, timeout):
            raise self.http_error(request, 403)
        with self.assertRaises(HTTPError):
            self.run_fake(handler)


if __name__ == "__main__":
    unittest.main()
