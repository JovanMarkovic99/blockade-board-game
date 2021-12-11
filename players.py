from re import fullmatch


class Player:
    def __init__(self, player, pawns, walls):
        self.player = player
        self.pawns = pawns
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

    def get_move(self, board):
        pass

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

    def valid_pawn_move(self, board, player, pawn, new_pos):
        if player != self.player:
            print("You cannot move your opponents pawns!")
            return False

        if new_pos[0] >= board.rows or new_pos[1] >= board.columns:
            print("Pawn indices are out of bounds!")
            return False

        prev_pos = self.pawns[pawn]
        old_square = board.board[prev_pos[0]][prev_pos[1]]
        new_square = board.board[new_pos[0]][new_pos[1]]

        if abs(prev_pos[0] - new_pos[0]) + abs(prev_pos[1] - new_pos[1]) == 0 or \
                abs(prev_pos[0] - new_pos[0]) + abs(prev_pos[1] - new_pos[1]) > 2:
            print("You cannot stay in place or move more than two squares from you current position!")
            return False

        if (new_square.center == 'X' or new_square.center == 'O') and \
                (new_square.starting is None or new_square.starting == player):
            print("You cannot jump to a square with a pawn!")
            return False

        # Top
        if new_pos[0] < prev_pos[0]:
            # Top-Left
            if new_pos[1] < prev_pos[1]:
                if old_square.top_left() or new_square.bottom_right() or \
                        (old_square.left and new_square.right) or (old_square.top and new_square.bottom):
                    print("You cannot jump over a wall!")
                    return False

            # Top-Right
            elif new_pos[1] > prev_pos[1]:
                if old_square.top_rigt() or new_square.bottom_left() or \
                        (old_square.right and new_square.left) or (old_square.top and new_square.bottom):
                    print("You cannot jump over a wall!")
                    return False

            else:
                # Top-Middle
                if prev_pos[0] - new_pos[0] == 1:
                    if new_square.bottom:
                        print("You cannot jump over a wall!")
                        return False
                    elif new_square.starting is not None:
                        pass
                    elif new_square.top:
                        print("You cannot jump just one space forward!")
                        return False
                    elif new_pos[0] == 0 or (board.board[new_pos[0] - 1][new_pos[1]].center != 'X' and
                                             board.board[new_pos[0] - 1][new_pos[1]].center != 'O'):
                        print("You cannot jump just one space forward!")
                        return False

                # Top-Middle-Long
                else:
                    if new_square.bottom or old_square.top:
                        print("You cannot jump over a wall!")
                        return False

        # Bottom
        elif new_pos[0] > prev_pos[0]:
            # Bottom-Left
            if new_pos[1] < prev_pos[1]:
                if old_square.bottom_left() or new_square.top_right() or \
                        (old_square.bottom and new_square.top) or (old_square.left and new_square.right):
                    print("You cannot jump over a wall!")
                    return False

            # Bottom-Right
            elif new_pos[1] > prev_pos[1]:
                if old_square.bottom_right() or new_square.top_left() or \
                        (old_square.bottom and new_square.top) or (old_square.right and new_square.left):
                    print("You cannot jump over a wall!")
                    return False

            else:
                # Bottom-Middle
                if new_pos[0] - prev_pos[0] == 1:
                    if new_square.top:
                        print("You cannot jump over a wall!")
                        return False
                    elif new_square.starting is not None:
                        pass
                    elif new_square.bottom:
                        print("You cannot jump just one space forward!")
                        return False
                    elif new_pos[0] == board.rows - 1 or (board.board[new_pos[0] + 1][new_pos[1]].center != 'X' and
                                                          board.board[new_pos[0] + 1][new_pos[1]].center != 'O'):
                        print("You cannot jump just one space forward!")
                        return False

                # Bottom-Middle-Long
                else:
                    if new_square.top or old_square.bottom:
                        print("You cannot jump over a wall!")
                        return False

        elif new_pos[1] > prev_pos[1]:
            # Middle-Right
            if new_pos[1] - prev_pos[1] == 1:
                if new_square.left:
                    print("You cannot jump over a wall!")
                    return False
                elif new_square.starting is not None:
                    pass
                elif new_square.right:
                    print("You cannot jump just one space forward!")
                    return False
                elif new_pos[1] == board.columns - 1 or (board.board[new_pos[0]][new_pos[1] + 1].center != 'X' and
                                                         board.board[new_pos[0]][new_pos[1] + 1].center != 'O'):
                    print("You cannot jump just one space forward!")
                    return False

            # Middle-Right-Long
            else:
                if new_square.left or old_square.right:
                    print("You cannot jump over a wall!")
                    return False

        else:
            # Middle-Left
            if prev_pos[1] - new_pos[1] == 1:
                if new_square.right:
                    print("You cannot jump over a wall!")
                    return False
                elif new_square.starting is not None:
                    pass
                elif new_square.left:
                    print("You cannot jump just one space forward!")
                    return False
                elif new_pos[1] == 0 or (board.board[new_pos[0]][new_pos[1] - 1].center != 'X' and
                                         board.board[new_pos[0]][new_pos[1] - 1].center != 'O'):
                    print("You cannot jump just one space forward!")
                    return False

            # Middle-Left-Long
            else:
                if new_square.right or old_square.left:
                    print("You cannot jump over a wall!")
                    return False

        return True

    def valid_wall_placement(self, board, wall=None, pos=None):
        if wall is None:
            if self.vertical_walls > 0 or self.horizontal_walls > 0:
                print("You must place a wall!")
                return False
            else:
                return True

        if (wall == 'Z' and self.vertical_walls == 0) or (wall == 'P' and self.horizontal_walls == 0):
            print("There are no more walls of that type to place!")
            return False

        row, column = pos[0], pos[1]
        if row >= board.rows - 1 or column >= board.columns - 1:
            print("Wall indices out of bound!")
            return False

        if (wall == 'Z' and (board.board[row][column].right or board.board[row + 1][column].right)) or \
                (wall == 'P' and (board.board[row][column].bottom or board.board[row][column + 1].bottom)):
            print("A wall already exists on those coordinates!")
            return False

        # TODO: Add check for a path existing to the initial pawns

        return True


class Computer(Player):
    def __init__(self, player, pawns, walls):
        super().__init__(player, pawns, walls)

    def get_move(self, board):
        pass


class Human(Player):
    def __init__(self, player, pawns, walls):
        super().__init__(player, pawns, walls)

    # Inputs the move from the user, validates it and packs it into the following format:
    # ((player, player_pawn, new_row, new_col), optional(wall_type, row, col))
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
