// ========================================
// COMPONENT 1: SITE HEADER
// ========================================
class SiteHeader extends HTMLElement {
    connectedCallback() {
        // Get attributes for customisation
        const logoUrl = this.getAttribute('logo-url') || '';
        const title = this.getAttribute('title') || 'Clan War Leageue Stats'
        const showRefresh = this.getAttribute('show-refresh') !== 'false';

        this.innerHTML = `
            <div class="site-header">
                <img src="${logoUrl}" alt="Clan Logo" class="site-logo">
                <span class="site-title">${title}</span>
                ${showRefresh ? `
                    <button id="refresh-btn" class="refresh-btn pastel-red-title">
                        &#x21bb; Refresh Data
                    </button>`
                : ''}
            </div> 
            `;
        
        // Event listener for refresh button if it exists
        if (showRefresh) {
            const refreshBtn = this.querySelector('#refresh-btn');   // Reference to the refresh button
            refreshBtn.addEventListener('click', () => {   // Add click event listener
                refreshBtn.disabled = true;   // Disable button to prevent multiple clicks
                refreshBtn.textContent = 'Refreshing...';   // Change button text to indicate action

                fetch('/refresh-data', {method: 'POST'})  // Send POST request to refresh data
                    .then(response => response.json())
                    .then(data => {
                        refreshBtn.textContent = data.message || 'Refreshed!';   // Update button text on success
                        
                        // Update status box with log if available
                        let log = data.log || [];
                        const statusBox = document.getElementById('status-box');
                        if (statusBox) {
                            if (statusBox) {
                                statusBox.textContent = log.join('\n');   // Update status box with log
                            }
                        }
                        setTimeout(() => {  // Reset button after delay
                            refreshBtn.disabled = false;   // Re-enable button after action
                            refreshBtn.textContent = '↻ Refresh Data';   // Reset button text
                        }, 1200);   // 1.2 seconds delay
                    })
                    .catch(error => { // Handle errors
                        console.error('Error refreshing data:', error);
                        refreshBtn.textContent = 'Error! Try Again';   // Update button text on error
                        setTimeout(() => {  // Reset button after delay
                            refreshBtn.disabled = false;   // Re-enable button after action
                            refreshBtn.textContent = '↻ Refresh Data';   // Reset button text
                        }, 2000);   // 2 seconds delay
                    });
            });
        }
    }
}

// ========================================
// COMPONENT 2: NAV BAR
// ========================================
class NavBar extends HTMLElement {
    connectedCallback() {
        const defaultLinks = [
            { href: '/', text: 'Home' },
            { href: '/war-table', text: 'War Table' },
            { href: '/progress-graphs', text: 'Progress Graphs' },
        ];

        // Get links from attribute or use default
        const linksAttr = this.getAttribute('links');
        const links = linksAttr ? JSON.parse(linksAttr) : defaultLinks;

        // Build nav links HTML
        this.innerHTML = `
            <div class="nav-bar">
                <nav>
                    ${links.map(link => `<a href="${link.href}">${link.text}</a>`).join(' ')}
                </nav>
            </div>
        `;
    }
}

// ========================================
// COMPONENT 3: FILTER DROPDOWNS
// ========================================
class FilterDropdown extends HTMLElement {
    connectedCallback() {
        // Get attributes for customisation
        const filterType = this.getAttribute('filter-type') || 'filter';
        const filterLabel = this.getAttribute('filter-label') || 'Items';
        const optionsAttr = this.getAttribute('options');
        
        const options = optionsAttr ? JSON.parse(optionsAttr) : []; // Parse options JSON or use empty array

        // Build dropdown HTML
        this.innerHTML = `
            <label> Select ${filterLabel}:<\label>
            <div class="multiselect-dropdown" data-filter-type="${filterType}"> 
                <div class="multi-select-trigger" id="${filterType}-trigger">
                    <span>Select ${filterLabel}</span>
                    <div class="arrow">&#9660;</div>
                </div>
                <div class="multi-select-panel" id="${filterType}-panel">
                    <div class="multi-select-option select-all-option">
                        <input type="checkbox" id="select-all-${filterType}">
                        <span>Select All</span>
                    </div>
                    ${options.map(option => `
                        <div class="multi-select-option">
                            <input type="checkbox" class="${filterType}-checkbox" value="${option.value}">
                            <span>${option}</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        // Initialise filter functionality
        setTimeout(() => {
            if (window.filterManager) {
                window.filterManager.setupFilter(filterType);
            }
        }, 0);   
    }
}

// ========================================
// COMPONENT 4: TABLE WITH FILTERING
// ========================================
class FilterableTable extends HTMLElement {
    connectedCallBack() {
        const tableId = this.getAttribute('table-id') || 'data-table';
        const title = this.getAttribute('title') || 'Data Table';
        const columnsAttr = this.getAttribute('columns');
        const dataAttr = this.getAttribute('data');
        const filterColumn = this.getAttribute('filter-column') || '0';

        const columns = columnsAttr ? JSON.parse(columnsAttr) : [];
        const data = dataAttr ? JSON.parse(dataAttr) : [];

        // Build table HTML
        this.innerHTML = `
            <section>
                <h2>${title}</h2>
                <table id="${tableId}"
                    <thead>
                        <tr>
                            ${columns.map(col => `
                                <th class="sortable">
                                    <button class="sortable-button" data-column="${col}">
                                        ${col}
                                        <span class="sort-icon">&#9662;</span>
                                    </button>
                                </th>
                            `).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(row => `
                            <tr>
                                ${columns.map(col => `<td>${row[col] || ''}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </section>
        `;

        // Store original data for filtering
        this.originalData = data;
        this.filterColumn = filterColumn;
        this.tableId = tableId;

        // Register with filter Manager
        this.setupFiltering();
    }
    setupFiltering() {
        // Wait for filterManager to be ready
        const checkFilterManager = setInterval(() => {
            if (window.filterManager) {
                clearInterval(checkFilterManager);
                
                // Listen for filter changes
                window.filterManager.onApply((appliedFilters) => {
                this.applyFilters(appliedFilters);
                });
            }
        }, 100);
    }

    applyFilters(filters){
        const tbody = this.querySelector('tbody');
        const filterType = Object.keys(filters)[0]; // get the first filter type
        const selectedValues = filters[filterType] || [];

        // if no filters applied, show all data
        if (selectedValues.length === 0) {
            this.renderRows(this.originalData);
            return;
        }

        // Filter data based on selected values
        const filteredData = this.originalData.filter(row => {
            const columnValue = Object.values(row)[this.filterColumnIndex];
            return selectedValues.includes(columnValue);
        });

        // Render filtered rows
        this.renderRows(filteredData);
    }

    renderAllRows(data) {
        this.renderRows(data);
    }

    renderRows(data){
        const tbody = this.querySelector('tbody');
        const columns = Object.keys(data[0] || {});

        // If no data, show no data message
        if (data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="${columns.length}" style="text-align: center; font-style: italic; color: #666;">No data available for selected filters.</td>
                </tr>
            `;
            return;
        }

        // Build rows HTML
        tbody.innerHTML = data.map(row => `
            <tr>
                ${columns.map(col => `<td>${row[col] || ''}</td>`).join('')}
            </tr>
        `).join('');
    }
}

// ========================================
// COMPONENT 5: FILTER CONTROLS
// ========================================
class FilterControls extends HTMLElement {
    connectedCallback() {
        this.innerHTML = `
            <div class="filter-controls">
                <button id="apply-filters" type="button" class="filter-button">Apply</button>
                <button id="reset-filters" type="button" class="filter-button">Reset</button>
            </div>
            `;
        // The buttons will be picked up automatically by FilterManager
        // which looks for elements with id containing 'apply' or 'reset'
    }
}

// ========================================
// UNIVERSAL CHECKBOX FILTER SYSTEM
// ========================================
class FilterManager {
    constructor() {
        this.filters = {};
        this.appliedFilters = {};
        this.callbacks = [];
        this.init();
    }

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setupAll());
        } else {
            this.setupAll();
        }
    }

    setupAll() {
        this.setupAllFilters();
        this.setupApplyResetButtons();
        console.log('FilterManager initialised');
    }

    setupAllFilters() {
        document.querySelectorAll('[data-filter-type]').forEach(dropdown => {
            const filterType = filterGroup.dataset.filterType;
            this.setupFilter(filterType);
        });
    }

    setupFilter(filterType) {
        const trigger = document.getElementById(`${filterType}-trigger`);
        const panel = document.getElementById(`${filterType}-panel`);

        // Setup dropdown toggle
        if (trigger && panel) {
            // Toggle panel visibility
            trigger.addEventListener('click', () => {
                panel.classList.toggle('visible');
            });
        }

        // Setup "Select All" checkbox
        const selectAll = document.getElementById(`select-all-${filterType}`);
        if (selectAll) {
            selectAll.addEventListener('change', (e) => {
                this.toggleAllCheckboxes(`.${filterType}-checkbox`, e.target.checked);
                this.updateFilter(filterType);        
            });
        }

        // Setup individual checkbox changes
        document.querySelectorAll(`.${filterType}-checkbox`).forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateFilter(filterType);
                this.updateSelectAllState(`select-all-${filterType}`, `.${filterType}-checkbox`);
            });
        });

        // Setup clicks on checkboxes' parent divs
        document.querySelectorAll(`[data-filter-type="${filterType}"] .multi-select-option`).forEach(option => {
            option.addEventListener('click', (e) => {
                if (e.target.type === 'checkbox') return;

                const checkbox = option.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    checkbox.dispatchEvent(new Event('change'));
                }
            });
        });

        // Initialise filter state
        this.filters[filterType] = [];
        this.appliedFilters[filterType] = [];
    }

    setupApplyResetButtons() {
        // Get apply buttons and wire up event listeners
        const applyButtons = document.querySelectorAll('[id*="apply"], .apply-filters, btn-apply');
        applyButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.applyFilters();
            });
        });

        // Get reset buttons and wire up event listeners
        const resetButtons = document.querySelectorAll('[id*="reset"], .reset-filters, btn-reset');
        resetButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.resetFilters();
            });
        });

        console.log(`🎯 Found ${applyButtons.length} apply buttons and ${resetButtons.length} reset buttons`);
    }

    applyFilters() {
        // Copy current filters to applied filters
        this.appliedFilters = { ...this.filters };
        console.log('✅ Filters applied:', this.appliedFilters);
        
        // Trigger callbacks
        this.triggerApplyChange();
        this.showFilterFeedback('Filters applied!', 'success');
    }

    resetFilters() {
        // Clear all filters
        Object.keys(this.filters).forEach(filterType => {
            this.filters[filterType] = [];
            this.appliedFilters[filterType] = [];
        });

        this.applyAllFiltersToUI();
        console.log('♻️ Filters reset');
        this.triggerApplyChange();
        this.showFilterFeedback('Filters reset!', 'info');
    }

    updateFilter(filterType) {
        // Update filter values based on checked checkboxes
        this.filters[filterType] = Array.from(document.querySelectorAll(`.${filterType}-checkbox:checked`))
            .map(checkbox => checkbox.value);

        // Trigger filter change
        this.triggerFilterChange();
        console.log(`🔄 Updated filter "${filterType}":`, this.filters[filterType]);
    }

    toggleDropdown(trigger, panel) {
        const isVisible = panel.classList.contains('show'); // Check current visibility
        document.querySelectorAll('.multi-select-panel').forEach(p => {  // Close all panels
            p.classList.remove('show');      // Remove the show class, hiding the panel
            const relatedTrigger = p.previousElementSibling; 
            if (relatedTrigger) {
                relatedTrigger.classList.remove('active');  // removes active class from the button
            }
        });

        if (!isVisible) {
            // If closed and then opened mark as such
            panel.classList.add('show');
            trigger.classList.add('active');
        }
    }

    toggleAllCheckboxes(checkboxSelector, isChecked) {
        document.querySelectorAll(checkboxSelector).forEach(checkbox => {
            checkbox.checked = isChecked;
        });
    }

    updateSelectAllState(selectAllId, checkboxSelector) {
        const selectAll = document.getElementById(selectAllId);
        const checkboxes = document.querySelectorAll(checkboxSelector);
        const checkedBoxes = document.querySelectorAll(`${checkboxSelector}:checked`);

        if (selectAll) {
            selectAll.checked = checkboxes.length === checkedBoxes.length;
            selectAll.indeterminate = checkedBoxes.length > 0 && checkedBoxes.length < checkboxes.length;
        }
    }

    applyAllFiltersToUI() {
        document.querySelectorAll(`.${filterType}-checkbox`).forEach(checkbox => {
            checkbox.checked = false;
        });

        this.filters[filterType].forEach(value => {
            const checkbox = document.querySelector(`.${filterType}-checkbox[value="${value}"]`);
            if (checkbox) checkbox.checked = true;
        });

        this.updateSelectAllState(`select-all-${filterType}`, `.${filterType}-checkbox`);
    }

    showFilterFeedback(message, type = 'info') {
        let feedback = document.getElementById('filter-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.id = 'filter-feedback';
            feedback.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 10px 20px;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 9999;
                opacity: 0;
                transition: opacity 0.3s ease;
            `;
            document.body.appendChild(feedback);
        }

        const colors = {
            success: '#28a745',
            info: '#17a2b8',
            warning: '#ffc107',
            error: '#dc3545'
        };
        feedback.style.backgroundColor = colors[type] || colors.info;
        feedback.textContent = message;

        feedback.style.opacity = '1';
        setTimeout(() => {
        feedback.style.opacity = '0';
        }, 2000);
    }

    getFilters() {
        return this.appliedFilters;
    }

    getAppliedFilters() {
        return this.appliedFilters;
    }

    onFilterChange(callback) {
        this.callbacks.push({type: 'change',callback});
    }

    onApply(callback) {
        this.callbacks.push({type: 'apply',callback});
    }

    triggerFilterChange() {
        console.log('🎯 Filters updated:', this.filters);
        this.callbacks
            .filter(cb => cb.type === 'change')
            .forEach(cb => cb.callback(this.filters));
    }

    triggerApplyChange() {
        console.log('🎯 Filters applied:', this.appliedFilters);
        this.callbacks
            .filter(cb => cb.type === 'apply')
            .forEach(cb => cb.callback(this.appliedFilters));
    }
}

// ========================================
// PAGE LAYOUT COMPONENT 
// ========================================
class PageLayout extends HTMLElement {
    connectedCallBack() {
        const logoUrl = this.getAttribute('logo-url') || "https://api-assets.clashofclans.com/badges/512/Z4CSpLlobD7Xl40FZhCQ0BzvZUcAdLvBEBOavqiHN90.png";
        const title = this.getAttribute('title') || 'Clan War League Stats';
        const favicon = this.getAttribute('favicon') || "https://api-assets.clashofclans.com/badges/512/Z4CSpLlobD7Xl40FZhCQ0BzvZUcAdLvBEBOavqiHN90.png";
        const extraCss = this.getAttribute('extra-css') || ''; // Additional CSS URL if any

        this.setupHead(title, favicon, extraCss);

        const content = this.innerHTML;
        this.innerHTML = `
            <site-header logo-url="${logoUrl}" title="${title}" show-refresh="true"></site-header>
            <nav-bar></nav-bar>
            <main>
                ${content}
            </main>
        `;

        this.setRandomBackground();
    }

    setupHead(title, favicon, extraCss) {
        // Set document title
        document.title = title;
        
        // Set charset if not already set
        if (!document.querySelector('meta[charset]')) {
        const charset = document.createElement('meta');
        charset.setAttribute('charset', 'UTF-8');
        document.head.insertBefore(charset, document.head.firstChild);
        }
        
        // Set viewport if not already set
        if (!document.querySelector('meta[name="viewport"]')) {
        const viewport = document.createElement('meta');
        viewport.name = 'viewport';
        viewport.content = 'width=device-width, initial-scale=1.0';
        document.head.appendChild(viewport);
        }
        
        // Add Google Fonts
        if (!document.querySelector('link[href*="fonts.googleapis.com"]')) {
        const fontLink = document.createElement('link');
        fontLink.href = 'https://fonts.googleapis.com/css2?family=Montserrat:wght@600;400&display=swap';
        fontLink.rel = 'stylesheet';
        document.head.appendChild(fontLink);
        }
        
        // Add main stylesheet
        if (!document.querySelector('link[href*="style.css"]')) {
        const styleLink = document.createElement('link');
        styleLink.rel = 'stylesheet';
        styleLink.href = '../static/style.css';
        document.head.appendChild(styleLink);
        }
        
        // Set favicon if provided
        if (favicon) {
        let link = document.querySelector("link[rel*='icon']");
        if (!link) {
            link = document.createElement('link');
            link.rel = 'icon';
            link.type = 'image/png';
            document.head.appendChild(link);
        }
        link.href = favicon;
        }
        
        // Add any extra CSS files if specified (comma-separated)
        if (extraCss) {
        extraCss.split(',').forEach(cssFile => {
            const cssLink = document.createElement('link');
            cssLink.rel = 'stylesheet';
            cssLink.href = cssFile.trim();
            document.head.appendChild(cssLink);
        });
        }
    }
    setRandomBackground() {
        const backgrounds = [
            "https://images.alphacoders.com/782/782653.png",
            "https://wallpapercave.com/wp/wp14810994.webp",
            "https://wallpapercave.com/wp/wp14645871.jpg",
        ];

        const idx = Math.floor(Math.random() * backgrounds.length);
        document.body.style.backgroundImage = `url('${backgrounds[idx]}')`;
    }
}

// ========================================
// REGISTER ALL COMPONENTS
// ========================================

customElements.define('site-header', SiteHeader);
customElements.define('nav-bar', NavBar);
customElements.define('filter-dropdown', FilterDropdown);
customElements.define('filterable-table', FilterableTable);
customElements.define('filter-controls', FilterControls);
customElements.define('page-layout', PageLayout);

// Initialise FilterManager globally
window.filterManager = new FilterManager();

console.log('ðŸš€ Components loaded successfully');