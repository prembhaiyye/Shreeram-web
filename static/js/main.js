class NotificationManager {
    constructor() {
        this.notifications = JSON.parse(localStorage.getItem('hydro_notifications') || '[]');
        this.bell = document.getElementById('notification-bell');
        this.badge = document.getElementById('notification-badge');
        this.list = document.getElementById('notification-list');
        this.init();
    }

    init() {
        this.render();
        this.updateBadge();
        // Check for alerts every 5 seconds if not already polling elsewhere
        // For this app, fetchSensorData usually handles the data flow
    }

    generateAlerts(data) {
        let newAlerts = false;
        for (const [key, value] of Object.entries(data)) {
            const range = GLOBAL_IDEALS[key];
            if (!range) continue;

            let severity = null;
            let type = '';
            let action = '';

            const val = parseFloat(value);
            if (isNaN(val)) continue;

            if (val > range.max) {
                severity = 'critical';
                type = 'HIGH';
                action = this.getActionSuggestion(key, 'high');
            } else if (val < range.min) {
                severity = 'critical';
                type = 'LOW';
                action = this.getActionSuggestion(key, 'low');
            } else if (val > range.max * 0.9 || val < range.min * 1.1) {
                // Warning zone (within 10% of limits)
                severity = 'warning';
                type = val > range.max * 0.9 ? 'TRENDING HIGH' : 'TRENDING LOW';
                action = 'Monitor closely';
            }

            if (severity) {
                if (this.addNotification({
                    id: `${key}_${severity}`,
                    key: key,
                    title: `${key.toUpperCase()} ${type}`,
                    value: val.toFixed(1) + (range.unit || ''),
                    range: `${range.min} - ${range.max}${range.unit || ''}`,
                    severity: severity,
                    action: action,
                    timestamp: new Date().toISOString(),
                    unread: true
                })) {
                    newAlerts = true;
                }
            } else {
                // Clear notification if property returned to normal
                this.removeNotification(`${key}_critical`);
                this.removeNotification(`${key}_warning`);
            }
        }

        if (newAlerts) {
            this.playAlertAnimation();
        }
        this.render();
        this.save();
    }

    getActionSuggestion(key, state) {
        const actions = {
            temperature: { high: 'Turn ON Environmental Fan', low: 'Increase Heater Power' },
            ph: { high: 'Run pH-Down Pump', low: 'Run pH-Up Pump' },
            tds: { high: 'Dilute with Fresh Water', low: 'Run Nutrient Pumps' },
            humidity: { high: 'Increase Ventilation', low: 'Run Humidifier' },
            water_level: { low: 'Refill Reservoir' },
            gas: { high: '⚠️ EVACUATE / VENTILATE' }
        };
        return (actions[key] && actions[key][state]) ? actions[key][state] : 'Check system controls';
    }

    addNotification(notif) {
        const index = this.notifications.findIndex(n => n.id === notif.id);
        if (index !== -1) {
            // Update existing
            this.notifications[index].value = notif.value;
            this.notifications[index].timestamp = notif.timestamp;
            // Only return true if it was previously read and now is unread again (re-trigger)
            return false;
        } else {
            this.notifications.unshift(notif);
            if (this.notifications.length > 20) this.notifications.pop();
            return true;
        }
    }

    removeNotification(id) {
        const initialLen = this.notifications.length;
        this.notifications = this.notifications.filter(n => n.id !== id);
        if (this.notifications.length !== initialLen) {
            this.render();
            this.updateBadge();
            this.save();
        }
    }

    markAllAsRead() {
        this.notifications.forEach(n => n.unread = false);
        this.render();
        this.updateBadge();
        this.save();
    }

    clearAll() {
        this.notifications = [];
        this.render();
        this.updateBadge();
        this.save();
    }

    playAlertAnimation() {
        if (!this.bell) return;
        this.bell.classList.add('shake', 'pulse');
        setTimeout(() => this.bell.classList.remove('shake'), 500);
    }

    updateBadge() {
        if (!this.badge) return;
        const count = this.notifications.filter(n => n.unread).length;
        if (count > 0) {
            this.badge.style.display = 'flex';
            this.badge.textContent = count > 9 ? '9+' : count;
            this.bell.classList.add('pulse');
        } else {
            this.badge.style.display = 'none';
            this.bell.classList.remove('pulse');
        }
    }

    render() {
        if (!this.list) return;
        if (this.notifications.length === 0) {
            this.list.innerHTML = '<div class="empty-state">No active alerts</div>';
            return;
        }

        this.list.innerHTML = this.notifications.map(n => `
            <div class="notification-item ${n.unread ? 'unread' : ''} severity-${n.severity}" id="notif-${n.id}">
                <div class="item-icon">${this.getIcon(n.key)}</div>
                <div class="item-content">
                    <div class="item-title">${n.title}</div>
                    <div class="item-value">Current: <strong>${n.value}</strong></div>
                    <div class="item-range">Ideal: ${n.range}</div>
                    <div class="item-footer">
                        <span class="item-time">${this.timeAgo(n.timestamp)}</span>
                        <div class="item-actions">
                            <button class="item-btn" onclick="notificationManager.removeNotification('${n.id}')">Dismiss</button>
                            <a href="/graph/${n.key}" class="item-btn primary">View Graph</a>
                        </div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    getIcon(key) {
        const icons = { temperature: '🌡️', ph: '🧪', tds: '💧', humidity: '☁️', water_level: '🛢️', gas: '🛑', cpu_temp: '💻' };
        return icons[key] || '🔔';
    }

    timeAgo(date) {
        const seconds = Math.floor((new Date() - new Date(date)) / 1000);
        if (seconds < 60) return 'Just now';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return minutes + 'm ago';
        const hours = Math.floor(minutes / 60);
        return hours + 'h ago';
    }

    save() {
        localStorage.setItem('hydro_notifications', JSON.stringify(this.notifications));
        this.updateBadge();
    }
}

// Global instance
let notificationManager;

document.addEventListener('DOMContentLoaded', function () {
    notificationManager = new NotificationManager();

    // Start polling if we are NOT on the monitor page (which has its own poll)
    // Actually, it's safer to have a global poll that only runs if no other poll is active
    // but for this implementation, we'll just hook into the existing fetch cycle in main.js

    // Check if we need to start a global fetch loop
    // If there is no fetchSensorData running elsewhere, start one
    if (typeof fetchSensorData === 'function') {
        const originalFetch = fetchSensorData;
        window.fetchSensorData = async function () {
            try {
                const response = await fetch('/api/sensor-data');
                const data = await response.json();

                // Route to notification manager
                if (notificationManager) {
                    notificationManager.generateAlerts(data);
                }

                // Call original dashboard update if it exists
                if (typeof updateDashboard === 'function') {
                    updateDashboard(data);
                }

                return data;
            } catch (error) {
                console.error('Fetch failed:', error);
            }
        };

        // If not on monitor page, start our own interval
        if (!window.location.pathname.includes('/monitor')) {
            setInterval(window.fetchSensorData, 5000);
            window.fetchSensorData();
        }
    }
});

// Mock for updateDashboard if needed/already there
function updateDashboard(data) {
    for (const [key, value] of Object.entries(data)) {
        const element = document.getElementById(`val-${key}`);
        if (element) {
            element.innerText = typeof value === 'number' ? value.toFixed(1) : value;
        }
    }
}
