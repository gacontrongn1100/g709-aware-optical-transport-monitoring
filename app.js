const DATA_FILES = {
  channels: "/data/processed/channel_health_analysis.csv",
  frequencies: "/data/processed/frequency_health_analysis.csv",
  devices: "/data/processed/device_health_analysis.csv",
  alerts: "/data/processed/high_risk_recommendations.csv",
  ber: "/data/processed/pre_fec_ber_kpi.csv",
  power: "/data/processed/och_power_kpi.csv",
  edfa: "/data/processed/edfa_kpi.csv",
};

const state = {
  data: {},
  view: "overview",
  query: "",
  deviceFilter: "All",
  alertFilter: "All",
  analytics: "ber",
};

function parseCSV(text) {
  const rows = [];
  let row = [];
  let field = "";
  let quoted = false;
  for (let i = 0; i < text.length; i += 1) {
    const char = text[i];
    if (quoted) {
      if (char === '"' && text[i + 1] === '"') { field += '"'; i += 1; }
      else if (char === '"') quoted = false;
      else field += char;
    } else if (char === '"') quoted = true;
    else if (char === ",") { row.push(field); field = ""; }
    else if (char === "\n") { row.push(field.replace(/\r$/, "")); rows.push(row); row = []; field = ""; }
    else field += char;
  }
  if (field.length || row.length) { row.push(field.replace(/\r$/, "")); rows.push(row); }
  const headers = rows.shift() || [];
  return rows.filter((values) => values.some(Boolean)).map((values) => Object.fromEntries(headers.map((header, index) => [header, values[index] ?? ""])));
}

const number = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};
const formatInt = (value) => Math.round(number(value)).toLocaleString("en-US");
const formatFloat = (value, digits = 2) => Number.isFinite(Number(value)) ? Number(value).toLocaleString("en-US", { maximumFractionDigits: digits }) : "—";
const formatSci = (value) => Number.isFinite(Number(value)) ? Number(value).toExponential(2) : "—";
const safe = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]);
const statusClass = (value) => String(value || "").toLowerCase().replace(/[^a-z0-9]/g, "");
const badge = (value) => `<span class="status-badge ${statusClass(value)}"><i class="status-pip ${statusClass(value)}"></i>${safe(value || "Unknown")}</span>`;
const countBy = (rows, key) => rows.reduce((acc, row) => { const label = row[key] || "Unknown"; acc[label] = (acc[label] || 0) + 1; return acc; }, {});
const maxBy = (rows, key) => rows.reduce((max, row) => Math.max(max, number(row[key])), 0);
const average = (rows, key) => rows.length ? rows.reduce((sum, row) => sum + number(row[key]), 0) / rows.length : 0;
const includesQuery = (row) => !state.query || Object.values(row).some((value) => String(value).toLowerCase().includes(state.query));

async function loadData() {
  const entries = await Promise.all(Object.entries(DATA_FILES).map(async ([key, url]) => {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`Unable to load ${url} (${response.status})`);
    return [key, parseCSV(await response.text())];
  }));
  state.data = Object.fromEntries(entries);
}

function metricCard(label, value, sub, icon, tone = "") {
  return `<article class="metric-card ${tone}"><div><div class="metric-label">${safe(label)}</div><div class="metric-value">${safe(value)}</div><div class="metric-sub">${safe(sub)}</div></div><div class="metric-icon"><span class="material-symbols-outlined">${icon}</span></div></article>`;
}

function renderOverview() {
  const { channels, frequencies, devices, alerts, ber, power, edfa } = state.data;
  const channelStatus = countBy(channels, "overall_status");
  const frequencyStatus = countBy(frequencies, "frequency_status");
  const deviceStatus = countBy(devices, "device_status");
  const priorities = countBy(alerts, "priority");

  document.querySelector("#metric-grid").innerHTML = [
    metricCard("Transport channels", formatInt(channels.length), `${formatInt(channelStatus.Critical)} critical · ${formatInt(channelStatus.Warning)} warning`, "settings_input_antenna", channelStatus.Critical ? "critical" : ""),
    metricCard("Frequencies", formatInt(frequencies.length), `${formatInt(frequencyStatus.Critical)} critical · ${formatInt(frequencyStatus.Warning)} warning`, "spectrum", frequencyStatus.Critical ? "critical" : ""),
    metricCard("Optical devices", formatInt(devices.length), `${formatInt(deviceStatus.Critical)} critical · ${formatInt(deviceStatus.Warning)} warning`, "router", deviceStatus.Critical ? "critical" : ""),
    metricCard("High-risk objects", formatInt(alerts.length), `${formatInt(priorities.P1)} P1 · ${formatInt(priorities.P2)} P2`, "notification_important", "warning"),
  ].join("");

  document.querySelector("#domain-map").innerHTML = `
    <div class="domain-core"><div><strong>${formatInt(alerts.length)}</strong><span>risk objects</span></div></div>
    <div class="domain-node"><span>Channels</span><strong>${formatInt(channels.length)}</strong><small>${formatInt(channelStatus.Critical)} critical</small></div>
    <div class="domain-node"><span>Frequencies</span><strong>${formatInt(frequencies.length)}</strong><small>${formatInt(frequencyStatus.Critical)} critical</small></div>
    <div class="domain-node"><span>Devices</span><strong>${formatInt(devices.length)}</strong><small>${formatInt(deviceStatus.Critical)} critical</small></div>`;

  const groups = [
    ["Channel health", channelStatus, channels.length],
    ["Frequency health", frequencyStatus, frequencies.length],
    ["Device health", deviceStatus, devices.length],
  ];
  document.querySelector("#status-bars").innerHTML = groups.map(([label, counts, total]) => `
    <div class="status-group">
      <div class="status-group-head"><span>${label}</span><span>${formatInt(total)} objects</span></div>
      <div class="stacked-bar" aria-label="${label} status distribution">
        <i class="critical" style="width:${(number(counts.Critical) / total) * 100}%"></i>
        <i class="warning" style="width:${(number(counts.Warning) / total) * 100}%"></i>
        <i class="normal" style="width:${(number(counts.Normal) / total) * 100}%"></i>
      </div>
      <div class="status-detail"><span>Critical ${formatInt(counts.Critical)}</span><span>Warning ${formatInt(counts.Warning)}</span><span>Normal ${formatInt(counts.Normal)}</span></div>
    </div>`).join("");

  const priorityRows = alerts.filter(includesQuery).sort((a, b) => number(b.risk_score) - number(a.risk_score)).slice(0, 8);
  document.querySelector("#priority-rows").innerHTML = priorityRows.map((row) => `<tr class="${row.status === "Critical" ? "critical-row" : ""}"><td>${badge(row.priority)}</td><td class="mono truncate" title="${safe(row.object_id)}">${safe(row.object_id)}</td><td>${safe(row.source)}</td><td class="mono">${formatFloat(row.risk_score)}</td><td class="truncate" title="${safe(row.issue_category)}">${safe(row.issue_category)}</td></tr>`).join("") || emptyRow(5);

  const latestEnd = [...ber, ...power, ...edfa].map((row) => row.time_end).filter(Boolean).sort().at(-1) || "Unknown";
  const earliestStart = [...ber, ...power, ...edfa].map((row) => row.time_start).filter(Boolean).sort().at(0) || "Unknown";
  document.querySelector("#dataset-window").textContent = `${earliestStart.slice(0, 10)} → ${latestEnd.slice(0, 10)}`;
  document.querySelector("#telemetry-list").innerHTML = [
    ["Maximum Pre-FEC BER P95", formatSci(maxBy(ber, "ber_p95"))],
    ["Average OCH power", `${formatFloat(average(power, "power_mean"))} dBm`],
    ["Maximum OCH power risk", formatFloat(maxBy(power, "power_risk_score"))],
    ["Average EDFA gain", `${formatFloat(average(edfa, "actual_gain_mean"))} dB`],
    ["Maximum EDFA attenuation", `${formatFloat(maxBy(edfa, "attenuation_max"))} dB`],
    ["EDFA KPI objects", formatInt(edfa.length)],
  ].map(([label, value]) => `<div class="telemetry-item"><span>${label}</span><strong>${value}</strong></div>`).join("");
}

function emptyRow(cols) { return `<tr><td colspan="${cols}" class="muted">No records match the current search or filter.</td></tr>`; }

function renderDevices() {
  const rows = state.data.devices.filter((row) => (state.deviceFilter === "All" || row.device_status === state.deviceFilter) && includesQuery(row));
  document.querySelector("#device-table").innerHTML = rows.map((row) => `<tr class="${row.device_status === "Critical" ? "critical-row" : ""}">
    <td class="mono">Device ${safe(row.device_name)}</td><td>${badge(row.device_status)}</td><td>${badge(row.priority)}</td><td class="mono">${formatFloat(row.device_risk_score)}</td><td class="mono">${formatInt(row.och_channel_count)}</td><td class="mono">${formatInt(row.edfa_count)}</td><td>${safe(row.recommended_check)}</td></tr>`).join("") || emptyRow(7);
}

function renderAlerts() {
  const rows = state.data.alerts.filter((row) => (state.alertFilter === "All" || row.priority === state.alertFilter) && includesQuery(row));
  document.querySelector("#alert-table").innerHTML = rows.map((row) => `<tr class="${row.status === "Critical" ? "critical-row" : ""}">
    <td>${badge(row.priority)}</td><td>${badge(row.status)}</td><td>${safe(row.source)}</td><td class="mono truncate" title="${safe(row.object_id)}">${safe(row.object_id)}</td><td class="mono">${formatFloat(row.risk_score)}</td><td>${safe(row.issue_category)}</td><td>${safe(row.recommended_check)}</td></tr>`).join("") || emptyRow(7);
}

const analyticsConfig = {
  ber: {
    title: "Pre-FEC BER channels", status: "ber_status", risk: "ber_risk_score",
    metrics: (rows) => [["KPI channels", rows.length, "Pre-FEC BER groups", "settings_input_antenna"], ["Maximum P95", formatSci(maxBy(rows, "ber_p95")), "Dataset maximum", "show_chart"], ["Average BER", formatSci(average(rows, "ber_mean")), "Channel mean", "functions"], ["Critical", countBy(rows, "ber_status").Critical || 0, "Status count", "error"]],
    columns: [["Device", "device_name"], ["Interface", "logical_name"], ["Side", "side"], ["Frequency", "center_frequency"], ["BER mean", "ber_mean", "sci"], ["BER P95", "ber_p95", "sci"], ["Risk", "ber_risk_score", "float"], ["Status", "ber_status", "badge"]],
  },
  power: {
    title: "OCH power channels", status: "power_status", risk: "power_risk_score",
    metrics: (rows) => [["KPI channels", rows.length, "OCH channel groups", "spectrum"], ["Average power", `${formatFloat(average(rows, "power_mean"))} dBm`, "Across KPI rows", "bolt"], ["Maximum range", `${formatFloat(maxBy(rows, "power_range"))} dB`, "Observed drift range", "swap_vert"], ["Critical", countBy(rows, "power_status").Critical || 0, "Status count", "error"]],
    columns: [["Device", "device_name"], ["Logical name", "logical_name"], ["Frequency", "center_frequency"], ["Mean", "power_mean", "float"], ["Min", "power_min", "float"], ["Range", "power_range", "float"], ["Risk", "power_risk_score", "float"], ["Status", "power_status", "badge"]],
  },
  edfa: {
    title: "EDFA KPI objects", status: "edfa_status", risk: "edfa_risk_score",
    metrics: (rows) => [["EDFA objects", rows.length, "Amplifier components", "electrical_services"], ["Average gain", `${formatFloat(average(rows, "actual_gain_mean"))} dB`, "Actual gain mean", "vertical_align_top"], ["Max attenuation", `${formatFloat(maxBy(rows, "attenuation_max"))} dB`, "Dataset maximum", "signal_cellular_alt"], ["Critical", countBy(rows, "edfa_status").Critical || 0, "Status count", "error"]],
    columns: [["Device", "device_name"], ["Logical name", "logical_name"], ["PN", "pn"], ["Gain mean", "actual_gain_mean", "float"], ["Tilt max", "gain_tilt_abs_max", "float"], ["Attenuation", "attenuation_max", "float"], ["Risk", "edfa_risk_score", "float"], ["Status", "edfa_status", "badge"]],
  },
  frequency: {
    title: "Frequency health", status: "frequency_status", risk: "frequency_risk_score",
    metrics: (rows) => [["Frequencies", rows.length, "Health summary rows", "spectrum"], ["BER channels", rows.reduce((sum, row) => sum + number(row.ber_channel_count), 0), "Mapped channel count", "settings_input_antenna"], ["Power channels", rows.reduce((sum, row) => sum + number(row.power_channel_count), 0), "Mapped OCH groups", "bolt"], ["Critical", countBy(rows, "frequency_status").Critical || 0, "Status count", "error"]],
    columns: [["Frequency", "center_frequency"], ["BER channels", "ber_channel_count", "int"], ["Power channels", "power_channel_count", "int"], ["BER P95 max", "ber_p95_max", "sci"], ["Power min", "power_min", "float"], ["Risk", "frequency_risk_score", "float"], ["Priority", "priority", "badge"], ["Status", "frequency_status", "badge"]],
  },
};

function renderAnalytics() {
  const config = analyticsConfig[state.analytics];
  const rows = (state.analytics === "frequency" ? state.data.frequencies : state.data[state.analytics]).filter(includesQuery).sort((a, b) => number(b[config.risk]) - number(a[config.risk]));
  document.querySelector("#analytics-table-title").textContent = config.title;
  document.querySelector("#analytics-summary").innerHTML = config.metrics(rows).map(([label, value, sub, icon], index) => metricCard(label, formatInt(value) === "0" && typeof value === "string" ? value : String(value), sub, icon, index === 3 && number(value) ? "critical" : "")).join("");
  document.querySelector("#analytics-head").innerHTML = `<tr>${config.columns.map(([label]) => `<th>${label}</th>`).join("")}</tr>`;
  document.querySelector("#analytics-body").innerHTML = rows.map((row) => `<tr class="${row[config.status] === "Critical" ? "critical-row" : ""}">${config.columns.map(([, key, type]) => `<td class="${type === "sci" || type === "float" || type === "int" ? "mono" : ""}">${type === "badge" ? badge(row[key]) : type === "sci" ? formatSci(row[key]) : type === "float" ? formatFloat(row[key]) : type === "int" ? formatInt(row[key]) : safe(row[key] || "—")}</td>`).join("")}</tr>`).join("") || emptyRow(config.columns.length);
}

function renderCurrentView() {
  if (state.view === "overview") renderOverview();
  else if (state.view === "devices") renderDevices();
  else if (state.view === "alerts") renderAlerts();
  else renderAnalytics();
}

function switchView(view) {
  state.view = view;
  document.querySelectorAll(".view").forEach((section) => section.classList.toggle("active", section.id === `view-${view}`));
  document.querySelectorAll(".nav-item").forEach((button) => button.classList.toggle("active", button.dataset.view === view));
  document.body.classList.remove("nav-open");
  renderCurrentView();
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function wireInteractions() {
  document.querySelectorAll(".nav-item").forEach((button) => button.addEventListener("click", () => switchView(button.dataset.view)));
  document.querySelectorAll("[data-go]").forEach((button) => button.addEventListener("click", () => switchView(button.dataset.go)));
  document.querySelector("#mobile-menu").addEventListener("click", () => document.body.classList.toggle("nav-open"));
  document.querySelector("#global-search").addEventListener("input", (event) => { state.query = event.target.value.trim().toLowerCase(); renderCurrentView(); });
  document.querySelectorAll(".filter-row").forEach((group) => group.addEventListener("click", (event) => {
    const button = event.target.closest(".filter"); if (!button) return;
    group.querySelectorAll(".filter").forEach((item) => item.classList.toggle("active", item === button));
    if (group.dataset.filterTarget === "device-table") state.deviceFilter = button.dataset.status;
    else state.alertFilter = button.dataset.status;
    renderCurrentView();
  }));
  document.querySelector(".analytics-tabs").addEventListener("click", (event) => {
    const button = event.target.closest(".analytics-tab"); if (!button) return;
    state.analytics = button.dataset.dataset;
    document.querySelectorAll(".analytics-tab").forEach((item) => item.classList.toggle("active", item === button));
    renderAnalytics();
  });
}

function showError(error) {
  const toast = document.querySelector("#toast");
  toast.textContent = `Dashboard could not load: ${error.message}`;
  toast.classList.add("show");
  document.querySelector("#loading").classList.add("hidden");
}

async function init() {
  try {
    await loadData();
    wireInteractions();
    renderOverview();
    document.querySelector("#alert-dot").style.display = state.data.alerts.length ? "block" : "none";
    document.querySelector("#record-note").textContent = `${formatInt(Object.values(state.data).reduce((sum, rows) => sum + rows.length, 0))} KPI and health rows loaded`;
    document.querySelector("#loading").classList.add("hidden");
  } catch (error) { showError(error); }
}

init();
