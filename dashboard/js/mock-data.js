/**
 * Mock Data Generator - Drives the dashboard when no backend is available.
 * Used for GitHub Pages static deployment.
 */

const MockData = {
    devices: [
        { id: "d1", name: "WS-ENG-001", type: "workstation", os: "Windows 11 Pro", zone: "corporate", status: "online", trust_score: 87, pqc_enabled: true, auth_method: "mfa" },
        { id: "d2", name: "WS-ENG-002", type: "workstation", os: "macOS Sonoma", zone: "corporate", status: "online", trust_score: 92, pqc_enabled: true, auth_method: "biometric" },
        { id: "d3", name: "WS-ADMIN-001", type: "workstation", os: "Ubuntu 24.04", zone: "corporate", status: "online", trust_score: 95, pqc_enabled: true, auth_method: "certificate" },
        { id: "d4", name: "LAPTOP-ANA-001", type: "laptop", os: "Windows 11 Pro", zone: "vpn", status: "online", trust_score: 72, pqc_enabled: true, auth_method: "mfa" },
        { id: "d5", name: "LAPTOP-ENG-003", type: "laptop", os: "macOS Ventura", zone: "vpn", status: "idle", trust_score: 68, pqc_enabled: false, auth_method: "password" },
        { id: "d6", name: "MB-GUEST-001", type: "mobile", os: "iOS 18", zone: "guest", status: "online", trust_score: 45, pqc_enabled: false, auth_method: "password" },
        { id: "d7", name: "MB-ENG-002", type: "mobile", os: "Android 15", zone: "corporate", status: "online", trust_score: 78, pqc_enabled: true, auth_method: "biometric" },
        { id: "d8", name: "SRV-WEB-001", type: "server", os: "RHEL 9.3", zone: "dmz", status: "online", trust_score: 88, pqc_enabled: true, auth_method: "certificate" },
        { id: "d9", name: "SRV-DB-001", type: "server", os: "Ubuntu 22.04", zone: "corporate", status: "online", trust_score: 91, pqc_enabled: true, auth_method: "certificate" },
        { id: "d10", name: "SRV-API-001", type: "server", os: "Alpine Linux", zone: "cloud", status: "online", trust_score: 85, pqc_enabled: true, auth_method: "certificate" },
        { id: "d11", name: "IOT-SENSOR-001", type: "iot", os: "RTOS", zone: "iot", status: "online", trust_score: 55, pqc_enabled: false, auth_method: "password" },
        { id: "d12", name: "IOT-SENSOR-002", type: "iot", os: "RTOS", zone: "iot", status: "idle", trust_score: 52, pqc_enabled: false, auth_method: "password" },
        { id: "d13", name: "IOT-CAMERA-001", type: "iot", os: "Linux Embedded", zone: "iot", status: "online", trust_score: 48, pqc_enabled: true, auth_method: "certificate" },
        { id: "d14", name: "SRV-CLOUD-K8S", type: "server", os: "Container OS", zone: "cloud", status: "online", trust_score: 90, pqc_enabled: true, auth_method: "certificate" },
        { id: "d15", name: "FW-CORE-001", type: "firewall", os: "FortiOS", zone: "dmz", status: "online", trust_score: 96, pqc_enabled: true, auth_method: "certificate" },
    ],

    policies: [
        { id: "POL-001", name: "Engineering Database Access", resource: "/api/data/engineering-db", conditions: { roles: ["engineer", "admin"], min_trust_score: 75, required_zones: ["corporate", "vpn"], require_mfa: true, require_pqc: true }, enabled: true },
        { id: "POL-002", name: "Public API Access", resource: "/api/public/*", conditions: { roles: ["engineer", "analyst", "admin", "guest"], min_trust_score: 30, required_zones: ["corporate", "vpn", "guest"], require_mfa: false, require_pqc: false }, enabled: true },
        { id: "POL-003", name: "Admin Console Access", resource: "/admin/*", conditions: { roles: ["admin"], min_trust_score: 85, required_zones: ["corporate"], require_mfa: true, require_pqc: true }, enabled: true },
        { id: "POL-004", name: "IoT Sensor Data", resource: "/api/data/iot-sensors", conditions: { roles: ["engineer", "analyst", "admin"], min_trust_score: 50, required_zones: ["corporate", "vpn", "iot"], require_mfa: false, require_pqc: true }, enabled: true },
        { id: "POL-005", name: "Restricted Lab Access", resource: "/api/data/restricted-lab", conditions: { roles: ["admin"], min_trust_score: 90, required_zones: ["restricted"], require_mfa: true, require_pqc: true }, enabled: true },
        { id: "POL-006", name: "Cloud Services Gateway", resource: "/api/cloud/*", conditions: { roles: ["engineer", "admin"], min_trust_score: 65, required_zones: ["corporate", "vpn", "cloud"], require_mfa: true, require_pqc: true }, enabled: true },
    ],

    zones: {
        corporate: { name: "Corporate LAN", color: "#00d4ff" },
        dmz: { name: "DMZ", color: "#ffaa00" },
        guest: { name: "Guest WiFi", color: "#ff3366" },
        iot: { name: "IoT Segment", color: "#aa66ff" },
        cloud: { name: "Cloud Services", color: "#00ff88" },
        restricted: { name: "Restricted Lab", color: "#ff0044" },
        vpn: { name: "VPN Tunnel", color: "#44aaff" },
    },

    trustFactors: [
        { name: "Device Posture", weight: 0.25, value: 75 },
        { name: "Auth Strength", weight: 0.20, value: 80 },
        { name: "Behavioral Score", weight: 0.20, value: 70 },
        { name: "Network Context", weight: 0.15, value: 65 },
        { name: "Time Factor", weight: 0.10, value: 85 },
        { name: "PQC Compliance", weight: 0.10, value: 90 },
    ],

    threatTypes: [
        { type: "brute_force", severity: "high", description: "Brute force login attempt detected" },
        { type: "anomalous_access", severity: "medium", description: "Unusual access pattern detected" },
        { type: "policy_violation", severity: "medium", description: "Access policy violation" },
        { type: "zone_crossing", severity: "high", description: "Unauthorized network zone crossing" },
        { type: "cert_expiry", severity: "low", description: "Device certificate expiring soon" },
        { type: "port_scan", severity: "medium", description: "Port scanning activity detected" },
        { type: "suspicious_login", severity: "low", description: "Login from unusual location" },
        { type: "data_exfiltration", severity: "critical", description: "Potential data exfiltration detected" },
    ],

    threats: [],
    pqcKeyAge: 0,
    pqcRotations: 1,
    pqcEncryptions: 0,
    blockedRequests: 0,

    /** Generate a random threat */
    generateThreat() {
        const template = this.threatTypes[Math.floor(Math.random() * this.threatTypes.length)];
        const device = this.devices[Math.floor(Math.random() * this.devices.length)];
        const threat = {
            id: `THR-${Date.now() % 100000}`,
            type: template.type,
            severity: template.severity,
            description: template.description,
            source_device: device.name,
            source_ip: `10.${Math.floor(Math.random()*254)}.${Math.floor(Math.random()*254)}.${Math.floor(Math.random()*254)}`,
            source_zone: device.zone,
            timestamp: Date.now() / 1000,
        };
        this.threats.unshift(threat);
        if (this.threats.length > 100) this.threats.length = 100;
        return threat;
    },

    /** Simulate trust factor drift */
    driftTrustFactors() {
        this.trustFactors.forEach(f => {
            const drift = (Math.random() - 0.5) * 4;
            const meanRevert = (70 - f.value) * 0.05;
            f.value = Math.max(0, Math.min(100, f.value + drift + meanRevert));
        });
    },

    /** Simulate device status changes */
    driftDevices() {
        const device = this.devices[Math.floor(Math.random() * this.devices.length)];
        // Trust drift
        device.trust_score = Math.max(0, Math.min(100, device.trust_score + (Math.random() - 0.5) * 3));
        // Occasional status change
        if (Math.random() < 0.05) {
            const statuses = ["online", "online", "online", "idle", "offline"];
            device.status = statuses[Math.floor(Math.random() * statuses.length)];
        }
    },

    getCompositeScore() {
        return this.trustFactors.reduce((sum, f) => sum + f.value * f.weight, 0);
    },

    getRiskLevel(score) {
        if (score >= 80) return "low";
        if (score >= 60) return "medium";
        if (score >= 40) return "high";
        return "critical";
    },

    getTopology() {
        const nodes = this.devices.map(d => ({
            id: d.id,
            name: d.name,
            type: d.type,
            zone: d.zone,
            status: d.status,
            trust_score: d.trust_score,
        }));

        const zoneGateways = {};
        nodes.forEach(n => {
            if (!zoneGateways[n.zone] || n.type === 'server' || n.type === 'firewall') {
                zoneGateways[n.zone] = n.id;
            }
        });

        const edges = [];
        nodes.forEach(n => {
            const gw = zoneGateways[n.zone];
            if (gw && gw !== n.id) {
                edges.push({
                    source: n.id,
                    target: gw,
                    bandwidth: Math.floor(Math.random() * 900) + 100,
                    pqc_protected: Math.random() > 0.3,
                });
            }
        });

        // Zone-to-zone links
        const zoneLinks = [
            ["corporate", "dmz"], ["corporate", "cloud"], ["corporate", "vpn"],
            ["dmz", "cloud"], ["vpn", "cloud"],
        ];
        zoneLinks.forEach(([a, b]) => {
            if (zoneGateways[a] && zoneGateways[b]) {
                edges.push({
                    source: zoneGateways[a],
                    target: zoneGateways[b],
                    bandwidth: Math.floor(Math.random() * 5000) + 1000,
                    pqc_protected: true,
                    is_zone_link: true,
                });
            }
        });

        return { nodes, edges };
    }
};
