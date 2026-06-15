from backend.constants import BOARD_SIZE, PLAYER1, PLAYER2


def is_new_position_occupied(pieces, x, y):
    for piece in pieces:
        if piece.get_position() == (x, y):
            return True
    return False


def is_out_of_bounds(x, y):
    return x >= BOARD_SIZE or y >= BOARD_SIZE or x < 0 or y < 0


def is_players_piece(pieces, player, x, y):
    for piece in pieces:
        if piece.get_position() == (x, y) and piece.player_number == player:
            return True
    return False


def is_new_position_valid(x, y, new_x, new_y, pieces, player):
    moved_piece = find_piece(x, y, pieces)
    if moved_piece is None or moved_piece.player_number != player:
        return False

    if moved_piece.is_crown:
        possible_moves = [
            (x+1, y+1), (x-1, y+1), (x+2, y+2), (x-2, y+2),
            (x+1, y-1), (x-1, y-1), (x+2, y-2), (x-2, y-2)
        ]
    elif moved_piece.player_number == PLAYER1:
        possible_moves = [(x+1, y+1), (x-1, y+1), (x+2, y+2), (x-2, y+2)]
    else:
        possible_moves = [(x+1, y-1), (x-1, y-1), (x+2, y-2), (x-2, y-2)]

    return (new_x, new_y) in possible_moves


def find_piece(current_x, current_y, pieces):
    for piece in pieces:
        if piece.get_position() == (current_x, current_y):
            return piece
    return None


def find_possible_captures(player, piece, current_x, current_y):
    if piece.is_crown:
        return [
            [(current_x+2, current_y+2), (current_x+1, current_y+1)],
            [(current_x-2, current_y+2), (current_x-1, current_y+1)],
            [(current_x+2, current_y-2), (current_x+1, current_y-1)],
            [(current_x-2, current_y-2), (current_x-1, current_y-1)],
        ]

    if player == PLAYER1:
        return [
            [(current_x+2, current_y+2), (current_x+1, current_y+1)],
            [(current_x-2, current_y+2), (current_x-1, current_y+1)],
        ]
    else:
        return [
            [(current_x+2, current_y-2), (current_x+1, current_y-1)],
            [(current_x-2, current_y-2), (current_x-1, current_y-1)],
        ]
