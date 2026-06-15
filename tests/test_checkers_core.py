from backend.board import Board
from backend.constants import BOARD_SIZE, PLAYER1, PLAYER2


def test_board_initialisation():
    board = Board()

    expected_no_of_pieces = 3 * (BOARD_SIZE / 2)

    assert len(board.player1_pieces) == expected_no_of_pieces
    assert len(board.player2_pieces) == expected_no_of_pieces
    assert len(board.player1_pieces) + len(board.player2_pieces) == 2 * expected_no_of_pieces

def test_valid_first_move():
    board = Board()
    move = board.player_move(PLAYER1, (0, 2), (1, 3))

    assert move == 1

def test_invalid_first_move():
    board = Board()
    move = board.player_move(PLAYER1, (0, 2), (1, 1))

    assert move == 0

def test_player_two_moves_first():
    board = Board()
    move = board.player_move(PLAYER2, (1, 6), (0, 5))

    assert move == 0

def test_draw():
    board = Board()

    board.player1_pieces.clear()
    board.player2_pieces.clear()

    assert board.check_win() == -1

def test_win():
    board = Board()
    board.player1_pieces.clear()

    assert board.check_win() == PLAYER2

def test_find_possible_moves():
    board = Board()
    possible_moves = board.find_possible_moves(PLAYER1)

    assert len(possible_moves) == 7
