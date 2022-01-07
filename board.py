import heapq
from copy import deepcopy, copy


class Board:
    def __init__(self, rows, columns, player_1_pawns, player_2_pawns):
        self.rows = rows
        self.columns = columns
        self.player_1_pawns = deepcopy(player_1_pawns)
        self.player_2_pawns = deepcopy(player_2_pawns)
        self.player_1_start = (copy(player_1_pawns[0]), copy(player_1_pawns[1]))
        self.player_2_start = (copy(player_2_pawns[0]), copy(player_2_pawns[1]))

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
        return self.player_1_pawns[0] in self.player_2_start or self.player_1_pawns[1] in self.player_2_start or \
               self.player_2_pawns[0] in self.player_1_start or self.player_2_pawns[1] in self.player_1_start

    def valid_pawn_move(self, player, pawn_index, row, column, print_failure=True):
        # Check if pawn indices are in range
        if row >= self.rows or column >= self.columns:
            self.conditional_print("Pawn indices are out of bounds!", print_failure)
            return False

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
                    elif new_square.starting is not None and new_square.starting != player:
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
                    elif new_square.starting is not None and new_square.starting != player:
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
                elif new_square.starting is not None and new_square.starting != player:
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
                elif new_square.starting is not None and new_square.starting != player:
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

    def move_pawn(self, player, pawn_index, row, column):
        player_pawns = self.player_1_pawns if player == 'X' else self.player_2_pawns
        old_row, old_column = player_pawns[pawn_index][0], player_pawns[pawn_index][1]

        # Update pawn position
        player_pawns[pawn_index][0], player_pawns[pawn_index][1] = row, column

        # Update board
        self.board[old_row][old_column].center = \
            ' ' if self.board[old_row][old_column].starting is None else '·'
        self.board[row][column].center = player

        # Return the undoing move
        return player, pawn_index, old_row, old_column

    def valid_wall_placement(self, wall_type, row, column, print_failure=True):
        # Check if wall indices are in range
        if row >= self.rows - 1 or column >= self.columns - 1:
            self.conditional_print("Wall indices out of bound!", print_failure)
            return False

        if (wall_type == 'Z' and (self.board[row][column].right or self.board[row + 1][column].right)) or \
                (wall_type == 'P' and (self.board[row][column].bottom or self.board[row][column + 1].bottom)):
            self.conditional_print("A wall already exists on those coordinates!", print_failure)
            return False

        return True

    def place_wall(self, wall_type, row, column, lift=False):
        if wall_type == 'Z':
            self.board[row][column].right = not lift
            self.board[row][column + 1].left = not lift
            self.board[row + 1][column].right = not lift
            self.board[row + 1][column + 1].left = not lift
        else:
            self.board[row][column].bottom = not lift
            self.board[row][column + 1].bottom = not lift
            self.board[row + 1][column].top = not lift
            self.board[row + 1][column + 1].top = not lift

    def check_paths_after_move(self, move, print_failure=True):
        # Make the move
        undo_move = self.move_pawn(*(move[0]))
        self.place_wall(*(move[1]))

        if not self.check_path(self.player_1_pawns[0], self.player_2_start[0]) or \
                not self.check_path(self.player_1_pawns[0], self.player_2_start[1]) or \
                not self.check_path(self.player_1_pawns[1], self.player_2_start[0]) or \
                not self.check_path(self.player_1_pawns[1], self.player_2_start[1]) or \
                not self.check_path(self.player_2_pawns[0], self.player_1_start[0]) or \
                not self.check_path(self.player_2_pawns[0], self.player_1_start[1]) or \
                not self.check_path(self.player_2_pawns[1], self.player_1_start[0]) or \
                not self.check_path(self.player_2_pawns[1], self.player_1_start[1]):
            # Undo the move
            self.place_wall(*(move[1]), lift=True)
            self.move_pawn(*undo_move)

            self.conditional_print("You cannot block one of the pawns' path to the goal!", print_failure)
            return False

        # Undo the move
        self.place_wall(*(move[1]), lift=True)
        self.move_pawn(*undo_move)

        return True

    # A* algorithm to check if there is a pawn path from the source to the destination
    def check_path(self, source, destination):
        # Dictionary for keeping track of visited nodes
        seen_dict = {(source[0], source[1]): True}

        prio_queue = [(abs(source[1] - destination[1]) + abs(source[0] - destination[0]), *source)]
        while len(prio_queue):
            # noinspection PyTupleAssignmentBalance
            _, row, column = heapq.heappop(prio_queue)

            if row == destination[0] and column == destination[1]:
                return True

            for new_pos in filter(lambda jump: jump not in seen_dict, self.iter_non_blocking_jumps(row, column)):
                seen_dict[new_pos] = True
                heapq.heappush(prio_queue, (abs(new_pos[1] - destination[1]) + abs(new_pos[0] - destination[0]),
                                            *new_pos))

        return False

    # Returns all one square jumps from the square with the row and column taking into account only the walls.
    # It's similar to all legal jumps except it's jumps one square away and doesn't account for player position on
    # the squares. Used for path-checking
    def iter_non_blocking_jumps(self, row, column):
        # Top side
        if row > 0:
            # Top
            if not self.board[row][column].top:
                yield row - 1, column

            # Top-Left
            if column > 0 and not (
                    self.board[row][column].top_left() or
                    self.board[row - 1][column - 1].bottom_right() or
                    (self.board[row][column].top and self.board[row][column - 1].top) or
                    (self.board[row][column].left and self.board[row - 1][column].left)
            ):
                yield row - 1, column - 1

            # Top-Right
            if column < self.columns - 1 and not (
                    self.board[row][column].top_right() or
                    self.board[row - 1][column + 1].bottom_left() or
                    (self.board[row][column].top and self.board[row][column + 1].top) or
                    (self.board[row][column].right and self.board[row - 1][column].right)
            ):
                yield row - 1, column + 1

        # Bottom side
        if row < self.rows - 1:
            # Bottom
            if not self.board[row][column].bottom:
                yield row + 1, column

            # Bottom-Left
            if column > 0 and not (
                    self.board[row][column].bottom_left() or
                    self.board[row + 1][column - 1].top_right() or
                    (self.board[row][column].bottom and self.board[row][column - 1].bottom) or
                    (self.board[row][column].left and self.board[row + 1][column].left)
            ):
                yield row + 1, column - 1

            # Bottom-Right
            if column < self.columns - 1 and not (
                    self.board[row][column].bottom_right() or
                    self.board[row + 1][column + 1].top_left() or
                    (self.board[row][column].bottom and self.board[row][column + 1].bottom) or
                    (self.board[row][column].right and self.board[row + 1][column].right)
            ):
                yield row + 1, column + 1

        # Left
        if column > 0 and not self.board[row][column].left:
            yield row, column - 1

        # Right
        if column < self.columns - 1 and not self.board[row][column].right:
            yield row, column + 1

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
    def __init__(self, center=" ", top=False, left=False, right=False, bottom=False):
        self.center = center
        self.top = top
        self.left = left
        self.right = right
        self.bottom = bottom
        # Variable for remembering the starting position of the first or second player
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
