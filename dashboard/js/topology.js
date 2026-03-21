/**
 * D3.js Network Topology Visualization
 */

let topologySim = null;

const ZONE_COLORS = {
    corporate: "#00d4ff",
    dmz: "#ffaa00",
    guest: "#ff3366",
    iot: "#aa66ff",
    cloud: "#00ff88",
    restricted: "#ff0044",
    vpn: "#44aaff",
};

const DEVICE_ICONS = {
    workstation: "\uD83D\uDCBB",
    laptop: "\uD83D\uDCBB",
    mobile: "\uD83D\uDCF1",
    server: "\uD83D\uDDA5\uFE0F",
    iot: "\uD83D\uDCE1",
    firewall: "\uD83D\uDEE1\uFE0F",
};

function renderTopology(data) {
    const container = document.getElementById('topology-svg');
    if (!container) return;

    // Clear previous
    d3.select('#topology-svg').selectAll('*').remove();
    if (topologySim) topologySim.stop();

    const width = container.clientWidth || 600;
    const height = 380;

    const svg = d3.select('#topology-svg')
        .attr('width', width)
        .attr('height', height);

    // Defs for glow effect
    const defs = svg.append('defs');
    const filter = defs.append('filter').attr('id', 'glow');
    filter.append('feGaussianBlur').attr('stdDeviation', '3').attr('result', 'coloredBlur');
    const merge = filter.append('feMerge');
    merge.append('feMergeNode').attr('in', 'coloredBlur');
    merge.append('feMergeNode').attr('in', 'SourceGraphic');

    const nodes = data.nodes.map(d => ({ ...d }));
    const edges = data.edges.map(d => ({
        ...d,
        source: typeof d.source === 'string' ? d.source : d.source.id,
        target: typeof d.target === 'string' ? d.target : d.target.id,
    }));

    // Force simulation
    topologySim = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(edges).id(d => d.id).distance(d => d.is_zone_link ? 120 : 60))
        .force('charge', d3.forceManyBody().strength(-200))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(25))
        .alphaDecay(0.02);

    // Edges
    const link = svg.append('g')
        .selectAll('line')
        .data(edges)
        .join('line')
        .attr('stroke', d => d.pqc_protected ? '#00d4ff40' : '#1e284580')
        .attr('stroke-width', d => d.is_zone_link ? 2 : 1)
        .attr('stroke-dasharray', d => d.is_zone_link ? '6,3' : 'none');

    // Node groups
    const node = svg.append('g')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .attr('cursor', 'pointer')
        .call(d3.drag()
            .on('start', dragStarted)
            .on('drag', dragged)
            .on('end', dragEnded));

    // Node circles
    node.append('circle')
        .attr('r', d => d.type === 'server' || d.type === 'firewall' ? 16 : 12)
        .attr('fill', d => ZONE_COLORS[d.zone] || '#5a6480')
        .attr('fill-opacity', 0.2)
        .attr('stroke', d => ZONE_COLORS[d.zone] || '#5a6480')
        .attr('stroke-width', d => d.status === 'online' ? 2 : 1)
        .attr('stroke-opacity', d => d.status === 'online' ? 1 : 0.4)
        .attr('filter', d => d.status === 'online' ? 'url(#glow)' : 'none');

    // Node labels
    node.append('text')
        .text(d => DEVICE_ICONS[d.type] || '?')
        .attr('text-anchor', 'middle')
        .attr('dominant-baseline', 'central')
        .attr('font-size', '10px');

    // Name labels
    node.append('text')
        .text(d => d.name)
        .attr('text-anchor', 'middle')
        .attr('dy', 26)
        .attr('font-size', '8px')
        .attr('fill', '#5a6480');

    // Tooltip on hover
    node.append('title')
        .text(d => `${d.name}\nZone: ${d.zone}\nType: ${d.type}\nTrust: ${Math.round(d.trust_score)}\nStatus: ${d.status}`);

    topologySim.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node.attr('transform', d => {
            d.x = Math.max(20, Math.min(width - 20, d.x));
            d.y = Math.max(20, Math.min(height - 20, d.y));
            return `translate(${d.x},${d.y})`;
        });
    });

    function dragStarted(event, d) {
        if (!event.active) topologySim.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }
    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }
    function dragEnded(event, d) {
        if (!event.active) topologySim.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    // Render zone legend
    renderZoneLegend();
}

function renderZoneLegend() {
    const container = document.getElementById('zone-legend');
    if (!container) return;
    container.innerHTML = '';
    Object.entries(ZONE_COLORS).forEach(([zone, color]) => {
        container.innerHTML += `
            <div class="zone-dot">
                <span class="zone-dot-circle" style="background:${color}"></span>
                ${zone}
            </div>
        `;
    });
}
