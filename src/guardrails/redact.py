"""PII redaction for pulse output."""

from __future__ import annotations

import re

EMAIL_PATTERN = re.compile(
    r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
    re.IGNORECASE,
)
PHONE_PATTERN = re.compile(
    r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b",
)
PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b")
AADHAAR_PATTERN = re.compile(r"\b\d{4}\s?\d{4}\s?\d{4}\b")
HANDLE_PATTERN = re.compile(r"(?<!\w)@[A-Za-z0-9_]{2,}\b")
ACCOUNT_PATTERN = re.compile(
    r"\b(?:folio|account|acc(?:ount)?)\s*(?:no\.?|number|#)?\s*:?\s*\d{6,}\b",
    re.IGNORECASE,
)

REDACTIONS: list[tuple[re.Pattern[str], str]] = [
    (EMAIL_PATTERN, "[email redacted]"),
    (PHONE_PATTERN, "[phone redacted]"),
    (PAN_PATTERN, "[id redacted]"),
    (AADHAAR_PATTERN, "[id redacted]"),
    (ACCOUNT_PATTERN, "[account redacted]"),
]


def redact_handles(text: str) -> str:
    return HANDLE_PATTERN.sub("[handle redacted]", text)


def redact_text(text: str) -> str:
    result = text
    for pattern, replacement in REDACTIONS:
        result = pattern.sub(replacement, result)
    return redact_handles(result)


def contains_pii(text: str) -> bool:
    return bool(scan_pii_violations(text))


def scan_pii_violations(text: str) -> list[str]:
    violations: list[str] = []
    if EMAIL_PATTERN.search(text):
        violations.append("email pattern detected")
    if PHONE_PATTERN.search(text):
        violations.append("phone pattern detected")
    if PAN_PATTERN.search(text):
        violations.append("PAN-like pattern detected")
    if AADHAAR_PATTERN.search(text):
        violations.append("Aadhaar-like pattern detected")
    if HANDLE_PATTERN.search(text):
        violations.append("social handle detected")
    if ACCOUNT_PATTERN.search(text):
        violations.append("account number pattern detected")
    return violations
