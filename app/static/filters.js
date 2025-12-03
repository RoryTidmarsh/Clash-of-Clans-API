// ========================================
// UNIVERSAL CHECKBOX FILTER SYSTEM
// ========================================

class FilterManager {
    constructor() {
        this.filters = {};
        this.appliedFilters = {}; // Store the last applied state
        this.callbacks = [];
        this.init();
    }

    init() {
        document.addEventListener('DOMContentLoaded', () => {
            this.setupAllFilters();
            this.setupApplyResetButtons();
            console.log('🎯 FilterManager initialized');
        });
    }

    setupAllFilters() {
        // Auto-detect all filter groups on the page
        document.querySelectorAll('[data-filter-type]').forEach(filterGroup => {
            const filterType = filterGroup.dataset.filterType;
            this.setupFilter(filterType);
        });
    }

    setupFilter(filterType) {
        // Setup dropdown toggle
        const trigger = document.getElementById(`${filterType}-trigger`);
        const panel = document.getElementById(`${filterType}-panel`);
        
        if (trigger && panel) {
            trigger.addEventListener('click', () => {
                this.toggleDropdown(trigger, panel);
            });
        }

        // Setup "Select All"
        const selectAll = document.getElementById(`select-all-${filterType}`);
        if (selectAll) {
            selectAll.addEventListener('change', (e) => {
                this.toggleAllCheckboxes(`.${filterType}-checkbox`, e.target.checked);
                this.updateFilter(filterType);
            });
        }

        // Setup individual checkboxes
        document.querySelectorAll(`.${filterType}-checkbox`).forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateFilter(filterType);
                this.updateSelectAllState(`select-all-${filterType}`, `.${filterType}-checkbox`);
            });
        });

        // Setup clicks on the entire option div
        document.querySelectorAll(`[data-filter-type="${filterType}"] .multi-select-option`).forEach(option => {
            option.addEventListener('click', (e) => {
                // Don't trigger if clicking directly on the checkbox (it handles itself)
                if (e.target.type === 'checkbox') return;
                
                // Find the checkbox in this option and toggle it
                const checkbox = option.querySelector('input[type="checkbox"]');
                if (checkbox) {
                    checkbox.checked = !checkbox.checked;
                    // Trigger the change event to update filters
                    checkbox.dispatchEvent(new Event('change'));
                }
            });
        });

        // Initialize empty filter array
        this.filters[filterType] = [];
        this.appliedFilters[filterType] = [];
    }

    // === APPLY/RESET BUTTON FUNCTIONALITY ===
    setupApplyResetButtons() {
        // Setup Apply button (looks for any button with id containing 'apply')
        const applyButtons = document.querySelectorAll('[id*="apply"], .apply-filters, .btn-apply');
        applyButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.applyFilters();
            });
        });

        // Setup Reset button (looks for any button with id containing 'reset')
        const resetButtons = document.querySelectorAll('[id*="reset"], .reset-filters, .btn-reset');
        resetButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.resetFilters();
            });
        });

        console.log(`🎯 Found ${applyButtons.length} apply buttons and ${resetButtons.length} reset buttons`);
    }

    applyFilters() {
        // Store current filter state as applied state
        this.appliedFilters = { ...this.filters };
        
        console.log('✅ Filters applied:', this.appliedFilters);
        
        // Trigger callbacks with applied filters
        this.triggerApplyChange();
        
        // Visual feedback (optional)
        this.showFilterFeedback('Filters applied!', 'success');
    }

    resetFilters() {
        // Clear all filters
        Object.keys(this.filters).forEach(filterType => {
            this.filters[filterType] = [];
            this.appliedFilters[filterType] = [];
        });
        
        // Update UI to reflect cleared filters
        this.applyAllFiltersToUI();
        
        console.log('🔄 Filters reset');
        
        // Trigger callbacks with empty filters
        this.triggerApplyChange();
        
        // Visual feedback (optional)
        this.showFilterFeedback('Filters reset!', 'info');
    }

    // === HELPER METHODS ===
    updateFilter(filterType) {
        this.filters[filterType] = Array.from(document.querySelectorAll(`.${filterType}-checkbox:checked`))
            .map(cb => cb.value);
        this.triggerFilterChange();
    }

    toggleDropdown(trigger, panel) {
        const isVisible = panel.classList.contains('show');
        // Close all panels first
        document.querySelectorAll('.multi-select-panel').forEach(p => {
            p.classList.remove('show');
            const relatedTrigger = p.previousElementSibling;
            if (relatedTrigger) relatedTrigger.classList.remove('active');
        });
        
        // Toggle current panel
        if (!isVisible) {
            panel.classList.add('show');
            trigger.classList.add('active');
        }
    }

    toggleAllCheckboxes(selector, checked) {
        document.querySelectorAll(selector).forEach(cb => cb.checked = checked);
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
        Object.keys(this.filters).forEach(filterType => {
            this.applyFilterToUI(filterType);
        });
    }

    applyFilterToUI(filterType) {
        // Clear all checkboxes first
        document.querySelectorAll(`.${filterType}-checkbox`).forEach(cb => cb.checked = false);
        
        // Check selected values
        this.filters[filterType].forEach(value => {
            const checkbox = document.querySelector(`.${filterType}-checkbox[value="${value}"]`);
            if (checkbox) checkbox.checked = true;
        });

        this.updateSelectAllState(`select-all-${filterType}`, `.${filterType}-checkbox`);
    }

    showFilterFeedback(message, type = 'info') {
        // Create or update feedback element
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

        // Style based on type
        const colors = {
            success: '#28a745',
            info: '#17a2b8',
            warning: '#ffc107',
            error: '#dc3545'
        };
        feedback.style.backgroundColor = colors[type] || colors.info;
        feedback.textContent = message;

        // Show and hide with animation
        feedback.style.opacity = '1';
        setTimeout(() => {
            feedback.style.opacity = '0';
        }, 2000);
    }

    // === PUBLIC API ===
    getFilters() {
        return { ...this.filters };
    }

    getAppliedFilters() {
        return { ...this.appliedFilters };
    }

    getFilter(filterType) {
        return this.filters[filterType] || [];
    }

    getAppliedFilter(filterType) {
        return this.appliedFilters[filterType] || [];
    }

    setFilter(filterType, values) {
        this.filters[filterType] = values;
        this.applyFilterToUI(filterType);
        this.triggerFilterChange();
    }

    // Callback for real-time filter changes (as user checks/unchecks)
    onFilterChange(callback) {
        this.callbacks.push({ type: 'change', callback });
    }

    // Callback for when filters are applied (when Apply button is clicked)
    onApply(callback) {
        this.callbacks.push({ type: 'apply', callback });
    }

    triggerFilterChange() {
        console.log('🎯 Filters updated:', this.filters);
        this.callbacks
            .filter(cb => cb.type === 'change')
            .forEach(cb => cb.callback(this.filters));
    }

    triggerApplyChange() {
        console.log('✅ Applied filters:', this.appliedFilters);
        this.callbacks
            .filter(cb => cb.type === 'apply')
            .forEach(cb => cb.callback(this.appliedFilters));
    }
}

// Global instance
window.filterManager = new FilterManager();