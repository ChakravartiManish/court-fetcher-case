#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development

# Run the Flask application
python app.py