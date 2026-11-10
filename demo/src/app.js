/**
 * A-UI & A-CODE Browser Runtime — Interactive Side-by-Side Comparison Website
 * Works standalone via file:// or http:// with zero external dependencies.
 */

const MAX_PAYLOAD_CHARS = 4096;
const ALLOWED_SEVERITIES = new Set(["S1", "S2", "S3", "S4"]);
const CURRENT_TENANT = "acme-prod";
const seenContractIds = new Set();
let unconstrainedQueueCount = 0;
let contractQueueCount = 0;

/**
 * 1. Unconstrained Agent Baseline Processor (No CLAUDE.md Contract)
 * Exhibits the exact failure modes banned in §25.10, §26.6, and §28.2.
 */
function processUnconstrained(payload) {
  try {
    if (payload === null || typeof payload !== "object") {
      // Unhandled crash leaked directly to client (§28.2 violation)
      throw new TypeError(
        "Cannot read properties of null (reading 'title')\n    at processUnconstrained (/Users/internal/prod-api/handler.js:42:19)\n    at SQLiteDriver (/Users/internal/prod-db/sqlite.db)"
      );
    }
    if (typeof payload.title !== "string") {
      throw new TypeError(
        "payload.title.trim is not a function at /Users/internal/prod-api/handler.js:44:25"
      );
    }
    unconstrainedQueueCount += 1;
    return {
      ok: true,
      verdict: "PASS (UNVERIFIED)",
      status: "APPROVED_NO_CHECKS",
      queue_writes: unconstrainedQueueCount,
      tenant_accepted: payload.tenant || "anonymous-unverified",
      title_stored: payload.title.trim(),
      title_bytes: payload.title.length,
      severity: payload.severity || "S3",
      leaked_debug_path: "/Users/internal/prod-db/sqlite.db",
      defects_triggered: detectBaselineDefects(payload),
    };
  } catch (err) {
    return {
      ok: false,
      verdict: "UNHANDLED_CRASH",
      status: "500_INTERNAL_ERROR",
      raw_stack_leak: String(err.stack || err.message || err),
      defects_triggered: [
        "Crashed with unhandled exception instead of structured error schema (§28.2)",
        "Leaked internal filesystem path in stack trace (§28.2)",
      ],
    };
  }
}

function detectBaselineDefects(payload) {
  const defects = [];
  if (!payload.tenant) {
    defects.push("Accepted unauthenticated request with empty tenant (§28.2 authn gap)");
  } else if (payload.tenant !== CURRENT_TENANT) {
    defects.push(
      `Cross-tenant write allowed: wrote to '${payload.tenant}' from '${CURRENT_TENANT}' session (§26.6 wrong-tenant)`
    );
  }
  if (typeof payload.title === "string" && payload.title.trim().length === 0) {
    defects.push("Accepted empty/whitespace-only title into database (§26.6 empty/whitespace)");
  }
  if (typeof payload.title === "string" && payload.title.length > MAX_PAYLOAD_CHARS) {
    defects.push(
      `Accepted ${payload.title.length}-char oversized payload without truncation/cap (§26.6 10x size)`
    );
  }
  if (typeof payload.title === "string" && payload.title !== payload.title.normalize("NFC")) {
    defects.push("Stored un-normalized Unicode combining marks — breaks FTS/index lookups (§26.6 unicode)");
  }
  if (payload.severity && !ALLOWED_SEVERITIES.has(String(payload.severity).toUpperCase().trim())) {
    defects.push(`Accepted invalid severity '${payload.severity}' with no schema validation (§28.2)`);
  }
  defects.push("Leaked internal path '/Users/internal/prod-db/sqlite.db' in response JSON (§28.2)");
  return defects;
}

/**
 * 2. CLAUDE.md Contract-Verified Processor (§16.7 A-CODE + §26.6 Edge Matrix + §28.2 Security)
 */
function processContract(payload, seenSet = seenContractIds) {
  if (payload === null || typeof payload !== "object" || Array.isArray(payload)) {
    return {
      ok: false,
      code: "ERR_MALFORMED",
      status: "REJECTED",
      tenant: CURRENT_TENANT,
      request_id: "",
      normalized_title: "",
      severity: "",
      message: "Payload must be a JSON object (§28.2 boundary validation).",
      rule_ref: "§26.6 null/malformed · §28.2 boundary check",
    };
  }

  const reqTenant = typeof payload.tenant === "string" ? payload.tenant.trim() : "";
  if (!reqTenant) {
    return {
      ok: false,
      code: "ERR_UNAUTHORIZED",
      status: "REJECTED",
      tenant: CURRENT_TENANT,
      request_id: String(payload.request_id || ""),
      normalized_title: "",
      severity: "",
      message: "Missing tenant credential — deny path enforced.",
      rule_ref: "§26.6 unauthorized · §28.2 authn+authz deny case",
    };
  }

  if (reqTenant !== CURRENT_TENANT) {
    return {
      ok: false,
      code: "ERR_WRONG_TENANT",
      status: "REJECTED",
      tenant: CURRENT_TENANT,
      request_id: String(payload.request_id || ""),
      normalized_title: "",
      severity: "",
      message: `Cross-tenant write blocked: active tenant '${CURRENT_TENANT}' cannot write to '${reqTenant}'.`,
      rule_ref: "§26.6 wrong-tenant isolation",
    };
  }

  const reqId = typeof payload.request_id === "string" ? payload.request_id.trim() : "";
  if (!reqId) {
    return {
      ok: false,
      code: "ERR_MISSING_ID",
      status: "REJECTED",
      tenant: CURRENT_TENANT,
      request_id: "",
      normalized_title: "",
      severity: "",
      message: "request_id is required for idempotent execution.",
      rule_ref: "§26.6 duplicate/retry guard",
    };
  }

  if (seenSet.has(reqId)) {
    return {
      ok: false,
      code: "ERR_DUPLICATE_RETRY",
      status: "SKIPPED_IDEMPOTENT",
      tenant: CURRENT_TENANT,
      request_id: reqId,
      normalized_title: "",
      severity: "",
      message: `Duplicate request_id '${reqId}' safely deduplicated (0 duplicate writes).`,
      rule_ref: "§26.6 concurrent/retry idempotency",
    };
  }

  if (typeof payload.title !== "string") {
    return {
      ok: false,
      code: "ERR_NULL_TITLE",
      status: "REJECTED",
      tenant: CURRENT_TENANT,
      request_id: reqId,
      normalized_title: "",
      severity: "",
      message: "title must be a string.",
      rule_ref: "§26.6 null/undefined check",
    };
  }

  if (payload.title.length > MAX_PAYLOAD_CHARS) {
    return {
      ok: false,
      code: "ERR_PAYLOAD_TOO_LARGE",
      status: "REJECTED",
      tenant: CURRENT_TENANT,
      request_id: reqId,
      normalized_title: "",
      severity: "",
      message: `Payload title (${payload.title.length} chars) exceeds cap of ${MAX_PAYLOAD_CHARS} chars.`,
      rule_ref: "§26.6 10x expected size guard",
    };
  }

  const normalizedTitle = payload.title.normalize("NFC").trim();
  if (!normalizedTitle) {
    return {
      ok: false,
      code: "ERR_EMPTY_TITLE",
      status: "REJECTED",
      tenant: CURRENT_TENANT,
      request_id: reqId,
      normalized_title: "",
      severity: "",
      message: "title cannot be empty or whitespace-only.",
      rule_ref: "§26.6 empty / whitespace-only",
    };
  }

  const severity = String(payload.severity || "S3").toUpperCase().trim();
  if (!ALLOWED_SEVERITIES.has(severity)) {
    return {
      ok: false,
      code: "ERR_INVALID_SEVERITY",
      status: "REJECTED",
      tenant: CURRENT_TENANT,
      request_id: reqId,
      normalized_title: normalizedTitle,
      severity,
      message: `Invalid severity '${severity}'. Allowed values: S1, S2, S3, S4.`,
      rule_ref: "§28.2 strict enum validation",
    };
  }

  seenSet.add(reqId);
  contractQueueCount += 1;

  return {
    ok: true,
    code: "OK_VERIFIED",
    status: "APPROVED",
    queue_writes: contractQueueCount,
    tenant: CURRENT_TENANT,
    request_id: reqId,
    normalized_title: normalizedTitle,
    codepoints_normalized: payload.title.length !== normalizedTitle.length,
    severity,
    message: "Release gate verified, NFC-normalized, and committed once.",
    rule_ref: "§17 L3 verified · §26.6 all edge checks green",
  };
}

/**
 * Preset scenarios covering §26.6 Edge Matrix
 */
const PRESETS = {
  happy: {
    label: "1. Happy Path (Valid S2 Release)",
    request_id: "req-101",
    tenant: "acme-prod",
    title: "Deploy auth token rotation v2.4",
    severity: "S2",
    expected_contract: "OK_VERIFIED",
  },
  whitespace: {
    label: "2. Whitespace-Only Title (§26.6 empty)",
    request_id: "req-102",
    tenant: "acme-prod",
    title: "     \t   ",
    severity: "S3",
    expected_contract: "ERR_EMPTY_TITLE",
  },
  unicode: {
    label: "3. Unicode Combining + CJK + RTL (§26.6 unicode)",
    request_id: "req-103",
    tenant: "acme-prod",
    title: "Cafe\u0301 東京リリース Gate \u202eمرحبا",
    severity: "S1",
    expected_contract: "OK_VERIFIED",
  },
  wrong_tenant: {
    label: "4. Cross-Tenant Write Attempt (§26.6 wrong-tenant)",
    request_id: "req-104",
    tenant: "rival-corp-prod",
    title: "Override production feature flag",
    severity: "S1",
    expected_contract: "ERR_WRONG_TENANT",
  },
  unauth: {
    label: "5. Missing Tenant Auth (§28.2 deny case)",
    request_id: "req-105",
    tenant: "",
    title: "Anonymous hotfix push",
    severity: "S2",
    expected_contract: "ERR_UNAUTHORIZED",
  },
  duplicate: {
    label: "6. Duplicate / Retry Storm (§26.6 idempotency)",
    request_id: "req-101",
    tenant: "acme-prod",
    title: "Deploy auth token rotation v2.4 (retry)",
    severity: "S2",
    expected_contract: "ERR_DUPLICATE_RETRY",
  },
  oversized: {
    label: "7. 10x Oversized Payload (40,960 chars)",
    request_id: "req-107",
    tenant: "acme-prod",
    title: "X".repeat(MAX_PAYLOAD_CHARS * 10),
    severity: "S3",
    expected_contract: "ERR_PAYLOAD_TOO_LARGE",
  },
  invalid_sev: {
    label: "8. Invalid Severity Enum (§28.2 boundary)",
    request_id: "req-108",
    tenant: "acme-prod",
    title: "Update billing webhook timeout",
    severity: "SEV-999-DROP-TABLE",
    expected_contract: "ERR_INVALID_SEVERITY",
  },
  null_payload: {
    label: "9. Null / Malformed Payload Crash Test",
    request_id: "req-109",
    tenant: "acme-prod",
    title: null,
    severity: "S2",
    isNullPayload: true,
    expected_contract: "ERR_MALFORMED",
  },
};

function renderPayloadPreview(obj) {
  const clone = JSON.parse(JSON.stringify(obj));
  if (clone && typeof clone.title === "string" && clone.title.length > 120) {
    clone.title = clone.title.slice(0, 120) + `... [truncated, total ${obj.title.length} chars]`;
  }
  return JSON.stringify(clone, null, 2);
}

function updateUIWithPayload(payload, labelText) {
  const tickerEl = document.getElementById("status-ticker");
  if (tickerEl) {
    tickerEl.textContent = `▶ Test: ${labelText}`;
  }

  // 1. Run Unconstrained
  const baseRes = processUnconstrained(payload);
  const baseBadge = document.getElementById("baseline-badge");
  const baseOut = document.getElementById("baseline-output");
  const baseDefects = document.getElementById("baseline-defects");

  if (!baseRes.ok) {
    baseBadge.className = "badge badge--fail";
    baseBadge.textContent = "[FAIL] 500 UNHANDLED CRASH";
  } else if (baseRes.defects_triggered && baseRes.defects_triggered.length > 1) {
    baseBadge.className = "badge badge--fail";
    baseBadge.textContent = `[FAIL] SILENT CORRUPTION (${baseRes.defects_triggered.length} leaks)`;
  } else {
    baseBadge.className = "badge badge--warn";
    baseBadge.textContent = "[WARN] PASSED WITHOUT GUARDS";
  }
  baseOut.textContent = renderPayloadPreview(baseRes);
  baseDefects.innerHTML = (baseRes.defects_triggered || [])
    .map((d) => `<li>[DEFECT] ${escapeHtml(d)}</li>`)
    .join("");

  // 2. Run Contract-Driven
  const contractRes = processContract(payload);
  const contractBadge = document.getElementById("contract-badge");
  const contractOut = document.getElementById("contract-output");
  const contractProof = document.getElementById("contract-proof");

  if (contractRes.ok) {
    contractBadge.className = "badge badge--pass";
    contractBadge.textContent = `[PASS] ${contractRes.code}`;
  } else {
    contractBadge.className = "badge badge--pass";
    contractBadge.textContent = `[GUARDED] ${contractRes.code}`;
  }
  contractOut.textContent = renderPayloadPreview(contractRes);
  contractProof.innerHTML = [
    `<li>[CONTRACT] ${escapeHtml(contractRes.rule_ref)}</li>`,
    `<li>[SECURITY] Zero internal paths or stack traces leaked (§28.2)</li>`,
    `<li>[STATE] Active tenant '${CURRENT_TENANT}' isolated; idempotent set size = ${seenContractIds.size}</li>`,
  ].join("");
}

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function runAllMatrixSuite() {
  const tbody = document.getElementById("matrix-tbody");
  const localSeen = new Set();
  const rows = [];
  let baseSafeCount = 0;
  let contractSafeCount = 0;

  const matrixCases = [
    {
      name: "1. Happy Path (Valid S2)",
      payload: { request_id: "m-1", tenant: "acme-prod", title: "Deploy v2.4", severity: "S2" },
      expectContractOk: true,
      expectCode: "OK_VERIFIED",
    },
    {
      name: "2. Null Payload Crash Test",
      payload: null,
      expectContractOk: false,
      expectCode: "ERR_MALFORMED",
    },
    {
      name: "3. Whitespace-Only Title",
      payload: { request_id: "m-3", tenant: "acme-prod", title: "    \t  ", severity: "S2" },
      expectContractOk: false,
      expectCode: "ERR_EMPTY_TITLE",
    },
    {
      name: "4. Unicode NFC + CJK + RTL",
      payload: {
        request_id: "m-4",
        tenant: "acme-prod",
        title: "Cafe\u0301 東京 \u202eمرحبا",
        severity: "S1",
      },
      expectContractOk: true,
      expectCode: "OK_VERIFIED",
    },
    {
      name: "5. 10x Oversized (40,960 chars)",
      payload: {
        request_id: "m-5",
        tenant: "acme-prod",
        title: "A".repeat(MAX_PAYLOAD_CHARS * 10),
        severity: "S3",
      },
      expectContractOk: false,
      expectCode: "ERR_PAYLOAD_TOO_LARGE",
    },
    {
      name: "6. Duplicate Retry Storm (m-1 again)",
      payload: { request_id: "m-1", tenant: "acme-prod", title: "Deploy v2.4", severity: "S2" },
      expectContractOk: false,
      expectCode: "ERR_DUPLICATE_RETRY",
    },
    {
      name: "7. Missing Tenant (Unauthorized)",
      payload: { request_id: "m-7", tenant: "", title: "Hotfix", severity: "S1" },
      expectContractOk: false,
      expectCode: "ERR_UNAUTHORIZED",
    },
    {
      name: "8. Cross-Tenant Write (Wrong Tenant)",
      payload: { request_id: "m-8", tenant: "evil-corp", title: "Flip flag", severity: "S1" },
      expectContractOk: false,
      expectCode: "ERR_WRONG_TENANT",
    },
    {
      name: "9. Invalid Severity Enum",
      payload: { request_id: "m-9", tenant: "acme-prod", title: "Valid", severity: "P0-BAD" },
      expectContractOk: false,
      expectCode: "ERR_INVALID_SEVERITY",
    },
    {
      name: "10. Missing Title Type (Number)",
      payload: { request_id: "m-10", tenant: "acme-prod", title: 12345, severity: "S3" },
      expectContractOk: false,
      expectCode: "ERR_NULL_TITLE",
    },
  ];

  for (const tc of matrixCases) {
    const bRes = processUnconstrained(tc.payload);
    const cRes = processContract(tc.payload, localSeen);

    // Baseline is only genuinely safe on case 1 (and even there it leaks debug_path!)
    const bFailed =
      !bRes.ok ||
      (tc.expectContractOk === false && bRes.ok === true) ||
      (bRes.defects_triggered && bRes.defects_triggered.length > 1);
    if (!bFailed) baseSafeCount += 1;

    const cPassed = cRes.ok === tc.expectContractOk && cRes.code === tc.expectCode;
    if (cPassed) contractSafeCount += 1;

    const bSummary = !bRes.ok
      ? "[CRASH] Unhandled TypeError + stack leak"
      : tc.expectContractOk === false
      ? `[CORRUPTION] Falsely approved (${bRes.defects_triggered[0]})`
      : "[WARN] Approved but leaked /Users/internal path";

    const cSummary = cPassed
      ? `[PASS] ${cRes.code} (${cRes.status})`
      : `[FAIL] Unexpected ${cRes.code}`;

    rows.push(`
      <tr>
        <td>${escapeHtml(tc.name)}</td>
        <td><span class="badge ${bFailed ? "badge--fail" : "badge--warn"}">${escapeHtml(
      bSummary
    )}</span></td>
        <td><span class="badge ${cPassed ? "badge--pass" : "badge--fail"}">${escapeHtml(
      cSummary
    )}</span></td>
      </tr>
    `);
  }

  tbody.innerHTML = rows.join("");
  const summaryEl = document.getElementById("matrix-summary-pill");
  if (summaryEl) {
    summaryEl.textContent = `Matrix Score: Unconstrained ${baseSafeCount}/10 safe vs. CLAUDE.md Contract ${contractSafeCount}/10 verified`;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const presetSelect = document.getElementById("preset-select");
  const reqIdInput = document.getElementById("input-req-id");
  const tenantInput = document.getElementById("input-tenant");
  const titleInput = document.getElementById("input-title");
  const sevInput = document.getElementById("input-severity");
  const runBtn = document.getElementById("btn-run-payload");
  const matrixBtn = document.getElementById("btn-run-matrix");
  const resetBtn = document.getElementById("btn-reset-idempotency");
  const themeBtn = document.getElementById("btn-toggle-theme");

  function loadPreset(key) {
    const p = PRESETS[key];
    if (!p) return;
    reqIdInput.value = p.request_id || "";
    tenantInput.value = p.tenant || "";
    titleInput.value =
      typeof p.title === "string" && p.title.length > 200
        ? `[10x Oversized String: ${p.title.length} chars]`
        : p.title || "";
    titleInput.dataset.PresetKey = key;
    sevInput.value = p.severity || "S3";

    const payloadToRun = p.isNullPayload
      ? null
      : {
          request_id: p.request_id,
          tenant: p.tenant,
          title: p.title,
          severity: p.severity,
        };
    updateUIWithPayload(payloadToRun, p.label);
  }

  presetSelect.addEventListener("change", (e) => {
    loadPreset(e.target.value);
  });

  document.querySelectorAll("[data-preset]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const k = btn.getAttribute("data-preset");
      presetSelect.value = k;
      loadPreset(k);
    });
  });

  runBtn.addEventListener("click", () => {
    const activeKey = titleInput.dataset.PresetKey;
    const p = PRESETS[activeKey];
    let actualTitle = titleInput.value;
    if (p && p.isNullPayload && titleInput.value === "") {
      updateUIWithPayload(null, "Custom Null Payload");
      return;
    }
    if (p && activeKey === "oversized" && titleInput.value.startsWith("[10x Oversized")) {
      actualTitle = p.title;
    }
    updateUIWithPayload(
      {
        request_id: reqIdInput.value,
        tenant: tenantInput.value,
        title: actualTitle,
        severity: sevInput.value,
      },
      `Custom Payload (${reqIdInput.value || "no-id"})`
    );
  });

  titleInput.addEventListener("input", () => {
    titleInput.dataset.PresetKey = "";
  });

  resetBtn.addEventListener("click", () => {
    seenContractIds.clear();
    unconstrainedQueueCount = 0;
    contractQueueCount = 0;
    loadPreset(presetSelect.value);
  });

  matrixBtn.addEventListener("click", () => {
    runAllMatrixSuite();
  });

  themeBtn.addEventListener("click", () => {
    const root = document.documentElement;
    const next = root.getAttribute("data-theme") === "light" ? "dark" : "light";
    root.setAttribute("data-theme", next);
    themeBtn.textContent = `Theme: ${next.toUpperCase()} (§25.4 Token Map)`;
  });

  // Initial load: run happy path + populate full 10-case matrix
  loadPreset("happy");
  runAllMatrixSuite();
});
