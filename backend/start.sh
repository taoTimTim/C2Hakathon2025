#!/bin/bash

# 1. Run your setup scripts
echo "Running setup scripts..."
# python initial_setup.py
python recommendation_service.py

# 2. Start the main server
echo "Starting the server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
