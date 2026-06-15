from backend.constants import BOARD_SIZE, PLAYER1, PLAYER2, PLAYER1_COLOR, PLAYER2_COLOR
from backend.helpers import (
    find_piece, is_out_of_bounds, is_new_position_valid,
    is_new_position_occupied, is_players_piece, find_possible_captures
)


class Piece:
    def __init__(self, x, y, player_number, is_crown=False):
        self.x = x
        self.y = y
        self.player_number = player_number
        self.is_crown = is_crown
        self.color = PLAYER1_COLOR if player_number == PLAYER1 else PLAYER2_COLOR
        self.visited_coordinates = []

    def move(self, x, y):
        self.x = x
        self.y = y
        if self.is_crown:
            self.visited_coordinates.append((x, y))

    def get_position(self):
        return (self.x, self.y)

    def is_previously_visited(self, x, y):
        return (x, y) in self.visited_coordinates


class Board:
    def __init__(self):
        self.player1_pieces = []
        self.player2_pieces = []
        self._initialise_pieces()

    def _initialise_pieces(self):
        for i in range(BOARD_SIZE):
            if i % 2 == 0:
                self.player1_pieces.append(Piece(i, 0, PLAYER1))
                self.player1_pieces.append(Piece(i, 2, PLAYER1))
                self.player2_pieces.append(Piece(i, BOARD_SIZE - 2, PLAYER2))
            else:
                self.player1_pieces.append(Piece(i, 1, PLAYER1))
                self.player2_pieces.append(Piece(i, BOARD_SIZE - 1, PLAYER2))
                self.player2_pieces.append(Piece(i, BOARD_SIZE - 3, PLAYER2))

    def assemble_board(self):
        pieces = self.player1_pieces + self.player2_pieces
        board = []
        for i in range(BOARD_SIZE):
            row = []
            for j in range(BOARD_SIZE):
                piece = find_piece(j, i, pieces)
                row.append(piece)
            board.append(row)
        return board

    def check_win(self):
        if len(self.player1_pieces) == 0:
            return PLAYER2
        if len(self.player2_pieces) == 0:
            return PLAYER1
        return 0

    def check_crown(self):
        for piece in self.player1_pieces:
            if piece.y == BOARD_SIZE - 1:
                piece.is_crown = True
        for piece in self.player2_pieces:
            if piece.y == 0:
                piece.is_crown = True

    def is_move_valid(self, current_x, current_y, new_x, new_y, player):
        """
        Returns:
            (0, None, None) - invalid move
            (1, None, None) - valid move
            (2, x, y)       - valid capture, (x, y) is the captured piece position
        """
        pieces = self.player1_pieces + self.player2_pieces

        if find_piece(current_x, current_y, pieces) is None:
            return 0, None, None
        if is_out_of_bounds(new_x, new_y):
            return 0, None, None
        if not is_new_position_valid(current_x, current_y, new_x, new_y, pieces, player):
            return 0, None, None
        if is_new_position_occupied(pieces, new_x, new_y):
            return 0, None, None
        if not is_players_piece(pieces, player, current_x, current_y):
            return 0, None, None

        piece = find_piece(current_x, current_y, pieces)
        possible_captures = find_possible_captures(player, piece, current_x, current_y)
        capturable_pieces = self.player2_pieces if player == PLAYER1 else self.player1_pieces
        opponent = PLAYER2 if player == PLAYER1 else PLAYER1

        for capture in possible_captures:
            for target in capturable_pieces:
                if ((new_x, new_y) == capture[0] and
                        target.get_position() == capture[1] and
                        target.player_number == opponent):
                    return 2, capture[1][0], capture[1][1]

        return 1, None, None

    def player_move(self, player, current_sq, new_sq):
        """
        Returns:
            0 - invalid move
            1 - move performed
            2 - capture performed
        """
        pieces = self.player1_pieces if player == PLAYER1 else self.player2_pieces
        current_x, current_y = current_sq
        new_x, new_y = new_sq

        move_valid = self.is_move_valid(current_x, current_y, new_x, new_y, player)

        if move_valid[0] == 0:
            return 0

        piece = find_piece(current_x, current_y, pieces)
        piece.move(new_x, new_y)

        if move_valid[0] == 2:
            _, cx, cy = move_valid
            target_list = self.player2_pieces if player == PLAYER1 else self.player1_pieces
            captured = find_piece(cx, cy, target_list)
            if captured:
                target_list.remove(captured)
            return 2

        return 1

    def find_possible_moves(self, player):
        pieces = self.player1_pieces if player == PLAYER1 else self.player2_pieces
        moves = []

        for piece in pieces:
            x, y = piece.get_position()

            if player == PLAYER1:
                candidates = [(x+1, y+1), (x-1, y+1), (x+2, y+2), (x-2, y+2)]
                if piece.is_crown:
                    candidates += [(x+1, y-1), (x-1, y-1), (x+2, y-2), (x-2, y-2)]
            else:
                candidates = [(x+1, y-1), (x-1, y-1), (x+2, y-2), (x-2, y-2)]
                if piece.is_crown:
                    candidates += [(x+1, y+1), (x-1, y+1), (x+2, y+2), (x-2, y+2)]

            for new_x, new_y in candidates:
                if self.is_move_valid(x, y, new_x, new_y, player)[0] != 0:
                    moves.append((x, y, new_x, new_y))

        return moves
