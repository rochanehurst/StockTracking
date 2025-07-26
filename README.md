# 📈 StockTracking - Modern Real-Time Stock Data App

A beautiful, responsive web application for tracking real-time stock prices with a modern UI inspired by Robinhood and Apple Stocks.

![StockTracking App](https://img.shields.io/badge/Status-Production%20Ready-brightgreen)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Flask](https://img.shields.io/badge/Flask-2.0+-lightgrey)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-blueviolet)

## ✨ Features

### 🎨 Modern UI/UX
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Dark Mode**: Toggle between light and dark themes
- **Smooth Animations**: Elegant transitions and hover effects
- **Professional Styling**: Clean, modern interface inspired by fintech apps

### 📊 Stock Data
- **Real-time Prices**: Live stock data from Alpha Vantage API
- **Price Changes**: Visual indicators for price movements (green/red)
- **Comprehensive Data**: Open, High, Low, Close, Volume
- **Company Names**: Automatic company name resolution
- **Timezone Support**: Eastern and Pacific time displays

### 🔧 Enhanced Functionality
- **Watchlist**: Save favorite stocks locally
- **Interactive Charts**: Compare multiple stocks with beautiful line charts
- **Form Validation**: Smart input validation and error handling
- **Loading States**: Beautiful loading animations
- **Error Handling**: User-friendly error messages
- **Keyboard Support**: Enter key to submit forms

### 🛡️ Backend Improvements
- **Input Validation**: Secure symbol validation
- **Error Handling**: Comprehensive error management
- **Logging**: Detailed application logging
- **Configuration**: Environment-based settings
- **CORS Support**: Cross-origin request handling

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Alpha Vantage API key (free at [alphavantage.co](https://www.alphavantage.co/support/#api-key))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd StockTracking
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   ALPHA_VANTAGE_API_KEY=your_api_key_here
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

4. **Run the application**
   ```bash
   python run.py
   ```

5. **Open your browser**
   Navigate to `http://localhost:8080` (Frontend)
   API available at `http://localhost:5001` (Backend)

## 📁 Project Structure

```
StockTracking/
├── app/
│   ├── __init__.py
│   └── app.py              # Flask backend application
├── frontend/
│   ├── index.html          # Main HTML template
│   ├── app.js              # JavaScript application logic
│   └── styles.css          # Custom CSS styles
├── config.py               # Configuration settings
├── run.py                  # Application entry point
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🎯 Usage

### Basic Stock Lookup
1. Enter a stock symbol (e.g., `AAPL`, `TSLA`, `GOOGL`)
2. Click "Get Data" or press Enter
3. View real-time stock information

### Watchlist Management
1. Look up a stock
2. Click "Add to Watchlist" to save it
3. View your saved stocks in the watchlist section
4. Remove stocks by clicking the "X" button

### Interactive Charts
1. Add multiple stocks to your watchlist
2. Click "Show Chart" to display the comparison chart
3. Hover over data points to see detailed information
4. Click "Refresh Data" to update all stock prices
5. Toggle between chart and list view

### Dark Mode
- Click the moon/sun icon in the navigation bar to toggle themes

## 🔧 Configuration

### Environment Variables
- `ALPHA_VANTAGE_API_KEY`: Your Alpha Vantage API key (required)
- `FLASK_ENV`: Environment mode (development/production)
- `FLASK_DEBUG`: Enable debug mode (True/False)
- `SECRET_KEY`: Flask secret key (auto-generated in development)

### Supported Stock Symbols
The app supports popular stock symbols including:
- **Tech**: AAPL, TSLA, GOOGL, MSFT, AMZN, META, NVDA, NFLX
- **ETFs**: SPY, QQQ, IWM, VTI, VOO, ARKK
- **Crypto**: BTC, ETH, COIN
- **Finance**: SQ, PYPL, ADBE, CRM, ORCL, IBM, INTC, AMD

## 🛠️ Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python run.py
```

### Code Structure
- **Frontend**: Modular JavaScript with ES6 classes
- **Backend**: Flask with proper error handling and logging
- **Styling**: CSS custom properties for theming
- **Configuration**: Environment-based settings

### Adding New Features
1. **Frontend**: Add new UI components in `frontend/`
2. **Backend**: Extend Flask routes in `app/app.py`
3. **Styling**: Add CSS classes in `frontend/styles.css`
4. **Configuration**: Update settings in `config.py`

## 📱 Mobile Responsiveness

The app is fully responsive and optimized for:
- **Desktop**: Full-featured experience
- **Tablet**: Adaptive layout with touch-friendly controls
- **Mobile**: Streamlined interface for small screens

## 🔒 Security Features

- **Input Validation**: Sanitized stock symbol input
- **Error Handling**: Secure error messages
- **CORS Configuration**: Controlled cross-origin requests
- **Environment Variables**: Secure API key storage

## 🚀 Deployment

### Local Development
```bash
python run.py
```

### Production Deployment
1. Set environment variables for production
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Configure reverse proxy (Nginx, Apache)
4. Set up SSL certificates

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app.app:app
```

## 📊 API Endpoints

### GET `/`
Returns API information and documentation

### GET `/stock/<symbol>`
Returns real-time stock data for the given symbol

**Response Example:**
```json
{
  "symbol": "AAPL",
  "company_name": "Apple Inc.",
  "last_refreshed": "2024-01-15 16:00:00",
  "latest_time_pacific": "2024-01-15 13:00:00 PST",
  "open": "185.50",
  "high": "187.20",
  "low": "184.80",
  "close": "186.30",
  "volume": "1234567",
  "price_change": 0.80,
  "price_change_percent": 0.43,
  "market_status": "open",
  "data_quality": "real_time",
  "source": "Alpha Vantage API"
}
```

## 🐛 Troubleshooting

### Common Issues

**API Key Not Found**
- Ensure your `.env` file contains `ALPHA_VANTAGE_API_KEY`
- Check that the API key is valid and active

**Rate Limit Exceeded**
- Alpha Vantage free tier has rate limits
- Wait a few minutes before making new requests
- Consider upgrading to a premium plan

**Stock Symbol Not Found**
- Verify the symbol is correct (e.g., `GOOGL` not `GOOG`)
- Check that the symbol is supported by Alpha Vantage

**CORS Errors**
- Ensure the Flask backend is running on the correct port
- Check CORS configuration in `app/app.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Alpha Vantage**: For providing the stock data API
- **Bootstrap**: For the responsive CSS framework
- **Bootstrap Icons**: For the beautiful icon set
- **Inter Font**: For the modern typography

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the error logs in the browser console
3. Check the Flask application logs
4. Open an issue on GitHub

---

**Happy Trading! 📈💰** 