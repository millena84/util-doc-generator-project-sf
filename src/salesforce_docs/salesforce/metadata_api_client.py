"""Cliente mínimo da Metadata API (SOAP) usando apenas a biblioteca padrão.

Endpoint: {instanceUrl}/services/Soap/m/{apiVersion}
Operação: describeValueType(type="{http://soap.sforce.com/2006/04/metadata}<Tipo>")
"""

from __future__ import annotations

import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from xml.sax.saxutils import escape

from salesforce_docs.errors import SessionExpiredError
from salesforce_docs.utils import iso_now

MD_NS = "http://soap.sforce.com/2006/04/metadata"
SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"

_ENVELOPE = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    f'<soapenv:Envelope xmlns:soapenv="{SOAP_NS}" xmlns:met="{MD_NS}">'
    "<soapenv:Header><met:SessionHeader><met:sessionId>{session}</met:sessionId>"
    "</met:SessionHeader></soapenv:Header>"
    "<soapenv:Body>{body}</soapenv:Body></soapenv:Envelope>"
)


class MetadataApiResponse:
    def __init__(self, operation, endpoint, api_version, request_args, http_status,
                 content_type, body, requested_at, error=None):
        self.operation = operation
        self.endpoint = endpoint
        self.api_version = api_version
        self.request_args = request_args
        self.http_status = http_status
        self.content_type = content_type
        self.body = body
        self.requested_at = requested_at
        self.error = error

    @property
    def ok(self) -> bool:
        return self.http_status == 200 and self.error is None and fault_of(self.body) is None

    def fault(self):
        return fault_of(self.body)

    def to_raw(self) -> dict:
        """Envelope JSON do raw. `response.body` é o XML exatamente como recebido.

        O token NÃO é gravado (a requisição é descrita sem o SessionHeader).
        """
        return {
            "rawFormat": "metadata-api-soap-capture/v1",
            "operation": self.operation,
            "request": {
                "endpoint": self.endpoint,
                "apiVersion": self.api_version,
                "arguments": self.request_args,
                "requestedAt": self.requested_at,
            },
            "response": {
                "httpStatus": self.http_status,
                "contentType": self.content_type,
                "transportError": self.error,
                "body": self.body,
            },
        }


def fault_of(body):
    """Retorna (faultcode, faultstring) se o corpo for um SOAP Fault."""
    if not body:
        return None
    try:
        root = ET.fromstring(body.encode("utf-8") if isinstance(body, str) else body)
    except ET.ParseError:
        return None
    fault = root.find(f".//{{{SOAP_NS}}}Fault")
    if fault is None:
        return None
    return (fault.findtext("faultcode") or "", fault.findtext("faultstring") or "")


class _TypeProxy:
    def __init__(self, client, metadata_type):
        self._client = client
        self._type = metadata_type

    def describe(self) -> MetadataApiResponse:
        return self._client.describe_value_type(self._type)


class MetadataApiClient:
    """Uso: `mdapi.Flow.describe()` equivale a describeValueType('{ns}Flow')."""

    def __init__(self, instance_url, access_token, api_version, timeout=120, opener=None):
        """access_token: str ou callable sem argumentos que devolve o token no momento
        da chamada (preferível: o cliente não guarda cópia própria do token)."""
        self._instance_url = instance_url.rstrip("/")
        self._token = access_token
        self.api_version = api_version
        self.timeout = timeout
        self._opener = opener or urllib.request.build_opener()

    def __repr__(self):
        return f"MetadataApiClient(endpoint={self.endpoint!r}, accessToken='***')"

    def __getstate__(self):
        raise TypeError("MetadataApiClient contém token de acesso e não pode ser serializado")

    def _current_token(self):
        return self._token() if callable(self._token) else self._token

    @property
    def endpoint(self) -> str:
        return f"{self._instance_url}/services/Soap/m/{self.api_version}"

    def __getattr__(self, name):
        if name[:1].isupper():
            return _TypeProxy(self, name)
        raise AttributeError(name)

    def describe_value_type(self, metadata_type: str) -> MetadataApiResponse:
        qname = f"{{{MD_NS}}}{metadata_type}"
        body = f"<met:describeValueType><met:type>{escape(qname)}</met:type></met:describeValueType>"
        return self._call("describeValueType", {"type": qname}, body)

    def _call(self, operation, args, body_xml) -> MetadataApiResponse:
        payload = _ENVELOPE.format(session=escape(self._current_token() or ""), body=body_xml).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint,
            data=payload,
            method="POST",
            headers={"Content-Type": "text/xml; charset=UTF-8", "SOAPAction": '""'},
        )
        requested_at = iso_now()
        status, ctype, text, error = None, None, None, None
        try:
            with self._opener.open(req, timeout=self.timeout) as resp:
                status = resp.status
                ctype = resp.headers.get("Content-Type")
                text = resp.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            status = exc.code
            ctype = exc.headers.get("Content-Type") if exc.headers else None
            text = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
        except (urllib.error.URLError, OSError) as exc:
            error = f"{type(exc).__name__}: {exc}"
        response = MetadataApiResponse(operation, self.endpoint, self.api_version, args,
                                       status, ctype, text, requested_at, error)
        fault = response.fault()
        if status == 401 or (fault and "INVALID_SESSION_ID" in (fault[0] + fault[1])):
            response.session_expired = True
        else:
            response.session_expired = False
        return response


def raise_if_session_expired(response: MetadataApiResponse):
    if getattr(response, "session_expired", False):
        fault = response.fault()
        detail = f"{fault[0]}: {fault[1]}" if fault else f"HTTP {response.http_status}"
        raise SessionExpiredError(f"Metadata API {response.operation}: {detail}")
