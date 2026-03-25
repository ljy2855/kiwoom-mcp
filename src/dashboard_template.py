"""HTML template for the Kiwoom dashboard."""

DASHBOARD_HTML = r"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Kiwoom Trading Dashboard</title>
  <style>
    :root {
      --bg: #f3efe6;
      --panel: rgba(255, 253, 248, 0.88);
      --panel-strong: rgba(255, 255, 255, 0.95);
      --line: rgba(33, 38, 45, 0.10);
      --ink: #18212f;
      --muted: #5f6979;
      --positive: #0c8f62;
      --negative: #c04f39;
      --warning: #b9841f;
      --accent: #153552;
      --accent-soft: rgba(21, 53, 82, 0.08);
      --shadow: 0 20px 60px rgba(24, 33, 47, 0.10);
      --radius-xl: 28px;
      --radius-lg: 20px;
      --radius-md: 14px;
      --radius-sm: 10px;
      --display-font: "Iowan Old Style", "Palatino Linotype", "Book Antiqua", Palatino, serif;
      --body-font: "Avenir Next", "Segoe UI Variable", "Noto Sans KR", sans-serif;
      --mono-font: "IBM Plex Mono", "SFMono-Regular", Consolas, monospace;
    }

    * {
      box-sizing: border-box;
    }

    html {
      scroll-behavior: smooth;
    }

    body {
      margin: 0;
      min-height: 100vh;
      font-family: var(--body-font);
      color: var(--ink);
      background:
        radial-gradient(circle at top left, rgba(222, 201, 149, 0.36), transparent 28%),
        radial-gradient(circle at top right, rgba(180, 214, 224, 0.34), transparent 24%),
        linear-gradient(180deg, #f7f3ea 0%, #f1ede5 52%, #edf2f0 100%);
    }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image:
        linear-gradient(rgba(24, 33, 47, 0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(24, 33, 47, 0.025) 1px, transparent 1px);
      background-size: 32px 32px;
      mask-image: radial-gradient(circle at center, black 48%, transparent 86%);
    }

    .shell {
      width: min(1320px, calc(100vw - 28px));
      margin: 0 auto;
      padding: 24px 0 56px;
    }

    .hero,
    .panel,
    .toolbar {
      background: var(--panel);
      backdrop-filter: blur(18px);
      border: 1px solid var(--line);
      box-shadow: var(--shadow);
      border-radius: var(--radius-xl);
    }

    .hero {
      display: grid;
      grid-template-columns: 1.4fr 1fr;
      gap: 22px;
      padding: 26px;
      margin-bottom: 20px;
    }

    .eyebrow {
      margin: 0 0 12px;
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.24em;
      text-transform: uppercase;
    }

    h1 {
      margin: 0;
      font-family: var(--display-font);
      font-size: clamp(2.35rem, 5.2vw, 4.2rem);
      line-height: 0.95;
      letter-spacing: -0.04em;
    }

    .hero-copy {
      margin: 16px 0 0;
      max-width: 54ch;
      color: var(--muted);
      line-height: 1.65;
      font-size: 1rem;
    }

    .identity-strip {
      margin-top: 20px;
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      align-items: center;
    }

    .pill,
    .meta-pill,
    .status-pill {
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      font-size: 0.92rem;
      border: 1px solid rgba(24, 33, 47, 0.08);
      background: rgba(255, 255, 255, 0.72);
    }

    .pill strong,
    .meta-pill strong {
      font-weight: 700;
    }

    .pill.env-mock {
      background: rgba(185, 132, 31, 0.10);
      color: #8a6116;
    }

    .pill.env-live {
      background: rgba(12, 143, 98, 0.10);
      color: var(--positive);
    }

    .hero-side {
      display: grid;
      gap: 12px;
      align-content: start;
    }

    .side-box {
      padding: 16px 18px;
      border-radius: var(--radius-lg);
      border: 1px solid rgba(24, 33, 47, 0.08);
      background: rgba(255, 255, 255, 0.62);
    }

    .side-box .label {
      display: block;
      margin-bottom: 6px;
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }

    .side-box .value {
      font-size: 0.98rem;
      line-height: 1.5;
      word-break: break-word;
    }

    .toolbar {
      margin-bottom: 20px;
      padding: 16px 18px;
    }

    .toolbar form {
      display: grid;
      grid-template-columns: repeat(4, minmax(0, auto));
      gap: 12px;
      align-items: end;
    }

    .field {
      display: grid;
      gap: 8px;
      min-width: 150px;
    }

    .field label,
    .toggle {
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }

    .field input[type="text"] {
      width: 100%;
      padding: 11px 12px;
      border-radius: var(--radius-sm);
      border: 1px solid rgba(24, 33, 47, 0.12);
      background: rgba(255, 255, 255, 0.85);
      font: inherit;
      color: var(--ink);
    }

    .toggle-wrap {
      display: flex;
      align-items: center;
      min-height: 46px;
      gap: 10px;
      padding: 0 6px;
    }

    .toggle-wrap input {
      width: 18px;
      height: 18px;
      accent-color: var(--accent);
    }

    .toolbar button {
      height: 46px;
      border: 0;
      border-radius: 999px;
      padding: 0 18px;
      font: inherit;
      font-weight: 700;
      color: white;
      background: linear-gradient(135deg, #173552 0%, #275174 100%);
      box-shadow: 0 12px 26px rgba(23, 53, 82, 0.25);
      cursor: pointer;
    }

    .toolbar-note {
      margin-top: 10px;
      color: var(--muted);
      font-size: 0.92rem;
    }

    .error-banner {
      margin-bottom: 16px;
      padding: 14px 16px;
      border-radius: var(--radius-lg);
      border: 1px solid rgba(192, 79, 57, 0.16);
      background: rgba(192, 79, 57, 0.10);
      color: var(--negative);
    }

    .overview-grid,
    .content-grid {
      display: grid;
      gap: 18px;
      margin-bottom: 20px;
    }

    .overview-grid {
      grid-template-columns: 1.55fr 1fr;
    }

    .content-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .panel {
      padding: 18px;
    }

    .span-2 {
      grid-column: span 2;
    }

    .span-3 {
      grid-column: span 3;
    }

    .section-head {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 12px;
      margin-bottom: 16px;
    }

    .section-head h2,
    .section-head h3 {
      margin: 0;
      font-family: var(--display-font);
      letter-spacing: -0.03em;
    }

    .section-head h2 {
      font-size: 2rem;
      line-height: 1;
    }

    .section-head h3 {
      font-size: 1.45rem;
      line-height: 1;
    }

    .section-kicker {
      margin: 0 0 6px;
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
    }

    .section-subtitle {
      margin: 0;
      color: var(--muted);
      font-size: 0.95rem;
      line-height: 1.5;
    }

    .metric-grid,
    .mini-metric-grid {
      display: grid;
      gap: 12px;
    }

    .metric-grid {
      grid-template-columns: repeat(3, minmax(0, 1fr));
    }

    .mini-metric-grid {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }

    .metric-card,
    .mini-metric,
    .focus-item,
    .notice {
      border: 1px solid rgba(24, 33, 47, 0.08);
      border-radius: var(--radius-lg);
      background: rgba(255, 255, 255, 0.72);
    }

    .metric-card {
      padding: 16px;
      min-height: 122px;
      display: grid;
      align-content: start;
      gap: 10px;
    }

    .metric-card .label,
    .mini-metric .label,
    .focus-item .label {
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }

    .metric-card .value {
      font-family: var(--display-font);
      font-size: clamp(1.7rem, 3vw, 2.4rem);
      line-height: 1;
      letter-spacing: -0.04em;
    }

    .mini-metric {
      padding: 14px;
      display: grid;
      gap: 8px;
    }

    .mini-metric .value {
      font-size: 1.05rem;
      font-weight: 700;
    }

    .focus-list {
      display: grid;
      gap: 10px;
      margin-bottom: 12px;
    }

    .focus-item {
      padding: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 12px;
    }

    .focus-item strong {
      font-size: 1.1rem;
    }

    .notice {
      padding: 14px;
      line-height: 1.6;
    }

    .notice strong {
      display: block;
      margin-bottom: 6px;
    }

    .notice.ok {
      background: rgba(12, 143, 98, 0.08);
      color: var(--positive);
    }

    .notice.warn {
      background: rgba(185, 132, 31, 0.10);
      color: #8a6116;
    }

    .notice.error {
      background: rgba(192, 79, 57, 0.10);
      color: var(--negative);
    }

    .notice ul {
      margin: 0;
      padding-left: 18px;
    }

    .table-meta {
      display: flex;
      justify-content: space-between;
      gap: 12px;
      align-items: center;
      margin-bottom: 10px;
      color: var(--muted);
      font-size: 0.92rem;
    }

    .table-wrap {
      overflow: auto;
      max-height: 420px;
      border-radius: var(--radius-md);
      border: 1px solid rgba(24, 33, 47, 0.06);
      background: rgba(255, 255, 255, 0.64);
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.94rem;
    }

    th,
    td {
      padding: 10px 12px;
      border-bottom: 1px solid rgba(24, 33, 47, 0.08);
      text-align: left;
      vertical-align: top;
      white-space: nowrap;
    }

    th {
      position: sticky;
      top: 0;
      z-index: 1;
      background: rgba(249, 246, 239, 0.94);
      color: var(--muted);
      font-size: 12px;
      letter-spacing: 0.10em;
      text-transform: uppercase;
    }

    td code,
    .mono {
      font-family: var(--mono-font);
      font-size: 0.88rem;
    }

    .tone-positive {
      color: var(--positive);
      font-weight: 700;
    }

    .tone-negative {
      color: var(--negative);
      font-weight: 700;
    }

    .tone-neutral {
      color: inherit;
    }

    .empty-state {
      min-height: 148px;
      display: grid;
      place-items: center;
      text-align: center;
      padding: 18px;
      border-radius: var(--radius-lg);
      border: 1px dashed rgba(24, 33, 47, 0.14);
      background: rgba(255, 255, 255, 0.45);
      color: var(--muted);
      line-height: 1.6;
    }

    .activity-grid {
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 14px;
    }

    .subpanel {
      border: 1px solid rgba(24, 33, 47, 0.08);
      border-radius: var(--radius-lg);
      background: rgba(255, 255, 255, 0.56);
      padding: 14px;
    }

    .subpanel-header {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 12px;
      margin-bottom: 10px;
    }

    .subpanel-header h4 {
      margin: 0;
      font-size: 1.02rem;
    }

    .diagnostics {
      border: 1px solid var(--line);
      border-radius: var(--radius-xl);
      background: rgba(255, 255, 255, 0.55);
      box-shadow: var(--shadow);
      overflow: hidden;
    }

    .diagnostics summary {
      cursor: pointer;
      padding: 16px 18px;
      font-weight: 700;
      list-style: none;
    }

    .diagnostics summary::-webkit-details-marker {
      display: none;
    }

    .diagnostics-body {
      padding: 0 18px 18px;
      display: grid;
      gap: 14px;
    }

    .source-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 12px;
    }

    .source-card {
      padding: 14px;
      border-radius: var(--radius-lg);
      border: 1px solid rgba(24, 33, 47, 0.08);
      background: rgba(255, 255, 255, 0.66);
    }

    .source-card header {
      display: flex;
      justify-content: space-between;
      gap: 10px;
      align-items: center;
      margin-bottom: 8px;
    }

    .source-title {
      font-weight: 700;
      font-size: 0.96rem;
    }

    .status-pill.ok {
      color: var(--positive);
      background: rgba(12, 143, 98, 0.10);
    }

    .status-pill.empty {
      color: #8a6116;
      background: rgba(185, 132, 31, 0.10);
    }

    .status-pill.unsupported,
    .status-pill.error {
      color: var(--negative);
      background: rgba(192, 79, 57, 0.10);
    }

    .source-card .meta {
      color: var(--muted);
      font-size: 0.9rem;
      line-height: 1.55;
    }

    .hidden-grid {
      display: grid;
      gap: 14px;
    }

    @media (max-width: 1120px) {
      .hero,
      .overview-grid,
      .content-grid,
      .activity-grid {
        grid-template-columns: 1fr;
      }

      .span-2,
      .span-3 {
        grid-column: span 1;
      }

      .metric-grid,
      .mini-metric-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }

      .toolbar form {
        grid-template-columns: repeat(2, minmax(0, 1fr));
      }
    }

    @media (max-width: 680px) {
      .shell {
        width: min(100vw - 16px, 100%);
        padding-top: 16px;
      }

      .hero,
      .toolbar,
      .panel,
      .diagnostics {
        border-radius: 22px;
      }

      .metric-grid,
      .mini-metric-grid,
      .toolbar form {
        grid-template-columns: 1fr;
      }

      th,
      td {
        padding: 9px 10px;
      }
    }
  </style>
</head>
<body>
  <main class="shell">
    <section class="hero">
      <div>
        <p class="eyebrow">Kiwoom OpenAPI Dashboard</p>
        <h1>Trading Dashboard</h1>
        <p class="hero-copy">계좌 상태, 보유 종목, 활성 주문, 최근 거래 흐름만 빠르게 읽을 수 있도록 화면을 줄였습니다. 빈 섹션과 진단 정보는 아래 접힌 패널에서 확인할 수 있습니다.</p>
        <div class="identity-strip">
          <span class="pill"><strong id="account-name">-</strong></span>
          <span class="meta-pill"><strong id="branch-name">-</strong></span>
          <span class="pill env-mock" id="env-pill"><strong id="env-label">-</strong></span>
        </div>
      </div>
      <div class="hero-side">
        <div class="side-box">
          <span class="label">Last Refresh</span>
          <div class="value" id="generated-at">-</div>
        </div>
        <div class="side-box">
          <span class="label">Base URL</span>
          <div class="value mono" id="base-url">-</div>
        </div>
        <div class="side-box">
          <span class="label">View Rule</span>
          <div class="value">핵심 섹션만 기본 노출, 빈 조회와 상세 진단은 접어두기</div>
        </div>
      </div>
    </section>

    <section class="toolbar">
      <form id="filter-form">
        <div class="field">
          <label for="start-date">Start Date</label>
          <input id="start-date" name="start_date" type="text" inputmode="numeric" pattern="\d{8}">
        </div>
        <div class="field">
          <label for="end-date">End Date</label>
          <input id="end-date" name="end_date" type="text" inputmode="numeric" pattern="\d{8}">
        </div>
        <div class="toggle-wrap">
          <input id="show-empty" type="checkbox">
          <label class="toggle" for="show-empty">빈 섹션 표시</label>
        </div>
        <button type="submit">새로 조회</button>
      </form>
      <div class="toolbar-note">YYYYMMDD 형식으로 기간을 바꾸면 기간 손익, 실현손익, 체결 이력을 다시 불러옵니다.</div>
    </section>

    <div id="page-error"></div>

    <section class="overview-grid">
      <section class="panel">
        <div class="section-head">
          <div>
            <p class="section-kicker">Overview</p>
            <h2>핵심 요약</h2>
          </div>
          <p class="section-subtitle" id="summary-note">-</p>
        </div>
        <div id="summary-grid" class="metric-grid"></div>
      </section>

      <aside class="panel">
        <div class="section-head">
          <div>
            <p class="section-kicker">Focus</p>
            <h3>지금 볼 것</h3>
          </div>
        </div>
        <div id="focus-grid" class="focus-list"></div>
        <div id="attention-box"></div>
      </aside>
    </section>

    <section class="content-grid">
      <section class="panel span-2">
        <div class="section-head">
          <div>
            <p class="section-kicker">Positions</p>
            <h3>보유 종목</h3>
          </div>
          <p class="section-subtitle">현재 포지션만 유지</p>
        </div>
        <div id="holdings-root"></div>
      </section>

      <section class="panel">
        <div class="section-head">
          <div>
            <p class="section-kicker">Orders</p>
            <h3>활성 주문</h3>
          </div>
          <p class="section-subtitle">미체결 또는 진행 중 주문</p>
        </div>
        <div id="orders-root"></div>
      </section>

      <section class="panel span-3">
        <div class="section-head">
          <div>
            <p class="section-kicker">Performance</p>
            <h3>기간 성과</h3>
          </div>
          <p class="section-subtitle" id="performance-note">-</p>
        </div>
        <div id="performance-root"></div>
      </section>
    </section>

    <section class="panel">
      <div class="section-head">
        <div>
          <p class="section-kicker">Recent Activity</p>
          <h3>최근 거래 이력</h3>
        </div>
        <p class="section-subtitle">체결과 실현손익만 분리해서 표시</p>
      </div>
      <div id="activity-root"></div>
    </section>

    <details class="diagnostics" id="diagnostics-fold">
      <summary id="diagnostics-summary">숨겨진 섹션과 데이터 상태</summary>
      <div class="diagnostics-body">
        <div id="source-root"></div>
        <div id="hidden-root" class="hidden-grid"></div>
      </div>
    </details>
  </main>

  <script>
    const initialConfig = __INITIAL_CONFIG__;
    let currentPayload = null;

    const pageErrorRoot = document.getElementById("page-error");
    const startInput = document.getElementById("start-date");
    const endInput = document.getElementById("end-date");
    const showEmptyInput = document.getElementById("show-empty");
    const summaryRoot = document.getElementById("summary-grid");
    const focusRoot = document.getElementById("focus-grid");
    const attentionRoot = document.getElementById("attention-box");
    const holdingsRoot = document.getElementById("holdings-root");
    const ordersRoot = document.getElementById("orders-root");
    const performanceRoot = document.getElementById("performance-root");
    const activityRoot = document.getElementById("activity-root");
    const sourceRoot = document.getElementById("source-root");
    const hiddenRoot = document.getElementById("hidden-root");
    const diagnosticsFold = document.getElementById("diagnostics-fold");
    const diagnosticsSummary = document.getElementById("diagnostics-summary");

    startInput.value = initialConfig.start_date;
    endInput.value = initialConfig.end_date;

    function escapeHtml(value) {
      return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
    }

    function hasValue(value) {
      return value !== null && value !== undefined && value !== "";
    }

    function toNumber(value) {
      if (!hasValue(value)) {
        return null;
      }
      const text = String(value).replace(/,/g, "").trim();
      if (!text) {
        return null;
      }
      const parsed = Number(text);
      return Number.isFinite(parsed) ? parsed : null;
    }

    function normalizeCode(value) {
      const text = String(value ?? "");
      return /^A\d{6}$/.test(text) ? text.slice(1) : text;
    }

    function toneForValue(value) {
      const parsed = toNumber(value);
      if (parsed === null) {
        return "tone-neutral";
      }
      if (parsed > 0) {
        return "tone-positive";
      }
      if (parsed < 0) {
        return "tone-negative";
      }
      return "tone-neutral";
    }

    function formatMetric(value, kind) {
      const parsed = toNumber(value);
      if (parsed === null) {
        return hasValue(value) ? String(value) : "N/A";
      }
      if (kind === "currency") {
        return new Intl.NumberFormat("ko-KR").format(parsed) + "원";
      }
      if (kind === "ratio") {
        return new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 2 }).format(parsed) + "%";
      }
      return new Intl.NumberFormat("ko-KR").format(parsed);
    }

    function formatCell(key, value) {
      if (!hasValue(value)) {
        return "—";
      }

      if (key.includes("date") && String(value).length === 8 && /^\d+$/.test(String(value))) {
        return `${String(value).slice(0, 4)}-${String(value).slice(4, 6)}-${String(value).slice(6, 8)}`;
      }

      if (key.includes("time") && /^\d{4,6}$/.test(String(value))) {
        const padded = String(value).padStart(6, "0");
        return `${padded.slice(0, 2)}:${padded.slice(2, 4)}:${padded.slice(4, 6)}`;
      }

      if (key.includes("rate")) {
        return `<span class="${toneForValue(value)}">${escapeHtml(formatMetric(value, "ratio"))}</span>`;
      }

      if (["quantity", "order_qty", "filled_qty"].includes(key)) {
        return escapeHtml(formatMetric(value, "number"));
      }

      if (key.includes("amount") || key.includes("price") || key.includes("profit") || key === "deposit" || key === "estimated_assets" || key === "evaluation_amount") {
        return `<span class="${toneForValue(value)}">${escapeHtml(formatMetric(value, "currency"))}</span>`;
      }

      if (key.endsWith("_no")) {
        return `<code>${escapeHtml(value)}</code>`;
      }

      if (key.endsWith("_code")) {
        return `<code>${escapeHtml(normalizeCode(value))}</code>`;
      }

      return escapeHtml(value);
    }

    function humanizeKey(key) {
      return key.replaceAll("_", " ");
    }

    function chooseColumns(table) {
      const rows = table.rows || [];
      const visible = (table.columns || []).filter((column) =>
        rows.some((row) => hasValue(row[column.key]))
      );

      if (visible.length > 0) {
        return {
          columns: visible,
          rows,
        };
      }

      const rawRows = table.raw_rows || [];
      const firstRow = rawRows[0] || {};
      const rawColumns = Object.keys(firstRow)
        .filter((key) => key !== "return_code" && key !== "return_msg")
        .slice(0, 8)
        .map((key) => ({ key, label: humanizeKey(key) }));

      return {
        columns: rawColumns,
        rows: rawRows,
      };
    }

    function buildEmpty(message) {
      return `<div class="empty-state">${escapeHtml(message)}</div>`;
    }

    function buildTable(table, options = {}) {
      const rowCount = table.row_count || 0;
      if (rowCount === 0) {
        return buildEmpty(table.empty_message);
      }

      const chosen = chooseColumns(table);
      const columns = chosen.columns;
      const rows = chosen.rows || [];

      if (columns.length === 0) {
        return buildEmpty(table.empty_message);
      }

      const limit = options.limit || rows.length;
      const visibleRows = rows.slice(0, limit);
      const metaNote = rowCount > visibleRows.length
        ? `총 ${rowCount}건 중 ${visibleRows.length}건 표시`
        : `총 ${rowCount}건`;

      return `
        <div class="table-meta">
          <span>${escapeHtml(metaNote)}</span>
          ${options.note ? `<span>${escapeHtml(options.note)}</span>` : ""}
        </div>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>${columns.map((column) => `<th>${escapeHtml(column.label)}</th>`).join("")}</tr>
            </thead>
            <tbody>
              ${visibleRows.map((row) => `
                <tr>
                  ${columns.map((column) => `<td>${formatCell(column.key, row[column.key])}</td>`).join("")}
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      `;
    }

    function buildSubpanel(title, subtitle, table, options = {}) {
      return `
        <section class="subpanel">
          <div class="subpanel-header">
            <h4>${escapeHtml(title)}</h4>
            <span class="section-subtitle">${escapeHtml(subtitle)}</span>
          </div>
          ${buildTable(table, options)}
        </section>
      `;
    }

    function renderSummary(cards) {
      summaryRoot.innerHTML = cards.map((card) => `
        <article class="metric-card ${escapeHtml(card.tone || "neutral")}">
          <div class="label">${escapeHtml(card.label)}</div>
          <div class="value ${escapeHtml(toneForValue(card.value))}">${escapeHtml(formatMetric(card.value, card.kind))}</div>
        </article>
      `).join("");
    }

    function renderFocus(payload) {
      const overview = payload.overview || {};
      const items = [
        ["보유 종목 수", overview.holdings_count || 0],
        ["활성 주문 수", overview.active_orders_count || 0],
        ["최근 체결 건수", overview.executions_count || 0],
        ["숨은 진단 수", (overview.issues_count || 0) + (overview.empty_sources_count || 0)],
      ];

      focusRoot.innerHTML = items.map(([label, value]) => `
        <article class="focus-item">
          <span class="label">${escapeHtml(label)}</span>
          <strong>${escapeHtml(String(value))}</strong>
        </article>
      `).join("");
    }

    function renderAttention(payload) {
      const issues = (payload.sources || []).filter((source) => source.status === "error" || source.status === "unsupported");
      const empties = (payload.sources || []).filter((source) => source.status === "empty");

      if (issues.length > 0) {
        attentionRoot.innerHTML = `
          <article class="notice error">
            <strong>확인 필요한 항목</strong>
            <ul>${issues.map((source) => `<li>${escapeHtml(source.title)}: ${escapeHtml(source.message || source.status_label)}</li>`).join("")}</ul>
          </article>
        `;
        return;
      }

      if (empties.length > 0) {
        attentionRoot.innerHTML = `
          <article class="notice warn">
            <strong>현재 비어 있는 조회</strong>
            <div>${escapeHtml(empties.map((source) => source.title).join(", "))}</div>
          </article>
        `;
        return;
      }

      attentionRoot.innerHTML = `
        <article class="notice ok">
          <strong>핵심 조회 정상</strong>
          <div>계좌 요약과 주요 섹션이 모두 정상 응답입니다.</div>
        </article>
      `;
    }

    function renderHoldings(payload) {
      const table = payload.tables.holdings;
      holdingsRoot.innerHTML = buildTable(table, { limit: 10, note: "손익 기준 컬럼 우선 표시" });
    }

    function renderOrders(payload) {
      const unexecuted = payload.tables.unexecuted_orders;
      const orderStatus = payload.tables.order_status;
      const orderSource = (payload.sources || []).find((source) => source.title === "주문 체결 현황");

      if ((unexecuted.row_count || 0) > 0) {
        ordersRoot.innerHTML = buildTable(unexecuted, { limit: 8, note: "미체결 주문 기준" });
        return;
      }

      if ((orderStatus.row_count || 0) > 0) {
        ordersRoot.innerHTML = buildTable(orderStatus, { limit: 8, note: "주문 진행 상태 기준" });
        return;
      }

      const sourceMessage = orderSource && (orderSource.status === "error" || orderSource.status === "unsupported")
        ? orderSource.message
        : "현재 활성 주문이 없습니다.";
      ordersRoot.innerHTML = buildEmpty(sourceMessage || "현재 활성 주문이 없습니다.");
    }

    function renderPerformance(payload) {
      const performance = (payload.performance || []).filter((item) => hasValue(item.value));
      const filter = payload.filters || {};
      document.getElementById("performance-note").textContent = `${filter.start_date} ~ ${filter.end_date}`;

      if (performance.length === 0) {
        performanceRoot.innerHTML = buildEmpty("기간 성과 데이터가 없습니다.");
        return;
      }

      performanceRoot.innerHTML = `
        <div class="mini-metric-grid">
          ${performance.map((item) => `
            <article class="mini-metric">
              <div class="label">${escapeHtml(item.label)}</div>
              <div class="value ${escapeHtml(toneForValue(item.value))}">${escapeHtml(formatMetric(item.value, item.kind))}</div>
            </article>
          `).join("")}
        </div>
      `;
    }

    function renderActivity(payload, showEmpty) {
      const blocks = [];
      const executions = payload.tables.executions;
      const realized = payload.tables.realized_profit;

      if ((executions.row_count || 0) > 0 || showEmpty) {
        blocks.push(buildSubpanel("체결 이력", "최근 체결", executions, { limit: 6 }));
      }

      if ((realized.row_count || 0) > 0 || showEmpty) {
        blocks.push(buildSubpanel("실현손익", "기간 기준", realized, { limit: 6 }));
      }

      if (blocks.length === 0) {
        activityRoot.innerHTML = buildEmpty("선택 기간에 표시할 체결 이력이나 실현손익이 없습니다.");
        return;
      }

      activityRoot.innerHTML = `<div class="activity-grid">${blocks.join("")}</div>`;
    }

    function renderDiagnostics(payload, showEmpty) {
      const sources = payload.sources || [];
      const issueSources = sources.filter((source) => source.status !== "ok");
      const hiddenBlocks = [];

      const hiddenTables = [
        ["주문 체결 현황 상세", payload.tables.order_status, 6],
        ["기간 수익률 원본", payload.tables.daily_profit_detail, 6],
      ];

      for (const [title, table, limit] of hiddenTables) {
        if ((table.row_count || 0) > 0 || showEmpty) {
          hiddenBlocks.push(buildSubpanel(title, table.row_count ? "상세 데이터" : "빈 섹션", table, { limit }));
        }
      }

      const sourceBlocks = issueSources.length > 0 || showEmpty
        ? `
          <div class="source-grid">
            ${(showEmpty ? sources : issueSources).map((source) => `
              <article class="source-card">
                <header>
                  <div class="source-title">${escapeHtml(source.title)}</div>
                  <span class="status-pill ${escapeHtml(source.status)}">${escapeHtml(source.status_label)}</span>
                </header>
                <div class="meta">${escapeHtml(source.api_id || "-")} · ${escapeHtml(String(source.record_count))}건<br>${escapeHtml(source.message || "메시지 없음")}</div>
              </article>
            `).join("")}
          </div>
        `
        : "";

      if (!sourceBlocks && hiddenBlocks.length === 0) {
        diagnosticsFold.hidden = true;
        return;
      }

      diagnosticsFold.hidden = false;
      diagnosticsFold.open = issueSources.length > 0;
      diagnosticsSummary.textContent = `숨겨진 섹션 ${hiddenBlocks.length}개 · 데이터 상태 ${showEmpty ? sources.length : issueSources.length}건`;
      sourceRoot.innerHTML = sourceBlocks;
      hiddenRoot.innerHTML = hiddenBlocks.join("");
    }

    function renderDashboard(payload) {
      currentPayload = payload;
      const showEmpty = showEmptyInput.checked;

      document.getElementById("account-name").textContent = payload.identity.account_name;
      document.getElementById("branch-name").textContent = payload.identity.branch_name;
      document.getElementById("env-label").textContent = payload.environment.label;
      document.getElementById("generated-at").textContent = new Date(payload.generated_at).toLocaleString("ko-KR");
      document.getElementById("base-url").textContent = payload.environment.base_url;
      document.getElementById("summary-note").textContent = `${payload.filters.start_date} ~ ${payload.filters.end_date}`;

      const envPill = document.getElementById("env-pill");
      envPill.className = `pill ${payload.environment.mode === "mock" ? "env-mock" : "env-live"}`;

      renderSummary(payload.summary || []);
      renderFocus(payload);
      renderAttention(payload);
      renderHoldings(payload);
      renderOrders(payload);
      renderPerformance(payload);
      renderActivity(payload, showEmpty);
      renderDiagnostics(payload, showEmpty);
    }

    async function loadDashboard() {
      pageErrorRoot.innerHTML = "";
      const params = new URLSearchParams({
        start_date: startInput.value,
        end_date: endInput.value,
      });

      try {
        const response = await fetch(`/api/dashboard?${params.toString()}`);
        const payload = await response.json();

        if (!response.ok) {
          throw new Error(payload.error || "Dashboard request failed");
        }

        renderDashboard(payload);
      } catch (error) {
        pageErrorRoot.innerHTML = `<div class="error-banner">${escapeHtml(error.message || String(error))}</div>`;
      }
    }

    document.getElementById("filter-form").addEventListener("submit", (event) => {
      event.preventDefault();
      loadDashboard();
    });

    showEmptyInput.addEventListener("change", () => {
      if (currentPayload) {
        renderDashboard(currentPayload);
      }
    });

    loadDashboard();
  </script>
</body>
</html>
"""


__all__ = ["DASHBOARD_HTML"]
