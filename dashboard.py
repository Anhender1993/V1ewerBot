from flask import Flask, render_template_string
import os
import json

app = Flask(__name__)

STREAMERS_FILE = 'streamers.json'

def load_streamers():
    if os.path.exists(STREAMERS_FILE):
        with open(STREAMERS_FILE, 'r') as f:
            return json.load(f)
    return []

@app.route('/')
def dashboard():
    streamers = load_streamers()
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>V1ewerbot Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; background: #f7f7f7; }
            h1 { color: #333; }
            ul { background: white; padding: 20px; border-radius: 8px; list-style-type: none; }
            li { padding: 8px; border-bottom: 1px solid #eee; }
            li:last-child { border-bottom: none; }
        </style>
    </head>
    <body>
        <h1>Currently Tracked Streamers</h1>
        <ul>
            {% for streamer in streamers %}
                <li>{{ streamer }}</li>
            {% endfor %}
        </ul>
    </body>
    </html>
    ''', streamers=streamers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
