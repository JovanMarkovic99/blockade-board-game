from itertools import chain
from copy import deepcopy


class Board:
    def __init__(self, rows, columns, player_1_pawns, player_2_pawns):
        self.rows = rows
        self.columns = columns
        self.player_1_pawns = deepcopy(player_1_pawns)
        self.player_2_pawns = deepcopy(player_2_pawns)

        self.board = [[BoardSquare() for _ in range(columns)] for _ in range(rows)]
        self.board[player_1_pawns[0][0]][player_1_pawns[0][1]].set_start('X')
        self.board[player_1_pawns[1][0]][player_1_pawns[1][1]].set_start('X')
        self.board[player_2_pawns[0][0]][player_2_pawns[0][1]].set_start('O')
        self.board[player_2_pawns[1][0]][player_2_pawns[1][1]].set_start('O')

    def print_board(self):
        for i in range(2 * self.rows + 3):
            # When i and j are divisible by 2 index_i and index_j are board coordinates
            index_i = i // 2 - 1

            for j in range(2 * self.columns + 3):
                index_j = j // 2 - 1

                # Top-bottom border
                if i == 0 or i == 2 * self.rows + 2:
                    if j == 0 or j == 2 * self.columns + 2 or j % 2 == 1:
                        print(" ", end="")
                    else:
                        print(self.matrix_index_to_board_index(index_j), end="")
                elif i == 1 or i == 2 * self.rows + 1:
                    if j == 0 or j == 2 * self.columns + 2 or j % 2 == 1:
                        print(" ", end="")
                    else:
                        print("=", end="")

                # Square rows
                elif i % 2 == 0:
                    # Left-right border
                    if j == 0 or j == 2 * self.columns + 2:
                        print(self.matrix_index_to_board_index(index_i), end="")
                    elif j == 1 or j == 2 * self.columns + 1:
                        print("‖", end="")

                    # Squares
                    elif j % 2 == 0:
                        print(self.board[index_i][index_j].center, end="")

                    # Left-right walls
                    else:
                        print("‖" if self.board[index_i][index_j].right else "|", end="")

                # Top-bottom wall rows

                # Top-bottom walls
                elif j != 0 and j != 2 * self.columns + 2 and j % 2 == 0:
                    print("=" if self.board[index_i][index_j].bottom else "—", end="")

                else:
                    print(" ", end="")
            print()

    def game_end(self):
        return any(map(lambda square: (square.starting == 'O' and square.center == 'X') or
                                      (square.starting == 'X' and square.center == 'O'),
                       chain(*iter(self.board))))

    def valid_pawn_move(self, player, pawn_index, row, column, print_failure=True):
        prev_pos = self.player_1_pawns[pawn_index] if player == 'X' else self.player_2_pawns[pawn_index]
        old_square = self.board[prev_pos[0]][prev_pos[1]]
        new_square = self.board[row][column]

        if abs(prev_pos[0] - row) + abs(prev_pos[1] - column) == 0 or \
                abs(prev_pos[0] - row) + abs(prev_pos[1] - column) > 2:
            self.conditional_print("You cannot stay in place or move more than two squares from you current position!",
                                   print_failure)
            return False

        if (new_square.center == 'X' or new_square.center == 'O') and \
                (new_square.starting is None or new_square.starting == player):
            self.conditional_print("You cannot jump to a square with a pawn!", print_failure)
            return False

        # Top
        if row < prev_pos[0]:
            # Top-Left
            if column < prev_pos[1]:
                if old_square.top_left() or new_square.bottom_right() or \
                        (old_square.left and new_square.right) or (old_square.top and new_square.bottom):
                    self.conditional_print("You cannot jump over a wall!", print_failure)
                    return False

            # Top-Right
            elif column > prev_pos[1]:
                if old_square.top_right() or new_square.bottom_left() or \
                        (old_square.right and new_square.left) or (old_square.top and new_square.bottom):
                    self.conditional_print("You cannot jump over a wall!", print_failure)
                    return False

            else:
                # Top-Middle
                if prev_pos[0] - row == 1:
                    if new_square.bottom:
                        self.conditional_print("You cannot jump over a wall!", print_failure)
                        return False
                    elif new_square.starting is not None:
                        pass
                    elif new_square.top:
                        self.conditional_print("You cannot jump just one space forward!", print_failure)
                        return False
                    elif row == 0 or (self.board[row - 1][column].center != 'X' and
                                      self.board[row - 1][column].center != 'O'):
                        self.conditional_print("You cannot jump just one space forward!", print_failure)
                        return False

                # Top-Middle-Long
                else:
                    if new_square.bottom or old_square.top:
                        self.conditional_print("You cannot jump over a wall!", print_failure)
                        return False

        # Bottom
        elif row > prev_pos[0]:
            # Bottom-Left
            if column < prev_pos[1]:
                if old_square.bottom_left() or new_square.top_right() or \
                        (old_square.bottom and new_square.top) or (old_square.left and new_square.right):
                    self.conditional_print("You cannot jump over a wall!", print_failure)
                    return False

            # Bottom-Right
            elif column > prev_pos[1]:
                if old_square.bottom_right() or new_square.top_left() or \
                        (old_square.bottom and new_square.top) or (old_square.right and new_square.left):
                    self.conditional_print("You cannot jump over a wall!", print_failure)
                    return False

            else:
                # Bottom-Middle
                if row - prev_pos[0] == 1:
                    if new_square.top:
                        self.conditional_print("You cannot jump over a wall!", print_failure)
                        return False
                    elif new_square.starting is not None:
                        pass
                    elif new_square.bottom:
                        self.conditional_print("You cannot jump just one space forward!", print_failure)
                        return False
                    elif row == self.rows - 1 or (self.board[row + 1][column].center != 'X' and
                                                  self.board[row + 1][column].center != 'O'):
                        self.conditional_print("You cannot jump just one space forward!", print_failure)
                        return False

                # Bottom-Middle-Long
                else:
                    if new_square.top or old_square.bottom:
                        self.conditional_print("You cannot jump over a wall!", print_failure)
                        return False

        elif column > prev_pos[1]:
            # Middle-Right
            if column - prev_pos[1] == 1:
                if new_square.left:
                    self.conditional_print("You cannot jump over a wall!", print_failure)
                    return False
                elif new_square.starting is not None:
                    pass
                elif new_square.right:
                    self.conditional_print("You cannot jump just one space forward!", print_failure)
                    return False
                elif column == self.columns - 1 or (self.board[row][column + 1].center != 'X' and
                                                    self.board[row][column + 1].center != 'O'):
                    self.conditional_print("You cannot jump just one space forward!", print_failure)
                    return False

            # Middle-Right-Long
            else:
                if new_square.left or old_square.right:
                    self.conditional_print("You cannot jump over a wall!", print_failure)
                    return False

        else:
            # Middle-Left
            if prev_pos[1] - column == 1:
                if new_square.right:
                    self.conditional_print("You cannot jump over a wall!", print_failure)
                    return False
                elif new_square.starting is not None:
                    pass
                elif new_square.left:
                    self.conditional_print("You cannot jump just one space forward!", print_failure)
                    return False
                elif column == 0 or (self.board[row][column - 1].center != 'X' and
                                     self.board[row][column - 1].center != 'O'):
                    self.conditional_print("You cannot jump just one space forward!", print_failure)
                    return False

            # Middle-Left-Long
            else:
                if new_square.right or old_square.left:
                    self.conditional_print("You cannot jump over a wall!", print_failure)
                    return False

        return True

    def valid_wall_placement(self, wall_type, row, column, print_failure=True):
        if (wall_type == 'Z' and (self.board[row][column].right or self.board[row + 1][column].right)) or \
                (wall_type == 'P' and (self.board[row][column].bottom or self.board[row][column + 1].bottom)):
            self.conditional_print("A wall already exists on those coordinates!", print_failure)
            return False

        return True

    @staticmethod
    def matrix_index_to_board_index(index):
        return chr(ord('0') + index + 1) if index < 9 else chr(ord('A') - 9 + index)

    @staticmethod
    def board_index_to_matrix_index(char):
        return ord(char) - ord('0') - 1 if ord('0') <= ord(char) <= ord('9') else ord(char) - ord('A') + 9

    # Helper method for printing a message if a condition is true
    @staticmethod
    def conditional_print(message, condition):
        if condition:
            print(message)


class BoardSquare:
    def __init__(self, center=" "):
        self.center = center
        self.top = False
        self.left = False
        self.right = False
        self.bottom = False
        # Variable for remembering the starting position of first or second player
        self.starting = None

    def set_start(self, player):
        self.center = player
        self.starting = player

    def top_left(self):
        return self.top and self.left

    def top_right(self):
        return self.top and self.right

    def bottom_left(self):
        return self.bottom and self.left

    def bottom_right(self):
        return self.bottom and self.right
