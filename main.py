#!/usr/bin/env python3
"""
Entry point for running the D&D Character Sheet server.

Usage:
    python main.py
"""

import socket
from app.server import app

if __name__ == '__main__':
    try:
        local_ip = socket.gethostbyname(socket.gethostname())
    except BaseException:
        local_ip = '127.0.0.1'

    print("\n🎲 D&D Character Sheet Server (5e 2014 + 2024)")
    print("   Local:   http://localhost:5000")
    print(f"   Network: http://{local_ip}:5000\n")
    app.run(host='0.0.0.0', port=5000, debug=False)
