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

        # Strip trailing and leading spaces and check the format
        move = move.strip()
        if not fullmatch("\[[XO] [12]\] \[[1-9A-Z] [1-9A-Z]\]?( \[[ZP] [1-9A-Z] [1-9A-Z]\])", move):
            print("Invalid format! Input must be of [X/O 1/2] [new_row new_column] ([Z/P row column])")
            return False

        return self.valid_pawn_move(board, move[1], move[3], (move[7], move[9])) and \
               (self.valid_wall_placement(board) if len(move) == 11 else self.valid_wall_placement(board, move[13],
                                                                                                   (move[15],
                                                                                                    move[17])))

    def valid_pawn_move(self, board, player, pawn, new_pos):
        if player != self.player:
            print("You cannot move your opponents pawns!")
            return False

        prev_pos = self.pawns[pawn - 1]
        # Unsupported movement
        if 1 > abs(prev_pos[0] - new_pos[0]) + abs(prev_pos[1] + prev_pos[1]) > 2:
            print("You cannot stay in place or move more than two squares from you current position")
            return False

        # Diagonal movement
        if abs(prev_pos[0] - new_pos[0]) == 1 and abs(prev_pos[1] + prev_pos[1]) == 1:
            pass

        # Straight movement
        else:
            pass

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

        row, column = board.board_index_to_matrix_index(pos[0]), board.board_index_to_matrix_index(pos[1])
        if row >= board.rows - 1 or column >= board.columns - 1:
            print("Wall indices out of bound!")
            return False

        if (wall == 'Z' and (board.board[row][column].right is not None or
                             board.board[row + 1][column].right is not None)) or \
                (wall == 'P' and (board.board[row][column].bottom is not None or
                                  board.board[row][column + 1].bottom is not None)):
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

    def get_move(self, board):
        move = None
        while self.valid_move(board, move):
            move = input("Enter the move: ")

        # TODO: Return a move
