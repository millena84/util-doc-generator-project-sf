import io
import json
import unittest
import urllib.error

from tests.helpers import FAKE_TOKEN, describe_body, fault_body
from salesforce_docs.errors import SessionExpiredError
from salesforce_docs.extraction.schema_extractor import parse_describe_body
from salesforce_docs.salesforce.metadata_api_client import MetadataApiClient, raise_if_session_expired


class _Resp:
    def __init__(self, status, body):
        self.status = status
        self.headers = {"Content-Type": "text/xml"}
        self._body = body.encode()

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class _Opener:
    def __init__(self, status=200, body="", http_error=None):
        self.status, self.body, self.http_error = status, body, http_error
        self.requests = []

    def open(self, req, timeout=None):
        self.requests.append(req)
        if self.http_error:
            code, body = self.http_error
            raise urllib.error.HTTPError(req.full_url, code, "err", {"Content-Type": "text/xml"},
                                         io.BytesIO(body.encode()))
        return _Resp(self.status, self.body)


class MetadataApiClientTest(unittest.TestCase):
    def client(self, opener):
        return MetadataApiClient("https://x.my.salesforce.com/", FAKE_TOKEN, "67.0", opener=opener)

    def test_describe_request_and_raw_without_token(self):
        opener = _Opener(body=describe_body("Flow"))
        resp = self.client(opener).Flow.describe()  # equivalente a mdapi.Flow.describe()
        req = opener.requests[0]
        self.assertEqual(req.full_url, "https://x.my.salesforce.com/services/Soap/m/67.0")
        payload = req.data.decode()
        self.assertIn("{http://soap.sforce.com/2006/04/metadata}Flow", payload)
        self.assertIn(FAKE_TOKEN, payload)  # token só na requisição em memória
        self.assertTrue(resp.ok)
        raw = json.dumps(resp.to_raw())
        self.assertNotIn(FAKE_TOKEN, raw)
        self.assertEqual(resp.to_raw()["response"]["body"], describe_body("Flow"))
        parsed = parse_describe_body(resp.body)
        self.assertEqual([f["name"] for f in parsed["valueTypeFields"]][:2], ["apiVersion", "description"])

    def test_invalid_session_raises(self):
        opener = _Opener(http_error=(500, fault_body("INVALID_SESSION_ID", "Session expired or invalid")))
        resp = self.client(opener).describe_value_type("Flow")
        with self.assertRaises(SessionExpiredError):
            raise_if_session_expired(resp)

    def test_http_401_raises(self):
        opener = _Opener(http_error=(401, ""))
        with self.assertRaises(SessionExpiredError):
            raise_if_session_expired(self.client(opener).describe_value_type("Flow"))

    def test_permission_fault_is_not_session(self):
        opener = _Opener(http_error=(500, fault_body("INSUFFICIENT_ACCESS", "sem permissão")))
        resp = self.client(opener).describe_value_type("Flow")
        raise_if_session_expired(resp)
        self.assertFalse(resp.ok)
        self.assertEqual(resp.fault()[0], "sf:INSUFFICIENT_ACCESS")


if __name__ == "__main__":
    unittest.main()
