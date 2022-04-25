"""
Tic Tac Toe Player
"""
import copy
import math

X = "X"
O = "O"
EMPTY = None


class InvalidMoveError(Exception):
    pass


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    empty_count = 0
    for row in board:
        for col in row:
            if col == EMPTY:
                empty_count += 1
    if empty_count % 2 == 0:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    action_set = []
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == EMPTY:
                cur = board[i][j]
                action_set.append((i, j))
    return action_set


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    new_board = copy.deepcopy(board)
    if board[action[0]][action[1]] == EMPTY:
        new_board[action[0]][action[1]] = player(board)
        return new_board
    else:
        raise InvalidMoveError


def check_row(board):
    for row in board:
        symbol = row[0]
        for col in row:
            if col != symbol:
                break
        else:
            return symbol


def check_diag(board):
    diag_1 = [r[i] for i, r in enumerate(board)]
    diag_2 = [r[-i-1] for i, r in enumerate(board)]
    return check_row([diag_1, diag_2])


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    return check_row(board) or check_row(zip(*board)) or check_diag(board) or None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board):
        return True

    for row in board:
        for col in row:
            if col == EMPTY:
                return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    point = winner(board)
    if point == X:
        return 1
    elif point == O:
        return -1
    else:
        return 0


def get_max(board, cur_max):
    """
    Returns the max utility and action as a set for current board
    """
    score = -math.inf, ()
    for action in actions(board):
        new_board = result(board, action)
        if terminal(new_board):
            return utility(new_board), action
        else:
            cur = get_min(new_board, score)
            if cur > score:
                score = cur[0], action
            # AB-Pruning
            if cur[0] > cur_max[0]:
                return score
    return score


def get_min(board, cur_min):
    """
    Returns the min utility and action as a set for current board
    """
    score = math.inf, ()
    for action in actions(board):
        new_board = result(board, action)
        if terminal(new_board):
            return utility(new_board), action
        else:
            cur = get_max(new_board, score)
            if cur < score:
                score = cur[0], action
            # AB-Pruning
            if cur[0] < cur_min[0]:
                return score
    return score


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if player(board) == X:
        optimal_action = get_max(board, (math.inf, ()))
    else:
        optimal_action = get_min(board, (-math.inf, ()))
    return optimal_action[1]
