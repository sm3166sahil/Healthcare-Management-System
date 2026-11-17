/**
 * MediAnalytics - Healthcare Analytics & Patient Management System
 * Main Frontend Application Script
 */

document.addEventListener('DOMContentLoaded', function () {
    'use strict';

    // =========================================================================
    // 1. Auto-dismiss Alerts after 5 Seconds
    // =========================================================================
    const autoDismissAlerts = document.querySelectorAll('.alert:not(.alert-permanent)');
    autoDismissAlerts.forEach(function (alertEl) {
        setTimeout(function () {
            // Check if Bootstrap 5 alert instance exists or can be used
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
                if (bsAlert) {
                    bsAlert.close();
                    return;
                }
            }
            // Fallback smooth fade and remove
            alertEl.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            alertEl.style.opacity = '0';
            alertEl.style.transform = 'translateY(-10px)';
            setTimeout(function () {
                if (alertEl.parentNode) {
                    alertEl.parentNode.removeChild(alertEl);
                }
            }, 500);
        }, 5000);
    });

    // =========================================================================
    // 2. Sidebar Active Link Highlighting
    // =========================================================================
    const currentPath = window.location.pathname;
    const sidebarNavLinks = document.querySelectorAll('.sidebar-nav .nav-link');
    
    sidebarNavLinks.forEach(function (link) {
        const linkHref = link.getAttribute('href');
        if (!linkHref) return;

        // Exact match or active route prefix match (except root '/')
        if (linkHref === currentPath || (linkHref !== '/' && currentPath.startsWith(linkHref))) {
            link.classList.add('active');
            // If inside a collapsible parent menu
            const parentCollapse = link.closest('.collapse');
            if (parentCollapse) {
                parentCollapse.classList.add('show');
            }
        }
    });

    // =========================================================================
    // 3. Mobile Sidebar Toggle & Backdrop Overlay
    // =========================================================================
    const mobileToggleBtn = document.querySelector('.mobile-toggle');
    const sidebarEl = document.querySelector('.sidebar');

    // Create or locate sidebar overlay
    let sidebarOverlay = document.querySelector('.sidebar-overlay');
    if (!sidebarOverlay && sidebarEl) {
        sidebarOverlay = document.createElement('div');
        sidebarOverlay.className = 'sidebar-overlay';
        document.body.appendChild(sidebarOverlay);
    }

    function toggleMobileSidebar() {
        if (!sidebarEl) return;
        sidebarEl.classList.toggle('active');
        if (sidebarOverlay) {
            sidebarOverlay.classList.toggle('active');
        }
    }

    function closeMobileSidebar() {
        if (!sidebarEl) return;
        sidebarEl.classList.remove('active');
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove('active');
        }
    }

    if (mobileToggleBtn) {
        mobileToggleBtn.addEventListener('click', function (e) {
            e.stopPropagation();
            toggleMobileSidebar();
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', closeMobileSidebar);
    }

    // Close mobile sidebar on window resize if expanded to desktop
    window.addEventListener('resize', function () {
        if (window.innerWidth > 992 && sidebarEl && sidebarEl.classList.contains('active')) {
            closeMobileSidebar();
        }
    });

    // =========================================================================
    // 4. Confirm Delete Dialogs
    // =========================================================================
    const deleteButtons = document.querySelectorAll('.btn-delete, [data-confirm]');
    deleteButtons.forEach(function (button) {
        button.addEventListener('click', function (event) {
            const confirmMessage = button.getAttribute('data-confirm') || 
                'Are you sure you want to delete this record? This action cannot be undone.';
            if (!window.confirm(confirmMessage)) {
                event.preventDefault();
                event.stopPropagation();
                return false;
            }
        });
    });

    // =========================================================================
    // 5. Form Validation Feedback
    // =========================================================================
    const formsToValidate = document.querySelectorAll('.needs-validation');
    formsToValidate.forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // =========================================================================
    // 6. Live Search / AJAX Filter with Debounce
    // =========================================================================
    function debounce(func, delay) {
        let timer;
        return function (...args) {
            clearTimeout(timer);
            timer = setTimeout(() => func.apply(this, args), delay);
        };
    }

    const searchInput = document.querySelector('#searchInput, .search-live');
    if (searchInput) {
        const targetTable = document.querySelector(searchInput.getAttribute('data-target-table') || '.table');
        if (targetTable) {
            searchInput.addEventListener('input', debounce(function () {
                const query = this.value.trim().toLowerCase();
                const tableRows = targetTable.querySelectorAll('tbody tr');
                tableRows.forEach(function (row) {
                    const rowText = row.textContent.toLowerCase();
                    if (rowText.includes(query)) {
                        row.style.display = '';
                    } else {
                        row.style.display = 'none';
                    }
                });
            }, 250));
        }
    }

    // =========================================================================
    // 7. Table Row Click Navigation
    // =========================================================================
    const clickableRows = document.querySelectorAll('tr[data-href]');
    clickableRows.forEach(function (row) {
        row.style.cursor = 'pointer';
        row.addEventListener('click', function (event) {
            // Ignore if clicked on links, buttons, inputs, dropdowns, or icons inside buttons
            if (event.target.closest('a, button, input, select, textarea, .dropdown-menu, .btn-action')) {
                return;
            }
            const destination = row.getAttribute('data-href');
            if (destination) {
                window.location.href = destination;
            }
        });
    });

    // =========================================================================
    // 8. Bootstrap Tooltip Initialization
    // =========================================================================
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // =========================================================================
    // 9. Loading Indicators on Submit
    // =========================================================================
    const submitForms = document.querySelectorAll('form:not(.no-loading)');
    submitForms.forEach(function (form) {
        form.addEventListener('submit', function () {
            if (!form.checkValidity || form.checkValidity()) {
                const submitBtn = form.querySelector('button[type="submit"]');
                if (submitBtn && !submitBtn.disabled) {
                    const originalText = submitBtn.innerHTML;
                    submitBtn.disabled = true;
                    submitBtn.classList.add('loading');
                    submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span> Processing...';

                    // Revert after 15 seconds in case response is a file download (which won't redirect)
                    setTimeout(function () {
                        submitBtn.disabled = false;
                        submitBtn.classList.remove('loading');
                        submitBtn.innerHTML = originalText;
                    }, 15000);
                }
            }
        });
    });

    // =========================================================================
    // 10. Number Formatting
    // =========================================================================
    const numberElements = document.querySelectorAll('.format-number');
    numberElements.forEach(function (el) {
        const rawVal = parseFloat(el.textContent.replace(/[^0-9.-]+/g, ''));
        if (!isNaN(rawVal)) {
            el.textContent = rawVal.toLocaleString('en-US');
        }
    });

    // =========================================================================
    // 11. Date Formatting
    // =========================================================================
    const dateElements = document.querySelectorAll('.format-date');
    dateElements.forEach(function (el) {
        const rawDate = el.getAttribute('data-date') || el.textContent.trim();
        if (rawDate) {
            const parsed = new Date(rawDate);
            if (!isNaN(parsed.getTime())) {
                const options = { year: 'numeric', month: 'short', day: 'numeric' };
                el.textContent = parsed.toLocaleDateString(undefined, options);
            }
        }
    });

    // =========================================================================
    // 12. Filter Form Auto-Submit
    // =========================================================================
    const autoSubmitSelects = document.querySelectorAll('.filter-auto-submit, .auto-submit');
    autoSubmitSelects.forEach(function (selectEl) {
        selectEl.addEventListener('change', function () {
            const form = selectEl.closest('form');
            if (form) {
                form.submit();
            }
        });
    });

    // =========================================================================
    // 13. CSRF Token Handling for AJAX
    // =========================================================================
    window.getCookie = function (name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    };

    window.fetchWithCsrf = function (url, options = {}) {
        const headers = options.headers || {};
        headers['X-CSRFToken'] = window.getCookie('csrftoken');
        options.headers = headers;
        return fetch(url, options);
    };

    // =========================================================================
    // 14. Print Functionality
    // =========================================================================
    const printButtons = document.querySelectorAll('.btn-print, [data-action="print"]');
    printButtons.forEach(function (button) {
        button.addEventListener('click', function (e) {
            e.preventDefault();
            window.print();
        });
    });
});
