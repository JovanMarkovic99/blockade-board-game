import timeit
from re import fullmatch
from copy import deepcopy
from itertools import product, chain
import heapq
from math import hypot, inf

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

        new_board.move_pawn(*(move[0]))

        if len(move) == 2:
            new_board.place_wall(*(move[1]))

            # Update the number of walls
            if update_walls:
                if move[1][0] == 'Z':
                    self.vertical_walls -= 1
                else:
                    self.horizontal_walls -= 1

        return new_board

    def iter_next_legal_board_states(self, board, moves=None):
        return map(lambda move: self.play_move(board, move, update_walls=False),
                   self.legal_board_moves(board) if moves is None else moves)

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
        # TODO: Rewrite function as a generator

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

        # Filter out walls that block the path of the opponents pawns
        wall_moves = Player.filter_blocking_walls(board, 'O' if player == 'X' else 'X', wall_moves)

        # TODO: Change algorithm to use a search tree and process all pawn moves at the same time
        moves = []

        # Walls that don't block the first and second pawn at their base position
        non_pawn_blocking = (Player.filter_blocking_walls(board, player, wall_moves, only_pawn_index=0),
                             Player.filter_blocking_walls(board, player, wall_moves, only_pawn_index=1))

        for pawn_move in pawn_moves:
            undo_move = board.move_pawn(*pawn_move)

            new_wall_moves = Player.filter_blocking_walls(board, player, non_pawn_blocking[(pawn_move[1] + 1) % 2],
                                                          only_pawn_index=pawn_move[1])

            board.move_pawn(*undo_move)

            moves += product([pawn_move], new_wall_moves)

        return moves

    # Returns a filtered list of wall moves that don't block the path of the given player's pawns
    # The algorithm tries to find two non-adjacent paths for every path that needs to be checked.
    # If found, both of the paths cannot be blocked, so path-checking for that path is excluded.
    # If not, it tests if any of the walls obstruct the path and then tries to reconstruct it
    @staticmethod
    def filter_blocking_walls(board, player, wall_moves, only_pawn_index=None):
        if player == 'X':
            pawns = board.player_1_pawns
            goals = board.player_2_start
        else:
            pawns = board.player_2_pawns
            goals = board.player_1_start

        # Try to find two non-adjacent paths from each start to each pawn
        paths = [True] * 4
        for pawn_index in range(2):
            if only_pawn_index is not None and pawn_index != only_pawn_index:
                continue

            for goal_index in range(2):
                path, jump_filter = \
                    Player.find_non_adjacent_paths(board, pawns[pawn_index], goals[goal_index])
                new_path, _ = \
                    Player.find_non_adjacent_paths(board, pawns[pawn_index], goals[goal_index], jump_filter=jump_filter)

                # If two paths are found blocking both the paths is impossible otherwise it is possible
                if type(new_path) is not dict:
                    paths[pawn_index * 2 + goal_index] = path

        # Check if there are is no way to block any of the paths
        if paths == [True, True, True, True]:
            return wall_moves

        # Test if any of the walls obstructs the paths and reconstruct the path if necessary
        filtered_wall_moves = []
        for wall_move in wall_moves:
            legal = True
            board.place_wall(*wall_move)

            for index, path in enumerate(paths):
                if type(path) is dict:
                    # Check for parts of the path that need to be reconstructed
                    first_affected_square = None
                    last_affected_square = None
                    for potential_square in Player.iter_wall_placement_affected_squares(board, *wall_move):
                        if potential_square in path and path[potential_square] not in \
                                board.iter_non_blocking_jumps(potential_square[0], potential_square[1]):
                            if first_affected_square is None:
                                first_affected_square = potential_square
                            last_affected_square = path[potential_square]

                    # Try and reconstruct the path
                    if first_affected_square is not None and \
                            not board.check_path(first_affected_square, last_affected_square):
                        legal = False
                        break

            board.place_wall(*wall_move, lift=True)
            if legal:
                filtered_wall_moves.append(wall_move)

        return filtered_wall_moves

    @staticmethod
    def find_non_adjacent_paths(board, source, destination, jump_filter=None):
        if source[0] == destination[0] and source[1] == destination[1]:
            return {}, {}

        # Dictionary for keeping track of the path
        prev_jump = {(source[0], source[1]): None}

        # Heapq is used instead of PriorityQueue because the performance of lists in this case is faster
        prio_queue = [(hypot(source[1] - destination[1], source[0] - destination[0]), *source)]

        while len(prio_queue):
            # noinspection PyTupleAssignmentBalance
            _, row, column = heapq.heappop(prio_queue)
            pos = (row, column)

            if row == destination[0] and column == destination[1]:
                break

            for new_pos in filter(
                    lambda jump: jump not in prev_jump and (jump_filter is None or jump not in jump_filter),
                    board.iter_non_blocking_jumps(row, column)):
                prev_jump[new_pos] = pos
                heapq.heappush(prio_queue, (hypot(new_pos[1] - destination[1], new_pos[0] - destination[0]), *new_pos))

        # Check if a path is found
        if (destination[0], destination[1]) not in prev_jump:
            return False, False

        # Fill out the filter dictionary and the path
        if jump_filter is None:
            jump_filter = dict()

        path = dict()
        current = (destination[0], destination[1])
        while current[0] != source[0] or current[1] != source[1]:
            path[current] = prev_jump[current]

            for adjacent_square in Player.iter_adjacent_squares_from_jump(board, current, prev_jump[current]):
                jump_filter[adjacent_square] = True

            current = prev_jump[current]

        del jump_filter[(source[0], source[1])]
        del jump_filter[(destination[0], destination[1])]

        return path, jump_filter

    # Returns all the squares that cannot be jumped to in order for the paths to be non-adjacent
    @staticmethod
    def iter_adjacent_squares_from_jump(board, prev_pos, pos, include_jump_squares=True):
        if include_jump_squares:
            yield prev_pos
            yield pos

        # Top-side
        if prev_pos[0] > pos[0]:
            # Top-Middle
            if prev_pos[1] == pos[1]:
                if pos[1] > 0:
                    yield pos[0], pos[1] - 1
                    yield prev_pos[0], prev_pos[1] - 1
                if pos[1] < board.columns - 1:
                    yield pos[0], pos[1] + 1
                    yield prev_pos[0], prev_pos[1] + 1

            # Top-Left
            elif prev_pos[1] > pos[1]:
                yield pos[0], pos[1] + 1
                yield pos[0] + 1, pos[1]
                if pos[0] > 0:
                    yield pos[0] - 1, pos[1] + 1
                if pos[1] > 0:
                    yield pos[0] + 1, pos[1] - 1
                if prev_pos[0] < board.rows - 1:
                    yield prev_pos[0] + 1, prev_pos[1] - 1
                if prev_pos[1] < board.columns - 1:
                    yield prev_pos[0] - 1, prev_pos[1] + 1

            # Top-Right
            else:
                yield pos[0], pos[1] - 1
                yield pos[0] + 1, pos[1]
                if pos[0] > 0:
                    yield pos[0] - 1, pos[1] - 1
                if pos[1] < board.columns - 1:
                    yield pos[0] + 1, pos[1] + 1
                if prev_pos[0] < board.rows - 1:
                    yield prev_pos[0] + 1, prev_pos[1] + 1
                if prev_pos[1] > 0:
                    yield prev_pos[0] - 1, prev_pos[1] - 1

        # Middle
        elif prev_pos[0] == pos[0]:
            # Left and Right
            if pos[0] > 0:
                yield pos[0] - 1, pos[1]
                yield prev_pos[0] - 1, prev_pos[1]
            if pos[0] < board.rows - 1:
                yield pos[0] + 1, pos[1]
                yield prev_pos[0] + 1, prev_pos[1]

        # Bottom-side
        else:
            # Since the edges are undirected the bottom side is symmetrical to the top side
            yield from Player.iter_adjacent_squares_from_jump(board, pos, prev_pos, include_jump_squares=False)

    # Returns all squares whose non-blocking jumps may be changed if a given wall is placed
    @staticmethod
    def iter_wall_placement_affected_squares(board, wall_type, row, column):
        yield row, column
        yield row, column + 1
        yield row + 1, column
        yield row + 1, column + 1

        if wall_type == 'Z':
            if row > 0:
                yield row - 1, column
                yield row - 1, column + 1

            if row < board.rows - 2:
                yield row + 2, column
                yield row + 2, column + 1
        else:
            if column > 0:
                yield row, column - 1
                yield row + 1, column - 1

            if column < board.columns - 2:
                yield row, column + 2
                yield row + 1, column + 2

    def minimax(self, board, depth, alpha, beta, maximizing_eval):
        if depth == 0 or board.game_end():
            return self.static_evaluation(board)

        opponent = self.game.player_2 if self.player == 'X' else self.game.player_1
        if maximizing_eval:
            max_eval = -inf
            for new_board in self.iter_next_legal_board_states(board):
                evaluation = opponent.minimax(new_board, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, evaluation)

                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break

            return max_eval
        else:
            min_eval = inf
            for new_board in self.iter_next_legal_board_states(board):
                evaluation = opponent.minimax(new_board, depth - 1, alpha, beta, True)
                min_eval = min(min_eval, evaluation)

                beta = min(beta, evaluation)
                if beta <= alpha:
                    break

            return min_eval

    @staticmethod
    def static_evaluation(board):
        evaluation = 0

        for pawn in board.player_1_pawns:
            pawn_distance_1 = hypot(pawn[0] - board.player_2_start[0][0], pawn[1] - board.player_2_start[0][1])
            pawn_distance_2 = hypot(pawn[0] - board.player_2_start[1][0], pawn[1] - board.player_2_start[1][0])

            if pawn_distance_1 == 0 or pawn_distance_2 == 0:
                return inf

            evaluation += 1 / pawn_distance_1 + 1 / pawn_distance_2

        for pawn in board.player_2_pawns:
            pawn_distance_1 = hypot(pawn[0] - board.player_1_start[0][0], pawn[1] - board.player_1_start[0][1])
            pawn_distance_2 = hypot(pawn[0] - board.player_1_start[1][0], pawn[1] - board.player_1_start[1][0])

            if pawn_distance_1 == 0 or pawn_distance_2 == 0:
                return -inf

            evaluation -= 1 / pawn_distance_1 + 1 / pawn_distance_2

        return evaluation


class Computer(Player):
    def __init__(self, player, walls, game):
        super().__init__(player, walls, game)

    def get_move(self, board):
        time = timeit.default_timer()
        moves = self.legal_board_moves(board)
        boards = tuple(self.iter_next_legal_board_states(board, moves=moves))

        best_eval = -inf if self.player == 'X' else inf
        best_move = None
        for new_board, move in zip(boards, moves):
            evaluation = self.minimax(new_board, 0, -inf, inf, self.player == 'X')

            if (self.player == 'X' and best_eval <= evaluation) or (self.player == 'O' and best_eval >= evaluation):
                best_eval = evaluation
                best_move = move

        print(timeit.default_timer() - time)
        return best_move


class Human(Player):
    def __init__(self, player, walls, game):
        super().__init__(player, walls, game)

    def get_move(self, board):
        # Ask for input until the move is valid
        move = None
        while not self.valid_move(board, move):
            move = input("Enter the move: ").strip()

        player, pawn_index, pawn_row, pawn_column, wall_type, wall_row, wall_column = self.extract_move_info(move)

        return \
            ((player, pawn_index, pawn_row, pawn_column),) \
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
