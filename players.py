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


class Computer(Player):
    def __init__(self, player, walls):
        super().__init__(player, walls)

    def get_move(self, board):
        return choice(self.legal_board_moves(board))

    def next_legal_board_states(self, board):
        return map(lambda move: self.play_move(board, move, update_walls=False), self.legal_board_moves(board))

    def legal_board_moves(self, board):
        if self.vertical_walls > 0 or self.horizontal_walls > 0:
            # TODO: Add path check
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
                if board.valid_pawn_move(self.player, pawn_index, new_row, new_col, print_failure=False):
                    legal_moves.append((self.player, pawn_index, new_row, new_col))

        return legal_moves

    def legal_wall_placements(self, board):
        legal_moves = []

        for row in range(board.rows - 1):
            for column in range(board.columns - 1):
                if self.vertical_walls > 0:
                    if board.valid_wall_placement('Z', row, column, print_failure=False):
                        legal_moves.append(('Z', row, column))

                if self.horizontal_walls > 0:
                    if board.valid_wall_placement('P', row, column, print_failure=False):
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
        player = move[1]
        player_index = int(move[3]) - 1
        pawn_row, pawn_column = board.board_index_to_matrix_index(move[7]), board.board_index_to_matrix_index(move[9])

        if len(move) == 1:
            return player, player_index, (pawn_row, pawn_column)
        else:
            wall_type = move[13]
            wall_row = board.board_index_to_matrix_index(move[15])
            wall_column = board.board_index_to_matrix_index(move[17])

            return (player, player_index, pawn_row, pawn_column), (wall_type, wall_row, wall_column)

    def valid_move(self, board, move):
        if move is None:
            return False

        # Check the format
        if not fullmatch("\[[XO] [12]] \[[1-9A-Z] [1-9A-Z]]?( \[[ZP] [1-9A-Z] [1-9A-Z]])", move):
            print("Invalid format! Input must be of [X/O 1/2] [new_row new_column] ([Z/P row column])")
            return False

        player = move[1]
        pawn_index = int(move[3]) - 1
        pawn_row, pawn_column = board.board_index_to_matrix_index(move[7]), board.board_index_to_matrix_index(move[9])

        # Check the player
        if move[1] != self.player:
            print("You cannot move your opponents pawns!")
            return False

        # Check if pawn indices are in range
        if pawn_row >= board.rows or pawn_column >= board.columns:
            print("Pawn indices are out of bounds!")
            return False

        # Check pawn move
        if not board.valid_pawn_move(player, pawn_index, pawn_row, pawn_column):
            return False

        if len(move) != 11:
            wall_type = move[13]
            wall_row = board.board_index_to_matrix_index(move[15])
            wall_column = board.board_index_to_matrix_index(move[17])

            # Check if the player has the wall type
            if (wall_type == 'Z' and self.vertical_walls == 0) or (wall_type == 'P' and self.horizontal_walls == 0):
                print("There are no more walls of that type to place!")
                return False

            # Check if wall indices are in range
            if wall_row >= board.rows - 1 or wall_column >= board.columns - 1:
                print("Wall indices out of bound!")
                return False

            # Check wall placement
            if not board.valid_wall_placement(wall_type, wall_row, wall_column):
                return False

            # TODO: Add path check

        # Check if wall can be placed
        elif self.vertical_walls > 0 or self.horizontal_walls > 0:
            print("You must place a wall!")
            return False

        return True
