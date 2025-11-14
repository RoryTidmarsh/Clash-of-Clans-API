// ========================================
// CLASH OF CLANS - GRAPHS.JS
// Handles interactive filtering and chart updates
// ========================================

// Global variables
let lineChart = null; // Will store Chart.js instance

// Function to initialize the line chart
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Graphs.js loaded!');
    
    // ============================================
    // 1. MULTI-SELECT DROPDOWN FUNCTIONALITY
    // ============================================
    const playerTrigger = document.getElementById('player-trigger');
    const playerPanel = document.getElementById('player-panel');
    const selectAllCheckbox = document.getElementById('select-all-players');
    const playerCheckboxes = document.querySelectorAll('.player-checkbox');
    
    console.log('🔍 Found elements:');
    console.log('  - Trigger button:', playerTrigger);
    console.log('  - Panel:', playerPanel);
    console.log('  - Checkboxes:', playerCheckboxes.length);
    
    // Toggle dropdown when clicking the button
    if (playerTrigger) {
        playerTrigger.addEventListener('click', function(e) {
            e.stopPropagation();
            playerPanel.classList.toggle('show');
            console.log('🔽 Dropdown toggled, show:', playerPanel.classList.contains('show'));
        });
    }
    
    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (playerPanel && !playerPanel.contains(e.target) && e.target !== playerTrigger) {
            playerPanel.classList.remove('show');
        }
    });
    
    // "Select All" checkbox functionality
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            playerCheckboxes.forEach(cb => {
                cb.checked = isChecked;
            });
            updateFilterDisplay();
            console.log(isChecked ? '✅ All players selected' : '❌ All players deselected');
        });
    }
    
    // Update display when individual checkboxes change
    playerCheckboxes.forEach(cb => {
        cb.addEventListener('change', function() {
            updateFilterDisplay();
            
            // Update "Select All" checkbox state
            const allChecked = Array.from(playerCheckboxes).every(c => c.checked);
            const noneChecked = Array.from(playerCheckboxes).every(c => !c.checked);
            
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = allChecked;
                selectAllCheckbox.indeterminate = !allChecked && !noneChecked;
            }
        });
    });
        // Function to update the button text showing selection
    function updateFilterDisplay() {
        const selected = Array.from(playerCheckboxes)
            .filter(cb => cb.checked)
            .map(cb => cb.value);
        
        const filterSelect = document.getElementById('filter-select');
        if (!filterSelect) return;
        
        if (selected.length === 0) {
            filterSelect.textContent = 'Select players';
        } else if (selected.length === playerCheckboxes.length) {
            filterSelect.textContent = 'All players';
        } else if (selected.length === 1) {
            filterSelect.textContent = selected[0];
        } else {
            filterSelect.textContent = `${selected.length} players selected`;
        }
        
        console.log('📝 Selection updated:', selected);
    }

    // ============================================
    // CHART FUNCTIONALLITY
    // ============================================
    if (!chartData) {
        console.error('No chart data found!');
        return; // Exit early
    } else {
        console.log('Chart data found:', chartData);
    };

    function initialiseLineChart(chartData) {
        const ctx = document.getElementById('lineChart').getContext('2d');

        // 3. Log what we received
        console.log('📊 Chart data received:');
        console.log('  Labels:', chartData.labels);
        console.log('  Datasets:', chartData.datasets.length, 'players');

        lineChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: chartData.labels,
                datasets: chartData.datasets
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                aspectRatio: 2,
                scales: {                  // axis labels
                    xAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Season'
                        }
                    }],
                    yAxes: [{
                        scaleLabel: {
                            display: true,
                            labelString: 'Attack Stars'
                        },
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                },
                legend: {
                    display: true,
                    position: 'top'
                }
            }
        });
    };


    // ============================================
    // INITIALIZATION
    // ============================================
    // GRAPH INITIALIZATION
    if (window.chartData) {
        console.log('✅ Initializing chart with data from window object');
        initialiseLineChart(window.chartData);
    } else {
        console.error('❌ No chart data found on window object');
    
    }
    // FILTER DISPLAY INITIALIZATION
    if (playerCheckboxes.length > 0) {
        updateFilterDisplay();
        console.log('✅ Initial filter display updated');
    }
});