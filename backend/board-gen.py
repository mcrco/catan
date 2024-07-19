import random
import matplotlib

# CONSTANTS
num_hexes = 19
positions = range(0, num_hexes)

probabilities = [2, 3, 3, 4, 4, 5, 5, 6, 6, 8, 8, 9, 9, 10, 10, 11, 11, 12]

resource_dist = {
    'brick': 3, 'wood': 4, 'sheep': 4, 'wheat': 4, 'ore': 3, 'desert': 1
}

resource_map = {
    'brick': 'B', 'wood': 'L', 'sheep': 'S', 'wheat': 'W', 'ore': 'O', 'desert': 'D'
}

adjacencies = {
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

def display(type, board):
    display_format = """
----X-X-X----
---X-X-X-X---
--X-X-X-X-X--
---X-X-X-X---
----X-X-X----
"""
    pos_index = 0
    print("Board " + type + " layout: ")
    for char in display_format:
        if (char == '-' or char == '\n'):
            print(char, end='')
        else:
            curr_token = board[pos_index][type]
            if(curr_token is None):
                curr_token = '∅'
            elif(type == 'value'):
                curr_token = hex(curr_token)[2:]
            elif(type == 'resource'):
                curr_token = resource_map[curr_token]
            print(curr_token, end = '')
            pos_index += 1
    print() 


def is_valid_board(board):
    """ Checks if a board is valid by checking
    if a 6 and 8 are adjacent to one another. """
    for pos, tile in board.items():
        if tile['value'] in [6, 8]:
            for neighbor in adjacencies[pos]:
                if board[neighbor]['value'] in [6, 8]:
                    return False
    return True


def generate_board():
    """ Generates a randomized Catan board, ensuring
    the desert has no number attached to it. """
    # full list of resources based on dist
    resources = []
    for resource, count in resource_dist.items():
        resources.extend([resource] * count)
    random.shuffle(resources)

    # shuffling probability list
    shuffled_probabilities = probabilities[:]
    random.shuffle(shuffled_probabilities)

    # rndom resource to number assignment
    board = {}
    prob_index = 0
    for position in positions:
        resource = resources.pop()
        val = None
        if resource != 'desert':
            val = shuffled_probabilities[prob_index]
            prob_index += 1
        board[position] = {'resource': resource, 'value': val}

    return board


board = generate_board()
while not is_valid_board(board):
    board = generate_board()

