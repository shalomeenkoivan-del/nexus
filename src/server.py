from flask import Flask, render_template, request, jsonify, session
from main import ip
import secrets
from datetime import datetime
import os
from core import Core

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)
core = Core()

chat_history = []
active_sessions = set()

@app.route('/')
def index():
    if session.get('logged_in'):
        return render_template('chat.html')
    return render_template('console.html')

@app.route('/chat')
def chat_page():
    if not session.get('logged_in'):
        return '<script>window.location.href="/";</script>'
    return render_template('chat.html')

@app.route('/command', methods=['POST'])
def command():
    data = request.json
    cmd = data.get('command', '').strip()
    
    if cmd == "login nyxx":
        session['logged_in'] = True
        session['user_id'] = "NYXX_MASTER"
        session['username'] = "NYXX"
        active_sessions.add("NYXX_MASTER")
        timestamp = datetime.now().strftime("%H:%M:%S")
        chat_history.append({
            "user": "SYSTEM", "user_id": "SYSTEM",
            "message": "NYXX(MASTER) entered the Shadows!", "time": timestamp, "system": True
        })
        return jsonify({'output': 'MASTER NYXX-mode activated! Opening chat...', 'redirect': '/chat'})

    elif cmd == "register":
        user_data = core.register()
        output_lines = [
            "Account is succesfully created!",
            f"Your username: {user_data['username']}",
            f"Your user ID: {user_data['user_id']}",
            "Your seed phrase:",
            user_data['seed_phrase'],
            "",
            "> Save it and use to login!"
        ]
        return jsonify({
            'output': '\n'.join(output_lines),
            'username': user_data['username'],
            'user_id': user_data['user_id'],
            'seed_phrase': user_data['seed_phrase'],
            'update_status': True
        })
        
    elif cmd == "login":
        return jsonify({'output': 'Enter: login [seed phrase]'})
    
    if cmd.startswith("login "):
        seed = cmd[6:].strip()
        user_data = core.login(seed)
        if user_data:
            session['logged_in'] = True
            session['user_id'] = user_data['user_id']
            session['username'] = user_data['username']
            active_sessions.add(user_data['user_id'])
            timestamp = datetime.now().strftime("%H:%M:%S")
            chat_history.append({
                "user": "SYSTEM", "user_id": "SYSTEM",
                "message": f"{user_data['username']} entered the Shadows!", "time": timestamp, "system": True
            })
            return jsonify({'output': f'Successfully authenticated! Opening chat...', 'redirect': '/chat'})
        else:
            return jsonify({'output': 'Invalid seed!'})
    
    if session.get('logged_in') and cmd == "exit":
        user_id = session.get('user_id')
        timestamp = datetime.now().strftime("%H:%M:%S")
        chat_history.append({
            "user": "SYSTEM", "user_id": "SYSTEM",
            "message": f"{session.get('username')} left the Shadows", "time": timestamp, "system": True
        })
        if user_id:
            active_sessions.discard(user_id)
        session.clear()
        return jsonify({'output': 'Logged out', 'redirect': True})

    return jsonify({'output': 'Commands: register / login [seed phrase]'})

@app.route('/chat_send', methods=['POST'])
def chat_send():
    if not session.get('logged_in'):
        return jsonify({'error': 'Login first!'})
    data = request.json
    message = data.get('message', '').strip()
    if message:
        timestamp = datetime.now().strftime("%H:%M:%S")
        chat_history.append({
            "user": session['username'],
            "user_id": session['user_id'],
            "message": message,
            "time": timestamp,
            "system": False
        })
    return jsonify({'status': 'ok'})

@app.route('/chat_history')
def chat_history_route():
    return jsonify({'history': chat_history[-50:]})

@app.route('/current_user')
def current_user():
    return jsonify({'username': session.get('username', 'Guest')})

@app.route('/status')
def status():
    return jsonify({
        'current_user': session.get('username', 'Guest'),
        'online_users': len(active_sessions),
        'total_messages': len(chat_history)
    })

@app.route('/console_status')
def console_status():
    if not os.path.exists('data/users'):
        return jsonify({'total_users': 0})
    user_files = [f for f in os.listdir('data/users') if f.endswith('.json')]
    return jsonify({'total_users': len(user_files)})

if __name__ == '__main__':
    os.makedirs('data/users', exist_ok=True)
    os.makedirs('data/images', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    print(f"Shadows: {ip}:5000")
    app.run(host=ip, port=5000, debug=True, threaded=True)