"""
Configuration settings for StockTracking application
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class"""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # API settings
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
    ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
    
    # Request settings
    REQUEST_TIMEOUT = 10  # seconds
    MAX_RETRIES = 3
    
    # CORS settings
    CORS_ORIGINS = [
        'http://localhost:3000',
        'http://127.0.0.1:5000',
        'http://localhost:5000',
        'http://127.0.0.1:5500',
        'http://localhost:5500'
    ]
    
    # Supported stock symbols (for validation)
    SUPPORTED_SYMBOLS = {
        'AAPL', 'TSLA', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'NFLX', 
        'SPY', 'QQQ', 'IWM', 'VTI', 'VOO', 'ARKK', 'BTC', 'ETH', 'COIN',
        'SQ', 'PYPL', 'ADBE', 'CRM', 'ORCL', 'IBM', 'INTC', 'AMD'
    }
    
    # Company names mapping
    COMPANY_NAMES = {
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
    
    # Market hours (Eastern Time)
    MARKET_OPEN_HOUR = 9
    MARKET_OPEN_MINUTE = 30
    MARKET_CLOSE_HOUR = 16
    MARKET_CLOSE_MINUTE = 0
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Rate limiting (if implemented)
    RATE_LIMIT_REQUESTS = 100  # requests per hour
    RATE_LIMIT_WINDOW = 3600   # 1 hour in seconds

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    
    # Override with production settings
    SECRET_KEY = os.getenv('SECRET_KEY')
    
    @classmethod
    def validate(cls):
        if not cls.SECRET_KEY:
            raise ValueError("SECRET_KEY must be set in production")

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
