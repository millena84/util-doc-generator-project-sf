import copy
import json
import pickle
import unittest

from tests.helpers import FAKE_TOKEN, FakeRunner
from salesforce_docs.errors import GlobalFailure, SessionExpiredError
from salesforce_docs.salesforce.cli_runner import CliResult
from salesforce_docs.salesforce.org_session import OrgSession
from salesforce_docs.validation.org_session_validator import (validate_alias_present,
                                                              validate_display)


def result(obj, rc=0):
    return CliResult(["sf"], rc, json.dumps(obj), "", 0)


DISPLAY = {"status": 0, "result": {"apiVersion": "67.0", "accessToken": FAKE_TOKEN,
                                   "instanceUrl": "https://x.my.salesforce.com",
                                   "username": "u@example.com", "connectedStatus": "Connected"}}


class OrgSessionValidatorTest(unittest.TestCase):
    def test_alias_present(self):
        org = validate_alias_present(result({"status": 0, "result": {"nonScratchOrgs": [{"alias": "dev"}]}}), "dev")
        self.assertEqual(org["alias"], "dev")

    def test_alias_in_aliases_list(self):
        validate_alias_present(result({"status": 0, "result": {"other": [{"aliases": ["dev"]}]}}), "dev")

    def test_org_not_authenticated(self):
        with self.assertRaises(GlobalFailure) as ctx:
            validate_alias_present(result({"status": 0, "result": {"nonScratchOrgs": []}}), "dev")
        self.assertEqual(ctx.exception.code, "ORG_NOT_AUTHENTICATED")
        self.assertEqual(ctx.exception.suggestion, "sf org login web --alias dev")

    def test_display_not_connected(self):
        data = json.loads(json.dumps(DISPLAY))
        data["result"]["connectedStatus"] = "RefreshTokenAuthError"
        with self.assertRaises(GlobalFailure) as ctx:
            validate_display(result(data), "dev")
        self.assertEqual(ctx.exception.code, "ORG_NOT_CONNECTED")

    def test_display_missing_fields(self):
        data = json.loads(json.dumps(DISPLAY))
        del data["result"]["accessToken"]
        with self.assertRaises(GlobalFailure) as ctx:
            validate_display(result(data), "dev")
        self.assertIn("accessToken", ctx.exception.message)

    def test_session_api_version_override_and_masking(self):
        s = OrgSession.from_display_result("dev", DISPLAY["result"])
        self.assertEqual(s.api_version, "67.0")
        s2 = OrgSession.from_display_result("dev", DISPLAY["result"], api_version_override="66.0")
        self.assertEqual(s2.api_version, "66.0")
        self.assertEqual(s2.detected_api_version, "67.0")
        self.assertNotIn(FAKE_TOKEN, repr(s2))
        self.assertNotIn(FAKE_TOKEN, json.dumps(s2.describe()))

    def test_session_token_not_exposed_nor_serializable(self):
        s = OrgSession.from_display_result("dev", DISPLAY["result"])
        self.assertNotIn(FAKE_TOKEN, str(s))
        self.assertNotIn(FAKE_TOKEN, f"{s!r} {s}")
        with self.assertRaises(TypeError):
            pickle.dumps(s)
        with self.assertRaises(TypeError):
            copy.deepcopy(s)

    def test_session_clear_discards_token(self):
        s = OrgSession.from_display_result("dev", DISPLAY["result"])
        self.assertEqual(s.access_token, FAKE_TOKEN)
        s.clear()
        self.assertTrue(s.cleared)
        self.assertNotIn(FAKE_TOKEN, json.dumps(vars(s)))
        with self.assertRaises(SessionExpiredError):
            s.access_token


if __name__ == "__main__":
    unittest.main()
