from typing import List, Tuple

class Piece:
    def __init__(self, color: str):
        self.color = color

    def get_valid_moves(self, pos: Tuple[int, int], board) -> List[Tuple[int, int]]:
        return []

    def __str__(self):
        return "?"

class Pawn(Piece):
    def __str__(self):
        return "P" if self.color == "white" else "p"

    def get_valid_moves(self, pos, board):
        direction = -1 if self.color == "white" else 1
        x, y = pos
        moves = []

        if board.is_empty((x + direction, y)):
            moves.append((x + direction, y))
            if (self.color == "white" and x == 6) or (self.color == "black" and x == 1):
                if board.is_empty((x + 2 * direction, y)):
                    moves.append((x + 2 * direction, y))

        for dy in [-1, 1]:
            nx, ny = x + direction, y + dy
            if board.in_bounds((nx, ny)) and board.has_enemy((nx, ny), self.color):
                moves.append((nx, ny))
        return moves

class Rook(Piece):
    def __str__(self):
        return "R" if self.color == "white" else "r"

    def get_valid_moves(self, pos, board):
        return board.straight_moves(pos, self.color)

class Bishop(Piece):
    def __str__(self):
        return "B" if self.color == "white" else "b"

    def get_valid_moves(self, pos, board):
        return board.diagonal_moves(pos, self.color)

class Queen(Piece):
    def __str__(self):
        return "Q" if self.color == "white" else "q"

    def get_valid_moves(self, pos, board):
        return board.straight_moves(pos, self.color) + board.diagonal_moves(pos, self.color)

class Knight(Piece):
    def __str__(self):
        return "N" if self.color == "white" else "n"

    def get_valid_moves(self, pos, board):
        x, y = pos
        candidates = [(x + dx, y + dy) for dx, dy in
                      [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1)]]
        return [p for p in candidates if board.in_bounds(p) and not board.has_friendly(p, self.color)]

class King(Piece):
    def __str__(self):
        return "K" if self.color == "white" else "k"

    def get_valid_moves(self, pos, board):
        x, y = pos
        candidates = [(x + dx, y + dy) for dx in [-1, 0, 1] for dy in [-1, 0, 1]
                      if dx != 0 or dy != 0]
        return [p for p in candidates if board.in_bounds(p) and not board.has_friendly(p, self.color)]
