class Board:
    def __init__(self, columns, rows, player_1_pawns, player_2_pawns):
        self.columns = columns
        self.rows = rows
        self.board = [[BoardSquare() for _ in range(columns)] for _ in range(rows)]
        self.board[player_1_pawns[0][1] - 1][player_1_pawns[0][0] - 1].set_start('X')
        self.board[player_1_pawns[1][1] - 1][player_1_pawns[1][0] - 1].set_start('X')
        self.board[player_2_pawns[0][1] - 1][player_2_pawns[0][0] - 1].set_start('O')
        self.board[player_2_pawns[1][1] - 1][player_2_pawns[1][0] - 1].set_start('O')
        for row in self.board:
            for piece in row:
                print(piece.center, end="")

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
                        print("|" if self.board[index_i][index_j].right is None else "‖", end="")

                # Top-bottom wall rows

                # Top-bottom walls
                elif j != 0 and j != 2 * self.columns + 2 and j % 2 == 0:
                    print("—" if self.board[index_i][index_j].top is None else "=", end="")

                else:
                    print(" ", end="")
            print()

    @staticmethod
    def matrix_index_to_board_index(index):
        return chr(ord('0') + index + 1) if index < 9 else chr(ord('A') - 9 + index)

    @staticmethod
    def board_index_to_matrix_index(char):
        return ord(char) - ord('0') - 1 if ord('0') <= ord(char) <= ord('9') else ord(char) - ord('A') + 9


class BoardSquare:
    def __init__(self, center=" "):
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
