from flask import Flask, render_template_string, request, redirect
import os
import json

app = Flask(__name__)

STREAMERS_FILE = 'streamers.json'

def load_streamers():
    if os.path.exists(STREAMERS_FILE):
        with open(STREAMERS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_streamers(streamers):
    with open(STREAMERS_FILE, 'w') as f:
        json.dump(streamers, f, indent=2)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    streamers = load_streamers()

    if request.method == 'POST':
        action = request.form.get('action')
        streamer = request.form.get('streamer').strip()

        if action == 'add' and streamer:
            if streamer not in streamers:
                streamers.append(streamer)
                save_streamers(streamers)
        elif action == 'remove' and streamer:
            if streamer in streamers:
                streamers.remove(streamer)
                save_streamers(streamers)
        return redirect('/')

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
            form { margin-top: 20px; }
            input, button { padding: 8px; margin-right: 10px; }
        </style>
    </head>
    <body>
        <h1>Currently Tracked Streamers</h1>
        <ul>
            {% for streamer in streamers %}
                <li>{{ streamer }}</li>
            {% endfor %}
        </ul>

        <form method="post">
            <input type="text" name="streamer" placeholder="Streamer Name" required>
            <button type="submit" name="action" value="add">Add Streamer</button>
            <button type="submit" name="action" value="remove">Remove Streamer</button>
        </form>
    </body>
    </html>
    ''', streamers=streamers)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
