from flask import Flask, render_template, request, jsonify, session, send_from_directory
import socket
import secrets
from datetime import datetime
import os
import json
from ip_config import get_server_ip
from config import DIRS, TEMPLATES_DIR
from services import AuthService
from storage import RoomStorage
from typing import List
import threading
import time
from waitress import serve
import hashlib
from werkzeug.middleware.proxy_fix import ProxyFix

chat_rooms_lock = threading.Lock()
active_sessions_lock = threading.Lock()
unread_counts_lock = threading.Lock()
unread_counts = {}

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))
app.secret_key = secrets.token_hex(32)

auth_service = AuthService()
room_storage = RoomStorage()

USER_ROOMS_DIR = DIRS["user_rooms"]

chat_rooms = room_storage.load_global_chat_rooms()
active_sessions = set()

user_current_room = {}
user_current_room_lock = threading.Lock()

def mark_room_read(user_id, room_name):
    with unread_counts_lock:
        if user_id in unread_counts:
            unread_counts[user_id][room_name] = 0

def get_user_rooms_file(user_id):
    os.makedirs(USER_ROOMS_DIR, exist_ok=True)
    return os.path.join(USER_ROOMS_DIR, f"{user_id}.json")

def load_user_rooms(user_id):
    file_path = get_user_rooms_file(user_id)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return ["general"]

def save_user_rooms(user_id, user_rooms):
    file_path = get_user_rooms_file(user_id)
    with open(file_path, 'w') as f:
        json.dump(user_rooms, f)

def get_user_color(user_id):
    if user_id == "SYSTEM":
        return "#FFFFFF"
    
    if user_id == "NYXX_MASTER":
        return "#00FF88"
    
    hash_val = int(hashlib.md5(user_id.encode()).hexdigest(), 16) % 360
    return f"hsl({hash_val}, 70%, 60%)"

@app.route('/set_current_room', methods=['POST'])
def set_current_room():
    if not session.get('logged_in'):
        return jsonify({'success': False})
    room = request.json.get('room', 'general')
    with user_current_room_lock:
        user_current_room[session['user_id']] = room
    return jsonify({'success': True})

@app.route('/unread_counts_only')
def unread_counts_only():
    if not session.get('logged_in'):
        return jsonify({'unread_counts': {}})
    user_id = session['user_id']
    with unread_counts_lock:
        user_unread = unread_counts.get(user_id, {})
    return jsonify({'unread_counts': user_unread})

@app.route('/user_color/<user_id>')
def user_color(user_id):
    color = get_user_color(user_id)
    return jsonify({'color': color})

@app.route('/')
def index():
    return render_template('loading.html')

@app.route('/chat')
def chat_page():
    if not session.get('logged_in'):
        return '<script>window.location.href="/";</script>'
    return render_template('chat.html', username=session['username'])

@app.route('/chat.html')
def chat_html():
    if not session.get('logged_in'):
        return '<script>window.location.href="/";</script>'
    return render_template('chat.html', username=session['username'])

@app.route('/console', methods=['GET', 'POST'])
def console():
    if request.method == 'POST':
        username = request.form.get('username') or request.form.get('shadow_name', '').strip()
        if username:
            session['logged_in'] = True
            session['user_id'] = username
            session['username'] = username
            with active_sessions_lock:
                active_sessions.add(username)
            with chat_rooms_lock:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                chat_rooms["general"].append({
                    "user": "SYSTEM", "user_id": "SYSTEM",
                    "message": f"{username} entered the Shadows!", "time": timestamp, "system": True
                })
            return render_template('login.html', username=username)
    return render_template('console.html')

@app.route('/login')
def login_page():
    if not session.get('logged_in'):
        return '<script>window.location.href="/console";</script>'
    username = session.get('username', 'Unknown')
    return render_template('login.html', username=username)

@app.route('/command', methods=['POST'])
def command():
    data = request.json
    cmd = data.get('command', '').strip()
    
    if cmd == "login nyxx":
        with active_sessions_lock:
            session['logged_in'] = True
            session['user_id'] = "NYXX_MASTER"
            session['username'] = "NYXX"
            active_sessions.add("NYXX_MASTER")
            
        with chat_rooms_lock:    
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            chat_rooms["general"].append({
                "user": "SYSTEM", "user_id": "SYSTEM",
                "message": "NYXX(MASTER) entered the Shadows!", "time": timestamp, "system": True
            })
        
        return jsonify({'output': 'MASTER NYXX-mode activated! Opening chat...', 'redirect': '/chat'})

    elif cmd == "register":
        user_data = auth_service.register()
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
        user_data = auth_service.login(seed)
        if user_data:
            session['logged_in'] = True
            session['user_id'] = user_data.user_id
            session['username'] = user_data.username
            with active_sessions_lock:
                active_sessions.add(user_data.user_id)
            with chat_rooms_lock:
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                chat_rooms["general"].append({
                    "user": "SYSTEM", "user_id": "SYSTEM",
                    "message": f"{user_data.username} entered the Shadows!", "time": timestamp, "system": True
                })
            return jsonify({'output': f'Successfully authenticated! Opening chat...', 'redirect': '/login'})
        else:
            return jsonify({'output': 'Invalid seed!'})
    
    if session.get('logged_in') and cmd == "exit":
        user_id = session.get('user_id')
        with chat_rooms_lock:
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            chat_rooms["general"].append({
                "user": "SYSTEM", "user_id": "SYSTEM",
                "message": f"{session.get('username')} left the Shadows", "time": timestamp, "system": True
            })
        with active_sessions_lock:
            if user_id:
                active_sessions.discard(user_id)
        session.clear()
        return jsonify({'output': 'Logged out', 'redirect': True})

    return jsonify({'output': 'Commands: register / login [seed phrase]'})

@app.route('/add_room', methods=['POST'])
def add_room():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Login first!'})

    data = request.json
    room_name = data.get('room', '').strip().lower()

    if not room_name or room_name == 'general':
        return jsonify({'success': False, 'message': 'Invalid room name'})

    user_id = session['user_id']
    username = session['username']
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    if user_id == "NYXX_MASTER":
        with chat_rooms_lock:
            if room_name in chat_rooms:
                return jsonify({'success': False, 'message': 'Room already exists!'})

            chat_rooms[room_name] = [{
                "user": "SYSTEM", "user_id": "SYSTEM",
                "message": f"Global room '{room_name}' created by NYXX",
                "time": timestamp, "system": True
            }]
            chat_rooms["general"].append({
                "user": "SYSTEM", "user_id": "SYSTEM",
                "message": f"NYXX created global room \"{room_name}\"!",
                "time": timestamp, "system": True
            })

        global_names = room_storage.load_global_room_names()
        if room_name not in global_names:
            global_names.append(room_name)
            room_storage.save_global_room_names(global_names)

        return jsonify({
            'success': True,
            'message': f'Global room "{room_name}" created!',
            'switch_to': room_name
        })

    user_rooms = load_user_rooms(user_id)

    if room_name in user_rooms:
        return jsonify({
            'success': True,
            'message': f'Already in room "{room_name}"!',
            'switch_to': room_name
        })

    with chat_rooms_lock:
        if room_name in chat_rooms:
            pass
        else:
            chat_rooms[room_name] = [{
                "user": "SYSTEM", "user_id": "SYSTEM",
                "message": f"Room '{room_name}' created by {username}",
                "time": timestamp, "system": True
            }]

    global_rooms = room_storage.load_global_room_names()
    if room_name not in global_rooms:
        user_rooms.append(room_name)
        save_user_rooms(user_id, user_rooms)

    return jsonify({
        'success': True,
        'message': f'{"Created" if room_name not in chat_rooms else "Joined"} room "{room_name}"!',
        'switch_to': room_name
    })

@app.route('/delete_room', methods=['POST'])
def delete_room():
    if not session.get('logged_in'):
        return jsonify({'success': False, 'message': 'Login first!'})

    data = request.json
    room_name = data.get('room', '').strip().lower()

    if room_name == 'general':
        return jsonify({'success': False, 'message': 'Cannot remove general room'})

    user_id = session['user_id']
    
    if user_id == "NYXX_MASTER":
        global_rooms = room_storage.load_global_room_names()
        if room_name in global_rooms:
            with chat_rooms_lock:
                if room_name in chat_rooms:
                    del chat_rooms[room_name]
                timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                chat_rooms["general"].append({
                    "user": "SYSTEM", "user_id": "SYSTEM",
                    "message": f"NYXX deleted global room \"{room_name}\"",
                    "time": timestamp, "system": True
                })
            
            global_rooms.remove(room_name)
            room_storage.save_global_room_names(global_rooms)

            return jsonify({
                'success': True,
                'message': f'Global room "{room_name}" deleted by NYXX!',
            })
        else:
            return jsonify({'success': False, 'message': 'Room not found'})

    global_rooms = room_storage.load_global_room_names()
    if room_name in global_rooms:
        return jsonify({'success': False, 'message': 'Global rooms cannot be removed!'})

    user_rooms = load_user_rooms(user_id)

    if room_name in user_rooms:
        user_rooms.remove(room_name)
        save_user_rooms(user_id, user_rooms)
        return jsonify({
            'success': True,
            'message': f'Room "{room_name}" removed!',
        })

    return jsonify({'success': False, 'message': 'Room not found in your list'})

@app.route('/rooms_separated_with_unread')
def get_rooms_separated_with_unread():
    if not session.get('logged_in'):
        return jsonify({'global_rooms': [], 'user_rooms': [], 'unread_counts': {}})
    
    user_id = session['user_id']
    global_rooms_raw = room_storage.load_global_room_names()
    
    global_rooms = ['general']
    other_globals = sorted([r for r in global_rooms_raw if r != 'general'])
    global_rooms.extend(other_globals)
    
    user_rooms = load_user_rooms(user_id)
    personal_rooms = [r for r in user_rooms if r not in global_rooms]
    
    with unread_counts_lock:
        user_unread = unread_counts.get(user_id, {})
    
    return jsonify({
        'global_rooms': global_rooms,
        'user_rooms': personal_rooms,
        'unread_counts': user_unread,
        'is_nyxx': user_id == "NYXX_MASTER"
    })

@app.route('/save_user_rooms_order', methods=['POST'])
def save_user_rooms_order():
    if not session.get('logged_in'):
        return jsonify({'success': False})
    
    data = request.json
    user_id = session['user_id']
    rooms = data.get('rooms', [])
    
    save_user_rooms(user_id, rooms)
    return jsonify({'success': True})

@app.route('/mark_read', methods=['POST'])
def mark_read():
    if not session.get('logged_in'):
        return jsonify({'success': False})
    
    data = request.json
    room_name = data.get('room', 'general')
    user_id = session['user_id']
    
    mark_room_read(user_id, room_name)
    return jsonify({'success': True})

@app.route('/chat_history')
def chat_history_route():
    room = request.args.get('room', 'general').lower()
    since = request.args.get('since')

    with chat_rooms_lock:
        full_history = chat_rooms.get(room, [])
        if since:
            try:
                for i, msg in enumerate(full_history):
                    if msg["time"] > since:
                        history = full_history[i:]
                        break
                else:
                    history = []
            except Exception:
                history = full_history[-50:]
        else:
            history = full_history[-50:]

    response = jsonify({'history': history})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/chat_send', methods=['POST'])
def chat_send():
    if not session.get('logged_in'):
        return jsonify({'error': 'Login first!'})
    
    data = request.json
    message = data.get('message', '').strip()
    room = data.get('room', 'general').lower()
    
    sender_id = session['user_id']
    sender_name = session['username']

    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]

    if message and room in chat_rooms:
        with chat_rooms_lock:
            chat_rooms[room].append({
                "user": sender_name,
                "user_id": sender_id,
                "message": message,
                "time": timestamp,
                "system": False
            })

    with unread_counts_lock:
        for user_id in list(active_sessions):
            if user_id == sender_id:
                continue
            with user_current_room_lock:
                user_room = user_current_room.get(user_id, 'general')
            if user_room == room:
                continue
            if user_id not in unread_counts:
                unread_counts[user_id] = {}
            unread_counts[user_id][room] = unread_counts[user_id].get(room, 0) + 1
    
    return jsonify({'status': 'ok'})

@app.route('/current_user')
def current_user():
    return jsonify({'username': session.get('username', 'Guest')})

@app.route('/status')
def status():
    with active_sessions_lock:
        online_count = len(active_sessions)
    
    with chat_rooms_lock:
        total_messages = sum(len(messages) for messages in chat_rooms.values())
            
    return jsonify({
        'current_user': session.get('username', 'Guest'),
        'online_users': online_count,
        'total_messages': total_messages
    })

@app.route('/console_status')
def console_status():
    from storage.user_storage import UserStorage
    storage = UserStorage()
    return jsonify({'total_users': storage.total_users()})

@app.route('/data/sounds/<path:filename>')
def serve_sounds(filename):
    return send_from_directory('data/sounds', filename)

@app.route('/data/images/<path:filename>')
def serve_images(filename):
    mimetypes = {
        '.mp4': 'video/mp4',
        '.png': 'image/png',
        '.ico': 'image/x-icon'
    }
    ext = os.path.splitext(filename)[1].lower()
    mime = mimetypes.get(ext, 'application/octet-stream')
    return send_from_directory(str(DIRS["images"]), filename, mimetype=mime)

def background_save():
    while True:
        time.sleep(60.0)
        try:
            with chat_rooms_lock:
                chat_rooms_snapshot = {room: list(messages) for room, messages in chat_rooms.items()}
            room_storage.save_global_chat_rooms(chat_rooms_snapshot)
            print("SAVED!")
        except Exception:
            pass

app.wsgi_app = ProxyFix(
    app.wsgi_app, 
    x_for=1, 
    x_proto=1, 
    x_host=1, 
    x_prefix=1
)

if __name__ == '__main__':
    for path in [DIRS["users"], DIRS["images"], DIRS["user_rooms"]]:
        path.mkdir(exist_ok=True)
    app.static_folder = str(DIRS["images"])
    app.static_url_path = '/data/images'
    ip = get_server_ip()
    print(f"Shadows: {ip}:5000")
    print("PER-USER ROOMS SYSTEM!")
    print(f"Global chats: {len(chat_rooms)} rooms")
    threading.Thread(target=background_save, daemon=True).start()
    print("Background saver started!")
    serve(app, host='0.0.0.0', port=5000, threads=16)