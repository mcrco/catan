import random

# CONSTANTS
NUM_HEXES = 19
NUM_VERTICES = 54
POSITIONS = range(0, NUM_HEXES)

PROBABILITIES = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

RESOURCE_DIST = {
    'brick': 3, 'wood': 4, 'sheep': 4, 'wheat': 4, 'ore': 3, 'desert': 1
}

HEX_ADJACENCIES = {
    0: [1, 3, 4],
    1: [0, 2, 4, 5],
    2: [1, 5, 6],
    3: [0, 4, 7, 8],
    4: [0, 1, 3, 5, 8, 9],
    5: [1, 2, 4, 6, 9, 10],
    6: [2, 5, 10, 11],
    7: [3, 8, 12],
    8: [3, 4, 7, 9, 12, 13],
    9: [4, 5, 8, 10, 13, 14],
    10: [5, 6, 9, 11, 14, 15],
    11: [6, 10, 15],
    12: [7, 8, 13, 16],
    13: [8, 9, 12, 14, 16, 17],
    14: [9, 10, 13, 15, 17, 18],
    15: [10, 11, 14, 18],
    16: [12, 13, 17],
    17: [13, 14, 16, 18],
    18: [14, 15, 17]
}

VERTEX_ADJACENCIES = {
    0: [0, 1, 2, 3, 4, 5],
    1: [6, 7, 0, 5, 8, 9],
    2: [10, 11, 6, 9, 12, 13],
  3: [14, 15, 16, 17, 2, 1],
  4: [18, 19, 14, 1, 0, 7],
  5: [20, 21, 18, 7, 6, 11],
  6: [22, 23, 20, 11, 10, 24],
  7: [25, 26, 27, 28, 16, 15],
  8: [29, 30, 25, 15, 14, 19],
  9: [31, 32, 29, 19, 18, 21],
  10: [33, 34, 31, 21, 20, 23],
  11: [35, 36, 33, 23, 22, 37],
  12: [38, 39, 40, 26, 25, 30],
  13: [41, 42, 38, 30, 29, 32],
  14: [43, 44, 41, 32, 31, 34],
  15: [45, 46, 43, 34, 33, 36],
  16: [47, 48, 49, 39, 38, 42],
  17: [50, 51, 47, 42, 41, 44],
  18: [52, 53, 50, 44, 43, 46]
}

HEXES_FOR_VERTEX = {}
for hex, vertices in VERTEX_ADJACENCIES.items():
    for v in vertices:
        if v not in HEXES_FOR_VERTEX:
            HEXES_FOR_VERTEX[v] = []
        HEXES_FOR_VERTEX[v].append(hex)

def get_hexes_for_vertex(location):
    return HEXES_FOR_VERTEX[location]

def is_valid_board(board):
    """ Checks if a board is valid by checking
    if a 6 and 8 are adjacent to one another. """
    for pos, tile in board.items():
        if tile['value'] in [6, 8]:
            for neighbor in HEX_ADJACENCIES[pos]:
                if board[neighbor]['value'] in [6, 8]:
                    return False
    return True


def generate_board():
    """ Generates a randomized Catan board, ensuring
    the desert has no number attached to it. """
    # full list of resources based on dist
    resources = []
    for resource, count in RESOURCE_DIST.items():
        resources.extend([resource] * count)
    random.shuffle(resources)

    # shuffling probability list
    shuffled_probabilities = PROBABILITIES[:]
    random.shuffle(shuffled_probabilities)

    # rndom resource to number assignment
    board = {}
    prob_index = 0
    for position in POSITIONS:
        resource = resources.pop()
        val = None
        if resource != 'desert':
            val = shuffled_probabilities[prob_index]
            prob_index += 1
        board[position] = {'resource': resource, 'value': val}

    return board

def generate_valid_board():
    board = generate_board()
    while not is_valid_board(board):
        board = generate_board()
    return board
