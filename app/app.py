from flask import Flask, jsonify, request
import requests
import os
import re
from dotenv import load_dotenv
from datetime import datetime
import pytz
from flask_cors import CORS
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
SUPPORTED_SYMBOLS = {
    'AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'NFLX', 
    'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'ARKK', 'BTC', 'ETH', 'COIN',
    'SQ', 'PYPL', 'ADBE', 'CRM', 'ORCL', 'IBM', 'INTC', 'AMD', 'NFLX'
}

@app.route('/')
def home():
    """Home route with API information"""
    return jsonify({
        'message': 'StockTracking API',
        'version': '1.0.0',
        'endpoints': {
            'GET /stock/<symbol>': 'Get real-time stock data for a given symbol'
        },
        'supported_symbols': list(SUPPORTED_SYMBOLS)[:10],  # Show first 10
        'documentation': 'Enter a stock symbol to get real-time market data'
    })

@app.route('/stock/<symbol>', methods=['GET'])
def get_stock(symbol):
    """
    Get real-time stock data for a given symbol
    
    Args:
        symbol (str): Stock symbol (e.g., AAPL, TSLA)
    
    Returns:
        JSON response with stock data or error message
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

    # Clean and validate symbol format
    symbol = symbol.upper().strip()
    if not re.match(r'^[A-Z]{1,5}$', symbol):
        return jsonify({
            'error': f'Invalid stock symbol format: {symbol}. Please use 1-5 uppercase letters.',
            'code': 'INVALID_SYMBOL_FORMAT'
        }), 400

    logger.info(f"Fetching stock data for symbol: {symbol}")

    try:
        # Construct API URL
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': '5min',
            'apikey': api_key
        }

        # Make API request with timeout
        response = requests.get(
            ALPHA_VANTAGE_BASE_URL, 
            params=params, 
            timeout=10
        )
        
        # Check for HTTP errors
        response.raise_for_status()
        
        data = response.json()
        logger.info(f"API Response keys: {list(data.keys())}")

        # Handle API-specific errors
        if 'Information' in data:
            if 'rate limit' in data['Information'].lower():
                logger.warning("API rate limit reached")
                return jsonify({
                    'error': 'API rate limit reached. Please try again later or consider upgrading to a premium plan.',
                    'code': 'RATE_LIMIT_EXCEEDED',
                    'details': data['Information']
                }), 429
            else:
                logger.warning(f"API Information message: {data['Information']}")
                return jsonify({
                    'error': f'API Information: {data["Information"]}',
                    'code': 'API_INFORMATION'
                }), 400

        # Check for API error responses
        if 'Error Message' in data:
            logger.error(f"API Error for {symbol}: {data['Error Message']}")
            return jsonify({
                'error': f'Stock symbol "{symbol}" not found. Please check the symbol and try again.',
                'code': 'SYMBOL_NOT_FOUND',
                'details': data['Error Message']
            }), 404

        if 'Note' in data:
            logger.warning(f"API Note for {symbol}: {data['Note']}")
            return jsonify({
                'error': 'API rate limit reached. Please try again later.',
                'code': 'RATE_LIMIT_NOTE',
                'details': data['Note']
            }), 429

        # Validate required data structure
        if 'Meta Data' not in data:
            logger.error(f"Missing Meta Data in API response for {symbol}")
            return jsonify({
                'error': 'Invalid API response format. Please try again.',
                'code': 'INVALID_API_RESPONSE'
            }), 500

        # Extract time series data
        time_series_key = 'Time Series (5min)'
        if time_series_key not in data:
            logger.error(f"Missing time series data for {symbol}. Available keys: {list(data.keys())}")
            return jsonify({
                'error': 'No time series data available for this symbol.',
                'code': 'NO_TIME_SERIES_DATA',
                'available_keys': list(data.keys())
            }), 404

        # Process stock data
        result = process_stock_data(data, symbol)
        logger.info(f"Successfully processed data for {symbol}")
        
        return jsonify(result)

    except requests.exceptions.Timeout:
        logger.error(f"Timeout error fetching data for {symbol}")
        return jsonify({
            'error': 'Request timeout. Please try again.',
            'code': 'REQUEST_TIMEOUT'
        }), 408

    except requests.exceptions.ConnectionError:
        logger.error(f"Connection error fetching data for {symbol}")
        return jsonify({
            'error': 'Network connection error. Please check your internet connection.',
            'code': 'CONNECTION_ERROR'
        }), 503

    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception for {symbol}: {str(e)}")
        return jsonify({
            'error': f'Network error: {str(e)}',
            'code': 'REQUEST_ERROR'
        }), 500

    except Exception as e:
        logger.error(f"Unexpected error processing {symbol}: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred. Please try again.',
            'code': 'INTERNAL_ERROR'
        }), 500

def process_stock_data(data, symbol):
    """
    Process and format stock data from Alpha Vantage API
    
    Args:
        data (dict): Raw API response data
        symbol (str): Stock symbol
    
    Returns:
        dict: Formatted stock data
    """
    meta_data = data['Meta Data']
    time_series = data['Time Series (5min)']
    
    # Get the most recent data point
    latest_time = max(time_series.keys())
    latest_data = time_series[latest_time]
    
    # Convert time to datetime for timezone conversion
    latest_time_dt = datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S')
    
    # Timezone conversion
    eastern_tz = pytz.timezone('US/Eastern')
    pacific_tz = pytz.timezone('US/Pacific')
    
    # Localize and convert time
    latest_time_eastern = eastern_tz.localize(latest_time_dt)
    latest_time_pacific = latest_time_eastern.astimezone(pacific_tz)
    latest_time_pacific_str = latest_time_pacific.strftime('%Y-%m-%d %H:%M:%S %Z')
    
    # Calculate additional metrics
    open_price = float(latest_data['1. open'])
    close_price = float(latest_data['4. close'])
    high_price = float(latest_data['2. high'])
    low_price = float(latest_data['3. low'])
    volume = int(latest_data['5. volume'])
    
    price_change = close_price - open_price
    price_change_percent = (price_change / open_price) * 100 if open_price > 0 else 0
    
    # Format response
    result = {
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
    
    return result

def get_company_name(symbol):
    """
    Get company name for a given symbol
    
    Args:
        symbol (str): Stock symbol
    
    Returns:
        str: Company name or symbol if not found
    """
    company_names = {
        'AAPL': 'Apple Inc.',
        'TSLA': 'Tesla, Inc.',
        'GOOGL': 'Alphabet Inc.',
        'MSFT': 'Microsoft Corporation',
        'AMZN': 'Amazon.com, Inc.',
        'META': 'Meta Platforms, Inc.',
        'NVDA': 'NVIDIA Corporation',
        'NFLX': 'Netflix, Inc.',
        'SPY': 'SPDR S&P 500 ETF Trust',
        'QQQ': 'Invesco QQQ Trust',
        'IWM': 'iShares Russell 2000 ETF',
        'VTI': 'Vanguard Total Stock Market ETF',
        'VOO': 'Vanguard S&P 500 ETF',
        'ARKK': 'ARK Innovation ETF',
        'BTC': 'Bitcoin',
        'ETH': 'Ethereum',
        'COIN': 'Coinbase Global, Inc.',
        'SQ': 'Block, Inc.',
        'PYPL': 'PayPal Holdings, Inc.',
        'ADBE': 'Adobe Inc.',
        'CRM': 'Salesforce, Inc.',
        'ORCL': 'Oracle Corporation',
        'IBM': 'International Business Machines Corporation',
        'INTC': 'Intel Corporation',
        'AMD': 'Advanced Micro Devices, Inc.'
    }
    
    return company_names.get(symbol, symbol)

def get_market_status(pacific_time):
    """
    Determine if market is open based on Pacific time
    
    Args:
        pacific_time (datetime): Pacific time
    
    Returns:
        str: Market status
    """
    # Simple market hours check (9:30 AM - 4:00 PM ET, Monday-Friday)
    # This is a basic implementation - you might want to use a more sophisticated approach
    weekday = pacific_time.weekday()  # Monday = 0, Sunday = 6
    hour = pacific_time.hour
    
    if weekday >= 5:  # Weekend
        return 'closed'
    elif 6 <= hour <= 13:  # 9:30 AM - 4:00 PM ET (6:30 AM - 1:00 PM PT)
        return 'open'
    else:
        return 'closed'

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'code': 'ENDPOINT_NOT_FOUND'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error. Please try again later.',
        'code': 'INTERNAL_SERVER_ERROR'
    }), 500

if __name__ == '__main__':
    # Validate environment
    if not os.getenv('ALPHA_VANTAGE_API_KEY'):
        logger.warning("ALPHA_VANTAGE_API_KEY not found in environment variables")
        logger.info("Please set your Alpha Vantage API key in a .env file")
    
    logger.info("Starting StockTracking API server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
