"""HTTP client for the Railway Google MCP server (no Google SDK in repo)."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from src.publish.exceptions import McpError


class McpHttpClient:
    def __init__(self, base_url: str, *, timeout: int = 120) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=data,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "LIP-4-4/1.0 (Weekly App Review Pulse)",
            },
            method=method,
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read().decode("utf-8")
                if not body:
                    return {}
                parsed = json.loads(body)
                if isinstance(parsed, dict):
                    return parsed
                return {"data": parsed}
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise McpError(f"MCP HTTP {exc.code} on {path}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise McpError(f"MCP request failed for {path}: {exc}") from exc
        except json.JSONDecodeError as exc:
            raise McpError(f"MCP returned invalid JSON from {path}") from exc

    def list_tools(self) -> list[dict[str, Any]]:
        result = self._request("GET", "/tools")
        if isinstance(result, list):
            return result
        data = result.get("data")
        if isinstance(data, list):
            return data
        raise McpError("Unexpected /tools response shape")

    def has_tool(self, name: str) -> bool:
        return any(tool.get("name") == name for tool in self.list_tools())

    def append_to_doc(self, doc_id: str, content: str) -> dict[str, Any]:
        result = self._request(
            "POST",
            "/append_to_doc",
            {"doc_id": doc_id, "content": content},
        )
        if result.get("status") == "rejected":
            raise McpError(result.get("message", "append_to_doc rejected"))
        if result.get("status") == "error":
            raise McpError(result.get("message", "append_to_doc failed"))
        return result

    def create_document(self, title: str, content: str) -> dict[str, Any]:
        result = self._request(
            "POST",
            "/create_document",
            {"title": title, "content": content},
        )
        if result.get("status") == "rejected":
            raise McpError(result.get("message", "create_document rejected"))
        if result.get("status") == "error":
            raise McpError(result.get("message", "create_document failed"))
        return result

    def create_email_draft(self, to: str, subject: str, body: str) -> dict[str, Any]:
        result = self._request(
            "POST",
            "/create_email_draft",
            {"to": to, "subject": subject, "body": body},
        )
        if result.get("status") == "rejected":
            raise McpError(result.get("message", "create_email_draft rejected"))
        if result.get("status") == "error":
            raise McpError(result.get("message", "create_email_draft failed"))
        return result


def google_doc_url(doc_id: str) -> str:
    return f"https://docs.google.com/document/d/{doc_id}/edit"
