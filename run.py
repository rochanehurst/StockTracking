from app import app

if __name__ == '__main__': #ensures the app runs only if the file is executed directly
    app.run(debug=True) #starts flask with debug mode enabled