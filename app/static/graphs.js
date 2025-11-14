// ========================================
// CLASH OF CLANS - GRAPHS.JS
// Handles interactive filtering and chart updates
// ========================================

// Global variables
let lineChart = null; // Will store Chart.js instance

// Function to initialize the line chart
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Graphs.js loaded!');
    const button = document.getElementById('apply-filters');
    
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

    // Check if chart data exists (from Flask)
    if (window.chartData) {
        console.log('✅ Initializing chart with data from window object');
        initialiseLineChart(window.chartData);
    } else {
        console.error('❌ No chart data found on window object');
    
    }

});