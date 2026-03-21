/**
 * ZTNA-PQC Dashboard - Main Application
 * Connects to WebSocket backend or falls back to mock data.
 */

let ws = null;
let useMockData = false;
let mockInterval = null;
let chartTickInterval = null;

// ============ INITIALIZATION ============

document.addEventListener('DOMContentLoaded', () => {
    initTrustGauge();
    initThreatChart();
    connectWebSocket();

    // Chart tick interval for threat timeline
    chartTickInterval = setInterval(tickThreatChart, 10000);
});

// ============ WEBSOCKET ============

function connectWebSocket() {
    const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${location.hostname}:${location.port || 8000}/ws/live-feed`;

    try {
        ws = new WebSocket(wsUrl);

        ws.onopen = () => {
            document.getElementById('connection-status').textContent = 'Live Connected';
            document.querySelector('.pulse-dot').classList.add('connected');
            useMockData = false;
            if (mockInterval) { clearInterval(mockInterval); mockInterval = null; }
            fetchInitialData();
        };

        ws.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                handleMessage(msg);
            } catch (e) { /* ignore parse errors */ }
        };

        ws.onclose = () => {
            document.getElementById('connection-status').textContent = 'Reconnecting...';
            document.querySelector('.pulse-dot').classList.remove('connected');
            setTimeout(() => {
                if (!useMockData) connectWebSocket();
            }, 3000);
        };

        ws.onerror = () => {
            ws.close();
            startMockMode();
        };

        // Timeout: if not connected in 2s, go mock
        setTimeout(() => {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                startMockMode();
            }
        }, 2000);

    } catch (e) {
        startMockMode();
    }
}

// ============ MOCK MODE ============

function startMockMode() {
    if (useMockData) return;
    useMockData = true;
    document.getElementById('connection-status').textContent = 'Demo Mode';
    document.querySelector('.pulse-dot').classList.add('connected');
    document.querySelector('.pulse-dot').style.background = '#aa66ff';

    // Load initial mock data
    renderDevices(MockData.devices);
    renderPolicies(MockData.policies);
    renderTopology(MockData.getTopology());
    updateTrustDisplay();
    updateStats();

    // Generate initial threats
    for (let i = 0; i < 5; i++) {
        const threat = MockData.generateThreat();
        addThreatToFeed(threat);
        addThreatToChart(threat.severity);
    }
    updateThreatCounts();

    // Periodic updates
    mockInterval = setInterval(() => {
        // Trust drift
        MockData.driftTrustFactors();
        updateTrustDisplay();

        // Device drift
        MockData.driftDevices();
        renderDevices(MockData.devices);

        // Random threat
        if (Math.random() < 0.35) {
            const threat = MockData.generateThreat();
            addThreatToFeed(threat);
            addThreatToChart(threat.severity);
            updateThreatCounts();
            if (threat.severity === 'high' || threat.severity === 'critical') {
                MockData.blockedRequests++;
            }
        }

        // PQC stats
        MockData.pqcKeyAge += 3;
        MockData.pqcEncryptions += Math.floor(Math.random() * 3);
        if (MockData.pqcKeyAge > 300) {
            MockData.pqcKeyAge = 0;
            MockData.pqcRotations++;
        }

        updateStats();
        updatePQCStats();
    }, 3000);
}

// ============ API FETCH ============

async function fetchInitialData() {
    try {
        const [statsRes, devicesRes, threatsRes, policiesRes, topoRes] = await Promise.all([
            fetch('/api/dashboard/stats'),
            fetch('/api/dashboard/devices'),
            fetch('/api/dashboard/threats'),
            fetch('/api/policies'),
            fetch('/api/network/topology'),
        ]);

        const stats = await statsRes.json();
        const devices = await devicesRes.json();
        const threats = await threatsRes.json();
        const policies = await policiesRes.json();
        const topology = await topoRes.json();

        renderDevices(devices);
        renderPolicies(policies);
        renderTopology(topology);
        threats.forEach(t => {
            addThreatToFeed(t);
            addThreatToChart(t.severity);
        });
        updateThreatCounts();

        if (stats.trust_factors) {
            MockData.trustFactors = stats.trust_factors;
        }
        updateTrustDisplay();
        applyStats(stats);
    } catch (e) {
        startMockMode();
    }
}

// ============ MESSAGE HANDLER ============

function handleMessage(msg) {
    switch (msg.type) {
        case 'trust_update':
            if (msg.data && msg.data.factors) {
                const factors = msg.data.factors;
                MockData.trustFactors = Object.entries(factors).map(([key, f]) => ({
                    name: key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
                    weight: f.weight,
                    value: f.value,
                }));
            }
            updateTrustDisplay();
            break;

        case 'threat_event':
            addThreatToFeed(msg.data);
            addThreatToChart(msg.data.severity);
            updateThreatCounts();
            break;

        case 'device_status':
            updateDeviceStatus(msg.data);
            break;

        case 'stats_update':
            if (msg.data.stats) applyStats(msg.data.stats);
            if (msg.data.pqc) {
                MockData.pqcKeyAge = msg.data.pqc.key_age || 0;
                MockData.pqcRotations = msg.data.pqc.rotation_count || 0;
                updatePQCStats();
            }
            break;

        case 'pqc_rotation':
            MockData.pqcKeyAge = 0;
            MockData.pqcRotations = msg.data.rotation_count || MockData.pqcRotations + 1;
            updatePQCStats();
            break;
    }
}

// ============ RENDER FUNCTIONS ============

function renderDevices(devices) {
    const container = document.getElementById('device-list');
    if (!container) return;

    const icons = { workstation: '\uD83D\uDCBB', laptop: '\uD83D\uDCBB', mobile: '\uD83D\uDCF1', server: '\uD83D\uDDA5\uFE0F', iot: '\uD83D\uDCE1', firewall: '\uD83D\uDEE1\uFE0F' };

    container.innerHTML = devices.map(d => {
        const trustColor = d.trust_score >= 80 ? '#00ff88' : d.trust_score >= 60 ? '#00d4ff' : d.trust_score >= 40 ? '#ffaa00' : '#ff3366';
        return `
            <div class="device-item" data-id="${d.id}">
                <div class="device-icon ${d.type}">${icons[d.type] || '?'}</div>
                <div class="device-info">
                    <div class="device-name">${d.name}</div>
                    <div class="device-meta">${d.os || ''} &bull; ${d.zone}</div>
                </div>
                <div class="device-badges">
                    <span class="mini-badge ${d.status}">${d.status}</span>
                    ${d.pqc_enabled ? '<span class="mini-badge pqc">PQC</span>' : ''}
                </div>
                <div class="device-trust" style="color:${trustColor}">${Math.round(d.trust_score)}</div>
            </div>
        `;
    }).join('');

    const onlineCount = devices.filter(d => d.status === 'online' || d.status === 'idle').length;
    document.getElementById('device-count').textContent = `${onlineCount}/${devices.length} devices`;
    document.getElementById('stat-devices').textContent = onlineCount;
}

function renderPolicies(policies) {
    const container = document.getElementById('policy-list');
    if (!container) return;

    container.innerHTML = policies.map(p => {
        const conds = p.conditions || {};
        return `
            <div class="policy-item">
                <div class="policy-top">
                    <span class="policy-name">${p.name}</span>
                    <span class="policy-id">${p.id}</span>
                </div>
                <div class="policy-resource">${p.resource}</div>
                <div class="policy-conditions">
                    ${(conds.roles || []).map(r => `<span class="condition-tag">${r}</span>`).join('')}
                    ${conds.min_trust_score ? `<span class="condition-tag required">Trust ≥ ${conds.min_trust_score}</span>` : ''}
                    ${conds.require_mfa ? '<span class="condition-tag required">MFA</span>' : ''}
                    ${conds.require_pqc ? '<span class="condition-tag required">PQC</span>' : ''}
                    ${(conds.required_zones || []).map(z => `<span class="condition-tag">${z}</span>`).join('')}
                </div>
            </div>
        `;
    }).join('');

    document.getElementById('policy-count').textContent = `${policies.filter(p => p.enabled).length} active`;
}

function addThreatToFeed(threat) {
    const feed = document.getElementById('threat-feed');
    if (!feed) return;

    const time = threat.timestamp ? new Date(threat.timestamp * 1000).toLocaleTimeString() : new Date().toLocaleTimeString();
    const el = document.createElement('div');
    el.className = `threat-item ${threat.severity}`;
    el.innerHTML = `
        <span class="threat-time">${time}</span>
        <span class="threat-desc">${threat.description}</span>
        <span class="threat-source">${threat.source_device || ''}</span>
    `;

    feed.insertBefore(el, feed.firstChild);

    // Limit entries
    while (feed.children.length > 30) {
        feed.removeChild(feed.lastChild);
    }
}

// ============ UPDATE FUNCTIONS ============

function updateTrustDisplay() {
    const score = MockData.getCompositeScore();
    updateTrustGauge(score);

    const container = document.getElementById('trust-factors');
    if (!container) return;

    container.innerHTML = MockData.trustFactors.map(f => {
        const color = f.value >= 80 ? '#00ff88' : f.value >= 60 ? '#00d4ff' : f.value >= 40 ? '#ffaa00' : '#ff3366';
        return `
            <div class="factor-item">
                <div class="factor-header">
                    <span class="factor-name">${f.name}</span>
                    <span class="factor-value" style="color:${color}">${Math.round(f.value)}</span>
                </div>
                <div class="factor-bar">
                    <div class="factor-bar-fill" style="width:${f.value}%;background:${color}"></div>
                </div>
            </div>
        `;
    }).join('');

    document.getElementById('stat-trust').textContent = Math.round(score);
}

function updateThreatCounts() {
    const threats = MockData.threats;
    const counts = { critical: 0, high: 0, medium: 0, low: 0 };
    const oneHourAgo = Date.now() / 1000 - 3600;

    threats.forEach(t => {
        if (t.timestamp > oneHourAgo) counts[t.severity] = (counts[t.severity] || 0) + 1;
    });

    document.getElementById('threats-critical').textContent = counts.critical;
    document.getElementById('threats-high').textContent = counts.high;
    document.getElementById('threats-medium').textContent = counts.medium;
    document.getElementById('threats-low').textContent = counts.low;
    document.getElementById('stat-threats').textContent = Object.values(counts).reduce((a, b) => a + b, 0);
}

function updateStats() {
    const pqcDevices = MockData.devices.filter(d => d.pqc_enabled).length;
    const total = MockData.devices.length;
    document.getElementById('stat-pqc-coverage').textContent = `${Math.round(pqcDevices / total * 100)}%`;
    document.getElementById('stat-blocked').textContent = MockData.blockedRequests;
}

function applyStats(stats) {
    if (stats.online_devices != null) document.getElementById('stat-devices').textContent = stats.online_devices;
    if (stats.average_trust_score != null) document.getElementById('stat-trust').textContent = Math.round(stats.average_trust_score);
    if (stats.recent_threats_1h != null) document.getElementById('stat-threats').textContent = stats.recent_threats_1h;
    if (stats.pqc_coverage_percent != null) document.getElementById('stat-pqc-coverage').textContent = `${Math.round(stats.pqc_coverage_percent)}%`;
    if (stats.blocked_requests != null) {
        document.getElementById('stat-blocked').textContent = stats.blocked_requests;
        MockData.blockedRequests = stats.blocked_requests;
    }
    if (stats.pqc_encryptions != null) MockData.pqcEncryptions = stats.pqc_encryptions;
    if (stats.key_rotations != null) MockData.pqcRotations = stats.key_rotations;
    updatePQCStats();
}

function updatePQCStats() {
    const age = MockData.pqcKeyAge;
    let ageStr;
    if (age < 60) ageStr = `${Math.round(age)}s`;
    else if (age < 3600) ageStr = `${Math.floor(age / 60)}m ${Math.round(age % 60)}s`;
    else ageStr = `${Math.floor(age / 3600)}h`;

    document.getElementById('pqc-key-age').textContent = ageStr;
    document.getElementById('pqc-rotations').textContent = MockData.pqcRotations;
    document.getElementById('pqc-encryptions').textContent = MockData.pqcEncryptions;
}

function updateDeviceStatus(data) {
    const devices = MockData.devices;
    const device = devices.find(d => d.id === data.device_id || d.name === data.name);
    if (device) {
        device.status = data.new_status;
        if (data.trust_score != null) device.trust_score = data.trust_score;
        renderDevices(devices);
    }
}

// ============ PQC DEMO ============

async function demoEncrypt() {
    const input = document.getElementById('pqc-demo-input');
    const output = document.getElementById('pqc-demo-output');
    const message = input.value.trim() || 'Hello, Post-Quantum World!';

    output.classList.add('show');
    output.textContent = 'Encrypting with CRYSTALS-Kyber (ML-KEM-768)...';

    if (!useMockData) {
        try {
            const res = await fetch('/api/pqc/encrypt', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ plaintext: message }),
            });
            const data = await res.json();
            output.innerHTML = `
<span style="color:#00d4ff">// KEM Encapsulation (CRYSTALS-Kyber ML-KEM-768)</span>
Ciphertext: ${data.kem_encapsulation.ciphertext_hex.substring(0, 64)}...
Shared Secret: ${data.kem_encapsulation.shared_secret_hex}
CT Size: ${data.kem_encapsulation.ciphertext_size} bytes
Time: ${data.kem_encapsulation.encapsulation_time_ms}ms

<span style="color:#aa66ff">// Digital Signature (CRYSTALS-Dilithium ML-DSA-65)</span>
Signature: ${data.digital_signature.signature_hex.substring(0, 64)}...
Sig Size: ${data.digital_signature.signature_size} bytes
Time: ${data.digital_signature.signing_time_ms}ms`;
            MockData.pqcEncryptions++;
            updatePQCStats();
            return;
        } catch (e) { /* fall through to mock */ }
    }

    // Mock encryption
    setTimeout(() => {
        const fakeHex = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
        const fakeSecret = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
        const fakeSig = Array.from({ length: 64 }, () => Math.floor(Math.random() * 16).toString(16)).join('');
        output.innerHTML = `
<span style="color:#00d4ff">// KEM Encapsulation (CRYSTALS-Kyber ML-KEM-768)</span>
Ciphertext: ${fakeHex}...
Shared Secret: ${fakeSecret}
CT Size: 1088 bytes | Time: ${(Math.random() * 2).toFixed(3)}ms

<span style="color:#aa66ff">// Digital Signature (CRYSTALS-Dilithium ML-DSA-65)</span>
Signature: ${fakeSig}...
Sig Size: 3293 bytes | Time: ${(Math.random() * 3).toFixed(3)}ms

<span style="color:#ffaa00">Message: "${message}"</span> → Quantum-Safe Encrypted ✓`;
        MockData.pqcEncryptions++;
        updatePQCStats();
    }, 500);
}
