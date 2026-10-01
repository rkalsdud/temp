// =============================================================================
// 전역 변수
// =============================================================================
let subscribers = [];
let currentDevices = [];
let selectedUserId = null;
let selectedDeviceId = null;
let usageChart = null;


// =============================================================================
// [요구사항 #3] 상태 기반 Badge 스타일
// =============================================================================
// TODO [요구사항 #3]: 상태 값(value)에 따라 적절한 CSS 클래스를 반환하세요.
//
function badgeClass(value) {
    const v = (value || "").toLowerCase();

    // 매핑 규칙:
    // Active, Online, Normal   → "badge status-active"   (초록)
    // Paused, Standby          → "badge status-paused"   (파랑)
    // Expired, Error, Warning  → "badge status-expired"  (빨강)
    // Offline                  → "badge status-offline"  (회색)
    // On, Cleaning             → "badge status-on"       (노랑)
    // Off                      → "badge status-off"      (연회색)
    // 그 외                     → "badge"
    return "badge";
}


// =============================================================================
// [요구사항 #1] 구독 사용자 조회 + 검색/필터
// =============================================================================

// TODO [요구사항 #1-A]: GET /api/subscribers 를 호출하여
//   subscribers 변수에 저장하고 renderSubscribers()를 호출하세요.
//
async function fetchSubscribers() {
    try {
        const res = await fetch("/api/subscribers");
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        subscribers = await res.json();
        renderSubscribers();
    } catch (err) {
        console.error("Failed to fetch subscribers:", err);
        subscribers = [];
        renderSubscribers();
    }
}

// TODO [요구사항 #1-B]: subscribers 배열을 테이블에 렌더링하세요.
//
function renderSubscribers() {
    const tbody = document.getElementById("subscriber-body");
    const search = document.getElementById("subscriber-search").value.toLowerCase();
    const statusFilter = document.getElementById("subscriber-status-filter").value;

    const filtered = subscribers.filter((s) => {
        const matchesSearch =
            !search ||
            s.name.toLowerCase().includes(search) ||
            s.plan.toLowerCase().includes(search) ||
            s.status.toLowerCase().includes(search) ||
            s.userId.toLowerCase().includes(search);
        const matchesStatus = !statusFilter || s.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    tbody.innerHTML = "";

    if (filtered.length === 0) {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td colspan="5" class="empty-msg">No subscribers matched.</td>`;
        tbody.appendChild(tr);
        return;
    }

    for (const s of filtered) {
        const tr = document.createElement("tr");
        tr.className = "clickable";
        if (s.userId === selectedUserId) tr.classList.add("selected");
        tr.innerHTML = `
            <td>${s.userId}</td>
            <td>${s.name}</td>
            <td>${s.plan}</td>
            <td><span class="${badgeClass(s.status)}">${s.status}</span></td>
            <td>${s.deviceCount}</td>
        `;
        tr.addEventListener("click", () => selectSubscriber(s.userId));
        tbody.appendChild(tr);
    }
}


// =============================================================================
// [요구사항 #2] 사용자별 가전 목록 + 사용 현황 + 차트
// =============================================================================

// TODO [요구사항 #2-A]: 사용자 클릭 시 해당 사용자의 가전 목록을 조회하세요.
//
async function selectSubscriber(userId) {
    selectedUserId = userId;
    selectedDeviceId = null;
    renderSubscribers();

    document.getElementById("usage-empty").classList.remove("hidden");
    document.getElementById("usage-detail").classList.add("hidden");
    document.getElementById("usage-info").innerHTML = "";

    try {
        const res = await fetch(`/api/subscribers/${userId}/devices`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        currentDevices = await res.json();
    } catch (err) {
        console.error("Failed to fetch devices:", err);
        currentDevices = [];
    }
    renderDevices();
}

// TODO [요구사항 #2-B]: currentDevices 배열을 테이블에 렌더링하세요.
//
function renderDevices() {
    const emptyEl = document.getElementById("device-empty");
    const tableEl = document.getElementById("device-table");
    const tbody = document.getElementById("device-body");
    const search = document.getElementById("device-search").value.toLowerCase();
    const statusFilter = document.getElementById("device-status-filter").value;

    if (currentDevices.length === 0) {
        emptyEl.textContent = "No registered devices.";
        emptyEl.classList.remove("hidden");
        tableEl.classList.add("hidden");
        tbody.innerHTML = "";
        return;
    }

    const filtered = currentDevices.filter((d) => {
        const matchesSearch =
            !search ||
            d.type.toLowerCase().includes(search) ||
            d.model.toLowerCase().includes(search) ||
            d.status.toLowerCase().includes(search) ||
            d.deviceId.toLowerCase().includes(search) ||
            d.location.toLowerCase().includes(search);
        const matchesStatus = !statusFilter || d.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    if (filtered.length === 0) {
        emptyEl.textContent = "No devices matched.";
        emptyEl.classList.remove("hidden");
        tableEl.classList.add("hidden");
        tbody.innerHTML = "";
        return;
    }

    emptyEl.classList.add("hidden");
    tableEl.classList.remove("hidden");
    tbody.innerHTML = "";

    for (const d of filtered) {
        const tr = document.createElement("tr");
        tr.className = "clickable";
        if (d.deviceId === selectedDeviceId) tr.classList.add("selected");
        tr.innerHTML = `
            <td>${d.deviceId}</td>
            <td>${d.type}</td>
            <td>${d.model}</td>
            <td>${d.location}</td>
            <td><span class="${badgeClass(d.status)}">${d.status}</span></td>
        `;
        tr.addEventListener("click", () => selectDevice(d.deviceId));
        tbody.appendChild(tr);
    }
}

// TODO [요구사항 #2-C]: 가전 클릭 시 상세 사용 현황을 조회하세요.
//
async function selectDevice(deviceId) {
    selectedDeviceId = deviceId;
    renderDevices();

    let data;
    try {
        const res = await fetch(`/api/devices/${deviceId}/usage`);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        data = await res.json();
    } catch (err) {
        console.error("Failed to fetch usage:", err);
        return;
    }

    document.getElementById("usage-empty").classList.add("hidden");
    document.getElementById("usage-detail").classList.remove("hidden");

    const info = document.getElementById("usage-info");
    info.innerHTML = `
        <div class="label">Device ID</div><div class="value">${data.deviceId}</div>
        <div class="label">Device Name</div><div class="value">${data.deviceName}</div>
        <div class="label">Power Status</div><div class="value"><span class="${badgeClass(data.powerStatus)}">${data.powerStatus}</span></div>
        <div class="label">Last Used</div><div class="value">${data.lastUsedAt}</div>
        <div class="label">Total Usage Hours</div><div class="value">${data.totalUsageHours}</div>
        <div class="label">Weekly Usage Count</div><div class="value">${data.weeklyUsageCount}</div>
        <div class="label">Health Status</div><div class="value"><span class="${badgeClass(data.healthStatus)}">${data.healthStatus}</span></div>
        <div class="label">Remark</div><div class="value">${data.remark}</div>
    `;

    renderUsageChart(data.weeklyUsageTrend);
}

// TODO [요구사항 #2-D]: Chart.js를 사용하여 주간 사용량 Bar Chart를 그리세요.
//
function renderUsageChart(trend) {
    const ctx = document.getElementById("usageChart");

    if (usageChart) {
        usageChart.destroy();
    }

    usageChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            datasets: [{
                label: "Weekly Usage",
                data: trend,
                backgroundColor: "#3b82f6",
            }],
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: true },
            },
        },
    });
}


// =============================================================================
// 이벤트 바인딩 + 초기화
// =============================================================================
function bindEvents() {
    // [요구사항 #1] 완료 후 아래 주석을 해제하세요
    document.getElementById("subscriber-search").addEventListener("input", renderSubscribers);
    document.getElementById("subscriber-status-filter").addEventListener("change", renderSubscribers);

    // [요구사항 #2] 완료 후 아래 주석을 해제하세요
    document.getElementById("device-search").addEventListener("input", renderDevices);
    document.getElementById("device-status-filter").addEventListener("change", renderDevices);
}

bindEvents();

// [요구사항 #1] 완료 후 아래 주석을 해제하세요
fetchSubscribers();
