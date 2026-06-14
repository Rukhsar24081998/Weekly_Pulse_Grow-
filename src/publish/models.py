"""Phase 4 publish result types."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DocPublishResult:
    output_path: str
    doc_title: str
    google_doc_id: str
    google_doc_url: str
    mcp_tool: str
    week_ending: str
    word_count: int
    validation_passed: bool


@dataclass
class DraftPublishResult:
    output_path: str
    subject: str
    recipient: str
    gmail_draft_id: str
    week_ending: str
    word_count: int
    validation_passed: bool


@dataclass
class E2ERunResult:
    output_path: str
    google_doc_id: str
    google_doc_url: str
    gmail_draft_id: str
    week_ending: str
    validation_passed: bool
