from flask import Flask, json, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import random
import string
import uuid
from board import generate_valid_board

app = Flask(__name__, static_folder='../frontend/dist')
socketio = SocketIO(app, cors_allowed_origins="*")

games = {}

def generate_game_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def id_to_username(user_id, game_code):
    for player in games[game_code]['players']:
        if player.user_id == user_id:
            return player.username
    return None

def dupe_game_no_id(game):
    ret = {key: game[key] for key in game if key != 'players' and key != 'host'}
    ret['players'] = [player.username for player in game.players]
    ret['host'] = game.host.username
    ret['scores'] = {id_to_username(player, game.code): ret['scores'][player] for player in game['scores']}
    return ret

@app.route('/api/create_game', methods=['POST'])
def create_game():
    game_code = generate_game_code()
    games[game_code] = {'players': [], 'code': game_code}
    return jsonify({'game_code': game_code})

@app.route('/api/join_game', methods=['POST'])
def join_game():
    data = request.json
    game_code = data['game_code']
    if game_code in games:
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Game not found'}), 404

@app.route('/api/player_ready', methods=['POST'])
def player_ready():
    data = request.json
    game_code = data['game_code']
    username = data['username']
    user_id = uuid.uuid4()

    player = {'username': username, 'user_id': str(user_id)}
    game = games[game_code]

    ret = {
        'user_id': user_id,
    }
    # set first person to join room as host
    if len(game['players']) == 0:
        game['host'] = player

    game['players'].append(player)
    return ret

@app.route('/api/start_game', methods=['POST'])
def handle_start_game():
    data = request.json
    game_code = data['game_code']
    user_id = data['user_id']
    game = games[game_code]
    if game['host']['user_id'] != user_id:
        return jsonify({'success': False})

    game['board'] = generate_valid_board()
    game['scores'] = {player['user_id']: 0 for player in game['players']}
    game['cards'] = {player['user_id']: [] for player in game['players']}
    socketio.emit('game_update', dupe_game_no_id(game), to=game_code)

    return jsonify({'success': True})

# Serve built Vite app
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

@socketio.on('player_ready')
def handle_join_game(data):
    game_code = data['game_code']
    game = games[game_code]
    join_room(game_code)
    user_id = data['user_id']
    if user_id in [player['user_id'] for player in game['players']]:
        emit('game_update', dupe_game_no_id(game), to=game_code)

if __name__ == '__main__':
    socketio.run(app, debug=True)

