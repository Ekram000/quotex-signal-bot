from flask import Flask, render_template
import threading

app = Flask(__name__)
signal_data = []

@app.route('/')
def dashboard():
    return render_template('dashboard.html', signals=signal_data[::-1])

def update_signals(signals):
    global signal_data
    signal_data = signals

def start_dashboard():
    app.run(host="0.0.0.0", port=5000)