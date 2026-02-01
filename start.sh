#!/bin/bash
# Create Xauthority file to prevent X auth errors
touch ~/.Xauthority
xauth generate :99 . trusted 2>/dev/null || true

# Start virtual display for pywhatkit
Xvfb :99 -screen 0 1024x768x24 -ac +extension GLX +render -noreset > /dev/null 2>&1 &

# Wait for Xvfb to start
sleep 3

# Verify Xvfb is running
export DISPLAY=:99
xdpyinfo > /dev/null 2>&1 || echo "Warning: Xvfb may not be running properly"

# Start Streamlit app
exec python -m streamlit run src/app.py \
    --server.port=8501 \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.serverAddress=0.0.0.0 \
    --browser.gatherUsageStats=false
