#!/bin/bash

# Stop all running Python processes
echo "Stopping all running Python processes..."
pkill -f python3

# Wait for processes to terminate (optional)
sleep 2

# Start the Python application using uvicorn (adjust with your app's entry point)
echo "Starting the Python app using"
nohup python3 main.py > api.log 2>&1 &

# Start the Streamlit UI app in the background
echo "Starting the Streamlit UI..."
nohup streamlit run ui.py > streamlit.log 2>&1 &

# Print message
echo "Both applications are running in the background."
