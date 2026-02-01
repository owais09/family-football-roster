#!/bin/bash
# Start virtual display for pywhatkit
Xvfb :99 -screen 0 1024x768x24 > /dev/null 2>&1 &

# Wait a moment for Xvfb to start
sleep 2

# Start Streamlit app
python -m streamlit run src/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.serverAddress=0.0.0.0 \
    --browser.gatherUsageStats=false
