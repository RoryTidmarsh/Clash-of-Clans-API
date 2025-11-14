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
    function getYAxisLabel(statValue){
            const statDropdown = document.getElementById('stat-filter');
            const selectedOption = statDropdown.querySelector(`option[value="${statValue}"]`);
            return selectedOption ? selectedOption.textContent : statValue;
        }
    function updateChart(selectedPlayers, selectedStat) {
        console.log('🔄 Updating chart with:', { selectedPlayers, selectedStat });
        
        // Build query parameters
        const params = new URLSearchParams();
        selectedPlayers.forEach(player => params.append('selected_players', player));
        params.append('stat', selectedStat);
        
        // Show loading state (optional but nice UX)
        const graphSection = document.getElementById('graph-section');
        graphSection.style.opacity = '0.5';
        
        // Fetch new data from API
        fetch(`/api/graph-data?${params.toString()}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`API returned ${response.status}`);
                }
                return response.json();
            })
            .then(newChartData => {
                console.log('✅ Received new chart data:', newChartData);
                
                // Destroy old chart if it exists
                if (lineChart) {
                    lineChart.destroy();
                }
                
                // Get the Y-axis label for the selected stat
                const yAxisLabel = getYAxisLabel(selectedStat);
                
                // Create new chart with updated data
                const ctx = document.getElementById('lineChart').getContext('2d');
                lineChart = new Chart(ctx, {
                    type: 'line',
                    data: {
                        labels: newChartData.labels,
                        datasets: newChartData.datasets
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: true,
                        aspectRatio: 2,
                        scales: {
                            xAxes: [{
                                scaleLabel: {
                                    display: true,
                                    labelString: 'Season'
                                }
                            }],
                            yAxes: [{
                                scaleLabel: {
                                    display: true,
                                    labelString: yAxisLabel  // Dynamic label!
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
                
                // Remove loading state
                graphSection.style.opacity = '1';
                console.log('✅ Chart updated successfully');
            })
            .catch(error => {
                console.error('❌ Error updating chart:', error);
                alert('Failed to update chart. Please try again.');
                graphSection.style.opacity = '1';
            });
    }

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
                            labelString: window.yLabel || "Attack Stars"  // Default label
                        },
                        ticks: {
                            beginAtZero: true
                        }
                    }]
                },
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        
                        padding:15,
                        fontSize:13,
                        // generateLabels: function(chart) {
                        //     // Custom legend to show both line and point
                        //     return chart.data.datasets.map(function(dataset, i) {
                        //         return {
                        //             text: dataset.label,
                        //             fillStyle: dataset.borderColor,        // Color of the marker
                        //             strokeStyle: dataset.borderColor,      // Border color
                        //             lineWidth: 2,                           // Line thickness in legend
                        //             hidden: !chart.isDatasetVisible(i),
                        //             index: i
                        //         };
                        //     });
                        // }
                    }
                    }
            }
        });
    };

    // ============================================
    // APPLY BUTTON FUNCTIONALITY
    // ============================================
    const applyButton = document.getElementById('apply-filters');
    if (applyButton) {
        applyButton.addEventListener('click', function() {
            console.log('🎯 Apply button clicked');
            
            // Get selected players
            const selectedPlayers = Array.from(playerCheckboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            
            // Validate at least one player is selected
            if (selectedPlayers.length === 0) {
                alert('Please select at least one player');
                return;
            }
            
            // Get selected statistic
            const statDropdown = document.getElementById('stat-filter');
            const selectedStat = statDropdown.value;
            
            console.log('📊 Filters applied:', { selectedPlayers, selectedStat });
            
            // Update the chart
            updateChart(selectedPlayers, selectedStat);
        });
    }

    // ============================================
    // RESET BUTTON FUNCTIONALITY
    // ============================================
    const resetButton = document.getElementById('reset-filters');
    if (resetButton) {
        resetButton.addEventListener('click', function() {
            console.log('🔄 Reset button clicked');
            
            // 1. Check all player checkboxes
            playerCheckboxes.forEach(cb => {
                cb.checked = true;
            });
            
            // 2. Update "Select All" checkbox
            if (selectAllCheckbox) {
                selectAllCheckbox.checked = true;
                selectAllCheckbox.indeterminate = false;
            }
            
            // 3. Update filter display text
            updateFilterDisplay();
            
            // 4. Reset statistic dropdown to first option (Attack Stars)
            const statDropdown = document.getElementById('stat-filter');
            statDropdown.selectedIndex = 0;
            
            // 5. Get all players for the reset
            const allPlayers = Array.from(playerCheckboxes).map(cb => cb.value);
            
            // 6. Update chart with default settings
            updateChart(allPlayers, statDropdown.value);
            
            console.log('✅ Filters reset to defaults');
        });
    }


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