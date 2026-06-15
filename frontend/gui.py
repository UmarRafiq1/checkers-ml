import tkinter as tk

from backend.constants import (BOARD_SIZE, SQUARE_SIZE, GRIDCOLOR1, GRIDCOLOR2,
                                PLAYER1, PLAYER2, MAX_MOVES_WITHOUT_CAPTURE)
from backend.board import Board
from backend.ai import minimax, find_possible_moves
from frontend.config import root


class CheckersGUI:
    def __init__(self):
        self.board = Board()
        self.current_player = PLAYER1
        self.selected_square = (-1, -1)
        self.is_ai_mode = False
        self.depth = 0

    # -------------------------
    # Board Rendering
    # -------------------------

    def render(self):
        assembled = self.board.assemble_board()

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                new_row = BOARD_SIZE - 1 - row
                piece = assembled[new_row][col]
                sq_color = GRIDCOLOR1 if (new_row + col) % 2 == 0 else GRIDCOLOR2

                cell = tk.Canvas(root, width=SQUARE_SIZE, height=SQUARE_SIZE, bg=sq_color)
                cell.grid(row=row, column=col)

                if piece is None:
                    if not self.is_ai_mode:
                        cell.bind("<Button-1>",
                                  lambda e, r=new_row, c=col: self.player_versus_player(c, r))
                    else:
                        cell.bind("<Button-1>",
                                  lambda e, r=new_row, c=col: self.player_versus_ai(c, r))
                else:
                    outline = 'gold' if piece.is_crown else 'black'
                    cell.create_oval(6, 6, SQUARE_SIZE - 6, SQUARE_SIZE - 6,
                                     fill=piece.color, outline=outline, width=6)
                    is_human_turn = not (self.is_ai_mode and self.current_player == PLAYER2)
                    if piece.player_number == self.current_player and is_human_turn:
                        cell.bind("<Button-1>",
                                  lambda e, r=new_row, c=col: self.select_piece(c, r))

        root.mainloop()

    def draw_board(self, delay):
        assembled = self.board.assemble_board()

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                new_row = BOARD_SIZE - 1 - row
                piece = assembled[new_row][col]
                sq_color = GRIDCOLOR1 if (new_row + col) % 2 == 0 else GRIDCOLOR2

                cell = tk.Canvas(root, width=SQUARE_SIZE, height=SQUARE_SIZE, bg=sq_color)
                cell.grid(row=row, column=col)

                if piece is not None:
                    outline = 'gold' if piece.is_crown else 'black'
                    cell.create_oval(6, 6, SQUARE_SIZE - 6, SQUARE_SIZE - 6,
                                     fill=piece.color, outline=outline, width=6)
                    cell.bind("<Button-1>", lambda e: None)

        root.after(delay, root.quit)
        root.mainloop()
        

    # -------------------------
    # Player Input
    # -------------------------

    def select_piece(self, x, y):
        self.selected_square = (x, y)

    def player_versus_player(self, x, y):
        root.title(f"Checkers | Player vs Player | Player {self.current_player}'s turn")

        did_move = self.board.player_move(self.current_player, self.selected_square, (x, y))
        self.board.check_crown()

        if did_move != 0:
            self.current_player = PLAYER2 if self.current_player == PLAYER1 else PLAYER1

        self.draw_board(delay=10)

        if self._is_game_end():
            return

        self.render()

    def player_versus_ai(self, x, y):
        root.title("Checkers | Player vs AI")

        did_move = self.board.player_move(self.current_player, self.selected_square, (x, y))
        self.board.check_crown()

        self.draw_board(delay=200)

        if self._is_game_end():
            return

        if did_move != 0 and self.current_player == PLAYER1:
            self.current_player = PLAYER2
            self._run_ai_move(maximising=False)
            self.board.check_crown()
            self.current_player = PLAYER1

        if self._is_game_end():
            return

        self.render()

    def _run_ai_move(self, maximising):
        move = minimax(self.board.player1_pieces, self.board.player2_pieces,
                       depth=self.depth, alpha=float('-inf'), beta=float('inf'),
                       maximising_player=maximising)[1]
        if move is None:
            return
        player = PLAYER1 if maximising else PLAYER2
        self.board.player_move(player, (move[0], move[1]), (move[2], move[3]))

    # -------------------------
    # AI vs AI
    # -------------------------

    def ai_vs_ai(self, p1_depth, p2_depth):
        self.board = Board()
        self._ai_moves = []
        self._ai_moves_without_capture = 0
        self._ai_current_move = 0
        self._paint_board()
        root.after(300, self._ai_step, p1_depth, p2_depth)

    def _paint_board(self):
        """Redraw the board in-place without entering a new mainloop."""
        assembled = self.board.assemble_board()
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                new_row = BOARD_SIZE - 1 - row
                piece = assembled[new_row][col]
                sq_color = GRIDCOLOR1 if (new_row + col) % 2 == 0 else GRIDCOLOR2

                cell = tk.Canvas(root, width=SQUARE_SIZE, height=SQUARE_SIZE, bg=sq_color)
                cell.grid(row=row, column=col)

                if piece is not None:
                    outline = 'gold' if piece.is_crown else 'black'
                    cell.create_oval(6, 6, SQUARE_SIZE - 6, SQUARE_SIZE - 6,
                                     fill=piece.color, outline=outline, width=6)
                    cell.bind("<Button-1>", lambda e: None)

    def _ai_step(self, p1_depth, p2_depth):
        """One full round (P1 move + P2 move), then schedule the next round."""
        # --- Player 1 ---
        self.current_player = PLAYER1
        if self._is_game_end():
            return

        move = minimax(self.board.player1_pieces, self.board.player2_pieces,
                       p1_depth, float('-inf'), float('inf'), True)[1]
        if move is None:
            return

        status = self.board.player_move(PLAYER1, (move[0], move[1]), (move[2], move[3]))
        self.board.check_crown()
        self._ai_moves.append(((move[0], move[1]), (move[2], move[3])))

        self._ai_moves_without_capture = 0 if status == 2 else self._ai_moves_without_capture + 1
        if self._ai_moves_without_capture >= MAX_MOVES_WITHOUT_CAPTURE:
            self._paint_board()
            self._game_end(winner=None, is_draw=True)
            return

        self._ai_current_move += 1

        # --- Player 2 ---
        self.current_player = PLAYER2
        if self._is_game_end():
            self._paint_board()
            return

        move = minimax(self.board.player1_pieces, self.board.player2_pieces,
                       p2_depth, float('-inf'), float('inf'), False)[1]
        if move is None:
            return

        status = self.board.player_move(PLAYER2, (move[0], move[1]), (move[2], move[3]))
        self.board.check_crown()
        self._ai_moves.append(((move[0], move[1]), (move[2], move[3])))

        self._ai_moves_without_capture = 0 if status == 2 else self._ai_moves_without_capture + 1
        if self._ai_moves_without_capture >= MAX_MOVES_WITHOUT_CAPTURE:
            self._paint_board()
            self._game_end(winner=None, is_draw=True)
            return

        self._ai_current_move += 1

        if self._ai_current_move > 8 and self._is_draw_via_repetitions(self._ai_moves):
            self._paint_board()
            self._game_end(winner=None, is_draw=True)
            return

        if self._is_game_end():
            self._paint_board()
            return

        # Redraw then schedule next round — 300 ms gives tkinter time to paint
        self._paint_board()
        root.after(300, self._ai_step, p1_depth, p2_depth)


    def _is_draw_via_repetitions(self, moves):
        if len(moves) < 8:
            return False
        p1_repeated = (moves[-8][0] == moves[-6][1] and
                       moves[-6][0] == moves[-4][1] and
                       moves[-4][0] == moves[-2][1])
        p2_repeated = (moves[-7][0] == moves[-5][1] and
                       moves[-5][0] == moves[-3][1] and
                       moves[-3][0] == moves[-1][1])
        return p1_repeated and p2_repeated

    # -------------------------
    # Game State
    # -------------------------

    def _is_game_end(self):
        possible_moves = find_possible_moves(
            self.board.player1_pieces, self.board.player2_pieces, self.current_player)

        if not possible_moves:
            p1 = len(self.board.player1_pieces)
            p2 = len(self.board.player2_pieces)
            if p1 > p2:
                self._game_end(winner=PLAYER1, is_draw=False)
            elif p2 > p1:
                self._game_end(winner=PLAYER2, is_draw=False)
            else:
                self._game_end(winner=None, is_draw=True)
            return True

        winner = self.board.check_win()
        if winner != 0:
            self._game_end(winner=winner, is_draw=False)
            return True

        return False

    def _game_end(self, winner, is_draw):
        popup = tk.Toplevel(root)
        popup.title("Game Over")

        text = "Draw!" if is_draw else f"Winner: Player {winner}"
        tk.Label(popup, text=text, font=("Arial", 16)).pack(pady=20)

        def return_home():
            popup.destroy()
            for widget in root.winfo_children():
                widget.destroy()
            from frontend.start_screen import start
            start()

        tk.Button(popup, text="Return To Home", command=return_home).pack(pady=10)
        root.wait_window(popup)

    # -------------------------
    # Game Setup
    # -------------------------

    def start_game(self, is_ai_v_ai, is_player_v_ai):
        self.board = Board()
        self.current_player = PLAYER1
        self.selected_square = (-1, -1)

        for widget in root.winfo_children():
            widget.destroy()

        if is_ai_v_ai:
            p1_depth, p2_depth = self._depth_selector(is_player_v_ai=False)
            self.ai_vs_ai(p1_depth, p2_depth)
        elif is_player_v_ai:
            self.depth = self._depth_selector(is_player_v_ai=True)
            self.is_ai_mode = True
            self.render()
        else:
            self.is_ai_mode = False
            self.render()

    def _depth_selector(self, is_player_v_ai):
        popup = tk.Toplevel(root)
        popup.title("Depth Selector")
        tk.Label(popup, text="Choose AI Depth (1 = easy, 4 = hard)").pack(pady=10)

        depth_p1 = tk.Entry(popup)
        depth_p1.pack(pady=5)

        depth = {"p1": None, "p2": None}

        if is_player_v_ai:
            def submit():
                try:
                    depth["p1"] = int(depth_p1.get())
                    popup.destroy()
                except ValueError:
                    pass

            tk.Button(popup, text="Start", command=submit).pack(pady=10)
            root.wait_window(popup)
            return depth["p1"]
        else:
            tk.Label(popup, text="Player 2 AI Depth").pack(pady=5)
            depth_p2 = tk.Entry(popup)
            depth_p2.pack(pady=5)

            def submit():
                try:
                    depth["p1"] = int(depth_p1.get())
                    depth["p2"] = int(depth_p2.get())
                    popup.destroy()
                except ValueError:
                    pass

            tk.Button(popup, text="Start", command=submit).pack(pady=10)
            root.wait_window(popup)
            return depth["p1"], depth["p2"]