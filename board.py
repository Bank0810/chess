from pieces import Pawn, Rook, Knight, Bishop, Queen, King

class Board:
    def __init__(self):
        self.grid = [[None for _ in range(8)] for _ in range(8)]
        self.turn = "white"
        self.move_history = []
        self._setup()

    def _setup(self):
        for i in range(8):
            self.grid[1][i] = Pawn("black")
            self.grid[6][i] = Pawn("white")
        back_row = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for i, cls in enumerate(back_row):
            self.grid[0][i] = cls("black")
            self.grid[7][i] = cls("white")

    def move_piece(self, from_pos, to_pos):
        x1, y1 = from_pos
        x2, y2 = to_pos
        piece = self.grid[x1][y1]
        if not piece or piece.color != self.turn:
            return False
        valid_moves = piece.get_valid_moves((x1, y1), self)
        if (x2, y2) in valid_moves:
            captured = self.grid[x2][y2]
            self.move_history.append((from_pos, to_pos, piece, captured))
            self.grid[x2][y2] = piece
            self.grid[x1][y1] = None
            self.turn = "black" if self.turn == "white" else "white"
            return True
        return False

    def undo_last_move(self):
        if not self.move_history:
            return
        from_pos, to_pos, piece, captured = self.move_history.pop()
        self.grid[from_pos[0]][from_pos[1]] = piece
        self.grid[to_pos[0]][to_pos[1]] = captured
        self.turn = "black" if self.turn == "white" else "white"

    def in_bounds(self, pos):
        x, y = pos
        return 0 <= x < 8 and 0 <= y < 8

    def is_empty(self, pos):
        x, y = pos
        return self.in_bounds(pos) and self.grid[x][y] is None

    def has_friendly(self, pos, color):
        x, y = pos
        return self.in_bounds(pos) and self.grid[x][y] and self.grid[x][y].color == color

    def has_enemy(self, pos, color):
        x, y = pos
        return self.in_bounds(pos) and self.grid[x][y] and self.grid[x][y].color != color

    def straight_moves(self, pos, color):
        return self._line_moves(pos, color, [(1, 0), (-1, 0), (0, 1), (0, -1)])

    def diagonal_moves(self, pos, color):
        return self._line_moves(pos, color, [(1, 1), (-1, -1), (1, -1), (-1, 1)])

    def _line_moves(self, pos, color, directions):
        x, y = pos
        moves = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            while self.in_bounds((nx, ny)):
                if self.is_empty((nx, ny)):
                    moves.append((nx, ny))
                elif self.has_enemy((nx, ny), color):
                    moves.append((nx, ny))
                    break
                else:
                    break
                nx += dx
                ny += dy
        return moves
