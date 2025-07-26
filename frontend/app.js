/**
 * StockTracking - Modern Stock Data Application
 * Modular JavaScript with enhanced UX and functionality
 */

class StockTracker {
    constructor() {
        this.apiBaseUrl = 'http://127.0.0.1:5001';
        this.watchlist = this.loadWatchlist();
        this.currentTheme = localStorage.getItem('theme') || 'light';
        this.chart = null;
        this.chartData = {};
        this.isChartVisible = false;
        
        this.initializeApp();
        this.bindEvents();
        this.applyTheme();
    }

    /**
     * Initialize the application
     */
    initializeApp() {
        console.log('🚀 StockTracker initialized');
        this.renderWatchlist();
        this.setupFormValidation();
    }

    /**
     * Bind all event listeners
     */
    bindEvents() {
        // Form submission
        const form = document.getElementById('stock-form');
        if (form) {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        }

        // Dark mode toggle
        const darkModeToggle = document.getElementById('dark-mode-toggle');
        if (darkModeToggle) {
            darkModeToggle.addEventListener('click', () => this.toggleDarkMode());
        }

        // Add to watchlist button
        const addToWatchlistBtn = document.getElementById('add-to-watchlist');
        if (addToWatchlistBtn) {
            addToWatchlistBtn.addEventListener('click', () => this.addToWatchlist());
        }

        // Chart controls
        const refreshChartBtn = document.getElementById('refresh-chart');
        if (refreshChartBtn) {
            refreshChartBtn.addEventListener('click', () => this.refreshChartData());
        }

        const toggleChartBtn = document.getElementById('toggle-chart');
        if (toggleChartBtn) {
            toggleChartBtn.addEventListener('click', () => this.toggleChart());
        }

        // Enter key on input
        const stockInput = document.getElementById('stock-symbol');
        if (stockInput) {
            stockInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    this.handleFormSubmit(e);
                }
            });
        }
    }

    /**
     * Handle form submission
     */
    async handleFormSubmit(e) {
        e.preventDefault();
        
        const symbol = document.getElementById('stock-symbol').value.trim().toUpperCase();
        
        if (!this.validateSymbol(symbol)) {
            this.showError('Please enter a valid stock symbol (e.g., AAPL, TSLA)');
            return;
        }

        await this.fetchStockData(symbol);
    }

    /**
     * Validate stock symbol
     */
    validateSymbol(symbol) {
        if (!symbol) return false;
        
        // Basic validation: 1-5 characters, letters only
        const symbolRegex = /^[A-Z]{1,5}$/;
        return symbolRegex.test(symbol);
    }

    /**
     * Fetch stock data from API
     */
    async fetchStockData(symbol) {
        this.showLoading(true);
        this.hideError();
        this.hideStockInfo();

        try {
            console.log(`📊 Fetching data for ${symbol}...`);
            
            const response = await fetch(`${this.apiBaseUrl}/stock/${symbol}`);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP ${response.status}: ${response.statusText}`);
            }

            if (data.error) {
                throw new Error(data.error);
            }

            console.log('✅ Stock data received:', data);
            this.displayStockData(data);

        } catch (error) {
            console.error('❌ Error fetching stock data:', error);
            this.showError(this.formatErrorMessage(error.message));
        } finally {
            this.showLoading(false);
        }
    }

    /**
     * Display stock data in the UI
     */
    displayStockData(data) {
        const stockInfo = document.getElementById('stock-info');
        
        // Calculate price change
        const openPrice = parseFloat(data.open);
        const closePrice = parseFloat(data.close);
        const priceChange = closePrice - openPrice;
        const priceChangePercent = ((priceChange / openPrice) * 100);

        // Update company name (you can enhance this with a company lookup API)
        const companyNames = {
            'AAPL': 'Apple Inc.',
            'TSLA': 'Tesla, Inc.',
            'GOOGL': 'Alphabet Inc.',
            'MSFT': 'Microsoft Corporation',
            'AMZN': 'Amazon.com, Inc.',
            'META': 'Meta Platforms, Inc.',
            'NVDA': 'NVIDIA Corporation',
            'NFLX': 'Netflix, Inc.',
            'SPY': 'SPDR S&P 500 ETF Trust',
            'QQQ': 'Invesco QQQ Trust'
        };

        // Update UI elements
        document.getElementById('company-name').textContent = companyNames[data.symbol] || data.symbol;
        document.getElementById('stock-symbol-display').textContent = data.symbol;
        document.getElementById('current-price').textContent = this.formatCurrency(closePrice);
        document.getElementById('last-refreshed').textContent = data.latest_time_pacific;
        
        // Format and display price data
        document.getElementById('open').textContent = this.formatCurrency(openPrice);
        document.getElementById('high').textContent = this.formatCurrency(parseFloat(data.high));
        document.getElementById('low').textContent = this.formatCurrency(parseFloat(data.low));
        document.getElementById('volume').textContent = this.formatNumber(parseInt(data.volume));

        // Update price change indicators
        this.updatePriceChange(priceChange, priceChangePercent);

        // Show the stock info card with animation
        stockInfo.classList.remove('d-none');
        stockInfo.classList.add('shadow-glow');
        
        // Remove glow effect after animation
        setTimeout(() => {
            stockInfo.classList.remove('shadow-glow');
        }, 2000);
    }

    /**
     * Update price change display with appropriate styling
     */
    updatePriceChange(change, changePercent) {
        const changeAmount = document.getElementById('change-amount');
        const changePercentEl = document.getElementById('change-percent');
        const priceChangeContainer = document.getElementById('price-change');

        const isPositive = change > 0;
        const isNegative = change < 0;
        const isNeutral = change === 0;

        // Update text content
        changeAmount.textContent = `${isPositive ? '+' : ''}${this.formatCurrency(change)}`;
        changePercentEl.textContent = `(${isPositive ? '+' : ''}${changePercent.toFixed(2)}%)`;

        // Update styling
        priceChangeContainer.className = 'small';
        if (isPositive) {
            priceChangeContainer.classList.add('price-positive');
        } else if (isNegative) {
            priceChangeContainer.classList.add('price-negative');
        } else {
            priceChangeContainer.classList.add('price-neutral');
        }
    }

    /**
     * Show loading spinner
     */
    showLoading(show) {
        const spinner = document.getElementById('loading-spinner');
        const button = document.getElementById('fetch-stock');
        
        if (show) {
            spinner.classList.remove('d-none');
            button.disabled = true;
            button.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Loading...';
        } else {
            spinner.classList.add('d-none');
            button.disabled = false;
            button.innerHTML = '<i class="bi bi-lightning-charge me-2"></i>Get Data';
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const errorDiv = document.getElementById('error-message');
        const errorText = document.getElementById('error-text');
        
        errorText.textContent = message;
        errorDiv.classList.remove('d-none');
        
        // Auto-hide error after 5 seconds
        setTimeout(() => {
            this.hideError();
        }, 5000);
    }

    /**
     * Hide error message
     */
    hideError() {
        const errorDiv = document.getElementById('error-message');
        errorDiv.classList.add('d-none');
    }

    /**
     * Hide stock info card
     */
    hideStockInfo() {
        const stockInfo = document.getElementById('stock-info');
        stockInfo.classList.add('d-none');
    }

    /**
     * Format error messages for better UX
     */
    formatErrorMessage(error) {
        const errorMessages = {
            'API rate limit reached': 'API rate limit reached. Please try again later or upgrade your plan.',
            'stock not found': 'Stock symbol not found. Please check the symbol and try again.',
            'API Key not found': 'API configuration error. Please contact support.',
            'Network response was not ok': 'Network error. Please check your connection and try again.'
        };

        for (const [key, message] of Object.entries(errorMessages)) {
            if (error.toLowerCase().includes(key.toLowerCase())) {
                return message;
            }
        }

        return error || 'An unexpected error occurred. Please try again.';
    }

    /**
     * Format currency values
     */
    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(value);
    }

    /**
     * Format large numbers with commas
     */
    formatNumber(value) {
        return new Intl.NumberFormat('en-US').format(value);
    }

    /**
     * Toggle dark mode
     */
    toggleDarkMode() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.currentTheme);
        this.applyTheme();
        
        const toggle = document.getElementById('dark-mode-toggle');
        if (toggle) {
            const icon = toggle.querySelector('i');
            if (this.currentTheme === 'dark') {
                icon.className = 'bi bi-sun';
                toggle.title = 'Switch to light mode';
            } else {
                icon.className = 'bi bi-moon-stars';
                toggle.title = 'Switch to dark mode';
            }
        }
    }

    /**
     * Apply current theme
     */
    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        
        // Update chart colors if chart exists
        if (this.chart && this.isChartVisible) {
            this.refreshChartData();
        }
    }

    /**
     * Add current stock to watchlist
     */
    addToWatchlist() {
        const symbol = document.getElementById('stock-symbol-display').textContent;
        const companyName = document.getElementById('company-name').textContent;
        const currentPrice = document.getElementById('current-price').textContent;

        if (!symbol || symbol === 'SYMBOL') {
            this.showError('No stock data available to add to watchlist');
            return;
        }

        // Check if already in watchlist
        if (this.watchlist.some(item => item.symbol === symbol)) {
            this.showError(`${symbol} is already in your watchlist`);
            return;
        }

        const watchlistItem = {
            symbol,
            companyName,
            currentPrice,
            addedAt: new Date().toISOString()
        };

        this.watchlist.push(watchlistItem);
        this.saveWatchlist();
        this.renderWatchlist();

        // Update button text
        const button = document.getElementById('add-to-watchlist');
        button.innerHTML = '<i class="bi bi-star-fill me-1"></i>Added to Watchlist';
        button.classList.add('btn-success');
        button.classList.remove('btn-outline-primary');

        // Auto-refresh chart if visible
        if (this.isChartVisible) {
            setTimeout(() => {
                this.refreshChartData();
            }, 1000);
        }

        setTimeout(() => {
            button.innerHTML = '<i class="bi bi-star me-1"></i>Add to Watchlist';
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-primary');
        }, 2000);
    }

    /**
     * Remove item from watchlist
     */
    removeFromWatchlist(symbol) {
        this.watchlist = this.watchlist.filter(item => item.symbol !== symbol);
        this.saveWatchlist();
        this.renderWatchlist();
    }

    /**
     * Load watchlist from localStorage
     */
    loadWatchlist() {
        try {
            const saved = localStorage.getItem('stockWatchlist');
            return saved ? JSON.parse(saved) : [];
        } catch (error) {
            console.error('Error loading watchlist:', error);
            return [];
        }
    }

    /**
     * Save watchlist to localStorage
     */
    saveWatchlist() {
        try {
            localStorage.setItem('stockWatchlist', JSON.stringify(this.watchlist));
        } catch (error) {
            console.error('Error saving watchlist:', error);
        }
    }

    /**
     * Render watchlist in UI
     */
    renderWatchlist() {
        const watchlistSection = document.getElementById('watchlist-section');
        const watchlistItems = document.getElementById('watchlist-items');
        const chartControls = document.querySelector('.chart-controls');

        if (this.watchlist.length === 0) {
            watchlistSection.classList.add('d-none');
            return;
        }

        watchlistSection.classList.remove('d-none');
        watchlistItems.innerHTML = '';

        // Show chart controls when there are items
        if (chartControls) {
            chartControls.style.display = 'block';
            console.log('📊 Chart controls shown');
        }

        this.watchlist.forEach(item => {
            const itemElement = this.createWatchlistItem(item);
            watchlistItems.appendChild(itemElement);
        });

        console.log('📋 Watchlist rendered with', this.watchlist.length, 'items');

        // Auto-refresh chart if it's visible
        if (this.isChartVisible) {
            console.log('🔄 Auto-refreshing chart');
            this.refreshChartData();
        }
    }

    /**
     * Create watchlist item element
     */
    createWatchlistItem(item) {
        const div = document.createElement('div');
        div.className = 'col-md-6 col-lg-4';
        div.innerHTML = `
            <div class="watchlist-item">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h6 class="mb-1">${item.symbol}</h6>
                        <small class="text-muted">${item.companyName}</small>
                        <div class="mt-2 fw-bold">${item.currentPrice}</div>
                    </div>
                    <button class="btn btn-sm btn-outline-danger" onclick="stockTracker.removeFromWatchlist('${item.symbol}')">
                        <i class="bi bi-x"></i>
                    </button>
                </div>
            </div>
        `;
        return div;
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        const input = document.getElementById('stock-symbol');
        if (input) {
            input.addEventListener('input', (e) => {
                const value = e.target.value.toUpperCase();
                e.target.value = value.replace(/[^A-Z]/g, '');
            });
        }
    }

    /**
     * Toggle chart visibility
     */
    toggleChart() {
        console.log('🔄 Toggling chart visibility. Current state:', this.isChartVisible);
        
        const chartContainer = document.getElementById('chart-container');
        const toggleBtn = document.getElementById('toggle-chart');
        
        if (!chartContainer || !toggleBtn) {
            console.error('❌ Chart container or toggle button not found');
            return;
        }
        
        if (this.isChartVisible) {
            chartContainer.classList.add('d-none');
            toggleBtn.innerHTML = '<i class="bi bi-graph-up me-1"></i>Show Chart';
            this.isChartVisible = false;
            console.log('👁️ Chart hidden');
        } else {
            if (this.watchlist.length === 0) {
                this.showError('Add stocks to your watchlist to view the chart');
                console.log('⚠️ No stocks in watchlist');
                return;
            }
            
            chartContainer.classList.remove('d-none');
            toggleBtn.innerHTML = '<i class="bi bi-eye-slash me-1"></i>Hide Chart';
            this.isChartVisible = true;
            console.log('👁️ Chart shown, refreshing data...');
            this.refreshChartData();
        }
    }

    /**
     * Refresh chart data
     */
    async refreshChartData() {
        if (this.watchlist.length === 0) {
            this.showError('No stocks in watchlist to display');
            return;
        }

        const chartContainer = document.getElementById('chart-container');
        const canvas = document.getElementById('stockChart');
        
        // Show loading state
        canvas.style.display = 'none';
        chartContainer.querySelector('.card-body').innerHTML = '<div class="chart-loading"><i class="bi bi-hourglass-split me-2"></i>Loading chart data...</div>';

        try {
            console.log('🔄 Refreshing chart data for watchlist:', this.watchlist.map(item => item.symbol));
            
            // Fetch data for all watchlist items
            const promises = this.watchlist.map(item => this.fetchStockDataForChart(item.symbol));
            const results = await Promise.all(promises);
            
            // Filter out failed requests
            const validData = results.filter(result => result !== null);
            
            console.log('✅ Valid data received:', validData.length, 'out of', this.watchlist.length);
            
            if (validData.length === 0) {
                throw new Error('Failed to fetch data for any stocks');
            }

            // Restore canvas element
            chartContainer.querySelector('.card-body').innerHTML = '<canvas id="stockChart" width="400" height="200"></canvas>';
            
            // Update chart
            this.updateChart(validData);
            
            // Update last updated time
            document.getElementById('chart-last-updated').textContent = new Date().toLocaleTimeString();
            
            console.log('✅ Chart updated successfully');
            
        } catch (error) {
            console.error('❌ Error refreshing chart:', error);
            chartContainer.querySelector('.card-body').innerHTML = '<div class="chart-error"><i class="bi bi-exclamation-triangle me-2"></i>Failed to load chart data</div>';
        }
    }

    /**
     * Fetch stock data for chart
     */
    async fetchStockDataForChart(symbol) {
        try {
            console.log(`📊 Fetching chart data for ${symbol}...`);
            const response = await fetch(`${this.apiBaseUrl}/stock/${symbol}`);
            const data = await response.json();
            
            if (!response.ok || data.error) {
                console.warn(`❌ Failed to fetch data for ${symbol}:`, data.error);
                return null;
            }
            
            const chartData = {
                symbol: data.symbol,
                companyName: data.company_name,
                price: parseFloat(data.close),
                change: data.price_change,
                changePercent: data.price_change_percent,
                volume: parseInt(data.volume)
            };
            
            console.log(`✅ Chart data for ${symbol}:`, chartData);
            return chartData;
        } catch (error) {
            console.error(`❌ Error fetching data for ${symbol}:`, error);
            return null;
        }
    }

    /**
     * Update chart with new data
     */
    updateChart(data) {
        console.log('🎨 Updating chart with data:', data);
        
        const canvas = document.getElementById('stockChart');
        if (!canvas) {
            console.error('❌ Canvas element not found');
            return;
        }
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('❌ Could not get canvas context');
            return;
        }
        
        // Show canvas
        canvas.style.display = 'block';
        
        // Destroy existing chart if it exists
        if (this.chart) {
            console.log('🗑️ Destroying existing chart');
            this.chart.destroy();
        }

        // Prepare chart data
        const labels = data.map(item => item.symbol);
        const prices = data.map(item => item.price);
        const colors = this.generateColors(data.length);
        
        // Create gradient backgrounds
        const backgrounds = colors.map(color => {
            const gradient = ctx.createLinearGradient(0, 0, 0, 400);
            gradient.addColorStop(0, color.replace(')', ', 0.3)').replace('rgb', 'rgba'));
            gradient.addColorStop(1, color.replace(')', ', 0.1)').replace('rgb', 'rgba'));
            return gradient;
        });

        // Chart configuration
        const config = {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Current Price ($)',
                    data: prices,
                    borderColor: colors,
                    backgroundColor: backgrounds,
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: colors,
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    pointRadius: 6,
                    pointHoverRadius: 8
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        borderColor: 'rgba(255, 255, 255, 0.2)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        displayColors: false,
                        callbacks: {
                            title: function(context) {
                                const dataIndex = context[0].dataIndex;
                                const item = data[dataIndex];
                                return `${item.symbol} - ${item.companyName}`;
                            },
                            label: function(context) {
                                const dataIndex = context.dataIndex;
                                const item = data[dataIndex];
                                const changeText = item.change >= 0 ? `+$${item.change.toFixed(2)}` : `-$${Math.abs(item.change).toFixed(2)}`;
                                const percentText = item.changePercent >= 0 ? `+${item.changePercent.toFixed(2)}%` : `${item.changePercent.toFixed(2)}%`;
                                
                                return [
                                    `Price: $${item.price.toFixed(2)}`,
                                    `Change: ${changeText} (${percentText})`,
                                    `Volume: ${this.formatNumber(item.volume)}`
                                ];
                            }.bind(this)
                        }
                    }
                },
                scales: {
                    y: {
                        beginAtZero: false,
                        grid: {
                            color: this.currentTheme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
                            drawBorder: false
                        },
                        ticks: {
                            color: this.currentTheme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                            callback: function(value) {
                                return '$' + value.toFixed(2);
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        },
                        ticks: {
                            color: this.currentTheme === 'dark' ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.7)',
                            font: {
                                weight: 'bold'
                            }
                        }
                    }
                },
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                elements: {
                    point: {
                        hoverBackgroundColor: colors
                    }
                }
            }
        };

        // Create chart
        console.log('📈 Creating new chart with config:', config);
        this.chart = new Chart(ctx, config);
        console.log('✅ Chart created successfully');
    }

    /**
     * Generate colors for chart
     */
    generateColors(count) {
        const colors = [
            'rgb(59, 130, 246)',   // Blue
            'rgb(16, 185, 129)',   // Green
            'rgb(239, 68, 68)',    // Red
            'rgb(245, 158, 11)',   // Yellow
            'rgb(139, 92, 246)',   // Purple
            'rgb(236, 72, 153)',   // Pink
            'rgb(14, 165, 233)',   // Sky
            'rgb(34, 197, 94)',    // Emerald
            'rgb(249, 115, 22)',   // Orange
            'rgb(168, 85, 247)'    // Violet
        ];
        
        return colors.slice(0, count);
    }
}

// Initialize the application when DOM is loaded
let stockTracker;
document.addEventListener('DOMContentLoaded', () => {
    stockTracker = new StockTracker();
});

// Export for global access (for watchlist removal)
window.stockTracker = stockTracker;