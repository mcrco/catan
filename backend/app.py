from flask import Flask, json, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import random
import string
import sys
import uuid
from game.game import Game, Player

app = Flask(__name__, static_folder='../frontend/dist')
socketio = SocketIO(app, cors_allowed_origins="*")

games = {}

def generate_game_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

@app.route('/api/create_game', methods=['POST'])
def create_game():
    game_code = generate_game_code()
    games[game_code] = Game([])
    return jsonify({'game_code': game_code})

@app.route('/api/join_game', methods=['POST'])
def join_game():
    data = request.json
    game_code = data['gameCode']
    username = data['username']

    if game_code not in games:
        return jsonify({'success': False, 'message': 'Game not found'}), 404

    game = games[game_code]
    
    # Add player to the game
    user_id = str(uuid.uuid4())
    game.add_player(username, user_id)
    
    return jsonify({'success': True, 'userId': user_id})

@app.route('/api/player_ready', methods=['POST'])
def player_ready():
    data = request.json
    game_code = data['gameCode']
    user_id = data['user_id']

    # No need to update the game state here
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
def handle_player_ready(data):
    game_code = data['gameCode']
    game = games[game_code]
    join_room(game_code)

    user_id = data['userId']
    join_room(user_id)
    
    for player in game.players:
        emit('game_update', game.to_dict(player.id), to=player.id)

@socketio.on('start_game')
def handle_start_game(data):
    game_code = data['gameCode']
    if game_code not in games:
        return

    game = games[game_code]
    user_id = data['userId']
    if user_id != game.host.id:
        return

    if len(game.players) >= 2:  # Require at least 2 players
        game.current_turn = 0
        for player in game.players:
            emit('game_update', game.to_dict(player.id), to=player.id)

@socketio.on('roll_dice')
def roll_dice(data):
    user_id = data['userId']
    game_code = data['gameCode']
    game = games.get(game_code, None)
    if not game or user_id != game.host.id:
        return

    roll = game.roll_dice()
    game.distribute_resources(roll)
    
    for player in game.players:
        emit('game_update', game.to_dict(player.id), to=player.id)

if __name__ == '__main__':
    socketio.run(app, debug=True)
