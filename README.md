# 🛡️ Zero Trust Network Access with Post-Quantum Cryptography

A comprehensive **Zero Trust Network Access (ZTNA)** system implementing **Post-Quantum Cryptography (PQC)** using NIST FIPS 203/204 standardized algorithms. Features a real-time cybersecurity dashboard with live threat monitoring, trust scoring, and network topology visualization.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-green?logo=fastapi)
![PQC](https://img.shields.io/badge/PQC-CRYSTALS--Kyber%20%7C%20Dilithium-purple)
![NIST](https://img.shields.io/badge/NIST-FIPS%20203%2F204-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🌟 Features

### Zero Trust Architecture
- **Never Trust, Always Verify** — Every access request authenticated & authorized
- **Micro-Segmentation** — 7 network zones with explicit allow-list rules
- **Least Privilege** — RBAC + ABAC policy evaluation
- **Continuous Verification** — Trust scores recalculated every 3 seconds

### Post-Quantum Cryptography
- **CRYSTALS-Kyber (ML-KEM-768)** — Lattice-based Key Encapsulation Mechanism (FIPS 203)
- **CRYSTALS-Dilithium (ML-DSA-65)** — Lattice-based Digital Signature Algorithm (FIPS 204)
- **Key Rotation** — Automatic PQC key rotation every 5 minutes
- **Interactive Demo** — Encrypt & sign messages with PQC algorithms in the dashboard

### Real-Time Dashboard
- **Trust Score Gauge** — Composite trust score with 6 weighted factors
- **Device Authentication** — Live status of 15 network devices
- **Threat Monitoring** — Real-time threat feed with severity timeline charts
- **Network Topology** — Interactive D3.js force-directed graph visualization
- **Access Policies** — 6 pre-configured ZTNA policies with condition badges
- **PQC Status Panel** — Algorithm details, key age, encryption statistics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                 Dashboard (HTML/JS)              │
│  Trust Gauge │ Devices │ Threats │ Topology      │
│  PQC Panel   │ Policies│ Charts  │ Live Feed     │
└──────────────────┬──────────────────────────────┘
                   │ WebSocket + REST API
┌──────────────────▼──────────────────────────────┐
│              FastAPI Backend                      │
│  ┌──────────┐ ┌───────────┐ ┌────────────────┐  │
│  │ Auth     │ │ Trust     │ │ Policy Engine  │  │
│  │ Handler  │ │ Engine    │ │ RBAC + ABAC    │  │
│  └──────────┘ └───────────┘ └────────────────┘  │
│  ┌──────────────────────────────────────────┐   │
│  │ Post-Quantum Cryptography Engine         │   │
│  │ CRYSTALS-Kyber (ML-KEM) │ Dilithium     │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │ Network Simulator (Devices, Threats)     │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/Zero-Trust-Network-Access.git
cd Zero-Trust-Network-Access

# Install dependencies
pip install -r requirements.txt

# Run the server
python run.py
```

Open your browser to **http://localhost:8000** — the dashboard loads automatically with live data.

### API Documentation
Visit **http://localhost:8000/docs** for interactive Swagger API documentation.

---

## 📁 Project Structure

```
├── run.py                    # Entry point
├── requirements.txt          # Python dependencies
├── app/
│   ├── main.py              # FastAPI app assembly
│   ├── config.py            # Configuration
│   ├── pqc/
│   │   ├── kyber.py         # CRYSTALS-Kyber ML-KEM simulation
│   │   ├── dilithium.py     # CRYSTALS-Dilithium ML-DSA simulation
│   │   ├── manager.py       # Unified PQC manager
│   │   └── constants.py     # FIPS 203/204 parameter sets
│   ├── trust/
│   │   └── engine.py        # Trust score computation engine
│   ├── policies/
│   │   └── engine.py        # RBAC + ABAC policy engine
│   ├── auth/
│   │   └── handler.py       # JWT authentication handler
│   ├── api/
│   │   ├── routes.py        # REST API endpoints
│   │   └── websocket.py     # WebSocket live feed
│   ├── simulation/
│   │   └── simulator.py     # Network event simulator
│   └── storage/
│       └── store.py         # In-memory data store
└── dashboard/
    ├── index.html            # Dashboard SPA
    ├── css/styles.css        # Dark cybersecurity theme
    └── js/
        ├── app.js            # Main app logic + WebSocket client
        ├── charts.js         # Chart.js trust gauge & threat timeline
        ├── topology.js       # D3.js network topology graph
        └── mock-data.js      # Mock data for static deployment
```

---

## 🔐 Post-Quantum Cryptography Details

### Why PQC?
Quantum computers threaten current public-key cryptography (RSA, ECC). NIST has standardized post-quantum algorithms that resist both classical and quantum attacks.

### Algorithms Used

| Algorithm | Standard | Purpose | Security Level |
|-----------|----------|---------|---------------|
| CRYSTALS-Kyber | FIPS 203 (ML-KEM-768) | Key Encapsulation | Level 3 (≈AES-192) |
| CRYSTALS-Dilithium | FIPS 204 (ML-DSA-65) | Digital Signatures | Level 3 (≈AES-192) |

### Key Sizes (FIPS Compliant)

| Parameter | Kyber-768 | Dilithium-65 |
|-----------|-----------|-------------|
| Public Key | 1,184 bytes | 1,952 bytes |
| Secret Key | 2,400 bytes | 4,000 bytes |
| Ciphertext/Signature | 1,088 bytes | 3,293 bytes |

> **Note**: This is a simulation that mirrors FIPS 203/204 output formats. It uses HMAC-SHA256 internally and is not suitable for production cryptography.

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Authenticate user |
| POST | `/api/auth/mfa` | Verify MFA code |
| GET | `/api/dashboard/stats` | Dashboard statistics |
| GET | `/api/dashboard/devices` | Device list with status |
| GET | `/api/dashboard/threats` | Recent threat events |
| GET | `/api/pqc/status` | PQC algorithm status |
| POST | `/api/pqc/encrypt` | Demo PQC encryption |
| POST | `/api/pqc/sign` | Demo PQC signing |
| GET | `/api/trust/score` | Current trust score |
| GET | `/api/policies` | List access policies |
| POST | `/api/policies/evaluate` | Evaluate access request |
| GET | `/api/network/topology` | Network graph data |
| WS | `/ws/live-feed` | Real-time event stream |

---

## 🖥️ Dashboard Panels

1. **Trust Score Gauge** — Weighted composite of 6 trust factors with color-coded risk level
2. **Device Authentication** — 15 devices across 7 zones with trust scores and PQC badges
3. **PQC Encryption Panel** — Algorithm specs, key rotation status, interactive encrypt demo
4. **Threat Monitoring** — Severity-colored feed with Chart.js timeline visualization
5. **Access Policies** — 6 ZTNA policies with RBAC/ABAC condition tags
6. **Network Topology** — D3.js interactive force graph with draggable nodes

---

## 🌍 Deployment

### GitHub Pages (Static Dashboard)
The dashboard works standalone without the backend. When no WebSocket connection is available, it automatically switches to **Demo Mode** with simulated data.

1. Enable GitHub Pages in your repository settings
2. Set source to the `main` branch, `/dashboard` folder
3. The dashboard will be live at `https://username.github.io/Zero-Trust-Network-Access/`

### Full Application
```bash
python run.py
# Server runs at http://localhost:8000
```

---

## 🛠️ Technologies

- **Backend**: Python, FastAPI, Uvicorn
- **PQC**: CRYSTALS-Kyber (FIPS 203), CRYSTALS-Dilithium (FIPS 204)
- **Frontend**: Vanilla HTML/CSS/JS, Chart.js, D3.js
- **Auth**: JWT (python-jose), SHA-256
- **Real-time**: WebSocket
- **Design**: Dark cybersecurity theme, CSS Grid, responsive

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

**Built with 🛡️ Zero Trust principles and 🔬 Post-Quantum Cryptography**
