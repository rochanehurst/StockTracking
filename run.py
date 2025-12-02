#!/usr/bin/env python3
"""
StockTracking Application Entry Point
"""

import os
import sys

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import app

def main():
    """Main application entry point"""
    
    # Validate environment
    if not os.getenv('ALPHA_VANTAGE_API_KEY'):
        print("⚠️  Warning: ALPHA_VANTAGE_API_KEY not found")
        print("   Please set your Alpha Vantage API key in .env file")
        print()
    
    print("🚀 Starting StockTracking Application...")
    print(f"   API Key: {'✅ Set' if os.getenv('ALPHA_VANTAGE_API_KEY') else '❌ Missing'}")
    print()
    print("📱 Frontend: http://localhost:5001")
    print("🔧 API: http://localhost:5001/api")
    print()
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        app.run(host='0.0.0.0', port=5001, debug=True)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()