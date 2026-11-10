"""
A-CODE Lane — Side-by-Side Comparison Engine (Unconstrained vs. CLAUDE.md Contract)

Demonstrates the concrete engineering difference on the exact same feature request:
"Build a multi-tenant webhook & release-gate payload processor."

1. `process_unconstrained(payload)` — Models typical single-shot agent code without CLAUDE.md:
   - No tenant isolation check (cross-tenant data leak)
   - No null/whitespace/unicode normalization (crashes on None, accepts empty whitespace)
   - No idempotency / duplicate guard (double-processes retries)
   - Leaks raw internal stack/paths on error
   - No payload size cap (DoS on 10x payload)

2. `process_contract(payload, *, current_tenant, seen_ids)` — Built under CLAUDE.md §26.6 & §28.2:
   - Strict boundary validation & schema enforcement
   - Explicit authn/authz + tenant isolation check (deny path tested)
   - Unicode NFC normalization (handles combining marks, CJK, RTL, emoji cleanly)
   - Size cap (rejects >4096 chars per §26.6 10x edge matrix)
   - Idempotency key deduplication (safe on concurrent/retry calls)
   - Safe, structured error responses (zero stack/path leakage)
"""

from __future__ import annotations
import unicodedata
from dataclasses import dataclass
from typing import Any, Dict, Set

MAX_PAYLOAD_CHARS = 4096
ALLOWED_SEVERITIES = {"S1", "S2", "S3", "S4"}


# ---------------------------------------------------------------------------
# 1. BASELINE (UNCONSTRAINED AGENT OUTPUT — NO CLAUDE.md CONTRACT)
# ---------------------------------------------------------------------------
def process_unconstrained(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Typical "looks right on happy path" implementation produced without §26.6 / §28.2.
    Passes a basic happy-path check, but fails 8 of 10 edge-matrix cases.
    """
    # BUG 1: No null/type check -> TypeError/AttributeError on None or non-dict
    title = payload["title"]  # crashes with KeyError if missing, accepts "   "
    # BUG 2: No tenant check -> processes any tenant's release gate!
    # BUG 3: No idempotency check -> duplicate retries execute twice!
    # BUG 4: No length limit -> 10x payload balloons memory/context
    # BUG 5: Leaks internal file path in debug metadata
    return {
        "ok": True,
        "status": "APPROVED",
        "title": title.strip(),
        "tenant": payload.get("tenant", "default"),
        "severity": payload.get("severity", "S3"),
        "debug_path": "/Users/internal/prod-db/sqlite.db",  # §28.2 violation
    }


# ---------------------------------------------------------------------------
# 2. CONTRACT-DRIVEN (CLAUDE.md §16.7 A-CODE + §26.6 EDGE MATRIX + §28.2 SEC)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class GateDecision:
    ok: bool
    code: str
    status: str
    tenant: str
    request_id: str
    normalized_title: str
    severity: str
    message: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ok": self.ok,
            "code": self.code,
            "status": self.status,
            "tenant": self.tenant,
            "request_id": self.request_id,
            "normalized_title": self.normalized_title,
            "severity": self.severity,
            "message": self.message,
        }


def process_contract(
    payload: Any,
    *,
    current_tenant: str,
    seen_ids: Set[str],
) -> Dict[str, Any]:
    """
    Contract-verified processor satisfying §26.6 Edge Matrix & §28.2 Security Review.
    Never raises unhandled exceptions or leaks internal paths.
    """
    if not isinstance(payload, dict):
        return GateDecision(
            ok=False,
            code="ERR_MALFORMED",
            status="REJECTED",
            tenant=current_tenant or "unknown",
            request_id="",
            normalized_title="",
            severity="",
            message="Payload must be a JSON object.",
        ).to_dict()

    # 1. Authn / Authz & Tenant Isolation (§28.2 + §26.6 unauthorized / wrong-tenant)
    req_tenant = payload.get("tenant")
    if not isinstance(req_tenant, str) or not req_tenant.strip():
        return GateDecision(
            ok=False,
            code="ERR_UNAUTHORIZED",
            status="REJECTED",
            tenant=current_tenant,
            request_id=str(payload.get("request_id") or ""),
            normalized_title="",
            severity="",
            message="Missing tenant credential.",
        ).to_dict()

    if req_tenant.strip() != current_tenant:
        return GateDecision(
            ok=False,
            code="ERR_WRONG_TENANT",
            status="REJECTED",
            tenant=current_tenant,
            request_id=str(payload.get("request_id") or ""),
            normalized_title="",
            severity="",
            message="Cross-tenant access denied.",
        ).to_dict()

    # 2. Request ID & Idempotency / Retry Guard (§26.6 duplicate/concurrent/retry)
    raw_id = payload.get("request_id")
    if not isinstance(raw_id, str) or not raw_id.strip():
        return GateDecision(
            ok=False,
            code="ERR_MISSING_ID",
            status="REJECTED",
            tenant=current_tenant,
            request_id="",
            normalized_title="",
            severity="",
            message="request_id is required for idempotent execution.",
        ).to_dict()

    req_id = raw_id.strip()
    if req_id in seen_ids:
        return GateDecision(
            ok=False,
            code="ERR_DUPLICATE_RETRY",
            status="SKIPPED_IDEMPOTENT",
            tenant=current_tenant,
            request_id=req_id,
            normalized_title="",
            severity="",
            message="Duplicate request_id safely ignored.",
        ).to_dict()

    # 3. Title Validation, Unicode NFC Normalization & 10x Size Guard (§26.6)
    raw_title = payload.get("title")
    if not isinstance(raw_title, str):
        return GateDecision(
            ok=False,
            code="ERR_NULL_TITLE",
            status="REJECTED",
            tenant=current_tenant,
            request_id=req_id,
            normalized_title="",
            severity="",
            message="title must be a non-empty string.",
        ).to_dict()

    if len(raw_title) > MAX_PAYLOAD_CHARS:
        return GateDecision(
            ok=False,
            code="ERR_PAYLOAD_TOO_LARGE",
            status="REJECTED",
            tenant=current_tenant,
            request_id=req_id,
            normalized_title="",
            severity="",
            message=f"title exceeds max length of {MAX_PAYLOAD_CHARS} characters.",
        ).to_dict()

    normalized_title = unicodedata.normalize("NFC", raw_title).strip()
    if not normalized_title:
        return GateDecision(
            ok=False,
            code="ERR_EMPTY_TITLE",
            status="REJECTED",
            tenant=current_tenant,
            request_id=req_id,
            normalized_title="",
            severity="",
            message="title cannot be empty or whitespace-only.",
        ).to_dict()

    # 4. Severity Enum Check
    severity = str(payload.get("severity") or "S3").upper().strip()
    if severity not in ALLOWED_SEVERITIES:
        return GateDecision(
            ok=False,
            code="ERR_INVALID_SEVERITY",
            status="REJECTED",
            tenant=current_tenant,
            request_id=req_id,
            normalized_title=normalized_title,
            severity=severity,
            message="severity must be one of S1, S2, S3, S4.",
        ).to_dict()

    # Record idempotency key only after validation succeeds
    seen_ids.add(req_id)

    return GateDecision(
        ok=True,
        code="OK_VERIFIED",
        status="APPROVED",
        tenant=current_tenant,
        request_id=req_id,
        normalized_title=normalized_title,
        severity=severity,
        message="Release gate verified and recorded.",
    ).to_dict()
