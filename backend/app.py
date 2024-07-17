from flask import Flask, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import random
import string

app = Flask(__name__, static_folder='../frontend/dist')
socketio = SocketIO(app, cors_allowed_origins="*")

games = {}

def generate_game_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/api/create_game', methods=['POST'])
def create_game():
    game_code = generate_game_code()
    games[game_code] = {'players': []}
    return jsonify({'game_code': game_code})

@app.route('/api/join_game', methods=['POST'])
def join_game():
    data = request.json
    game_code = data['game_code']
    if game_code in games:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Game not found'}), 404

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@socketio.on('join_game')
def handle_join_game(data):
    game_code = data['game_code']
    username = data['username']
    join_room(game_code)
    games[game_code]['players'].append(username)
    emit('player_joined', {'username': username, 'players': games[game_code]['players']}, room=game_code)

if __name__ == '__main__':
    socketio.run(app, debug=True)

