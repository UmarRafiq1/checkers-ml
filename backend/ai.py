import copy
from backend.constants import BOARD_SIZE, PLAYER1, PLAYER2
from backend.board import Board

# -------------------------
# Default Heuristic Weights
# -------------------------

VAL_OF_PIECE = 1
VAL_OF_CROWN = 0
VAL_OF_RANK = 0
VAL_OF_POTENTIAL_CAPTURE = 0
VAL_OF_REVISITING = -2


def set_weights(val_of_piece, val_of_crown, val_of_rank, val_of_potential_capture):
    global VAL_OF_PIECE, VAL_OF_CROWN, VAL_OF_RANK, VAL_OF_POTENTIAL_CAPTURE
    VAL_OF_PIECE = val_of_piece
    VAL_OF_CROWN = val_of_crown
    VAL_OF_RANK = val_of_rank
    VAL_OF_POTENTIAL_CAPTURE = val_of_potential_capture


# -------------------------
# Position Analysis
# -------------------------

def analyse_position(board):
    p1_score = 0
    p2_score = 0

    for piece in board.player1_pieces:
        p1_score += VAL_OF_PIECE
        p1_score += (piece.y + 1) * VAL_OF_RANK
        if piece.is_crown:
            p1_score += VAL_OF_CROWN

        x, y = piece.get_position()
        captures = [(x+2, y+2), (x-2, y+2)]
        if piece.is_crown:
            captures += [(x+2, y-2), (x-2, y-2)]
        for nx, ny in captures:
            if board.is_move_valid(x, y, nx, ny, PLAYER1)[0] == 2:
                p1_score += VAL_OF_POTENTIAL_CAPTURE

    for piece in board.player2_pieces:
        p2_score += VAL_OF_PIECE
        p2_score += (BOARD_SIZE - piece.y) * VAL_OF_RANK
        if piece.is_crown:
            p2_score += VAL_OF_CROWN

        x, y = piece.get_position()
        captures = [(x+2, y-2), (x-2, y-2)]
        if piece.is_crown:
            captures += [(x+2, y+2), (x-2, y+2)]
        for nx, ny in captures:
            if board.is_move_valid(x, y, nx, ny, PLAYER2)[0] == 2:
                p2_score += VAL_OF_POTENTIAL_CAPTURE

    return p1_score - p2_score


# -------------------------
# Move Generation
# -------------------------

def find_possible_moves(p1_pieces, p2_pieces, player):
    temp = Board.__new__(Board)
    temp.player1_pieces = p1_pieces
    temp.player2_pieces = p2_pieces
    return temp.find_possible_moves(player)


# -------------------------
# Minimax
# -------------------------

def minimax(p1_pieces, p2_pieces, depth, alpha, beta, maximising_player):
    board = Board.__new__(Board)
    board.player1_pieces = copy.deepcopy(p1_pieces)
    board.player2_pieces = copy.deepcopy(p2_pieces)

    if depth == 0:
        return analyse_position(board), None

    player = PLAYER1 if maximising_player else PLAYER2
    moves = find_possible_moves(board.player1_pieces, board.player2_pieces, player)

    if not moves:
        return analyse_position(board), None

    best_score = float('-inf') if maximising_player else float('inf')
    best_move = None

    for move in moves:
        sim = Board.__new__(Board)
        sim.player1_pieces = copy.deepcopy(board.player1_pieces)
        sim.player2_pieces = copy.deepcopy(board.player2_pieces)

        current_sq = (move[0], move[1])
        new_sq = (move[2], move[3])

        src_list = sim.player1_pieces if maximising_player else sim.player2_pieces
        piece = next((p for p in src_list if p.get_position() == current_sq), None)
        adjust_eval = piece and piece.is_crown and piece.is_previously_visited(*new_sq)

        sim.player_move(player, current_sq, new_sq)
        sim.check_crown()

        evaluation = minimax(sim.player1_pieces, sim.player2_pieces,
                             depth - 1, alpha, beta, not maximising_player)[0]

        if adjust_eval:
            evaluation += VAL_OF_REVISITING if maximising_player else -VAL_OF_REVISITING

        if maximising_player:
            if evaluation > best_score:
                best_score = evaluation
                best_move = move
            alpha = max(alpha, evaluation)
        else:
            if evaluation < best_score:
                best_score = evaluation
                best_move = move
            beta = min(beta, evaluation)

        if beta <= alpha:
            break

    return best_score, best_move
