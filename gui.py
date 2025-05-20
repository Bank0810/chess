import tkinter as tk
from board import Board
from evaluation import evaluate_board
from PIL import Image, ImageTk
import os

TILE_SIZE = 64
PIECE_IMAGES = {}

# ตัวช่วยโหลดภาพหมากจากโฟลเดอร์ assets/
def load_images():
    base_path = os.path.join(os.path.dirname(__file__), "assets2")
    mapping = {
        'P': 'w_pawn.png', 'R': 'w_r.png', 'N': 'w_h.png', 'B': 'w_b.png', 'Q': 'w_q.png', 'K': 'w_k.png',
        'p': 'b_pawn.png', 'r': 'b_t.png', 'n': 'b_h.png', 'b': 'b_b.png', 'q': 'b_q.png', 'k': 'b_k.png'
    }
    for key, filename in mapping.items():
        img_path = os.path.join(base_path, filename)
        if os.path.exists(img_path):
            img = Image.open(img_path).resize((TILE_SIZE, TILE_SIZE))
            PIECE_IMAGES[key] = ImageTk.PhotoImage(img)

class ChessGUI:
    def undo_move(self):
        if self.move_log:
            self.board.undo_last_move()
            self.move_log.pop()
            self.move_log_box.delete(tk.END)
            self.selected = None
            self.valid_moves = []
            self.last_move_from = None
            self.last_move_to = None
            self.game_over = False
            self.status_label.config(text="")
            self.draw_board()

    def reset_game(self):
        self.board = Board()
        self.move_log.clear()
        self.move_log_box.delete(0, tk.END)
        self.selected = None
        self.valid_moves = []
        self.last_move_from = None
        self.last_move_to = None
        self.game_over = False
        self.status_label.config(text="")
        self.draw_board()
    def __init__(self, root):
        self.move_log = []
        self.root = root
        self.board = Board()
        self.canvas = tk.Canvas(root, width=8 * TILE_SIZE, height=8 * TILE_SIZE)
        self.canvas.pack(side="left")

        self.info_frame = tk.Frame(root)
        self.info_frame.pack(side="right", padx=10)

        self.turn_label = tk.Label(self.info_frame, text="", font=("Arial", 14))
        self.turn_label.pack(pady=5)

        self.eval_label = tk.Label(self.info_frame, text="", font=("Arial", 14))
        self.eval_label.pack(pady=5)

        self.status_label = tk.Label(self.info_frame, text="", font=("Arial", 14), fg="red")
        self.status_label.pack(pady=5)

        self.move_log_label = tk.Label(self.info_frame, text="Move Log", font=("Arial", 12, "bold"))
        self.move_log_label.pack(pady=5)
        self.move_log_box = tk.Listbox(self.info_frame, height=20, width=30)
        self.move_log_box.pack(pady=5)

        self.reset_button = tk.Button(self.info_frame, text="Reset Game", command=self.reset_game)
        self.undo_button = tk.Button(self.info_frame, text="Undo Move", command=self.undo_move)
        self.reset_button.pack(pady=5)
        self.undo_button.pack(pady=5)

        self.selected = None
        self.valid_moves = []
        self.game_over = False
        self.last_move_from = None
        self.last_move_to = None

        self.draw_board()
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

    def set_last_move(self, from_pos, to_pos):
        self.last_move_from = from_pos
        self.last_move_to = to_pos

    def get_square(self, event):
        return event.y // TILE_SIZE, event.x // TILE_SIZE

    def on_drag(self, event):
        if self.selected:
            self.drag_pos = (event.x, event.y)
            self.draw_board()
            row, col = self.selected
            piece = self.board.grid[row][col]
            if piece:
                img_key = str(piece)
                if img_key in PIECE_IMAGES:
                    self.canvas.create_image(event.x - TILE_SIZE // 2, event.y - TILE_SIZE // 2,
                                             image=PIECE_IMAGES[img_key], anchor="nw")

    def on_drop(self, event):
        if self.game_over:
            return
        if self.selected:
            target = self.get_square(event)
            if target == self.selected:
                self.selected = None
                self.valid_moves = []
                self.draw_board()
                return

            piece = self.board.grid[self.selected[0]][self.selected[1]]
            all_moves = piece.get_valid_moves(self.selected, self.board)
            legal_moves = []
            for move in all_moves:
                original = self.board.grid[move[0]][move[1]]
                self.board.grid[move[0]][move[1]] = piece
                self.board.grid[self.selected[0]][self.selected[1]] = None
                in_check, _ = self.is_in_check(piece.color)
                if not in_check:
                    legal_moves.append(move)
                self.board.grid[self.selected[0]][self.selected[1]] = piece
                self.board.grid[move[0]][move[1]] = original

            if target in legal_moves:
                moved = self.board.move_piece(self.selected, target)
                if moved:
                    self.set_last_move(self.selected, target)
                    move_str = f"{self.board.turn.title()} → {chr(self.selected[1] + 97)}{8 - self.selected[0]} → {chr(target[1] + 97)}{8 - target[0]}"
                    self.move_log.append(move_str)
                    self.move_log_box.insert(tk.END, move_str)

            self.selected = None
            self.valid_moves = []
            self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        in_check, king_pos = self.is_in_check(self.board.turn)

        for i in range(8):
            for j in range(8):
                x1, y1 = j * TILE_SIZE, i * TILE_SIZE
                x2, y2 = x1 + TILE_SIZE, y1 + TILE_SIZE
                fill = "#EEE" if (i + j) % 2 == 0 else "#444"

                if self.last_move_from == (i, j):
                    fill = "#ff0"
                elif self.last_move_to == (i, j):
                    fill = "#9f9"
                elif self.selected and (i, j) in self.valid_moves:
                    fill = "#88f"
                elif in_check and (i, j) == king_pos:
                    fill = "#f66"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill)
                piece = self.board.grid[i][j]
                if piece:
                    img_key = str(piece)
                    if img_key in PIECE_IMAGES:
                        self.canvas.create_image(x1, y1, image=PIECE_IMAGES[img_key], anchor="nw")

        self.turn_label.config(text=f"Turn: {self.board.turn.title()}")
        eval_score = evaluate_board(self.board)
        self.eval_label.config(text=f"Evaluation: {eval_score:+.2f}")

        if self.game_over:
            return

        if not self.has_legal_moves(self.board.turn):
            if in_check:
                self.status_label.config(text=f"Checkmate! {self.board.turn.title()} loses")
            else:
                self.status_label.config(text="Stalemate! Draw")
            self.game_over = True
        else:
            self.status_label.config(text="Check!" if in_check else "")

    def is_in_check(self, color):
        king_pos = None
        for i in range(8):
            for j in range(8):
                piece = self.board.grid[i][j]
                if piece and str(piece).lower() == 'k' and piece.color == color:
                    king_pos = (i, j)
        for i in range(8):
            for j in range(8):
                piece = self.board.grid[i][j]
                if piece and piece.color != color:
                    if king_pos in piece.get_valid_moves((i, j), self.board):
                        return True, king_pos
        return False, king_pos

    def has_legal_moves(self, color):
        for i in range(8):
            for j in range(8):
                piece = self.board.grid[i][j]
                if piece and piece.color == color:
                    from_pos = (i, j)
                    for move in piece.get_valid_moves(from_pos, self.board):
                        captured = self.board.grid[move[0]][move[1]]
                        self.board.grid[move[0]][move[1]] = piece
                        self.board.grid[i][j] = None
                        in_check, _ = self.is_in_check(color)
                        self.board.grid[i][j] = piece
                        self.board.grid[move[0]][move[1]] = captured
                        if not in_check:
                            return True
        return False

    def on_click(self, event):
        if self.game_over:
            return

        row = event.y // TILE_SIZE
        col = event.x // TILE_SIZE
        pos = (row, col)

        if self.selected:
            piece = self.board.grid[row][col]
            if piece and piece.color == self.board.turn:
                self.selected = pos
                all_moves = piece.get_valid_moves(pos, self.board)
                self.valid_moves = []
                for move in all_moves:
                    original = self.board.grid[move[0]][move[1]]
                    self.board.grid[move[0]][move[1]] = piece
                    self.board.grid[pos[0]][pos[1]] = None
                    in_check, _ = self.is_in_check(piece.color)
                    if not in_check:
                        self.valid_moves.append(move)
                    self.board.grid[pos[0]][pos[1]] = piece
                    self.board.grid[move[0]][move[1]] = original
                self.draw_board()
                return

        piece = self.board.grid[row][col]
        if piece and piece.color == self.board.turn:
            self.selected = pos
            all_moves = piece.get_valid_moves(pos, self.board)
            self.valid_moves = []
            for move in all_moves:
                original = self.board.grid[move[0]][move[1]]
                self.board.grid[move[0]][move[1]] = piece
                self.board.grid[pos[0]][pos[1]] = None
                in_check, _ = self.is_in_check(piece.color)
                if not in_check:
                    self.valid_moves.append(move)
                self.board.grid[pos[0]][pos[1]] = piece
                self.board.grid[move[0]][move[1]] = original

        elif self.selected and pos in self.valid_moves:
            moved = self.board.move_piece(self.selected, pos)
            if moved:
                self.set_last_move(self.selected, pos)
                move_str = f"{self.board.turn.title()} → {chr(self.selected[1] + 97)}{8 - self.selected[0]} → {chr(pos[1] + 97)}{8 - pos[0]}"
                self.move_log.append(move_str)
                self.move_log_box.insert(tk.END, move_str)
            self.selected = None
            self.valid_moves = []

        self.draw_board()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess Game GUI")
    load_images()
    gui = ChessGUI(root)
    root.mainloop()
