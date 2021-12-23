from re import fullmatch
from copy import deepcopy
from itertools import product, chain
from random import choice

from board import Board


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
    def play_move(self, board, move, update_walls=True):
        new_board = deepcopy(board)

        new_board.move_pawn(move[0][0], move[0][1], move[0][2], move[0][3])

        if len(move) == 2:
            new_board.place_wall(move[1][0], move[1][1], move[1][2])

            # Update the number of walls
            if update_walls:
                if move[1][0] == 'Z':
                    self.vertical_walls -= 1
                else:
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
            pawn_moves = self.legal_pawn_moves(board)
            wall_moves = self.legal_wall_placements(board)
            legal_moves = list(product(pawn_moves, wall_moves))

            # TODO: Implement parts of Boykov-Kolmogorov maxflow algorithm and replace this very inefficient algorithm
            return tuple(filter(lambda move: board.check_paths_after_move(move, print_failure=False), legal_moves))
        else:
            return tuple(map(lambda move: (move,), self.legal_pawn_moves(board)))

    def legal_pawn_moves(self, board):
        pawns = board.player_1_pawns if self.player == 'X' else board.player_2_pawns

        return tuple(chain(
            map(lambda l: (self.player, 0, *l), board.legal_jumps(self.player, pawns[0][0], pawns[0][1])),
            map(lambda l: (self.player, 1, *l), board.legal_jumps(self.player, pawns[1][0], pawns[1][1]))
        ))

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

        player, pawn_index, pawn_row, pawn_column, wall_type, wall_row, wall_column = self.extract_move_info(move)

        return ((player, pawn_index, pawn_row, pawn_column), ) if wall_type is None else \
               (player, pawn_index, pawn_row, pawn_column), (wall_type, wall_row, wall_column)

    def valid_move(self, board, move):
        if move is None:
            return False

        # Check the format
        if not fullmatch("\[[XO] [12]] \[[1-9A-Z] [1-9A-Z]]?( \[[ZP] [1-9A-Z] [1-9A-Z]])", move):
            print("Invalid format! Input must be of [X/O 1/2] [new_row new_column] ([Z/P row column])")
            return False

        player, pawn_index, pawn_row, pawn_column, wall_type, wall_row, wall_column = self.extract_move_info(move)

        # Check the player
        if player != self.player:
            print("You cannot move your opponents pawns!")
            return False

        # Check pawn move
        if not board.valid_pawn_move(player, pawn_index, pawn_row, pawn_column):
            return False

        if wall_type is not None:
            # Check if the player has the wall type
            if (wall_type == 'Z' and self.vertical_walls == 0) or (wall_type == 'P' and self.horizontal_walls == 0):
                print("There are no more walls of that type to place!")
                return False

            # Check wall placement
            if not board.valid_wall_placement(wall_type, wall_row, wall_column):
                return False

            # Check if new position has no blocked paths
            if not board.check_paths_after_move(((player, pawn_index, pawn_row, pawn_column),
                                                 (wall_type, wall_row, wall_column))):
                return False

        # Check if wall can be placed
        elif self.vertical_walls > 0 or self.horizontal_walls > 0:
            print("You must place a wall!")
            return False

        return True

    # Move must be of "[X/O 1/2] [new_row new_column] ([Z/P row column]" format
    # Returns player, pawn_index, pawn_row, pawn_column, wall_type, wall_row, wall_column
    @staticmethod
    def extract_move_info(move):
        player = move[1]
        pawn_index = int(move[3]) - 1
        pawn_row, pawn_column = Board.board_index_to_matrix_index(move[7]), Board.board_index_to_matrix_index(move[9])
        wall_type = None
        wall_row, wall_column = None, None

        if len(move) != 11:
            wall_type = move[13]
            wall_row = Board.board_index_to_matrix_index(move[15])
            wall_column = Board.board_index_to_matrix_index(move[17])

        return player, pawn_index, pawn_row, pawn_column, wall_type, wall_row, wall_column
