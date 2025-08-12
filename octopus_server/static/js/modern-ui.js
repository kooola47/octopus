// 🐙 Octopus Modern UI JavaScript

class OctopusUI {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.startPeriodicUpdates();
    }

    setupEventListeners() {
        // Auto-refresh toggle
        document.addEventListener('change', (e) => {
            if (e.target.id === 'autoRefresh') {
                this.toggleAutoRefresh(e.target.checked);
            }
        });

        // Search functionality
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('search-input')) {
                this.debounce(() => this.handleSearch(e.target), 300)();
            }
        });

        // Page size selector
        document.addEventListener('change', (e) => {
            if (e.target.classList.contains('page-size-selector')) {
                this.changePageSize(e.target.value);
            }
        });

        // Row click handlers
        document.addEventListener('click', (e) => {
            if (e.target.closest('.clickable-row')) {
                this.handleRowClick(e.target.closest('.clickable-row'));
            }
        });

        // Refresh buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('refresh-btn') || e.target.closest('.refresh-btn')) {
                e.preventDefault();
                this.refreshCurrentPage();
            }
        });
    }

    initializeComponents() {
        // Initialize tooltips
        this.initTooltips();
        
        // Initialize pagination
        this.initPagination();
        
        // Initialize auto-refresh
        this.initAutoRefresh();
        
        // Add loading states
        this.initLoadingStates();
    }

    initTooltips() {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    initPagination() {
        const paginationContainer = document.querySelector('.octopus-pagination');
        if (paginationContainer) {
            this.setupPaginationEvents();
        }
    }

    setupPaginationEvents() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('page-link') && !e.target.closest('.disabled')) {
                e.preventDefault();
                const page = e.target.dataset.page;
                if (page) {
                    this.loadPage(parseInt(page));
                }
            }
        });
    }

    initAutoRefresh() {
        const autoRefreshToggle = document.getElementById('autoRefresh');
        if (autoRefreshToggle && autoRefreshToggle.checked) {
            this.startAutoRefresh();
        }
    }

    initLoadingStates() {
        // Add loading overlay capability
        if (!document.querySelector('.loading-overlay')) {
            const overlay = document.createElement('div');
            overlay.className = 'loading-overlay position-fixed top-0 start-0 w-100 h-100 d-none';
            overlay.style.cssText = 'background: rgba(255,255,255,0.8); z-index: 9999;';
            overlay.innerHTML = `
                <div class="d-flex justify-content-center align-items-center h-100">
                    <div class="text-center">
                        <div class="octopus-loading mb-3"></div>
                        <div class="text-primary fw-semibold">Loading...</div>
                    </div>
                </div>
            `;
            document.body.appendChild(overlay);
        }
    }

    // Auto-refresh functionality
    startPeriodicUpdates() {
        // Update timestamps every minute
        setInterval(() => {
            this.updateTimestamps();
        }, 60000);

        // Update status indicators every 30 seconds
        setInterval(() => {
            this.updateStatusIndicators();
        }, 30000);
    }

    toggleAutoRefresh(enabled) {
        if (enabled) {
            this.startAutoRefresh();
        } else {
            this.stopAutoRefresh();
        }
    }

    startAutoRefresh() {
        this.stopAutoRefresh(); // Clear any existing interval
        this.autoRefreshInterval = setInterval(() => {
            this.refreshCurrentPage();
        }, 30000); // Refresh every 30 seconds
    }

    stopAutoRefresh() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
            this.autoRefreshInterval = null;
        }
    }

    // Search functionality
    handleSearch(input) {
        const searchTerm = input.value.trim();
        const currentUrl = new URL(window.location);
        
        if (searchTerm) {
            currentUrl.searchParams.set('search', searchTerm);
        } else {
            currentUrl.searchParams.delete('search');
        }
        currentUrl.searchParams.set('page', '1'); // Reset to first page
        
        this.loadUrl(currentUrl.toString());
    }

    // Pagination
    loadPage(page) {
        const currentUrl = new URL(window.location);
        currentUrl.searchParams.set('page', page.toString());
        this.loadUrl(currentUrl.toString());
    }

    changePageSize(size) {
        const currentUrl = new URL(window.location);
        currentUrl.searchParams.set('page_size', size);
        currentUrl.searchParams.set('page', '1'); // Reset to first page
        this.loadUrl(currentUrl.toString());
    }

    // URL loading with loading state
    loadUrl(url) {
        this.showLoading();
        window.location.href = url;
    }

    refreshCurrentPage() {
        this.showLoading();
        window.location.reload();
    }

    // Loading states
    showLoading() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.classList.remove('d-none');
        }
    }

    hideLoading() {
        const overlay = document.querySelector('.loading-overlay');
        if (overlay) {
            overlay.classList.add('d-none');
        }
    }

    // Row interactions
    handleRowClick(row) {
        const action = row.dataset.action;
        const id = row.dataset.id;
        
        if (action && id) {
            switch (action) {
                case 'view-task':
                    this.viewTask(id);
                    break;
                case 'view-execution':
                    this.viewExecution(id);
                    break;
                case 'view-client':
                    this.viewClient(id);
                    break;
            }
        }
    }

    viewTask(taskId) {
        // Navigate to tasks page with specific task highlighted
        console.log('View task:', taskId);
        window.location.href = `/modern/tasks?highlight=${taskId}`;
    }

    viewExecution(executionId) {
        // Navigate to executions page with specific execution highlighted
        console.log('View execution:', executionId);
        window.location.href = `/modern/executions?highlight=${executionId}`;
    }

    viewClient(clientId) {
        // Navigate to clients page with specific client highlighted
        console.log('View client:', clientId);
        window.location.href = `/modern/clients?highlight=${clientId}`;
    }

    // Utility functions
    updateTimestamps() {
        document.querySelectorAll('[data-timestamp]').forEach(element => {
            const timestamp = parseInt(element.dataset.timestamp);
            element.textContent = this.formatTimestamp(timestamp);
        });
    }

    updateStatusIndicators() {
        // Update client status indicators
        document.querySelectorAll('.client-status[data-client-id]').forEach(indicator => {
            const clientId = indicator.dataset.clientId;
            this.updateClientStatus(clientId, indicator);
        });
    }

    updateClientStatus(clientId, indicator) {
        // This would make an AJAX call to check client status
        // For now, we'll just add a subtle pulse animation for online clients
        if (indicator.classList.contains('online')) {
            indicator.style.animation = 'pulse 2s infinite';
        }
    }

    formatTimestamp(timestamp) {
        const now = Date.now() / 1000;
        const diff = now - timestamp;
        
        if (diff < 60) return 'Just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return `${Math.floor(diff / 86400)}d ago`;
    }

    // Debounce utility
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // Status formatting
    formatStatus(status) {
        const statusMap = {
            'success': { class: 'success', icon: 'check-circle', text: 'Success' },
            'failed': { class: 'danger', icon: 'x-circle', text: 'Failed' },
            'running': { class: 'warning', icon: 'play-circle', text: 'Running' },
            'pending': { class: 'secondary', icon: 'clock', text: 'Pending' },
            'online': { class: 'success', icon: 'circle-fill', text: 'Online' },
            'offline': { class: 'danger', icon: 'circle', text: 'Offline' }
        };
        
        return statusMap[status] || { class: 'secondary', icon: 'question-circle', text: status };
    }

    // Notification system
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 10000; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remove after duration
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, duration);
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.octopusUI = new OctopusUI();
    
    // Hide loading overlay once page is ready
    window.octopusUI.hideLoading();
});

// Global utility functions
window.OctopusUtils = {
    formatBytes: function(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    },
    
    formatDuration: function(seconds) {
        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
        return `${Math.floor(seconds / 86400)}d ${Math.floor((seconds % 86400) / 3600)}h`;
    }
};
