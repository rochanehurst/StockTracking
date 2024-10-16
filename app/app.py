from flask import Flask, jsonify, request  # Importing Flask utility functions
import requests  # Importing requests library to handle HTTP requests to external APIs
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route('/')
def home():
    return "Welcome to the Stock Tracker"


@app.route('/stock/<symbol>', methods=['GET'])  # Defines a route to fetch the stock data, symbol is stock symbol.
def get_stock(symbol):
    api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    # URL link to API
    if not api_key:
        return jsonify({'error': 'API Key not found'}), 500

    base_url = (f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='
                f'{symbol}&interval=5min&apikey={api_key}')

    # PLACEHOLDER: Add search API to match symbol to company's name // API has limit use

    # try and catch
    try:
        response = requests.get(base_url)  # makes an HTTP request to the URL to retrieve data
        data = response.json()  # converts to a python dictionary

        print("API Response:", data.keys())

        # Check for API rate limit in the response
        if 'Information' in data and 'rate limit' in data['Information']:
            return jsonify({'error': 'API rate limit reached. Please try again tomorrow or consider upgrading to a '
                            'premium plan.'}), 429

        # If 'Meta Data' is not found, handle it
        if 'Meta Data' not in data:
            return jsonify({'error': "An error occurred fetching stock data: 'Meta Data' not found"}), 500

        if 'Error' in data or 'Note' in data:
            # handles an error in case a stock symbol wasn't found or API limit was reached, and returns a 404 status
            return jsonify({'error': 'stock not found or API limit reached'}), 404

        # extracts metadata and latest stock price from the time series
        meta_data = data['Meta Data']

        # prints all available key for debugging purposes
        print("Time series keys:", data.keys())

        # stores the key for 5-minute time series data
        time_series_key = 'Time Series (5min)'
        # checks if time series(5 min) is not in data, then returns an error message
        # with the available keys
        if time_series_key not in data:
            return jsonify({'error': f"Time series data not found. Available keys: {list(data.keys())}"}), 404

        # if available, data is extracted and returned
        time_series = data[time_series_key]

        # get the most recent entry (like the latest stock price) with the latest time stamp
        latest_time = max(time_series.keys())
        # extracts the stock data (open,close,high,low, etc) for the latest time entry
        latest_data = time_series[latest_time]

        # converts latest time to datetime object
        latest_time_dt = datetime.strptime(latest_time, '%Y-%m-%d %H:%M:%S')

        # Timezones defined
        eastern_tz = pytz.timezone('US/Eastern')
        pacific_tz = pytz.timezone('US/Pacific')

        # localize latest time to eastern and converts to pacific
        latest_time_eastern = eastern_tz.localize(latest_time_dt)
        latest_time_pacific = latest_time_eastern.astimezone(pacific_tz)

        # formatted time pacific time zone
        latest_time_pacific_str = latest_time_pacific.strftime('%Y-%m-%d %H:%M:%S %Z')

        # dictionary formatted to return only relevant info
        result = {
            'symbol': meta_data['2. Symbol'],
            'last_refreshed': meta_data['3. Last Refreshed'],
            'latest_time_eastern': latest_time,
            'latest_time_pacific': latest_time_pacific_str,
            'open': latest_data['1. open'],
            'high': latest_data['2. high'],
            'low': latest_data['3. low'],
            'close': latest_data['4. close'],
            'volume': latest_data['5. volume']
        }

        # converts result into json and returns
        return jsonify(result)

    # catches HTTP related exceptions and prints error message
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {e}")
        return jsonify({'error': f'An error occurred fetching stock data: {e}'})

    # catches any other exceptions that might occur during execution.
    except Exception as e:
        return jsonify({'error': f'An error occurred fetching stock data: {e}'}), 500


if __name__ == '__main__':
    app.run(debug=True)
