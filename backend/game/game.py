import random
from game.board import generate_valid_board, display

# Define resource types
RESOURCES = ["wood", "brick", "sheep", "wheat", "ore", "desert"]

# Define the numbers associated with each hex (excluding desert)
NUMBERS = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]


class Player:
    def __init__(self, name, id):
        self.name = name
        self.id = id
        self.resources = {"wood": 0, "brick": 0, "sheep": 0, "wheat": 0, "ore": 0}
        self.points = 0
        self.settlements = []
        self.roads = []

    def build_settlement(self, location):
        # Simplified: Assume valid location
        self.settlements.append(location)

    def build_road(self, start, end):
        # Simplified: Assume valid road location
        self.roads.append((start, end))

    def collect_resources(self, resource_type, amount):
        if resource_type != "desert":
            self.resources[resource_type] += amount
    
    def to_dict(self, user_id):
        ret = {
            'name': self.name,
            'numResources': sum(self.resources.values()),
            'points': self.points
        }
        if self.id == user_id:
            ret['resources'] = self.resources

        return ret


class Hex:
    def __init__(self, resource, number):
        self.resource = resource
        self.number = number
        
    def to_dict(self):
        return {
            'resource': self.resource,
            'number': self.number
        }

class Settlement:
    def __init__(self, player_id, player_name):
        self.player_id = player_id
        self.player_name = player_name
        self.upgraded = False
    
    def upgrade(self):
        self.upgraded = True

    def to_dict(self):
        return {
            'playerName': self.player_name,
            'upgraded': self.upgraded
        }

class Board:
    def __init__(self):
        self.hexes = self.setup_hexes()
        self.settlements = {}  # Maps locations to players
        self.roads = []  # List of roads

    def setup_hexes(self):
        board_dict = generate_valid_board()
        hexes = []
        for position, hex_data in board_dict.items():
            hexes.append(Hex(hex_data['resource'], hex_data['value']))
        return hexes

    def place_settlement(self, player, location):
        # Simplified: Assume valid location
        self.settlements[location] = player
        
    def to_dict(self):
        settlements = []
        for position, settlement in self.settlements:
            settle_dict = settlement.to_dict()
            settle_dict['position'] = position
            settlements.append(settle_dict)
        return {
            'hexes': [hex.to_dict() for hex in self.hexes],
            'settlements': settlements,
            'roads': self.roads
        }

    def display(self):
        board_dict = {i: {'resource': hex.resource, 'value': hex.number} for i, hex in enumerate(self.hexes)}
        display('resource', board_dict)
        display('value', board_dict)


class Game:
    def __init__(self, players):
        self.players = [Player(name, user_id) for (name, user_id) in players]
        self.host = self.players[0] if self.players else None
        self.board = Board()
        self.roll = (1, 1)
        self.current_turn = -1
        
    def add_player(self, username, user_id):
        if self.current_turn != -1:
            return False

        new_player = Player(username, user_id)
        if not self.players:
            self.set_host(new_player)
        self.players.append(new_player)
        return True
    
    def set_host(self, player: Player):
        self.host = player
        
    def get_player(self, user_id):
        for player in self.players:
            if player.id == user_id:
                return player
        return None

    def roll_dice(self):
        self.roll = (random.randint(1, 6), random.randint(1, 6))
        return self.roll

    def distribute_resources(self, roll=None):
        if roll is None:
            roll = self.roll
        for hex in self.board.hexes:
            if hex.number == roll:
                for location, player in self.board.settlements.items():
                    if (
                        location in hex.resource
                    ):  # Simplified: check if settlement is on hex
                        player.collect_resources(hex.resource, 1)

    def take_turn(self):
        roll = self.roll_dice()
        print(f"Dice roll: {roll}")
        self.distribute_resources(roll)

        # Simplified: current player takes actions
        current_player = self.players[self.current_turn]
        print(f"{current_player.name}'s turn")
        # Actions like building roads, settlements, etc.

        self.current_turn = (self.current_turn + 1) % len(self.players)
        
    def to_dict(self, user_id):
        players = [player.to_dict(user_id) for player in self.players]
        host_name = self.host.name
        if self.current_turn == -1:
            return {
                'players': players,
                'host': host_name,
                'currentTurn': -1
            }

        player = self.get_player(user_id)
        if not player:
            return {}
        resources = player.resources
        board = self.board.to_dict()
        roll = list(self.roll)
        player_turn = self.players[self.current_turn].name
        return {
            'players': players,
            'host': host_name,
            'resources': resources,
            'board': board,
            'roll': roll,
            'playerTurn': player_turn,
            'currentTurn': self.current_turn
        }
        