#!/usr/bin/env python3

import signal
import configparser
from os import path
from itertools import cycle, chain

from players import *
from board import *


class Game:
    def __init__(self):
        self.rows = None
        self.columns = None
        self.walls = None
        self.player_1_pawns = [[None, None], [None, None]]
        self.player_2_pawns = [[None, None], [None, None]]
        self.player_1 = None
        self.player_2 = None
        self.board = None
        signal.signal(signal.SIGINT, self.handle_interrupt)

    # Board and initial settings setup
    def setup(self):
        if self.yes_no_prompt("Do you want to use the default settings?"):
            self.read_config()
        else:
            self.input_config()

        # TODO: Add player vs player and computer vs computer

        if self.yes_no_prompt("Do you wish to play first?"):
            self.player_1 = Human('X', self.player_1_pawns, self.walls)
            self.player_2 = Computer('O', self.player_2_pawns, self.walls)
        else:
            self.player_1 = Computer('X', self.player_1_pawns, self.walls)
            self.player_2 = Human('O', self.player_2_pawns, self.walls)

        self.board = Board(self.rows, self.columns, self.player_1_pawns, self.player_2_pawns)

    # Actual game logic
    def run(self):
        moves = 0
        current_player = None
        player_cycle = cycle((self.player_1, self.player_2))

        while not self.game_end():
            current_player = next(player_cycle)
            moves += 1

            self.board.print_board()
            print("Move: " + str(moves))
            current_player.print_player_info()

            self.play_move(current_player.get_move(self.board))

        current_player.print_winner(moves)
        self.board.print_board()

    def play_move(self, move):
        # TODO: Remove when the computer returns a move
        if move is None:
            return

        old_pos = None
        new_pos = (move[0][2], move[0][3])

        # Update pawn position
        if move[0][0] == 'X':
            old_pos = (self.player_1_pawns[move[0][1] - 1][0], self.player_1_pawns[move[0][1] - 1][1])
            self.player_1_pawns[move[0][1] - 1][0], self.player_1_pawns[move[0][1] - 1][1] = new_pos[0], new_pos[1]
        else:
            old_pos = (self.player_2_pawns[move[0][1] - 1][0], self.player_2_pawns[move[0][1] - 1][1])
            self.player_2_pawns[move[0][1] - 1][0], self.player_2_pawns[move[0][1] - 1][1] = new_pos[0], new_pos[1]

        # Update board
        self.board.board[old_pos[0]][old_pos[1]].center = \
            ' ' if self.board.board[old_pos[0]][old_pos[1]].starting is None else '·'
        self.board.board[new_pos[0]][new_pos[1]].center = move[0][0]

        # Update board walls
        if len(move) == 2:
            if move[1][0] == 'Z':
                self.board.board[move[1][1]][move[1][2]].right = True
                self.board.board[move[1][1]][move[1][2] + 1].left = True
                self.board.board[move[1][1] + 1][move[1][2]].right = True
                self.board.board[move[1][1] + 1][move[1][2] + 1].left = True
            else:
                self.board.board[move[1][1]][move[1][2]].bottom = True
                self.board.board[move[1][1]][move[1][2] + 1].bottom = True
                self.board.board[move[1][1] + 1][move[1][2]].top = True
                self.board.board[move[1][1] + 1][move[1][2] + 1].top = True

    def game_end(self):
        return any(map(lambda square: (square.starting == 'O' and square.center == 'X') or
                                      (square.starting == 'X' and square.center == 'O'),
                       chain(*iter(self.board.board))))

    # Input the config from the user
    def input_config(self):
        self.rows = self.integer_prompt("Enter an odd number of rows (11 <= x <= 22): ", lower_bound=11,
                                        upper_bound=22, even=False)
        self.columns = self.integer_prompt("Enter an even number of columns (14 <= x <= 28): ", lower_bound=14,
                                           upper_bound=28, even=True)
        self.walls = self.integer_prompt("Enter the number of walls (9 <= x <= 18): ", lower_bound=9,
                                         upper_bound=18)

        while True:
            # Player 1 pawn positions (-1 is because the in-game board coordinates starts from 1)
            self.player_1_pawns[0][0] = self.integer_prompt("Enter the row number of the first pawn of player 1 (1 "
                                                            "<= x <= " + str(self.rows) + "): ", lower_bound=1,
                                                            upper_bound=self.rows) - 1
            self.player_1_pawns[0][1] = self.integer_prompt("Enter the column number of the first pawn of player 1 (1 "
                                                            "<= x <= " + str(self.columns) + "): ", lower_bound=1,
                                                            upper_bound=self.columns) - 1
            self.player_1_pawns[1][0] = self.integer_prompt("Enter the row number of the second pawn of player 1 (1 "
                                                            "<= x <= " + str(self.rows) + "): ", lower_bound=1,
                                                            upper_bound=self.rows) - 1
            self.player_1_pawns[1][1] = self.integer_prompt("Enter the column number of the second pawn of player 1 (1 "
                                                            "<= x <= " + str(self.columns) + "): ", lower_bound=1,
                                                            upper_bound=self.columns) - 1

            # Player 2 pawn positions
            self.player_2_pawns[0][0] = self.integer_prompt("Enter the row number of the first pawn of player 2 (1 "
                                                            "<= x <= " + str(self.rows) + "): ", lower_bound=1,
                                                            upper_bound=self.rows) - 1
            self.player_2_pawns[0][1] = self.integer_prompt("Enter the column number of the first pawn of player 2 (1 "
                                                            "<= x <= " + str(self.columns) + "): ", lower_bound=1,
                                                            upper_bound=self.columns) - 1
            self.player_2_pawns[1][0] = self.integer_prompt("Enter the row number of the second pawn of player 2 (1 "
                                                            "<= x <= " + str(self.rows) + "): ", lower_bound=1,
                                                            upper_bound=self.rows) - 1
            self.player_2_pawns[1][1] = self.integer_prompt("Enter the column number of the second pawn of player 2 (1 "
                                                            "<= x <= " + str(self.columns) + "): ", lower_bound=1,
                                                            upper_bound=self.columns) - 1

            # Check for colliding pawns
            if self.player_1_pawns[0] in self.player_2_pawns or self.player_1_pawns[1] in self.player_2_pawns \
                    or self.player_1_pawns[0] == self.player_1_pawns[1] \
                    or self.player_2_pawns[0] == self.player_2_pawns[1]:
                print("Pawn placement invalid, pawns cannot be inside each other!")
            else:
                break

    # Read the config from the "config.ini" file
    def read_config(self):
        try:
            config = configparser.ConfigParser()

            if not path.isfile("config.ini"):
                self.create_config()

            config.read("config.ini")

            for key in config["BOARD_INFO"]:
                val = int(config["BOARD_INFO"][key])

                if key == "rows" and 11 <= val <= 22 and val % 2 == 1:
                    self.rows = val
                elif key == "columns" and 14 <= val <= 28 and val % 2 == 0:
                    self.columns = val
                elif key == "walls" and 9 <= val <= 18:
                    self.walls = val

                # Player 1 pawn positions (-1 is because the in-game board coordinates starts from 1)
                elif key == "p1_pawn1_row":
                    self.player_1_pawns[0][0] = val - 1
                elif key == "p1_pawn1_column":
                    self.player_1_pawns[0][1] = val - 1
                elif key == "p1_pawn2_row":
                    self.player_1_pawns[1][0] = val - 1
                elif key == "p1_pawn2_column":
                    self.player_1_pawns[1][1] = val - 1

                # Player 2 pawn positions
                elif key == "p2_pawn1_row":
                    self.player_2_pawns[0][0] = val - 1
                elif key == "p2_pawn1_column":
                    self.player_2_pawns[0][1] = val - 1
                elif key == "p2_pawn2_row":
                    self.player_2_pawns[1][0] = val - 1
                elif key == "p2_pawn2_column":
                    self.player_2_pawns[1][1] = val - 1

        except IOError:
            print("Unable to read or create config falling back to default values")
        finally:
            if self.rows is None:
                self.rows = 11
            if self.columns is None:
                self.columns = 14
            if self.walls is None:
                self.walls = 9
            if None in self.player_1_pawns[0] or self.player_1_pawns[0][0] >= self.rows or \
                    self.player_1_pawns[0][1] >= self.columns:
                self.player_1_pawns[0] = [3, 3]
            if None in self.player_1_pawns[1] or self.player_1_pawns[1][0] >= self.rows or \
                    self.player_1_pawns[1][1] >= self.columns:
                self.player_1_pawns[1] = [self.rows - 4, 3]
            if None in self.player_2_pawns[0] or self.player_2_pawns[0][0] >= self.rows or \
                    self.player_2_pawns[0][1] >= self.columns:
                self.player_2_pawns[0] = [3, self.columns - 4]
            if None in self.player_2_pawns[1] or self.player_2_pawns[1][0] >= self.rows or \
                    self.player_2_pawns[1][1] >= self.columns:
                self.player_2_pawns[1] = [self.rows - 4, self.columns - 4]

            # If pawns are placed inside each other default their position
            if self.player_1_pawns[0] in self.player_2_pawns or self.player_1_pawns[1] in self.player_2_pawns \
                    or self.player_1_pawns[0] == self.player_1_pawns[1] \
                    or self.player_2_pawns[0] == self.player_2_pawns[1]:
                self.player_1_pawns = [[3, 3], [self.rows - 4, 3]]
                self.player_2_pawns = [[3, self.columns - 4], [self.rows - 4, self.columns - 4]]

    @staticmethod
    def create_config():
        config = configparser.ConfigParser()
        config["BOARD_INFO"] = {"rows": "11", "columns": "14", "walls": "9",
                                "p1_pawn1_row": "4", "p1_pawn1_column": "4",
                                "p1_pawn2_row": "8", "p1_pawn2_column": "4",
                                "p2_pawn1_row": "4", "p2_pawn1_column": "11",
                                "p2_pawn2_row": "8", "p2_pawn2_column": "11"}
        with open("config.ini", "w") as configfile:
            config.write(configfile)

    @staticmethod
    def handle_interrupt(signum, frame):
        if Game.yes_no_prompt("Are you sure you want to quit?"):
            exit()

    @staticmethod
    def yes_no_prompt(message):
        res = input(message + " (y/n) \n")

        while True:
            if res.lower() == "y":
                return True
            elif res.lower() == "n":
                return False

            res = input("Please enter \"y\" or \"n\"\n")

    @staticmethod
    def integer_prompt(message, lower_bound=None, upper_bound=None, even=None):
        res = input(message)

        while True:
            if (res.isdigit() or (res.startswith('-') and res[1:].isdigit())) \
                    and (lower_bound is None or int(res) >= lower_bound) \
                    and (upper_bound is None or int(res) <= upper_bound) \
                    and (even is None or not bool(int(res) % 2) == even):
                return int(res)

            res = input("Please enter a valid"
                        + ("" if even is None else (" even " if even else " odd "))
                        + "number between "
                        + ("-inf" if lower_bound is None else str(lower_bound))
                        + " and "
                        + ("+inf" if upper_bound is None else str(upper_bound)) + ": ")


if __name__ == "__main__":
    g = Game()
    g.setup()
    g.run()
