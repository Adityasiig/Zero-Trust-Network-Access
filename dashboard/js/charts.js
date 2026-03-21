/**
 * Chart.js instances for the ZTNA dashboard.
 */

let trustGaugeChart = null;
let threatTimelineChart = null;
const threatHistory = [];

function initTrustGauge() {
    const ctx = document.getElementById('trust-gauge');
    if (!ctx) return;

    trustGaugeChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100],
                backgroundColor: ['#00d4ff', '#1a2035'],
                borderWidth: 0,
                circumference: 180,
                rotation: 270,
            }]
        },
        options: {
            responsive: false,
            cutout: '75%',
            plugins: {
                legend: { display: false },
                tooltip: { enabled: false },
            },
            animation: {
                animateRotate: true,
                duration: 800,
                easing: 'easeOutCubic',
            }
        }
    });
}

function updateTrustGauge(score) {
    if (!trustGaugeChart) return;

    let color;
    if (score >= 80) color = '#00ff88';
    else if (score >= 60) color = '#00d4ff';
    else if (score >= 40) color = '#ffaa00';
    else color = '#ff3366';

    trustGaugeChart.data.datasets[0].data = [score, 100 - score];
    trustGaugeChart.data.datasets[0].backgroundColor = [color, '#1a2035'];
    trustGaugeChart.update('none');

    const gaugeVal = document.getElementById('gauge-value');
    if (gaugeVal) {
        gaugeVal.textContent = Math.round(score);
        gaugeVal.style.color = color;
        gaugeVal.style.textShadow = `0 0 20px ${color}40`;
    }

    const riskLevel = score >= 80 ? 'low' : score >= 60 ? 'medium' : score >= 40 ? 'high' : 'critical';
    const riskBadge = document.getElementById('risk-badge');
    if (riskBadge) {
        riskBadge.textContent = `${riskLevel.toUpperCase()} RISK`;
        riskBadge.className = `badge ${riskLevel}-risk`;
    }
}

function initThreatChart() {
    const ctx = document.getElementById('threat-chart');
    if (!ctx) return;

    // Initialize with empty data
    for (let i = 0; i < 20; i++) {
        threatHistory.push({ critical: 0, high: 0, medium: 0, low: 0 });
    }

    threatTimelineChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: threatHistory.map((_, i) => ''),
            datasets: [
                {
                    label: 'Critical',
                    data: threatHistory.map(d => d.critical),
                    borderColor: '#ff3366',
                    backgroundColor: '#ff336620',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 2,
                },
                {
                    label: 'High',
                    data: threatHistory.map(d => d.high),
                    borderColor: '#ff6600',
                    backgroundColor: '#ff660020',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 2,
                },
                {
                    label: 'Medium',
                    data: threatHistory.map(d => d.medium),
                    borderColor: '#ffaa00',
                    backgroundColor: '#ffaa0020',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 2,
                },
                {
                    label: 'Low',
                    data: threatHistory.map(d => d.low),
                    borderColor: '#00ff88',
                    backgroundColor: '#00ff8820',
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    borderWidth: 2,
                },
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    display: false,
                },
                y: {
                    beginAtZero: true,
                    grid: { color: '#1e284520' },
                    ticks: { color: '#5a6480', font: { size: 10 } },
                }
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        color: '#8892a8',
                        font: { size: 10 },
                        boxWidth: 12,
                        padding: 10,
                    }
                },
                tooltip: {
                    backgroundColor: '#141929',
                    borderColor: '#1e2845',
                    borderWidth: 1,
                    titleColor: '#e4e8f1',
                    bodyColor: '#8892a8',
                }
            },
            animation: { duration: 300 }
        }
    });
}

function addThreatToChart(severity) {
    const current = threatHistory[threatHistory.length - 1];
    if (current) {
        current[severity] = (current[severity] || 0) + 1;
    }
}

function tickThreatChart() {
    threatHistory.push({ critical: 0, high: 0, medium: 0, low: 0 });
    if (threatHistory.length > 20) threatHistory.shift();

    if (threatTimelineChart) {
        threatTimelineChart.data.datasets[0].data = threatHistory.map(d => d.critical);
        threatTimelineChart.data.datasets[1].data = threatHistory.map(d => d.high);
        threatTimelineChart.data.datasets[2].data = threatHistory.map(d => d.medium);
        threatTimelineChart.data.datasets[3].data = threatHistory.map(d => d.low);
        threatTimelineChart.update('none');
    }
}
