def evaluate_board(board):
    piece_values = {
        'P': 1, 'N': 3, 'B': 3.2, 'R': 5, 'Q': 9, 'K': 0,
        'p': -1, 'n': -3, 'b': -3.2, 'r': -5, 'q': -9, 'k': 0
    }
    score = 0
    for row in board.grid:
        for piece in row:
            if piece:
                score += piece_values.get(str(piece), 0)
    return score
