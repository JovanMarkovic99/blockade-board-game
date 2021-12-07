class Board:
    def __init__(self, columns, rows, player_1_pawns, player_2_pawns):
        self.columns = columns
        self.rows = rows
        self.board = [[BoardSquare()] * columns] * rows
        self.board[player_1_pawns[0][1]][player_1_pawns[0][0]].set_start('X')
        self.board[player_1_pawns[1][1]][player_1_pawns[1][0]].set_start('X')
        self.board[player_2_pawns[0][1]][player_2_pawns[0][0]].set_start('O')
        self.board[player_2_pawns[1][1]][player_2_pawns[1][0]].set_start('O')

    def print_board(self):
        pass


class BoardSquare:
    def __init__(self, center=None):
        self.center = center
        self.top = None
        self.left = None
        self.right = None
        self.bottom = None
        # Variable for remembering the starting position of first or second player
        self.starting = None

    def set_start(self, player):
        self.starting = player
        self.center = player
