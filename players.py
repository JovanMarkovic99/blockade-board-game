from re import fullmatch
from copy import deepcopy
from itertools import product, chain
from random import choice
import heapq
from math import hypot

from board import Board


class Player:
    def __init__(self, player, walls, game):
        self.player = player
        self.vertical_walls = walls
        self.horizontal_walls = walls
        self.game = game

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

    def next_legal_board_states(self, board):
        return map(lambda move: self.play_move(board, move, update_walls=False), self.legal_board_moves(board))

    def legal_board_moves(self, board):
        if self.vertical_walls > 0 or self.horizontal_walls > 0:
            return self.legal_pawn_wall_move_combinations(board, self.legal_pawn_moves(board),
                                                          self.legal_wall_placements(board))
        else:
            return tuple(map(lambda move: (move,), self.legal_pawn_moves(board)))

    def legal_pawn_moves(self, board):
        pawns = board.player_1_pawns if self.player == 'X' else board.player_2_pawns

        return tuple(chain(
            map(lambda l: (self.player, 0, *l), self.legal_jumps(board, pawns[0][0], pawns[0][1])),
            map(lambda l: (self.player, 1, *l), self.legal_jumps(board, pawns[1][0], pawns[1][1]))
        ))

    # Returns all legal pawn jumps from the square with the row and column
    def legal_jumps(self, board, row, column):
        jumps = [(row - 2, column),  # Topmost
                 (row - 1, column),  # Top
                 (row - 1, column - 1),  # Top-left
                 (row - 1, column + 1),  # Top-right
                 (row, column - 2),  # Leftmost
                 (row, column - 1),  # Left
                 (row, column + 2),  # Rightmost
                 (row, column + 1),  # Right
                 (row + 2, column),  # Bottommost
                 (row + 1, column),  # Bottom,
                 (row + 1, column - 1),  # Bottom-left
                 (row + 1, column + 1),  # Bottom-right
                 ]
        source_square = board.board[row][column]

        if row == 0:
            # Top-side
            jumps[0] = jumps[1] = jumps[2] = jumps[3] = False
        else:
            # Top-left
            if column == 0 or (
                    (board.board[row - 1][column - 1].center == 'X' or board.board[row - 1][
                        column - 1].center == 'O') and
                    (board.board[row - 1][column - 1].starting is None or board.board[row - 1][
                        column - 1].starting == self.player)
            ) or (
                    source_square.top_left()
            ) or (
                    board.board[row - 1][column - 1].bottom_right()
            ) or (
                    source_square.top and board.board[row][column - 1].top
            ) or (
                    source_square.left and board.board[row - 1][column].left
            ):
                jumps[2] = False

            # Top-right
            if column == board.columns - 1 or (
                    (board.board[row - 1][column + 1].center == 'X' or board.board[row - 1][
                        column + 1].center == 'O') and
                    (board.board[row - 1][column + 1].starting is None or board.board[row - 1][
                        column + 1].starting == self.player)
            ) or (
                    source_square.top_right()
            ) or (
                    board.board[row - 1][column + 1].bottom_left()
            ) or (
                    source_square.top and board.board[row][column + 1].top
            ) or (
                    source_square.right and board.board[row - 1][column].right
            ):
                jumps[3] = False

            # Topmost and Top
            if source_square.top:
                jumps[0] = jumps[1] = False
            else:
                # Top
                if (board.board[row - 1][column].starting is None or board.board[row - 1][
                    column].starting == self.player) \
                        and (
                        board.board[row - 1][column].center == 'X' or board.board[row - 1][column].center == 'O' or
                        board.board[row - 1][column].top or
                        row == 1 or
                        (board.board[row - 2][column].center != 'X' and board.board[row - 2][column].center != 'O')
                ):
                    jumps[1] = False

                # Top-most
                if row == 1 or board.board[row - 1][column].top or \
                        (
                                (board.board[row - 2][column].starting is None or board.board[row - 2][
                                    column].starting == self.player)
                                and
                                (board.board[row - 2][column].center == 'X' or board.board[row - 2][
                                    column].center == 'O')
                        ):
                    jumps[0] = False

        if row == board.rows - 1:
            # Bottom-side
            jumps[8] = jumps[9] = jumps[10] = jumps[11] = False
        else:
            # Bottom-left
            if column == 0 or (
                    (board.board[row + 1][column - 1].center == 'X' or board.board[row + 1][
                        column - 1].center == 'O') and
                    (board.board[row + 1][column - 1].starting is None or board.board[row + 1][
                        column - 1].starting == self.player)
            ) or (
                    source_square.bottom_left()
            ) or (
                    board.board[row + 1][column - 1].top_right()
            ) or (
                    source_square.bottom and board.board[row][column - 1].bottom
            ) or (
                    source_square.left and board.board[row + 1][column].left
            ):
                jumps[10] = False

            # Bottom-right
            if column == board.columns - 1 or (
                    (board.board[row + 1][column + 1].center == 'X' or board.board[row + 1][
                        column + 1].center == 'O') and
                    (board.board[row + 1][column + 1].starting is None or board.board[row + 1][
                        column + 1].starting == self.player)
            ) or (
                    source_square.bottom_right()
            ) or (
                    board.board[row + 1][column + 1].top_left()
            ) or (
                    source_square.bottom and board.board[row][column + 1].bottom
            ) or (
                    source_square.right and board.board[row + 1][column].right
            ):
                jumps[11] = False

            # Bottommost and Bottom
            if source_square.bottom:
                jumps[8] = jumps[9] = False
            else:
                # Bottom
                if (board.board[row + 1][column].starting is None or board.board[row + 1][
                    column].starting == self.player) \
                        and (
                        board.board[row + 1][column].center == 'X' or board.board[row + 1][column].center == 'O' or
                        board.board[row + 1][column].bottom or
                        row == board.rows - 2 or
                        (board.board[row + 2][column].center != 'X' and board.board[row + 2][column].center != 'O')
                ):
                    jumps[9] = False

                # Bottom-most
                if row == board.rows - 2 or board.board[row + 1][column].bottom or \
                        (
                                (board.board[row + 2][column].starting is None or board.board[row + 2][
                                    column].starting == self.player)
                                and
                                (board.board[row + 2][column].center == 'X' or board.board[row + 2][
                                    column].center == 'O')
                        ):
                    jumps[8] = False

        # Left-most and Left
        if column == 0 or source_square.left:
            jumps[4] = jumps[5] = False
        else:
            # Left
            if (board.board[row][column - 1].starting is None or board.board[row][column - 1].starting == self.player) \
                    and (
                    board.board[row][column - 1].center == 'X' or board.board[row][column - 1].center == 'O' or
                    board.board[row][column - 1].left or
                    column == 1 or
                    (board.board[row][column - 2].center != 'X' and board.board[row][column - 2].center != 'O')
            ):
                jumps[5] = False

            # Left-most
            if column == 1 or board.board[row][column - 1].left or \
                    (
                            (board.board[row][column - 2].starting is None or board.board[row][
                                column - 2].starting == self.player)
                            and
                            (board.board[row][column - 2].center == 'X' or board.board[row][column - 2].center == 'O')
                    ):
                jumps[4] = False

        # Right-most and Right
        if column == board.columns - 1 or source_square.right:
            jumps[6] = jumps[7] = False
        else:
            # Right
            if (board.board[row][column + 1].starting is None or board.board[row][column + 1].starting == self.player) \
                    and (
                    board.board[row][column + 1].center == 'X' or board.board[row][column + 1].center == 'O' or
                    board.board[row][column + 1].right or
                    column == board.columns - 2 or
                    (board.board[row][column + 2].center != 'X' and board.board[row][column + 2].center != 'O')
            ):
                jumps[7] = False

            # Right-most
            if column == board.columns - 2 or board.board[row][column + 1].right or \
                    (
                            (board.board[row][column + 2].starting is None or board.board[row][
                                column + 2].starting == self.player)
                            and
                            (board.board[row][column + 2].center == 'X' or board.board[row][column + 2].center == 'O')
                    ):
                jumps[6] = False

        return tuple(filter(lambda jump: jump, jumps))

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

    # Find all move combinations that don't block any one of the pawns' path to the goal
    @staticmethod
    def legal_pawn_wall_move_combinations(board, pawn_moves, wall_moves):
        player = pawn_moves[0][0]

        import timeit
        start = timeit.default_timer()
        # Filter out walls that block the path of the opponents pawns
        wall_moves = Player.filter_blocking_walls(board, 'O' if player == 'X' else 'X', wall_moves)
        print(timeit.default_timer() - start)

        return tuple(
            filter(
                lambda move: board.check_paths_after_move(move, print_failure=False),
                product(pawn_moves, wall_moves)
            )
        )

    # Returns a filtered list of wall moves that don't block the path of the given player's pawns
    @staticmethod
    def filter_blocking_walls(board, player, wall_moves):
        if player == 'X':
            pawns = board.player_1_pawns
            goals = board.player_2_start
        else:
            pawns = board.player_2_pawns
            goals = board.player_1_start

        # Try to find two non-adjacent paths from each start to each pawn
        paths = [True] * 4

        for pawn_index in range(2):
            for goal_index in range(2):
                next_jump, prev_jump, jump_filter = \
                    Player.find_non_adjacent_paths(board, pawns[pawn_index], goals[goal_index])
                new_next_jump, new_prev_jump, _ = \
                    Player.find_non_adjacent_paths(board, pawns[pawn_index], goals[goal_index], jump_filter=jump_filter)

                if goals[goal_index] not in new_prev_jump:
                    paths[pawn_index * 2 + goal_index] = (next_jump, prev_jump)

        # If two paths are found blocking both the paths is impossible
        if paths == [True, True, True, True]:
            return wall_moves

        filtered_wall_moves = []

        # TODO: Filter out wall moves
        return wall_moves

        return filtered_wall_moves

    @staticmethod
    def find_non_adjacent_paths(board, source, destination, jump_filter=None):
        # Dictionaries for keeping track of the path
        next_jump = dict()
        prev_jump = dict()

        # Heapq is used instead of PriorityQueue because the performance of lists in this case is faster
        prio_queue = [(hypot(source[1] - destination[1], source[0] - destination[0]), *source)]

        while len(prio_queue):
            # noinspection PyTupleAssignmentBalance
            _, row, column = heapq.heappop(prio_queue)
            pos = (row, column)

            # Update path
            if row != source[0] or column != source[1]:
                next_jump[prev_jump[pos]] = pos

            if row == destination[0] and column == destination[1]:
                break

            for new_pos in filter(
                    lambda jump: jump not in prev_jump and (jump_filter is None or jump not in jump_filter),
                    board.iter_non_blocking_jumps(row, column)):
                prev_jump[new_pos] = pos
                heapq.heappush(prio_queue, (hypot(new_pos[1] - destination[1], new_pos[0] - destination[0]), *new_pos))

        # Fill out the filter dictionary
        if jump_filter is None:
            jump_filter = dict()

        current = (source[0], source[1])
        while current[0] != destination[0] or current[1] != destination[1]:
            current = next_jump[current]

            jump_filter[current] = True
            if current[0] > 0:
                jump_filter[(current[0] - 1, current[1])] = True
            if current[0] < board.rows - 1:
                jump_filter[(current[0] + 1, current[1])] = True
            if current[1] > 0:
                jump_filter[(current[0], current[1] - 1)] = True
            if current[1] < board.columns - 1:
                jump_filter[(current[0], current[1] + 1)] = True

        jump_filter.pop((source[0], source[1]), None)
        jump_filter.pop((destination[0], destination[1]), None)

        return next_jump, prev_jump, jump_filter


class Computer(Player):
    def __init__(self, player, walls, game):
        super().__init__(player, walls, game)

    def get_move(self, board):
        return choice(self.legal_board_moves(board))


class Human(Player):
    def __init__(self, player, walls, game):
        super().__init__(player, walls, game)

    def get_move(self, board):
        # Ask for input until the move is valid
        move = None
        while not self.valid_move(board, move):
            move = input("Enter the move: ").strip()

        player, pawn_index, pawn_row, pawn_column, wall_type, wall_row, wall_column = self.extract_move_info(move)

        return ((player, pawn_index, pawn_row, pawn_column),) \
                   if wall_type is None else \
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
