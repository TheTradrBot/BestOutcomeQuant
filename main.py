"""
FTMO 200K Trading Bot - Status Server

This is a minimal web server that provides status information about the project.
The actual trading bot (main_live_bot.py) runs on a Windows VM with MetaTrader 5.
"""

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "name": "FTMO 200K Trading Bot",
        "description": "MetaTrader 5 trading bot for FTMO 200K challenge accounts",
        "components": {
            "main_live_bot": "Standalone MT5 live trading bot (runs on Windows VM)",
            "ftmo_challenge_analyzer": "Optimization engine using 2024 historical data"
        }
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    print("Starting FTMO 200K Trading Bot Status Server...")
    app.run(host="0.0.0.0", port=5000, debug=False)
