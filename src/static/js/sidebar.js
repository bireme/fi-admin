// Left sidebar menu: collapse to icons, controlled-lists group, active item,
// tooltips while collapsed and off-canvas behavior on small screens.
(function () {
    var STORAGE_KEY = 'fiadmin.sidebar.collapsed';
    var root = document.documentElement;
    var sidebar = document.getElementById('app-sidebar');

    if (!sidebar) {
        return;
    }

    var collapseButton = sidebar.querySelector('.app-sidebar-collapse');
    var collapseLabel = collapseButton.querySelector('.app-sidebar-label');
    var mobileToggle = document.querySelector('.app-mobilebar-toggle');
    var scrim = document.querySelector('.app-sidebar-scrim');
    var mobileQuery = window.matchMedia('(max-width: 767px)');
    var tooltip = document.createElement('div');

    tooltip.className = 'app-sidebar-tooltip';
    tooltip.setAttribute('aria-hidden', 'true');
    document.body.appendChild(tooltip);

    function isCollapsed() {
        return root.classList.contains('sidebar-collapsed') && !mobileQuery.matches;
    }

    function setCollapsed(collapsed) {
        var label = collapsed ? collapseButton.getAttribute('data-label-expand') : collapseButton.getAttribute('data-label-collapse');

        root.classList.toggle('sidebar-collapsed', collapsed);
        collapseButton.setAttribute('aria-expanded', String(!collapsed));
        collapseLabel.textContent = label;
        hideTooltip();

        try {
            localStorage.setItem(STORAGE_KEY, collapsed ? '1' : '0');
        } catch (e) {}
    }

    function setGroupOpen(toggle, open) {
        var list = document.getElementById(toggle.getAttribute('aria-controls'));

        toggle.setAttribute('aria-expanded', String(open));
        list.hidden = !open;
    }

    // mobile off-canvas
    function setMobileOpen(open) {
        root.classList.toggle('sidebar-open', open);
        mobileToggle.setAttribute('aria-expanded', String(open));
        if (open) {
            sidebar.querySelector('a, button').focus();
        } else if (sidebar.contains(document.activeElement)) {
            mobileToggle.focus();
        }
    }

    // tooltips with the item label while only icons are visible
    function showTooltip(item) {
        var label = item.querySelector('.app-sidebar-label');
        var rect = item.getBoundingClientRect();

        if (!isCollapsed() || !label) {
            return;
        }
        tooltip.textContent = label.textContent.trim();
        tooltip.style.top = (rect.top + rect.height / 2) + 'px';
        tooltip.style.left = (sidebar.getBoundingClientRect().right + 8) + 'px';
        tooltip.classList.add('is-visible');
    }

    function hideTooltip() {
        tooltip.classList.remove('is-visible');
    }

    // mark the menu entry that best matches the current page
    function markActiveLink() {
        var best = null;
        var bestScore = 0;
        var path = window.location.pathname;
        var search = window.location.search;

        Array.prototype.forEach.call(sidebar.querySelectorAll('a.app-sidebar-link'), function (link) {
            var linkPath = link.pathname;
            var score = 0;

            if (linkPath === '/') {
                score = (path === '/') ? 1 : 0;
            } else if (path.indexOf(linkPath) === 0) {
                score = linkPath.length;
                if (link.search && search.indexOf(link.search.substring(1)) !== -1) {
                    score += 1;
                }
            }
            if (score > bestScore) {
                best = link;
                bestScore = score;
            }
        });

        if (best) {
            var group = best.closest('.app-sidebar-group');

            best.classList.add('is-active');
            best.setAttribute('aria-current', 'page');
            if (group) {
                setGroupOpen(group.querySelector('.app-sidebar-group-toggle'), true);
            }
        }
    }

    collapseButton.addEventListener('click', function () {
        setCollapsed(!root.classList.contains('sidebar-collapsed'));
    });

    Array.prototype.forEach.call(sidebar.querySelectorAll('.app-sidebar-group-toggle'), function (toggle) {
        toggle.addEventListener('click', function () {
            if (isCollapsed()) {
                setCollapsed(false);
                setGroupOpen(toggle, true);
                return;
            }
            setGroupOpen(toggle, toggle.getAttribute('aria-expanded') !== 'true');
        });
    });

    Array.prototype.forEach.call(sidebar.querySelectorAll('.app-sidebar-link, .app-sidebar-user'), function (item) {
        item.addEventListener('mouseenter', function () { showTooltip(item); });
        item.addEventListener('mouseleave', hideTooltip);
        item.addEventListener('focus', function () { showTooltip(item); });
        item.addEventListener('blur', hideTooltip);
    });
    sidebar.querySelector('.app-sidebar-body').addEventListener('scroll', hideTooltip);

    mobileToggle.addEventListener('click', function () {
        setMobileOpen(!root.classList.contains('sidebar-open'));
    });
    scrim.addEventListener('click', function () {
        setMobileOpen(false);
    });
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && root.classList.contains('sidebar-open')) {
            setMobileOpen(false);
        }
    });
    mobileQuery.addEventListener('change', function () {
        setMobileOpen(false);
        hideTooltip();
    });

    if (root.classList.contains('sidebar-collapsed')) {
        setCollapsed(true);
    }
    markActiveLink();

    // enable width transitions only after the initial state has been painted
    window.requestAnimationFrame(function () {
        window.requestAnimationFrame(function () {
            root.classList.add('sidebar-ready');
        });
    });
})();
