#!/bin/bash
# Start LifeOS on the local network (accessible from all devices on your WiFi)
# Usage: ./start.sh [--reload]

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtualenv if present
if [ -f "myenv/bin/activate" ]; then
    source myenv/bin/activate
fi

echo "Starting LifeOS at http://0.0.0.0:8000"
echo "Access from other devices: http://$(python3 -c 'import socket; s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM); s.connect(("8.8.8.8",80)); print(s.getsockname()[0]); s.close()' 2>/dev/null || echo "localhost"):8000"

exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
