import random

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
    def __init__(self, resource, number=None):
        self.resource = resource
        self.number = number


class Board:
    def __init__(self):
        self.hexes = self.setup_hexes()
        self.settlements = {}  # Maps locations to players
        self.roads = []  # List of roads

    def setup_hexes(self):
        # Randomize hex resources and numbers
        hexes = []
        random.shuffle(RESOURCES)
        number_iter = iter(NUMBERS)

        for resource in RESOURCES:
            if resource == "desert":
                hexes.append(Hex(resource, number=None))
            else:
                hexes.append(Hex(resource, number=next(number_iter)))
        return hexes

    def place_settlement(self, player, location):
        # Simplified: Assume valid location
        self.settlements[location] = player
        
    def to_dict(self):
        return {
            'hexes': [(hex.resource, hex.number) for hex in self.hexes],
            'settlements': self.settlements,
            'roads': self.roads
        }


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
        