import numpy as np
from tabulate import tabulate
from sklearn.linear_model import LinearRegression

from backend.constants import PLAYER1, PLAYER2, MAX_MOVES_WITHOUT_CAPTURE
from backend.board import Board
from backend.ai import minimax, set_weights, find_possible_moves


class Simulator:
    def __init__(self):
        self.board = Board()

    def reset(self):
        self.board = Board()

    # -------------------------
    # Feature Extraction
    # -------------------------

    def no_of_pieces(self, player):
        pieces = self.board.player1_pieces if player == PLAYER1 else self.board.player2_pieces
        return len(pieces)

    def no_of_crowns(self, player):
        pieces = self.board.player1_pieces if player == PLAYER1 else self.board.player2_pieces
        return sum(1 for p in pieces if p.is_crown)

    def sum_of_ranks(self):
        return sum(p.y + 1 for p in self.board.player1_pieces)

    def no_of_potential_captures(self):
        total = 0
        for piece in self.board.player1_pieces:
            x, y = piece.get_position()
            captures = [(x+2, y+2), (x-2, y+2)]
            if piece.is_crown:
                captures += [(x+2, y-2), (x-2, y-2)]
            for nx, ny in captures:
                if self.board.is_move_valid(x, y, nx, ny, PLAYER1)[0] == 2:
                    total += 1
        return total

    def extract_features(self, player):
        return [
            self.no_of_pieces(player),
            self.no_of_crowns(player),
            self.sum_of_ranks(),
            self.no_of_potential_captures(),
        ]

    # -------------------------
    # Game End Detection
    # -------------------------

    def _is_game_end(self, player):
        moves = find_possible_moves(self.board.player1_pieces,
                                    self.board.player2_pieces, player)
        if not moves:
            p1 = len(self.board.player1_pieces)
            p2 = len(self.board.player2_pieces)
            return PLAYER1 if p1 > p2 else PLAYER2 if p2 > p1 else 0

        winner = self.board.check_win()
        return winner if winner != 0 else -1

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
    # Simulation
    # -------------------------

    def simulate(self, p1_depth, p2_depth, is_new_weights=False,
                 default_weights=None, new_weights=None):
        self.reset()
        set_of_features = []
        moves_without_capture = 0
        current_move = 0
        moves = []

        while True:
            current_move += 1

            # Player 1's turn
            result = self._is_game_end(PLAYER1)
            if result != -1:
                return set_of_features, result

            if is_new_weights:
                set_weights(*new_weights)

            best_move = minimax(self.board.player1_pieces, self.board.player2_pieces,
                                p1_depth, float('-inf'), float('inf'), True)[1]
            if best_move is None:
                return set_of_features, 0

            move_status = self.board.player_move(
                PLAYER1, (best_move[0], best_move[1]), (best_move[2], best_move[3]))
            self.board.check_crown()

            moves_without_capture = 0 if move_status == 2 else moves_without_capture + 1
            if moves_without_capture >= MAX_MOVES_WITHOUT_CAPTURE:
                return set_of_features, 0

            moves.append(((best_move[0], best_move[1]), (best_move[2], best_move[3])))

            if current_move > 3:
                set_of_features.append(self.extract_features(PLAYER1))

            result = self._is_game_end(PLAYER1)
            if result != -1:
                return set_of_features, result

            # Player 2's turn
            result = self._is_game_end(PLAYER2)
            if result != -1:
                return set_of_features, result

            if is_new_weights:
                set_weights(*default_weights)

            best_move = minimax(self.board.player1_pieces, self.board.player2_pieces,
                                p2_depth, float('-inf'), float('inf'), False)[1]
            if best_move is None:
                return set_of_features, 0

            move_status = self.board.player_move(
                PLAYER2, (best_move[0], best_move[1]), (best_move[2], best_move[3]))
            self.board.check_crown()

            moves_without_capture = 0 if move_status == 2 else moves_without_capture + 1
            if moves_without_capture >= MAX_MOVES_WITHOUT_CAPTURE:
                return set_of_features, 0

            moves.append(((best_move[0], best_move[1]), (best_move[2], best_move[3])))

            result = self._is_game_end(PLAYER2)
            if result != -1:
                return set_of_features, result

            if current_move > 8 and self._is_draw_via_repetitions(moves):
                return set_of_features, 0

    # -------------------------
    # Weight Learning
    # -------------------------

    def improve_weights(self, iterations=20, depth=3):
        set_weights(1, 0, 0, 0)
        X, y = [], []

        for _ in range(iterations):
            for d1 in range(1, depth):
                for d2 in range(1, depth):
                    features, outcome = self.simulate(d1, d2)
                    result = 1 if outcome == PLAYER1 else -1 if outcome == PLAYER2 else 0
                    for f in features:
                        X.append(f)
                        y.append(result)


        model = LinearRegression()
        model.fit(np.array(X), np.array(y))
        set_weights(*model.coef_[:4])
        return tuple(model.coef_[:4])

    def compare_weights(self, default_weights, new_weights, depth=4):
        def tally(outcomes):
            wins = outcomes.count(1)
            losses = outcomes.count(-1)
            draws = outcomes.count(0)
            loss_pct = losses / len(outcomes) if outcomes else 0
            return wins, losses, draws, loss_pct

        set_weights(*default_weights)
        first = []
        for d1 in range(1, depth):
            for d2 in range(1, depth):
                _, outcome = self.simulate(d1, d2)
                first.append(1 if outcome == PLAYER1 else -1 if outcome == PLAYER2 else 0)

        second = []
        for d1 in range(1, depth):
            for d2 in range(1, depth):
                _, outcome = self.simulate(d1, d2, is_new_weights=True,
                                           default_weights=default_weights,
                                           new_weights=new_weights)
                second.append(1 if outcome == PLAYER1 else -1 if outcome == PLAYER2 else 0)

        dw, dl, dd, dp = tally(first)
        nw, nl, nd, np_ = tally(second)

        data = [
            ["Default vs Default", dw, dl, dd, f"{dp:.1%}"],
            ["New vs Default",     nw, nl, nd, f"{np_:.1%}"],
        ]
        print(tabulate(data, headers=["Game", "Wins", "Losses", "Draws", "Loss %"],
                       tablefmt="fancy_grid"))


if __name__ == "__main__":
    sim = Simulator()
    new_weights = sim.improve_weights()
    sim.compare_weights([1, 0, 0, 0], new_weights)
