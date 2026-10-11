"""Sessão da org obtida de `sf org display --json` (token só em memória)."""

from __future__ import annotations

from salesforce_docs.utils import normalize_api_version


class OrgSession:
    def __init__(self, alias, username, instance_url, access_token, detected_api_version,
                 api_version_override=None, org_id=None):
        self.alias = alias
        self.username = username
        self.instance_url = (instance_url or "").rstrip("/")
        self._access_token = access_token
        self.org_id = org_id
        self.detected_api_version = normalize_api_version(detected_api_version)
        self.api_version = normalize_api_version(api_version_override or detected_api_version)
        self.api_version_source = "argument" if api_version_override else "sf org display"

    @property
    def access_token(self) -> str:
        return self._access_token

    @classmethod
    def from_display_result(cls, alias, result: dict, api_version_override=None) -> "OrgSession":
        return cls(
            alias=alias,
            username=result.get("username"),
            instance_url=result.get("instanceUrl"),
            access_token=result.get("accessToken"),
            detected_api_version=result.get("apiVersion"),
            api_version_override=api_version_override,
            org_id=result.get("id"),
        )

    def describe(self) -> dict:
        """Representação segura (sem token) para logs e run state."""
        return {
            "alias": self.alias,
            "username": self.username,
            "instanceUrl": self.instance_url,
            "orgId": self.org_id,
            "detectedApiVersion": self.detected_api_version,
            "apiVersion": self.api_version,
            "apiVersionSource": self.api_version_source,
        }

    def __repr__(self):
        return f"OrgSession(alias={self.alias!r}, username={self.username!r}, accessToken='***')"
