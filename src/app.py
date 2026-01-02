from flask import Flask, render_template, request, jsonify, session, send_from_directory
import socket
import secrets
from datetime import datetime
import os
import json
from ip_config import get_server_ip
from config import DIRS, TEMPLATES_DIR
from services import AuthService, Crypto
from storage import RoomStorage

app = Flask(__name__, template_folder=str(TEMPLATES_DIR))
app.secret_key = secrets.token_hex(32)

auth_service = AuthService()
room_storage = RoomStorage()

DATA_DIR = DIRS["data"]
USER_ROOMS_DIR = DIRS["user_rooms"]

chat_rooms = room_storage.load_global_chat_rooms()
active_sessions = set()

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
        chat_rooms["general"].append({
            "user": "SYSTEM", "user_id": "SYSTEM",
            "message": "NYXX(MASTER) entered the Shadows!", "time": timestamp, "system": True
        })
        room_storage.save_global_chat_rooms(chat_rooms)
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
            active_sessions.add(user_data.user_id)
            timestamp = datetime.now().strftime("%H:%M:%S")
            chat_rooms["general"].append({
                "user": "SYSTEM", "user_id": "SYSTEM",
                "message": f"{user_data.username} entered the Shadows!", "time": timestamp, "system": True
            })
            room_storage.save_global_chat_rooms(chat_rooms)
            return jsonify({'output': f'Successfully authenticated! Opening chat...', 'redirect': '/chat'})
        else:
            return jsonify({'output': 'Invalid seed!'})
    
    if session.get('logged_in') and cmd == "exit":
        user_id = session.get('user_id')
        timestamp = datetime.now().strftime("%H:%M:%S")
        chat_rooms["general"].append({
            "user": "SYSTEM", "user_id": "SYSTEM",
            "message": f"{session.get('username')} left the Shadows", "time": timestamp, "system": True
        })
        room_storage.save_global_chat_rooms(chat_rooms)
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
    user_rooms = load_user_rooms(user_id)
    
    if room_name not in user_rooms:
        user_rooms.append(room_name)
        save_user_rooms(user_id, user_rooms)
    
        if room_name not in chat_rooms:
            chat_rooms[room_name] = []
            timestamp = datetime.now().strftime("%H:%M:%S")
            chat_rooms[room_name].append({
                "user": "SYSTEM", "user_id": "SYSTEM",
                "message": f"Room '{room_name}' created by {session['username']}", 
                "time": timestamp, "system": True
            })
            room_storage.save_global_chat_rooms(chat_rooms)
            return jsonify({
                'success': True, 
                'message': f'Room "{room_name}" created!',
                'rooms': user_rooms,
                'switch_to': room_name
            })
        else:
            timestamp = datetime.now().strftime("%H:%M:%S")
            chat_rooms[room_name].append({
                "user": "SYSTEM", "user_id": "SYSTEM",
                "message": f"{session['username']} joined room '{room_name}'", 
                "time": timestamp, "system": True
            })
            room_storage.save_global_chat_rooms(chat_rooms)
            return jsonify({
                'success': True, 
                'message': f'Joined existing room "{room_name}"!',
                'rooms': user_rooms,
                'switch_to': room_name
            })
    else:
        return jsonify({
            'success': True, 
            'message': f'Already in room "{room_name}"!',
            'rooms': user_rooms,
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
    user_rooms = load_user_rooms(user_id)
    
    if room_name in user_rooms:
        user_rooms.remove(room_name)
        save_user_rooms(user_id, user_rooms)
        return jsonify({
            'success': True, 
            'message': f'Room "{room_name}" removed!',
            'rooms': user_rooms
        })
    
    return jsonify({'success': False, 'message': 'Room not found'})

@app.route('/rooms')
def get_rooms():
    if not session.get('logged_in'):
        return jsonify({'rooms': []})
    
    user_id = session['user_id']
    user_rooms = load_user_rooms(user_id)
    return jsonify({'rooms': user_rooms})

@app.route('/chat_history')
def chat_history_route():
    room = request.args.get('room', 'general')
    history = chat_rooms.get(room, [])[-50:]
    return jsonify({'history': history})

@app.route('/chat_send', methods=['POST'])
def chat_send():
    if not session.get('logged_in'):
        return jsonify({'error': 'Login first!'})
    
    data = request.json
    message = data.get('message', '').strip()
    room = data.get('room', 'general').lower()
    
    if message and room in chat_rooms:
        timestamp = datetime.now().strftime("%H:%M:%S")
        chat_rooms[room].append({
            "user": session['username'],
            "user_id": session['user_id'],
            "message": message,
            "time": timestamp,
            "system": False
        })
        room_storage.save_global_chat_rooms(chat_rooms)
        return jsonify({'status': 'ok'})
    
    return jsonify({'error': 'Room not found'})

@app.route('/current_user')
def current_user():
    return jsonify({'username': session.get('username', 'Guest')})

@app.route('/status')
def status():
    return jsonify({
        'current_user': session.get('username', 'Guest'),
        'online_users': len(active_sessions),
        'total_messages': sum(len(messages) for messages in chat_rooms.values())
    })

@app.route('/console_status')
def console_status():
    from storage.user_storage import UserStorage
    storage = UserStorage()
    return jsonify({'total_users': storage.total_users()})

@app.route('/data/images/<path:filename>')
def serve_images(filename):
    return send_from_directory(str(DIRS["images"]), filename)

if __name__ == '__main__':
    for path in [DIRS["users"], DIRS["images"], DIRS["user_rooms"]]:
        path.mkdir(exist_ok=True)
    
    app.static_folder = str(DIRS["images"])
    app.static_url_path = '/data/images'
    
    ip = get_server_ip()
    print(f"Shadows: {ip}:5000")
    print("PER-USER ROOMS SYSTEM!")
    print(f"Global chats: {len(chat_rooms)} rooms")
    
    app.run(host=ip, port=5000, debug=True, threaded=True)