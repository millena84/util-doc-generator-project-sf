"""Utilitários de teste: projeto temporário, CLI simulada e Metadata API simulada."""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
# Testes nunca abrem prompt interativo (mesmo rodando num terminal).
os.environ["SFDOCS_NON_INTERACTIVE"] = "1"
sys.path.insert(0, str(ROOT / "src"))

from salesforce_docs.salesforce.cli_runner import CliResult  # noqa: E402
from salesforce_docs.salesforce.metadata_api_client import MD_NS, SOAP_NS, MetadataApiResponse  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures"
FAKE_SF = FIXTURES / "bin" / "sf"
FAKE_TOKEN = "00DFAKE!TOKEN.SIMULADO.NAO.REAL.1234567890"
SIMULATED_ORG_ID = "00D000000000000AAA"

# Campos simulados por tipo (apenas para testes; não representam a org real).
SIMULATED_SCHEMA_FIELDS = {
    "Flow": ["apiVersion", "description", "label", "processType", "screens", "start", "status"],
    "FlowDefinition": ["activeVersionNumber", "description", "masterLabel"],
    "ExternalClientApplication": ["contactEmail", "description", "distributionState", "isProtected", "label"],
    "ConnectedApp": ["contactEmail", "label", "oauthConfig"],
    "NamedCredential": ["allowMergeFieldsInBody", "allowMergeFieldsInHeader", "description",
                        "endpoint", "generateAuthorizationHeader", "label",
                        "namedCredentialParameters", "namedCredentialType"],
    "ExternalCredential": ["authenticationProtocol", "description", "externalCredentialParameters",
                           "label"],
    "RemoteSiteSetting": ["description", "disableProtocolSecurity", "isActive", "url"],
    "Certificate": ["caSigned", "encryptedWithPlatformEncryption", "expirationDate", "keySize",
                    "masterLabel", "privateKeyExportable"],
    "CustomObject": ["deploymentStatus", "description", "label", "pluralLabel", "sharingModel",
                     "visibility"],
    "ExtlClntAppConfigurablePolicies": ["externalClientApplication", "isEnabled",
                                        "isOauthPluginEnabled", "label", "startPage", "startUrl"],
}


def describe_body(metadata_type):
    fields = SIMULATED_SCHEMA_FIELDS.get(metadata_type, ["label"])
    vtf = "".join(
        f"<valueTypeFields><isForeignKey>false</isForeignKey><isNameField>false</isNameField>"
        f"<minOccurs>0</minOccurs><name>{n}</name><soapType>string</soapType>"
        f"<valueRequired>false</valueRequired></valueTypeFields>" for n in fields)
    return (f'<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="{SOAP_NS}" '
            f'xmlns="{MD_NS}"><soapenv:Body><describeValueTypeResponse><result>'
            f"<apiCreatable>true</apiCreatable><apiDeletable>true</apiDeletable>"
            f"<apiReadable>true</apiReadable><apiUpdatable>true</apiUpdatable>{vtf}"
            f"</result></describeValueTypeResponse></soapenv:Body></soapenv:Envelope>")


def fault_body(code, message):
    return (f'<?xml version="1.0" encoding="UTF-8"?><soapenv:Envelope xmlns:soapenv="{SOAP_NS}">'
            f"<soapenv:Body><soapenv:Fault><faultcode>sf:{code}</faultcode>"
            f"<faultstring>{code}: {message}</faultstring></soapenv:Fault></soapenv:Body></soapenv:Envelope>")


class FakeMetadataClient:
    def __init__(self, session, unavailable=(), expired=False):
        self.api_version = session.api_version
        self.unavailable = set(unavailable)
        self.expired = expired
        self.calls = []

    def describe_value_type(self, metadata_type):
        self.calls.append(metadata_type)
        args = {"type": f"{{{MD_NS}}}{metadata_type}"}
        endpoint = "https://simulado.my.salesforce.com/services/Soap/m/" + self.api_version
        if self.expired:
            r = MetadataApiResponse("describeValueType", endpoint, self.api_version, args, 500,
                                    "text/xml", fault_body("INVALID_SESSION_ID", "Session expired"), "t")
            r.session_expired = True
            return r
        if metadata_type in self.unavailable:
            r = MetadataApiResponse("describeValueType", endpoint, self.api_version, args, 500,
                                    "text/xml", fault_body("INSUFFICIENT_ACCESS", "sem permissão"), "t")
            r.session_expired = False
            return r
        r = MetadataApiResponse("describeValueType", endpoint, self.api_version, args, 200,
                                "text/xml", describe_body(metadata_type), "t")
        r.session_expired = False
        return r


class TempProject:
    """Cópia isolada de config/ e documentation/ em diretório temporário."""

    def __init__(self):
        self.dir = Path(tempfile.mkdtemp(prefix="sfdocs-test-"))
        shutil.copytree(ROOT / "config", self.dir / "config")
        shutil.copytree(ROOT / "documentation", self.dir / "documentation")
        # A org SIMULADA precisa estar aprovada (Prioridade 3: nenhuma coleta sem aprovação).
        cfg_path = self.dir / "config" / "config.json"
        cfg = json.loads(cfg_path.read_text())
        cfg["approvedOrgs"] = [{"orgId": SIMULATED_ORG_ID, "alias": "dev",
                                "note": "org SIMULADA dos testes"}]
        cfg_path.write_text(json.dumps(cfg, indent=2))

    def cleanup(self):
        shutil.rmtree(self.dir, ignore_errors=True)


def fake_sf_env(scenario=""):
    os.environ["FAKE_SF_FIXTURES"] = str(FIXTURES)
    os.environ["FAKE_SF_SCENARIO"] = scenario


class FakeRunner:
    """Runner em memória para testes unitários de validadores."""

    def __init__(self, responses):
        self.responses = responses
        self.history = []
        self.masker = lambda s: s

    def run(self, args, raw_path=None, error_raw_path=None, cwd=None, check_session=True):
        key = " ".join(args)
        rc, out = self.responses[key]
        self.history.append(key)
        return CliResult(["sf"] + list(args), rc, out, "", 0.0)
