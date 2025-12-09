// ========================================
// COMPONENT 1: SITE HEADER
// ========================================
class SiteHeader extends HTMLElement {
    connectedCallback() {
        // Get attributes for customisation
        const logoUrl = this.getAttribute('logo-url') || '';
        const title = this.getAttribute('title') || 'Clan War Leageue Stats'
        // const showRefresh = this.getAttribute('show-refresh') !== 'false';

        this.innerHTML = `
            <div class="site-header">
                <img src="${logoUrl}" alt="Clan Logo" class="site-logo">
                <span class="site-title">${title}</span>
                
            </div> 
            `;

        // // Commented out old refresh button- this is suppore in the ~/refresh/ directory now
        // // The website no longer directly handles data refreshes
        // ${showRefresh ? `
        //             <button id="refresh-btn" class="refresh-btn pastel-red-title">
        //                 &#x21bb; Refresh Data
        //             </button>`
        //         : ''}
        
        // // Event listener for refresh button if it exists
        // if (showRefresh) {
        //     const refreshBtn = this.querySelector('#refresh-btn');   // Reference to the refresh button
        //     refreshBtn.addEventListener('click', () => {   // Add click event listener
        //         refreshBtn.disabled = true;   // Disable button to prevent multiple clicks
        //         refreshBtn.textContent = 'Refreshing...';   // Change button text to indicate action

        //         fetch('/refresh-data', {method: 'POST'})  // Send POST request to refresh data
        //             .then(response => response.json())
        //             .then(data => {
        //                 refreshBtn.textContent = data.message || 'Refreshed!';   // Update button text on success
                        
        //                 // Update status box with log if available
        //                 let log = data.log || [];
        //                 const statusBox = document.getElementById('status-box');
        //                 if (statusBox) {
        //                     if (statusBox) {
        //                         statusBox.textContent = log.join('\n');   // Update status box with log
        //                     }
        //                 }
        //                 setTimeout(() => {  // Reset button after delay
        //                     refreshBtn.disabled = false;   // Re-enable button after action
        //                     refreshBtn.textContent = '↻ Refresh Data';   // Reset button text
        //                 }, 1200);   // 1.2 seconds delay
        //             })
        //             .catch(error => { // Handle errors
        //                 console.error('Error refreshing data:', error);
        //                 refreshBtn.textContent = 'Error! Try Again';   // Update button text on error
        //                 setTimeout(() => {  // Reset button after delay
        //                     refreshBtn.disabled = false;   // Re-enable button after action
        //                     refreshBtn.textContent = '↻ Refresh Data';   // Reset button text
        //                 }, 2000);   // 2 seconds delay
        //             });
        //     });
        // }
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
        
        let options = [];
        try {
            options = optionsAttr ? JSON.parse(optionsAttr) : [];
        } catch (e) {
            // Fallback if optionsAttr was passed as a simple CSV-like string
            options = optionsAttr ? optionsAttr.split(',').map(s => s.trim()) : [];
        }

        // Normalize options: allow either string or {value,label}
        const optionItems = options.map(opt => {
            if (typeof opt === 'object' && opt !== null) {
                return { value: String(opt.value), label: String(opt.label) };
            } else {
                return { value: String(opt), label: String(opt) };
            }
        });

        const isSingleSelect = (filterType === 'stat'); // special-case stat to single-select (radio)
        const selectAllHTML = isSingleSelect ? '' : `
            <div class="multi-select-option select-all-option">
                <input type="checkbox" id="select-all-${filterType}">
                <span>Select All</span>
            </div>`;

        // Build dropdown HTML. For 'stat' we render radio inputs (single-select) but keep the class `${filterType}-checkbox`
        this.innerHTML = `
            <label> Select ${filterLabel}:</label>
            <div class="multi-select-dropdown" data-filter-type="${filterType}"> 
                <div class="multi-select-trigger" id="${filterType}-trigger">
                    <span id="${filterType}-count">Select ${filterLabel}</span>
                    <div class="arrow">&#9660;</div>
                </div>
                <div class="multi-select-panel" id="${filterType}-panel">
                    ${selectAllHTML}
                    ${optionItems.map(option => `
                        <div class="multi-select-option">
                            <input type="${isSingleSelect ? 'radio' : 'checkbox'}" name="${filterType}-input" class="${filterType}-checkbox" value="${option.value}" id="${filterType}-${option.value}">
                            <label for="${filterType}-${option.value}">${option.label}</label>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
        
        // Initialise filter functionality
        setTimeout(() => {
            if (window.filterManager) {
                window.filterManager.setupFilter(filterType);

                // If single-select (stat), default to 'attack_stars' if present
                if (isSingleSelect) {
                    const defaultValue = 'attack_stars';
                    const defaultInput = this.querySelector(`.${filterType}-checkbox[value="${defaultValue}"]`);
                    if (defaultInput) {
                        defaultInput.checked = true;
                        // Update filter state inside FilterManager so the default appears without clicking Apply
                        if (window.filterManager && typeof window.filterManager.updateFilter === 'function') {
                            window.filterManager.updateFilter(filterType);
                            // Also pre-fill appliedFilters so graphs.js can see a starting value if it queries getAppliedFilters before Apply
                            window.filterManager.appliedFilters[filterType] = [defaultValue];
                        }
                        // Update visible trigger text to the label of the default
                        const countSpan = document.getElementById(`${filterType}-count`);
                        const optionLabel = this.querySelector(`label[for="${filterType}-${defaultValue}"]`);
                        if (countSpan && optionLabel) countSpan.textContent = optionLabel.textContent;
                    }
                } else {
                    // Add listeners to update count when checkboxes change
                    const checkboxes = this.querySelectorAll(`.${filterType}-checkbox`);
                    const countSpan = document.getElementById(`${filterType}-count`);
                    
                    checkboxes.forEach(checkbox => {
                        checkbox.addEventListener('change', () => {
                            const checkedCount = this.querySelectorAll(`.${filterType}-checkbox:checked`).length;
                            if (checkedCount > 0) {
                                countSpan.textContent = `${checkedCount} selected`;
                            } else {
                                countSpan.textContent = `Select ${filterLabel}`;
                            }
                        });
                    });
                }
            }
        }, 0);   
    }
}

// ========================================
// COMPONENT 4: TABLE WITH FILTERING
// ========================================
class FilterableTable extends HTMLElement {
    // Helper function to escape HTML to prevent XSS
    escapeHtml(text) {
        if (text == null) return '';
        const div = document.createElement('div');
        div.textContent = String(text);
        return div.innerHTML;
    }

    // Helper function to render table body
    _renderTableBody(data) {
        const tbody = this.querySelector('tbody');
        const columns = this.columns;
        
        if (!tbody || !columns) return;
        
        // Build rows HTML
        tbody.innerHTML = data.map(row => `
            <tr>
                ${columns.map(col => `<td>${this.escapeHtml(row[col])}</td>`).join('')}
            </tr>
        `).join('');
    }

    connectedCallback() {
        const tableId = this.getAttribute('table-id') || 'data-table';
        const title = this.getAttribute('title') || 'Data Table';
        const columnsAttr = this.getAttribute('columns');
        const dataAttr = this.getAttribute('data');
        const filterColumn = this.getAttribute('filter-column') || '0';

        console.log(`🔍 FilterableTable Debug (${tableId}):`, {
            columnsAttr,
            dataAttr: dataAttr ? dataAttr.substring(0, 100) + '...' : 'null',
            columnsAttrType: typeof columnsAttr
        });

        // Parse columns with error handling
        let columns = [];
        try {
            columns = columnsAttr ? JSON.parse(columnsAttr) : [];
        } catch (error) {
            console.error(`❌ Error parsing columns for ${tableId}:`, error);
            console.error('Columns attribute value:', columnsAttr);
            this.innerHTML = `<div style="color: red; padding: 20px;">Error parsing table columns: ${this.escapeHtml(error.message)}</div>`;
            return;
        }

        // Parse data with error handling
        let data = [];
        try {
            data = dataAttr ? JSON.parse(dataAttr) : [];
        } catch (error) {
            console.error(`❌ Error parsing data for ${tableId}:`, error);
            console.error('Data attribute value:', dataAttr ? dataAttr.substring(0, 200) : 'null');
            this.innerHTML = `<div style="color: red; padding: 20px;">Error parsing table data: ${this.escapeHtml(error.message)}</div>`;
            return;
        }

        console.log(`📊 Parsed data for ${tableId}:`, {
            columns,
            dataLength: data.length,
            firstRow: data[0] || 'empty'
        });

        // Validate that we have columns
        if (!columns || columns.length === 0) {
            console.warn(`⚠️  No columns provided for ${tableId}`);
            this.innerHTML = `<div style="text-align: center; padding: 20px; color: #999;">No columns defined for table</div>`;
            return;
        }

        // Build table HTML
        this.innerHTML = `
            <section>
                <h2>${this.escapeHtml(title)}</h2>
                <table id="${this.escapeHtml(tableId)}">
                    <thead>
                        <tr>
                            ${columns.map(col => `
                                <th class="sortable">
                                    <button class="sortable-button" data-column="${this.escapeHtml(col)}">
                                        ${this.escapeHtml(col)}
                                        <span class="sort-icon">&#9662;</span>
                                    </button>
                                </th>
                            `).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(row => `
                            <tr>
                                ${columns.map(col => `<td>${this.escapeHtml(row[col])}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </section>
        `;

        console.log(`✅ Table HTML injected for ${tableId} with ${data.length} rows`);

        // Store original data for filtering
        this.originalData = data;
        this.filterColumnIndex = parseInt(filterColumn);
        this.tableId = tableId;
        this.columns = columns;
        this.currentData = data;  // Initialize current data with original data

        // Setup sorting immediately after table creation
        this.setupSorting(columns);

        // Register with filter Manager
        this.setupFiltering();
    }
    setupFiltering() {
        // Wait for filterManager to be ready
        let checkInterval, timeoutId;
        
        checkInterval = setInterval(() => {
            if (window.filterManager) {
                clearInterval(checkInterval);
                clearTimeout(timeoutId);
                
                console.log(`🔗 FilterManager connected for ${this.tableId || 'table'}`);
                //Log current filters
                console.log('🎯 Current filters:', window.filterManager.getAppliedFilters());
                // Listen for filter changes
                window.filterManager.onApply((appliedFilters) => {
                this.applyFilters(appliedFilters);
                });
            }
        }, 100);
        
        timeoutId = setTimeout(() => {
            clearInterval(checkInterval);
            if (!window.filterManager) {
                console.warn('⚠️  FilterManager not found after timeout');
            }
        }, 5000);
    }

    applyFilters(filters){
        console.log(`🔍 applyFilters called with filters:`, filters);

        // Get all filter types
        const filterTypes = Object.keys(filters);
        
        if (filterTypes.length === 0) {
            this.renderRows(this.originalData);
            return;
        }

        // Filter data by ALL active filters
        const filteredData = this.originalData.filter(row => {
            // Row must match ALL filter conditions
            return filterTypes.every(filterType => {
                const selectedValues = filters[filterType] || [];
                
                // Skip if no values selected for this filter
                if (selectedValues.length === 0) return true;

                // Find matching column
                const columnName = this.columns.find(col => {
                    const colLower = col.toLowerCase();
                    const filterLower = filterType.toLowerCase();
                    const colClean = col.replace(/[^a-z0-9]/g, '').toLowerCase();
                    return colLower.includes(filterLower) || filterLower.includes(colClean);
                }) || filterType;

                const columnValue = String(row[columnName] || '');
                const matches = selectedValues.includes(columnValue);
            
                return matches;
            });
        });

        console.log(`✅ Filtered by ${filterTypes.join(', ')}:`, {matchedRows: filteredData.length});
        this.renderRows(filteredData);
    }

    renderAllRows(data) {
        this.renderRows(data);
    }

    renderRows(data){
        const tbody = this.querySelector('tbody');
        // Use stored columns instead of parsing from header
        const columns = this.columns;

        // If no data, show no data message
        if (data.length === 0) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="${columns.length}" style="text-align: center; font-style: italic; color: #666;">No data available for selected filters.</td>
                </tr>
            `;
            return;
        }

        // Store the current data for sorting
        this.currentData = data;
        
        // Reset sort state when data changes
        this.currentSortColumn = null;
        this.sortDirection = 1;
        
        // Update sort icons
        const headers = this.querySelectorAll('thead th.sortable');
        headers.forEach(h => {
            const icon = h.querySelector('.sort-icon');
            if (icon) {
                icon.textContent = '▾';
            }
            h.classList.remove('active'); // Remove active class instead of setting opacity
        });
        
        // Render the table body
        this._renderTableBody(data);
}

setupSorting(columns) {
    const table = this.querySelector('table');
    const headers = this.querySelectorAll('thead th.sortable');
    const tbody = this.querySelector('tbody');
    
    if (!table || !tbody) {
        console.warn('⚠️  Table or tbody not found, skipping sort setup');
        return;
    }
    
    // Initialize sorting state on the instance
    if (this.currentSortColumn === undefined) {
        this.currentSortColumn = null;
        this.sortDirection = 1;
    }

    if (!this.sortEventListeners) {
        this.sortEventListeners = new Map();
    }

    headers.forEach((header, index) => {
        const button = header.querySelector('.sortable-button');
        if (!button) return;
        
        button.style.cursor = 'pointer';
        
        const handleSort = (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            const columnName = columns[index];
            const dataToSort = [...this.currentData];

            if (dataToSort.length === 0) return;

            // If clicking the same column, toggle direction
            if (this.currentSortColumn === columnName) {
                this.sortDirection *= -1;
            } else {
                this.sortDirection = 1;
                this.currentSortColumn = columnName;
            }

            // Sort the data array
            dataToSort.sort((rowA, rowB) => {
                const cellA = rowA[columnName];
                const cellB = rowB[columnName];

                if (cellA == null && cellB == null) return 0;
                if (cellA == null) return 1;
                if (cellB == null) return -1;

                const strA = String(cellA).trim();
                const strB = String(cellB).trim();

                const numA = parseFloat(strA);
                const numB = parseFloat(strB);
                
                if (!isNaN(numA) && !isNaN(numB)) {
                    return (numA - numB) * this.sortDirection;
                } else {
                    const compareResult = strA.toLowerCase().localeCompare(strB.toLowerCase());
                    return compareResult * this.sortDirection;
                }
            });

            // Re-render the table with sorted data
            this._renderTableBody(dataToSort);

            // Remove active class from all headers and reset sort icons
            headers.forEach(h => {
                h.classList.remove('active');
                const icon = h.querySelector('.sort-icon');
                if (icon) {
                    icon.textContent = '▾';
                }
            });
            
            // Add active class to clicked header
            header.classList.add('active');
            const activeIcon = button.querySelector('.sort-icon');
            if (activeIcon) {
                activeIcon.textContent = this.sortDirection === 1 ? '▾' : '▴';
            }

            console.log(`📊 Sorted by ${columnName} (${this.sortDirection === 1 ? 'ASC' : 'DESC'})`);
        };
        
        const existingListener = this.sortEventListeners.get(button);
        if (existingListener) {
            button.removeEventListener('click', existingListener);
        }
        
        button.addEventListener('click', handleSort);
        this.sortEventListeners.set(button, handleSort);
    });
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
        document.querySelectorAll('[data-filter-type]').forEach(filterGroup => {
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
                this.toggleDropdown(trigger, panel);
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

        // Setup individual checkbox changes (works for both checkboxes and radio inputs)
        document.querySelectorAll(`.${filterType}-checkbox`).forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateFilter(filterType);
                this.updateSelectAllState(`select-all-${filterType}`, `.${filterType}-checkbox`);
            });
        });

        // Setup clicks on checkboxes' parent divs (fallback for clicking other areas)
        document.querySelectorAll(`[data-filter-type="${filterType}"] .multi-select-option`).forEach(option => {
            option.addEventListener('click', (e) => {
                // Skip if clicking the label or input (they have native behavior)
                if (e.target.tagName === 'LABEL' || e.target.type === 'checkbox' || e.target.type === 'radio') {
                    return;
                }

                // Only toggle checkbox if clicking other areas of the option div
                const checkbox = option.querySelector('input[type="checkbox"], input[type="radio"]');
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
        const applyButtons = document.querySelectorAll('[id*="apply"], .apply-filters, .btn-apply');
        applyButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.applyFilters();
            });
        });

        // Get reset buttons and wire up event listeners
        const resetButtons = document.querySelectorAll('[id*="reset"], .reset-filters, .btn-reset');
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
        // Update filter values based on checked inputs (works for checkboxes and radio inputs)
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
        Object.keys(this.filters).forEach(filterType => {  // FIXED: Loop through all filter types
            document.querySelectorAll(`.${filterType}-checkbox`).forEach(checkbox => {
                checkbox.checked = false;
            });

            this.filters[filterType].forEach(value => {
                const checkbox = document.querySelector(`.${filterType}-checkbox[value="${value}"]`);
                if (checkbox) checkbox.checked = true;
            });

            this.updateSelectAllState(`select-all-${filterType}`, `.${filterType}-checkbox`);
        });
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
    connectedCallback() {
        const logoUrl = this.getAttribute('logo-url') || "https://api-assets.clashofclans.com/badges/512/Z4CSpLlobD7Xl40FZhCQ0BzvZUcAdLvBEBOavqiHN90.png";
        const title = this.getAttribute('title') || 'Clan War League Stats';
        const favicon = this.getAttribute('favicon') || "https://api-assets.clashofclans.com/badges/512/Z4CSpLlobD7Xl40FZhCQ0BzvZUcAdLvBEBOavqiHN90.png";
        const extraCss = this.getAttribute('extra-css') || ''; // Additional CSS URL if any
        // const showRefresh = this.getAttribute('show-refresh') || 'true';

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

console.log('🚀 Components loaded successfully');