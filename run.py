#!/usr/bin/env python3
"""
StockTracking Application Entry Point
"""

import os
import sys
from app.app import app
from config import get_config

def main():
    """Main application entry point"""
    
    # Get configuration
    config = get_config()
    
    # Set Flask configuration
    app.config.from_object(config)
    
    # Validate environment
    if not os.getenv('ALPHA_VANTAGE_API_KEY'):
        print("⚠️  Warning: ALPHA_VANTAGE_API_KEY not found in environment variables")
        print("   Please set your Alpha Vantage API key in a .env file")
        print("   Get a free API key at: https://www.alphavantage.co/support/#api-key")
        print()
    
    # Print startup information
    print("🚀 Starting StockTracking Application...")
    print(f"   Environment: {os.getenv('FLASK_ENV', 'development')}")
    print(f"   Debug Mode: {config.DEBUG}")
    print(f"   API Key: {'✅ Set' if os.getenv('ALPHA_VANTAGE_API_KEY') else '❌ Missing'}")
    print()
    print("📱 Frontend: http://localhost:5001")
    print("🔧 API Docs: http://localhost:5001/")
    print()
    print("Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Run the application
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=config.DEBUG,
            use_reloader=config.DEBUG
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down StockTracking...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()