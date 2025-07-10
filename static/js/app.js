/**
 * Main JavaScript file for LOB Simulation Web Interface
 * Modular JavaScript with separate modules for different functionalities
 */

// Global state
const AppState = {
    socket: null,
    isConnected: false,
    isRunning: false,
    charts: {},
    updateInterval: null
};

// Utility functions
const Utils = {
    formatNumber: (num, decimals = 2) => {
        return Number(num).toFixed(decimals);
    },
    
    formatCurrency: (num) => {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD'
        }).format(num);
    },
    
    showNotification: (message, type = 'info') => {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 100);
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => document.body.removeChild(notification), 300);
        }, 3000);
    },
    
    debounce: (func, wait) => {
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
};

// WebSocket management
const WebSocketManager = {
    refreshRate: 1.0,
    updateInterval: null,
    
    connect: () => {
        // Connect to the same port as the current page
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const host = window.location.host;
        AppState.socket = io(`${protocol}//${host}`);
        console.log('Connecting to WebSocket at:', `${protocol}//${host}`);
        
        AppState.socket.on('connect', () => {
            AppState.isConnected = true;
            Utils.showNotification('Connected to server', 'success');
            UI.updateConnectionStatus(true);
            
            // Start requesting updates at the current refresh rate
            WebSocketManager.startUpdateRequests();
            
            // Request initial update immediately
            setTimeout(() => {
                WebSocketManager.requestUpdate();
            }, 100);
        });
        
        AppState.socket.on('disconnect', () => {
            AppState.isConnected = false;
            Utils.showNotification('Disconnected from server', 'error');
            UI.updateConnectionStatus(false);
            WebSocketManager.stopUpdateRequests();
        });
        
        AppState.socket.on('market_update', (data) => {
            console.log('Received market update:', data);
            DataManager.updateMarketData(data);
            UI.updateCharts();
            UI.updateOrderBook(data.order_book);
            UI.updateStrategyPerformance(data.strategy_performance || {});
        });
        
        AppState.socket.on('connected', (data) => {
            console.log('Socket connected:', data);
        });
    },
    
    disconnect: () => {
        if (AppState.socket) {
            AppState.socket.disconnect();
            AppState.socket = null;
        }
        WebSocketManager.stopUpdateRequests();
    },
    
    requestUpdate: () => {
        if (AppState.socket && AppState.isConnected) {
            console.log(`Requesting update (refresh rate: ${WebSocketManager.refreshRate}s)`);
            AppState.socket.emit('request_update');
        }
    },
    
    startUpdateRequests: () => {
        WebSocketManager.stopUpdateRequests(); // Clear any existing interval
        
        WebSocketManager.updateInterval = setInterval(() => {
            if (AppState.isConnected && AppState.socket) {
                WebSocketManager.requestUpdate();
            }
        }, WebSocketManager.refreshRate * 1000);
        
        console.log(`Started update requests every ${WebSocketManager.refreshRate} seconds`);
    },
    
    stopUpdateRequests: () => {
        if (WebSocketManager.updateInterval) {
            clearInterval(WebSocketManager.updateInterval);
            WebSocketManager.updateInterval = null;
            console.log('Stopped update requests');
        }
    },
    
    updateRefreshRate: (newRate) => {
        console.log(`WebSocket refresh rate changed from ${WebSocketManager.refreshRate}s to ${newRate}s`);
        WebSocketManager.refreshRate = newRate;
        if (AppState.isConnected) {
            WebSocketManager.startUpdateRequests();
        }
    }
};

// Data management
const DataManager = {
    marketData: {
        orderBook: {},
        priceHistory: { prices: [], times: [] },
        tradeHistory: [],
        strategyPerformance: {}
    },
    
    updateMarketData: (data) => {
        // Map backend snake_case to frontend camelCase
        if (data.price_history) {
            DataManager.marketData.priceHistory = data.price_history;
        }
        if (data.order_book) {
            DataManager.marketData.orderBook = data.order_book;
        }
        if (data.strategy_performance) {
            DataManager.marketData.strategyPerformance = data.strategy_performance;
        }
        if (data.trade_history) {
            DataManager.marketData.tradeHistory = data.trade_history;
        }
        // Merge any other fields as fallback
        DataManager.marketData = { ...DataManager.marketData, ...data };
    },
    
    getLatestPrice: () => {
        const prices = DataManager.marketData.priceHistory.prices;
        return prices.length > 0 ? prices[prices.length - 1] : 0;
    },
    
    getPriceHistory: () => {
        return DataManager.marketData.priceHistory;
    },
    
    getOrderBook: () => {
        return DataManager.marketData.orderBook;
    },
    
    getStrategyPerformance: () => {
        return DataManager.marketData.strategyPerformance;
    }
};

// API management
const APIManager = {
    async startSimulation(strategies = {}, refreshRate = 1.0) {
        try {
            const response = await fetch('/api/start_simulation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ strategies, refresh_rate: refreshRate })
            });
            
            const data = await response.json();
            
            if (response.ok) {
                AppState.isRunning = true;
                Utils.showNotification('Simulation started', 'success');
                UI.updateSimulationStatus(true);
                return data;
            } else {
                throw new Error(data.error || 'Failed to start simulation');
            }
        } catch (error) {
            Utils.showNotification(`Error: ${error.message}`, 'error');
            throw error;
        }
    },
    
    async stopSimulation() {
        try {
            const response = await fetch('/api/stop_simulation', {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                AppState.isRunning = false;
                Utils.showNotification('Simulation stopped', 'info');
                UI.updateSimulationStatus(false);
                return data;
            } else {
                throw new Error(data.error || 'Failed to stop simulation');
            }
        } catch (error) {
            Utils.showNotification(`Error: ${error.message}`, 'error');
            throw error;
        }
    },
    
    async getSimulationStatus() {
        try {
            const response = await fetch('/api/simulation_status');
            const data = await response.json();
            
            if (response.ok) {
                AppState.isRunning = data.running;
                UI.updateSimulationStatus(data.running);
                UI.updateSimulationTime(data.time);
                return data;
            } else {
                throw new Error(data.error || 'Failed to get status');
            }
        } catch (error) {
            console.error('Error getting simulation status:', error);
            return null;
        }
    },
    
    async getStrategyPerformance() {
        try {
            const response = await fetch('/api/strategy_performance');
            const data = await response.json();
            
            if (response.ok) {
                return data;
            } else {
                throw new Error(data.error || 'Failed to get strategy performance');
            }
        } catch (error) {
            console.error('Error getting strategy performance:', error);
            return {};
        }
    }
};

// Chart management
const ChartManager = {
    initCharts: () => {
        ChartManager.initPriceChart();
        ChartManager.initOrderBookChart();
    },
    
    initPriceChart: () => {
        const ctx = document.getElementById('priceChart');
        if (!ctx) return;
        
        AppState.charts.price = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Price',
                    data: [],
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Time (s)'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Price ($)'
                        }
                    }
                },
                animation: {
                    duration: 0
                }
            }
        });
    },
    
    initOrderBookChart: () => {
        const ctx = document.getElementById('orderBookChart');
        if (!ctx) return;
        
        AppState.charts.orderBook = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Bids',
                    data: [],
                    backgroundColor: 'rgba(39, 174, 96, 0.8)',
                    borderColor: '#27ae60',
                    borderWidth: 1
                }, {
                    label: 'Asks',
                    data: [],
                    backgroundColor: 'rgba(231, 76, 60, 0.8)',
                    borderColor: '#e74c3c',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Price Level'
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Quantity'
                        }
                    }
                }
            }
        });
    },
    
    updatePriceChart: () => {
        const chart = AppState.charts.price;
        if (!chart) {
            console.log('Price chart not found');
            return;
        }
        
        const priceData = DataManager.getPriceHistory();
        console.log('Updating price chart with:', priceData);
        
        chart.data.labels = priceData.times.map(t => Utils.formatNumber(t, 1));
        chart.data.datasets[0].data = priceData.prices;
        
        chart.update('none');
    },
    
    updateOrderBookChart: () => {
        const chart = AppState.charts.orderBook;
        if (!chart) {
            console.log('Order book chart not found');
            return;
        }
        
        const orderBook = DataManager.getOrderBook();
        console.log('Updating order book chart with:', orderBook);
        
        const bids = orderBook.bids || [];
        const asks = orderBook.asks || [];
        
        // Combine bid and ask prices for x-axis
        const allPrices = [...new Set([
            ...bids.map(b => b.price),
            ...asks.map(a => a.price)
        ])].sort((a, b) => a - b);
        
        // Create datasets
        const bidData = allPrices.map(price => {
            const bid = bids.find(b => b.price === price);
            return bid ? bid.quantity : 0;
        });
        
        const askData = allPrices.map(price => {
            const ask = asks.find(a => a.price === price);
            return ask ? ask.quantity : 0;
        });
        
        chart.data.labels = allPrices.map(p => Utils.formatNumber(p, 2));
        chart.data.datasets[0].data = bidData;
        chart.data.datasets[1].data = askData;
        
        chart.update('none');
    },
    
    updateRefreshRate: (newRate) => {
        console.log(`Chart refresh rate updated to ${newRate} seconds`);
        // Charts are updated when data is received, so no interval needed
        // The refresh rate is controlled by the WebSocket manager
    }
};

// UI management
const UI = {
    init: () => {
        UI.setupEventListeners();
        UI.updateConnectionStatus(false);
        UI.updateSimulationStatus(false);
    },
    
    setupEventListeners: () => {
        // Start simulation button
        const startBtn = document.getElementById('startSimulation');
        if (startBtn) {
            startBtn.addEventListener('click', async () => {
                try {
                    startBtn.disabled = true;
                    const strategies = UI.getStrategyConfig();
                    const refreshRate = UI.getRefreshRate();
                    await APIManager.startSimulation(strategies, refreshRate);
                } catch (error) {
                    console.error('Failed to start simulation:', error);
                } finally {
                    startBtn.disabled = false;
                }
            });
        }
        
        // Stop simulation button
        const stopBtn = document.getElementById('stopSimulation');
        if (stopBtn) {
            stopBtn.addEventListener('click', async () => {
                try {
                    stopBtn.disabled = true;
                    await APIManager.stopSimulation();
                } catch (error) {
                    console.error('Failed to stop simulation:', error);
                } finally {
                    stopBtn.disabled = false;
                }
            });
        }
        
        // Strategy selection
        const strategySelects = document.querySelectorAll('.strategy-select');
        strategySelects.forEach(select => {
            select.addEventListener('change', () => {
                UI.updateStrategyConfig();
            });
        });
        

    },
    
    getStrategyConfig: () => {
        const strategies = {};
        const strategySelects = document.querySelectorAll('.strategy-select');
        
        strategySelects.forEach(select => {
            if (select.checked) {
                const strategyName = select.value;
                strategies[strategyName] = {
                    initial_capital: 100000,
                    max_position: 1000
                };
            }
        });
        
        return strategies;
    },
    
    getRefreshRate: () => {
        const refreshRateSelect = document.getElementById('refreshRate');
        return refreshRateSelect ? parseFloat(refreshRateSelect.value) : 1.0;
    },
    
    initRefreshRateControl: () => {
        const refreshRateSelect = document.getElementById('refreshRate');
        if (refreshRateSelect) {
            refreshRateSelect.addEventListener('change', () => {
                const newRate = UI.getRefreshRate();
                console.log('Refresh rate changed to:', newRate, 'seconds');
                
                // Update WebSocket manager refresh rate
                if (WebSocketManager.updateRefreshRate) {
                    WebSocketManager.updateRefreshRate(newRate);
                }
                
                // Update chart refresh rates
                if (ChartManager.updateRefreshRate) {
                    ChartManager.updateRefreshRate(newRate);
                }
            });
        }
    },
    
    updateStrategyConfig: () => {
        const strategies = UI.getStrategyConfig();
        console.log('Strategy configuration updated:', strategies);
    },
    
    updateConnectionStatus: (connected) => {
        const statusElement = document.getElementById('connectionStatus');
        if (statusElement) {
            statusElement.innerHTML = `
                <span class="status-indicator ${connected ? 'status-running' : 'status-stopped'}"></span>
                ${connected ? 'Connected' : 'Disconnected'}
            `;
        }
    },
    
    updateSimulationStatus: (running) => {
        const statusElement = document.getElementById('simulationStatus');
        if (statusElement) {
            statusElement.innerHTML = `
                <span class="status-indicator ${running ? 'status-running' : 'status-stopped'}"></span>
                ${running ? 'Running' : 'Stopped'}
            `;
        }
        
        // Update button states
        const startBtn = document.getElementById('startSimulation');
        const stopBtn = document.getElementById('stopSimulation');
        
        if (startBtn) startBtn.disabled = running;
        if (stopBtn) stopBtn.disabled = !running;
    },
    
    updateSimulationTime: (time) => {
        const timeElement = document.getElementById('simulationTime');
        if (timeElement) {
            timeElement.textContent = `${Utils.formatNumber(time, 1)}s`;
        }
    },
    
    updateCharts: () => {
        console.log('UI.updateCharts called');
        ChartManager.updatePriceChart();
        ChartManager.updateOrderBookChart();
    },
    
    updateOrderBook: (orderBook) => {
        const table = document.getElementById('orderBookTable');
        if (!table) return;
        
        const bids = orderBook.bids || [];
        const asks = orderBook.asks || [];
        
        let html = `
            <tr>
                <th>Bid Price</th>
                <th>Bid Qty</th>
                <th>Ask Price</th>
                <th>Ask Qty</th>
            </tr>
        `;
        
        // Get the maximum number of levels to display
        const maxLevels = Math.max(bids.length, asks.length);
        const levelsToShow = Math.min(maxLevels, 10);
        
        for (let i = 0; i < levelsToShow; i++) {
            const bid = i < bids.length ? bids[i] : null;
            const ask = i < asks.length ? asks[i] : null;
            
            html += `
                <tr>
                    <td class="bid">${bid ? Utils.formatNumber(bid.price, 2) : '-'}</td>
                    <td>${bid ? bid.quantity : '-'}</td>
                    <td class="ask">${ask ? Utils.formatNumber(ask.price, 2) : '-'}</td>
                    <td>${ask ? ask.quantity : '-'}</td>
                </tr>
            `;
        }
        
        table.innerHTML = html;
    },
    
    updateStrategyPerformance: (performance) => {
        const container = document.getElementById('strategyPerformance');
        if (!container) return;
        
        let html = '';
        
        // Limit to first 4 strategies to prevent excessive content
        const limitedPerformance = Object.entries(performance).slice(0, 4);
        
        if (limitedPerformance.length === 0) {
            html = '<div class="strategy-card"><h4>No Strategies Active</h4><p>Start a simulation with strategies to see performance data.</p></div>';
        } else {
            limitedPerformance.forEach(([strategyName, data]) => {
                const pnlClass = data.total_pnl >= 0 ? 'positive' : 'negative';
                
                html += `
                    <div class="strategy-card">
                        <h4>${strategyName.replace('_', ' ').toUpperCase()}</h4>
                        <div class="strategy-metric">
                            <span class="label">PnL:</span>
                            <span class="value ${pnlClass}">${Utils.formatCurrency(data.total_pnl)}</span>
                        </div>
                        <div class="strategy-metric">
                            <span class="label">Position:</span>
                            <span class="value">${data.current_position}</span>
                        </div>
                        <div class="strategy-metric">
                            <span class="label">Trades:</span>
                            <span class="value">${data.num_trades}</span>
                        </div>
                        <div class="strategy-metric">
                            <span class="label">Win Rate:</span>
                            <span class="value">${Utils.formatNumber(data.win_rate * 100, 1)}%</span>
                        </div>
                        <div class="strategy-metric">
                            <span class="label">Sharpe Ratio:</span>
                            <span class="value">${Utils.formatNumber(data.sharpe_ratio, 3)}</span>
                        </div>
                    </div>
                `;
            });
        }
        
        container.innerHTML = html;
    }
};

// Initialize application
document.addEventListener('DOMContentLoaded', () => {
    console.log('LOB Simulation Web Interface initializing...');
    
    // Initialize UI
    UI.init();
    
    // Initialize charts
    ChartManager.initCharts();
    
    // Connect to WebSocket
    WebSocketManager.connect();
    
    // Start status polling
    setInterval(() => {
        APIManager.getSimulationStatus();
    }, 5000);
    
    // Initialize refresh rate control
    UI.initRefreshRateControl();
    
    console.log('LOB Simulation Web Interface initialized');
}); 