// ========================================
// CLASH OF CLANS - GRAPHS.JS
// Integrates with components.js FilterManager and renders Chart.js
// Adds a loading spinner overlay during network requests
// ========================================

let lineChart = null; // Chart.js instance
const canvasId = 'progress-graph'; // matches graphs.html

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Graphs.js loaded!');

    // Spinner state (handles concurrent requests)
    let spinnerCount = 0;
    let spinnerElement = null;

    // Ensure spinner exists and styles are injected
    function ensureSpinner() {
        if (spinnerElement) return spinnerElement;

        const container = document.getElementById('chart-container') || document.getElementById('graph-section') || document.body;

        // inject styles once
        if (!document.getElementById('graphs-spinner-styles')) {
            const style = document.createElement('style');
            style.id = 'graphs-spinner-styles';
            style.textContent = `
                .spinner-overlay {
                    position: absolute;
                    inset: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    background: rgba(255,255,255,0.6);
                    z-index: 1000;
                    transition: opacity 0.15s ease;
                }
                .spinner {
                    width: 48px;
                    height: 48px;
                    border: 6px solid rgba(0,0,0,0.08);
                    border-top-color: #3498db;
                    border-radius: 50%;
                    animation: gos_spin 1s linear infinite;
                    box-shadow: 0 2px 6px rgba(0,0,0,0.12);
                }
                @keyframes gos_spin { to { transform: rotate(360deg); } }
                .graphs-visually-hidden { position:absolute; width:1px; height:1px; padding:0; margin:-1px; overflow:hidden; clip:rect(0 0 0 0); white-space:nowrap; border:0; }
            `;
            document.head.appendChild(style);
        }

        // ensure container is positioned so absolute overlay aligns
        const cs = window.getComputedStyle(container);
        if (cs.position === 'static') container.style.position = 'relative';

        spinnerElement = document.createElement('div');
        spinnerElement.className = 'spinner-overlay';
        spinnerElement.style.display = 'none';
        spinnerElement.innerHTML = `
            <div class="spinner" role="status" aria-live="polite" aria-label="Loading chart"></div>
            <span class="graphs-visually-hidden">Loading chart data</span>
        `;
        container.appendChild(spinnerElement);

        return spinnerElement;
    }

    function showSpinner() {
        const el = ensureSpinner();
        spinnerCount++;
        el.style.display = 'flex';
        el.style.opacity = '1';
    }

    function hideSpinner(force = false) {
        const el = ensureSpinner();
        if (force) spinnerCount = 0;
        else spinnerCount = Math.max(0, spinnerCount - 1);
        if (spinnerCount === 0) {
            el.style.opacity = '0';
            // small delay to allow fade then hide
            setTimeout(() => { if (spinnerCount === 0) el.style.display = 'none'; }, 160);
        }
    }

    // Helper - convert appliedFilters to query params
    function buildQueryParamsFromFilters(appliedFilters) {
        const params = new URLSearchParams();
        // players filter expected at appliedFilters.players (array)
        const players = appliedFilters.players || appliedFilters.player || [];
        players.forEach(p => params.append('selected_players', p));
        // stat filter expected at appliedFilters.stat (array of values) - only first value used
        const statArr = appliedFilters.stat || appliedFilters.statistic || appliedFilters['stat'] || [];
        const statValue = (statArr && statArr.length > 0) ? statArr[0] : 'attack_stars';
        params.append('stat', statValue);
        return params;
    }

    // Fetch data from API and render chart
    function fetchAndRender(params) {
        const url = `/api/graph-data?${params.toString()}`;
        console.log('🔄 Fetching chart data from', url);

        const graphSection = document.getElementById('chart-container') || document.getElementById('graph-section') || document.body;
        // show spinner and dim container
        showSpinner();
        if (graphSection) graphSection.style.opacity = '0.5';

        return fetch(url)
            .then(response => {
                if (!response.ok) throw new Error(`API returned ${response.status}`);
                return response.json();
            })
            .then(chartData => {
                if (!chartData || !chartData.labels) {
                    throw new Error('Malformed chart data from API');
                }
                console.log('✅ Chart data received:', chartData);

                // Clean up old chart
                if (lineChart) lineChart.destroy();

                // Build Chart.js configuration (v3+ syntax)
                const config = {
                    type: 'line',
                    data: {
                        labels: chartData.labels,
                        datasets: chartData.datasets
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        aspectRatio: 2,
                        scales: {
                            x: {
                                title: {
                                    display: true,
                                    text: 'Season'
                                }
                            },
                            y: {
                                title: {
                                    display: true,
                                    text: window.yLabel || chartData.yLabel || 'Value'
                                },
                                beginAtZero: true
                            }
                        },
                        plugins: {
                            legend: {
                                display: true,
                                position: 'top',
                                labels: { usePointStyle: true, padding: 12 }
                            },
                            title: { display: false }
                        },
                        layout: { padding: { left: 10, right: 10, top: 10, bottom: 10 } }
                    }
                };

                const canvas = document.getElementById(canvasId);
                if (!canvas) {
                    throw new Error(`Canvas element with id "${canvasId}" not found`);
                }
                const ctx = canvas.getContext('2d');
                lineChart = new Chart(ctx, config);

                return chartData;
            })
            .catch(err => {
                console.error('❌ Error fetching/rendering chart:', err);
                throw err;
            })
            .finally(() => {
                // hide spinner and restore container opacity
                hideSpinner();
                if (graphSection) graphSection.style.opacity = '1';
            });
    }

    // Initialize: ask API for initial data using default stat attack_stars.
    (function init() {
        // Use default stat 'attack_stars' for initial load
        const params = new URLSearchParams();
        params.append('stat', 'attack_stars');
        fetchAndRender(params).catch(() => {}); // errors already logged
    })();

    // Integrate with FilterManager: when the user clicks "Apply", FilterManager triggers onApply callbacks
    function attachFilterManagerListener() {
        if (!window.filterManager) {
            console.log('🔁 Waiting for FilterManager...');
            setTimeout(attachFilterManagerListener, 100);
            return;
        }

        console.log('🔗 Attaching graph listener to FilterManager');

        // When Apply is clicked, FilterManager will call its apply callbacks with the appliedFilters
        window.filterManager.onApply((appliedFilters) => {
            console.log('🎯 Graphs received applied filters:', appliedFilters || {});
            const params = buildQueryParamsFromFilters(appliedFilters || {});
            fetchAndRender(params).catch(() => {});
        });

        // Also respond to existing applied filters on load (if any)
        const current = window.filterManager.getAppliedFilters();
        if (current && Object.keys(current).length > 0) {
            console.log('📥 Applying existing filters on load:', current);
            const params = buildQueryParamsFromFilters(current);
            fetchAndRender(params).catch(() => {});
        }
    }

    attachFilterManagerListener();
});