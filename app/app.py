from flask import Flask, jsonify, request, render_template
import requests
import os
import re
from dotenv import load_dotenv
from datetime import datetime
import pytz
from flask_cors import CORS
import logging

# Load environment variables from parent directory
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app with correct paths
app = Flask(__name__, 
            static_folder='../frontend',
            static_url_path='',
            template_folder='../frontend')
CORS(app)

# Configuration
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
SUPPORTED_SYMBOLS = {
    'AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'NFLX', 
    'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'ARKK', 'BTC', 'ETH', 'COIN',
    'SQ', 'PYPL', 'ADBE', 'CRM', 'ORCL', 'IBM', 'INTC', 'AMD', 'NFLX'
}

@app.route('/')
def home():
    """Serve the main HTML page"""
    return render_template('index.html')

@app.route('/api')
def api_info():
    """API information endpoint"""
    return jsonify({
        'message': 'StockTracking API',
        'version': '1.0.0',
        'endpoints': {
            'GET /': 'Main application page',
            'GET /api': 'API information',
            'GET /api/stock/<symbol>': 'Get real-time stock data for a given symbol'
        },
        'supported_symbols': list(SUPPORTED_SYMBOLS)[:10],
        'documentation': 'Enter a stock symbol to get real-time market data'
    })

@app.route('/api/stock/<symbol>', methods=['GET'])
def get_stock(symbol):
    """
    Get real-time stock data for a given symbol
    """
    # Validate API key
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        logger.error("API key not found in environment variables")
        return jsonify({
            'error': 'API configuration error. Please contact support.',
            'code': 'API_KEY_MISSING'
        }), 500

    # Validate and sanitize symbol
    if not symbol:
        return jsonify({
            'error': 'Stock symbol is required',
            'code': 'SYMBOL_REQUIRED'
        }), 400

    symbol = symbol.upper().strip()
    if not re.match(r'^[A-Z]{1,5}$', symbol):
        return jsonify({
            'error': f'Invalid stock symbol format: {symbol}. Please use 1-5 uppercase letters.',
            'code': 'INVALID_SYMBOL_FORMAT'
        }), 400

    logger.info(f"Fetching stock data for symbol: {symbol}")

    try:
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': '5min',
            'apikey': api_key
        }

        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"API Response keys: {list(data.keys())}")

        if 'Information' in data:
            if 'rate limit' in data['Information'].lower():
                return jsonify({
                    'error': 'API rate limit reached. Please try again later.',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'details': data['Information']
                }), 429
            else:
                return jsonify({
                    'error': f'API Information: {data["Information"]}',
                    'code': 'API_INFORMATION'
                }), 400

        if 'Error Message' in data:
            return jsonify({
                'error': f'Stock symbol "{symbol}" not found.',
                'code': 'SYMBOL_NOT_FOUND',
                'details': data['Error Message']
            }), 404

        if 'Note' in data:
            return jsonify({
                'error': 'API rate limit reached. Please try again later.',
                'code': 'RATE_LIMIT_NOTE',
                'details': data['Note']
            }), 429

        if 'Meta Data' not in data:
            return jsonify({
                'error': 'Invalid API response format.',
                'code': 'INVALID_API_RESPONSE'
            }), 500

        time_series_key = 'Time Series (5min)'
        if time_series_key not in data:
            return jsonify({
                'error': 'No time series data available.',
                'code': 'NO_TIME_SERIES_DATA'
            }), 404

        result = process_stock_data(data, symbol)
        return jsonify(result)

    except requests.exceptions.Timeout:
        return jsonify({'error': 'Request timeout.', 'code': 'REQUEST_TIMEOUT'}), 408
    except requests.exceptions.ConnectionError:
        return jsonify({'error': 'Network connection error.', 'code': 'CONNECTION_ERROR'}), 503
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Network error: {str(e)}', 'code': 'REQUEST_ERROR'}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred.', 'code': 'INTERNAL_ERROR'}), 500

def process_stock_data(data, symbol):
    """Process and format stock data"""
    meta_data = data['Meta Data']
    time_series = data['Time Series (5min)']
    
    latest_time = max(time_series.keys())
    latest_data = time_series[latest_time]
    
    latest_time_dt = datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S')
    eastern_tz = pytz.timezone('US/Eastern')
    pacific_tz = pytz.timezone('US/Pacific')
    
    latest_time_eastern = eastern_tz.localize(latest_time_dt)
    latest_time_pacific = latest_time_eastern.astimezone(pacific_tz)
    latest_time_pacific_str = latest_time_pacific.strftime('%Y-%m-%d %H:%M:%S %Z')
    
    open_price = float(latest_data['1. open'])
    close_price = float(latest_data['4. close'])
    
    price_change = close_price - open_price
    price_change_percent = (price_change / open_price) * 100 if open_price > 0 else 0
    
    return {
        'symbol': meta_data['2. Symbol'],
        'company_name': get_company_name(symbol),
        'last_refreshed': meta_data['3. Last Refreshed'],
        'latest_time_eastern': latest_time,
        'latest_time_pacific': latest_time_pacific_str,
        'open': latest_data['1. open'],
        'high': latest_data['2. high'],
        'low': latest_data['3. low'],
        'close': latest_data['4. close'],
        'volume': latest_data['5. volume'],
        'price_change': round(price_change, 2),
        'price_change_percent': round(price_change_percent, 2),
        'market_status': get_market_status(latest_time_pacific),
        'data_quality': 'real_time',
        'source': 'Alpha Vantage API'
    }

def get_company_name(symbol):
    """Get company name for symbol"""
    company_names = {
        'AAPL': 'Apple Inc.', 'TSLA': 'Tesla, Inc.', 'GOOGL': 'Alphabet Inc.',
        'MSFT': 'Microsoft Corporation', 'AMZN': 'Amazon.com, Inc.',
        'META': 'Meta Platforms, Inc.', 'NVDA': 'NVIDIA Corporation',
        'NFLX': 'Netflix, Inc.', 'SPY': 'SPDR S&P 500 ETF Trust',
        'QQQ': 'Invesco QQQ Trust', 'IWM': 'iShares Russell 2000 ETF',
        'VTI': 'Vanguard Total Stock Market ETF', 'VOO': 'Vanguard S&P 500 ETF',
        'ARKK': 'ARK Innovation ETF', 'BTC': 'Bitcoin', 'ETH': 'Ethereum',
        'COIN': 'Coinbase Global, Inc.', 'SQ': 'Block, Inc.',
        'PYPL': 'PayPal Holdings, Inc.', 'ADBE': 'Adobe Inc.',
        'CRM': 'Salesforce, Inc.', 'ORCL': 'Oracle Corporation',
        'IBM': 'International Business Machines Corporation',
        'INTC': 'Intel Corporation', 'AMD': 'Advanced Micro Devices, Inc.'
    }
    return company_names.get(symbol, symbol)

def get_market_status(pacific_time):
    """Determine market status"""
    weekday = pacific_time.weekday()
    hour = pacific_time.hour
    
    if weekday >= 5:
        return 'closed'
    elif 6 <= hour <= 13:
        return 'open'
    else:
        return 'closed'

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'code': 'ENDPOINT_NOT_FOUND'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error.', 'code': 'INTERNAL_SERVER_ERROR'}), 500

if __name__ == '__main__':
    if not os.getenv('ALPHA_VANTAGE_API_KEY'):
        logger.warning("ALPHA_VANTAGE_API_KEY not found")
    logger.info("Starting StockTracking API server...")
    app.run(debug=True, host='0.0.0.0', port=5001)