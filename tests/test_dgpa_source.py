import ssl
import unittest
from unittest import mock
from urllib.error import URLError

from typhoon_day_research.sources.dgpa import fetch_url


class _FakeResponse:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False

    def read(self):
        return b"ok"


class DgpaSourceTests(unittest.TestCase):
    def test_fetch_url_retries_with_relaxed_tls_for_strict_certificate_error(self):
        calls = []

        def fake_urlopen(url, timeout, context):
            calls.append(context)
            if len(calls) == 1:
                reason = ssl.SSLCertVerificationError("certificate verify failed: Missing Subject Key Identifier")
                raise URLError(reason)
            return _FakeResponse()

        with mock.patch("typhoon_day_research.sources.dgpa.urlopen", side_effect=fake_urlopen):
            self.assertEqual(fetch_url("https://www.dgpa.gov.tw/"), b"ok")

        self.assertEqual(len(calls), 2)
        if hasattr(ssl, "VERIFY_X509_STRICT"):
            self.assertFalse(calls[1].verify_flags & ssl.VERIFY_X509_STRICT)


if __name__ == "__main__":
    unittest.main()
