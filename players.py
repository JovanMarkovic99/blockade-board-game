from re import fullmatch
from copy import deepcopy
from itertools import product
from random import choice


class Player:
    def __init__(self, player, walls):
        self.player = player
        self.vertical_walls = walls
        self.horizontal_walls = walls

    def print_player_info(self):
        print("Playing: " + self.__class__.__name__ + " '" + self.player + "'")
        print("Vertical walls: " + str(self.vertical_walls))
        print("Horizontal walls: " + str(self.horizontal_walls))

    def print_winner(self, moves):
        print('-' * 50)
        print(("WINNER IN " + str(moves) + " MOVES: " + self.__class__.__name__ + " '" + self.player + "'")
              .center(50, '-'))
        print('-' * 50)

    # Inputs the move from the user or gets the move from the computer and packs it into the following format:
    # ((player, player_pawn, new_row, new_col), optional(wall_type, row, col))
    def get_move(self, board):
        pass

    # Plays the move and updates the number of player walls if update_walls is True,
    # afterwards returns the new board state
    # move = ((player, player_pawn, new_row, new_col), optional(wall_type, row, col))
    def play_move(self, board, move, update_walls=True):
        new_board = deepcopy(board)

        # Update player pawn and board
        player = move[0][0]
        pawn_index = move[0][1]
        new_row, new_col = move[0][2], move[0][3]
        player_pawns = new_board.player_1_pawns if player == 'X' else new_board.player_2_pawns

        # Update board
        new_board.board[player_pawns[pawn_index][0]][player_pawns[pawn_index][1]].center = \
            ' ' if new_board.board[player_pawns[pawn_index][0]][player_pawns[pawn_index][1]].starting is None else '·'
        new_board.board[new_row][new_col].center = player

        # Update pawn position
        player_pawns[pawn_index][0], player_pawns[pawn_index][1] = new_row, new_col

        # Update player walls and board walls
        if len(move) == 2:
            wall_row, wall_column = move[1][1], move[1][2]

            # Vertical walls
            if move[1][0] == 'Z':
                new_board.board[wall_row][wall_column].right = True
                new_board.board[wall_row][wall_column + 1].left = True
                new_board.board[wall_row + 1][wall_column].right = True
                new_board.board[wall_row + 1][wall_column + 1].left = True

                if update_walls:
                    self.vertical_walls -= 1

            # Horizontal walls
            else:
                new_board.board[wall_row][wall_column].bottom = True
                new_board.board[wall_row][wall_column + 1].bottom = True
                new_board.board[wall_row + 1][wall_column].top = True
                new_board.board[wall_row + 1][wall_column + 1].top = True

                if update_walls:
                    self.horizontal_walls -= 1

        return new_board

    def valid_move(self, board, move):
        if move is None:
            return False

        # Check the format
        if not fullmatch("\[[XO] [12]] \[[1-9A-Z] [1-9A-Z]]?( \[[ZP] [1-9A-Z] [1-9A-Z]])", move):
            print("Invalid format! Input must be of [X/O 1/2] [new_row new_column] ([Z/P row column])")
            return False

        return \
            self.valid_pawn_move(board, move[1], int(move[3]) - 1, (board.board_index_to_matrix_index(move[7]),
                                                                    board.board_index_to_matrix_index(move[9]))) \
            and \
            (self.valid_wall_placement(board) if len(move) == 11 else self.valid_wall_placement(board, move[13],
                                                                                                (
                                                                        board.board_index_to_matrix_index(move[15]),
                                                                        board.board_index_to_matrix_index(move[17]))
                                                                                                )
             )

    def valid_pawn_move(self, board, player, pawn, new_pos, output=True):
        if player != self.player:
            self.conditional_print("You cannot move your opponents pawns!", output)
            return False

        if new_pos[0] >= board.rows or new_pos[1] >= board.columns:
            self.conditional_print("Pawn indices are out of bounds!", output)
            return False

        prev_pos = board.player_1_pawns[pawn] if player == 'X' else board.player_2_pawns[pawn]
        old_square = board.board[prev_pos[0]][prev_pos[1]]
        new_square = board.board[new_pos[0]][new_pos[1]]

        if abs(prev_pos[0] - new_pos[0]) + abs(prev_pos[1] - new_pos[1]) == 0 or \
                abs(prev_pos[0] - new_pos[0]) + abs(prev_pos[1] - new_pos[1]) > 2:
            self.conditional_print("You cannot stay in place or move more than two squares from you current position!",
                                   output)
            return False

        if (new_square.center == 'X' or new_square.center == 'O') and \
                (new_square.starting is None or new_square.starting == player):
            self.conditional_print("You cannot jump to a square with a pawn!", output)
            return False

        # Top
        if new_pos[0] < prev_pos[0]:
            # Top-Left
            if new_pos[1] < prev_pos[1]:
                if old_square.top_left() or new_square.bottom_right() or \
                        (old_square.left and new_square.right) or (old_square.top and new_square.bottom):
                    self.conditional_print("You cannot jump over a wall!", output)
                    return False

            # Top-Right
            elif new_pos[1] > prev_pos[1]:
                if old_square.top_right() or new_square.bottom_left() or \
                        (old_square.right and new_square.left) or (old_square.top and new_square.bottom):
                    self.conditional_print("You cannot jump over a wall!", output)
                    return False

            else:
                # Top-Middle
                if prev_pos[0] - new_pos[0] == 1:
                    if new_square.bottom:
                        self.conditional_print("You cannot jump over a wall!", output)
                        return False
                    elif new_square.starting is not None:
                        pass
                    elif new_square.top:
                        self.conditional_print("You cannot jump just one space forward!", output)
                        return False
                    elif new_pos[0] == 0 or (board.board[new_pos[0] - 1][new_pos[1]].center != 'X' and
                                             board.board[new_pos[0] - 1][new_pos[1]].center != 'O'):
                        self.conditional_print("You cannot jump just one space forward!", output)
                        return False

                # Top-Middle-Long
                else:
                    if new_square.bottom or old_square.top:
                        self.conditional_print("You cannot jump over a wall!", output)
                        return False

        # Bottom
        elif new_pos[0] > prev_pos[0]:
            # Bottom-Left
            if new_pos[1] < prev_pos[1]:
                if old_square.bottom_left() or new_square.top_right() or \
                        (old_square.bottom and new_square.top) or (old_square.left and new_square.right):
                    self.conditional_print("You cannot jump over a wall!", output)
                    return False

            # Bottom-Right
            elif new_pos[1] > prev_pos[1]:
                if old_square.bottom_right() or new_square.top_left() or \
                        (old_square.bottom and new_square.top) or (old_square.right and new_square.left):
                    self.conditional_print("You cannot jump over a wall!", output)
                    return False

            else:
                # Bottom-Middle
                if new_pos[0] - prev_pos[0] == 1:
                    if new_square.top:
                        self.conditional_print("You cannot jump over a wall!", output)
                        return False
                    elif new_square.starting is not None:
                        pass
                    elif new_square.bottom:
                        self.conditional_print("You cannot jump just one space forward!", output)
                        return False
                    elif new_pos[0] == board.rows - 1 or (board.board[new_pos[0] + 1][new_pos[1]].center != 'X' and
                                                          board.board[new_pos[0] + 1][new_pos[1]].center != 'O'):
                        self.conditional_print("You cannot jump just one space forward!", output)
                        return False

                # Bottom-Middle-Long
                else:
                    if new_square.top or old_square.bottom:
                        self.conditional_print("You cannot jump over a wall!", output)
                        return False

        elif new_pos[1] > prev_pos[1]:
            # Middle-Right
            if new_pos[1] - prev_pos[1] == 1:
                if new_square.left:
                    self.conditional_print("You cannot jump over a wall!", output)
                    return False
                elif new_square.starting is not None:
                    pass
                elif new_square.right:
                    self.conditional_print("You cannot jump just one space forward!", output)
                    return False
                elif new_pos[1] == board.columns - 1 or (board.board[new_pos[0]][new_pos[1] + 1].center != 'X' and
                                                         board.board[new_pos[0]][new_pos[1] + 1].center != 'O'):
                    self.conditional_print("You cannot jump just one space forward!", output)
                    return False

            # Middle-Right-Long
            else:
                if new_square.left or old_square.right:
                    self.conditional_print("You cannot jump over a wall!", output)
                    return False

        else:
            # Middle-Left
            if prev_pos[1] - new_pos[1] == 1:
                if new_square.right:
                    self.conditional_print("You cannot jump over a wall!", output)
                    return False
                elif new_square.starting is not None:
                    pass
                elif new_square.left:
                    self.conditional_print("You cannot jump just one space forward!", output)
                    return False
                elif new_pos[1] == 0 or (board.board[new_pos[0]][new_pos[1] - 1].center != 'X' and
                                         board.board[new_pos[0]][new_pos[1] - 1].center != 'O'):
                    self.conditional_print("You cannot jump just one space forward!", output)
                    return False

            # Middle-Left-Long
            else:
                if new_square.right or old_square.left:
                    self.conditional_print("You cannot jump over a wall!", output)
                    return False

        return True

    def valid_wall_placement(self, board, wall=None, pos=None, output=True):
        if wall is None:
            if self.vertical_walls > 0 or self.horizontal_walls > 0:
                self.conditional_print("You must place a wall!", output)
                return False
            else:
                return True

        if (wall == 'Z' and self.vertical_walls == 0) or (wall == 'P' and self.horizontal_walls == 0):
            self.conditional_print("There are no more walls of that type to place!", output)
            return False

        row, column = pos[0], pos[1]
        if row >= board.rows - 1 or column >= board.columns - 1:
            self.conditional_print("Wall indices out of bound!", output)
            return False

        if (wall == 'Z' and (board.board[row][column].right or board.board[row + 1][column].right)) or \
                (wall == 'P' and (board.board[row][column].bottom or board.board[row][column + 1].bottom)):
            self.conditional_print("A wall already exists on those coordinates!", output)
            return False

        # TODO: Add check for a path existing to the initial pawns

        return True

    # Helper method for printing a message if a condition is true
    @staticmethod
    def conditional_print(message, condition):
        if condition:
            print(message)


class Computer(Player):
    def __init__(self, player, walls):
        super().__init__(player, walls)

    def get_move(self, board):
        return choice(self.legal_board_moves(board))

    def next_legal_board_states(self, board):
        return map(lambda move: self.play_move(board, move, update_walls=False), self.legal_board_moves(board))

    def legal_board_moves(self, board):
        if self.vertical_walls > 0 or self.horizontal_walls > 0:
            return tuple(product(self.legal_pawn_moves(board), self.legal_wall_placements(board)))
        else:
            return tuple(self.legal_pawn_moves(board))

    def legal_pawn_moves(self, board):
        pawns = board.player_1_pawns if self.player == 'X' else board.player_2_pawns

        # All pawn offsets in every direction, calculated with the code below then manually added for efficiency
        # pawn_offset_permutations = tuple(filter(lambda offset: 0 <= abs(offset[0]) + abs(offset[1]) <= 2,
        #                                  product((-2, -1, 0, 1, 2), (-2, -1, 0, 1, 2))))
        pawn_offset_permutations = ((-2, 0), (-1, -1), (-1, 0), (-1, 1), (0, -2), (0, -1), (0, 0), (0, 1), (0, 2),
                                    (1, -1), (1, 0), (1, 1), (2, 0))

        # Check which permutations make legal moves
        legal_moves = []
        for pawn_index in range(2):
            for row_offset, column_offset in pawn_offset_permutations:
                new_row, new_col = pawns[pawn_index][0] + row_offset, pawns[pawn_index][1] + column_offset

                # Instead of recalling the function, if needed, this can be optimized by checking the squares around the
                # pawn and adding the appropriate moves, which would effectively be the same as calling this function
                # twice, once for both pawns, instead of recalling it for every potential legal move.
                if self.valid_pawn_move(board, self.player, pawn_index, (new_row, new_col), output=False):
                    legal_moves.append((self.player, pawn_index, new_row, new_col))

        return legal_moves

    def legal_wall_placements(self, board):
        legal_moves = []

        for row in range(board.rows - 1):
            for column in range(board.columns - 1):
                if self.vertical_walls > 0:
                    if self.valid_wall_placement(board, 'Z', (row, column), output=False):
                        legal_moves.append(('Z', row, column))

                if self.horizontal_walls > 0:
                    if self.valid_wall_placement(board, 'P', (row, column), output=False):
                        legal_moves.append(('P', row, column))

        return legal_moves


class Human(Player):
    def __init__(self, player, walls):
        super().__init__(player, walls)

    def get_move(self, board):
        # Ask for input until the move is valid
        move = None
        while not self.valid_move(board, move):
            move = input("Enter the move: ").strip()

        # Extract the move information from the string and send it
        return (
                    (
                        move[1],
                        int(move[3]) - 1,
                        (board.board_index_to_matrix_index(move[7]), board.board_index_to_matrix_index(move[9]))
                    )
                ) \
            if len(move) == 11 else \
            (
                (
                    move[1],
                    int(move[3]) - 1,
                    board.board_index_to_matrix_index(move[7]),
                    board.board_index_to_matrix_index(move[9])
                ),
                (
                    move[13],
                    board.board_index_to_matrix_index(move[15]),
                    board.board_index_to_matrix_index(move[17])
                )
             )
