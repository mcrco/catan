from flask import Flask, json, jsonify, request, send_from_directory
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
import random
import string
import uuid
from game.game import Game, Player
from game.board import get_hexes_for_vertex

app = Flask(__name__, static_folder='../frontend/dist')
socketio = SocketIO(app, cors_allowed_origins="*")

games = {}

def generate_game_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

def check_game_player(game_code, player_id):
    if game_code not in games:
        return False
    game = games[game_code]
    turn = game.current_turn
    return player_id == game.players[turn % len(game.players)].id

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

    if len(game.players) >= 1:  # Require at least 2 players
        game.current_turn = 0
        for player in game.players:
            emit('game_update', game.to_dict(player.id), to=player.id)

@socketio.on('finish_turn')
def finish_turn(data):
    user_id = data['userId']
    game_code = data['gameCode']
    if not check_game_player(game_code, user_id):
        return
    
    game = games[game_code]
    game.current_turn += 1
    for player in game.players:
        emit('game_update', game.to_dict(player.id), to=player.id)

@socketio.on('roll_dice')
def roll_dice(data):
    user_id = data['userId']
    game_code = data['gameCode']
    if not check_game_player(game_code, user_id):
        return

    game = games.get(game_code, None)

    roll = game.roll_dice()
    game.distribute_resources(roll)
    
    for player in game.players:
        emit('game_update', game.to_dict(player.id), to=player.id)
        
@socketio.on('place_settlement')
def place_settlement(data):
    user_id = data['userId']
    game_code = data['gameCode']
    check_game_player(game_code, user_id)

    try:
        location = int(data['location'])
    except ValueError:
        return
    
    game = games[game_code]
    player = game.get_player(user_id)

    # check if player has resources for settlement
    if (player.resources["wood"] < 1 or player.resources["brick"] < 1 or
        player.resources["wheat"] < 1 or player.resources["sheep"] < 1):
        # check that it's not the second settlement
        if game.current_turn >= 2 * len(game.players) or len(player.settlements) > 1:
            return
        # check that it's not the first settlement
        if game.current_turn >= len(game.players) or len(player.settlements) > 0:
            return

    game.board.place_settlement(user_id, player.name, location)
    player.settlements.append(location)
    if len(player.settlements) == 2:
        for hex_index in get_hexes_for_vertex(location):
            hex = game.board.hexes[hex_index]
            player.collect_resources(hex.resource, 1)

    for player in game.players:
        emit('game_update', game.to_dict(player.id), to=player.id)

if __name__ == '__main__':
    socketio.run(app, debug=True)
