#!/usr/bin/env python3

import signal
import configparser
from os import path
from itertools import cycle

from players import *
from board import *


class Game:
    def __init__(self):
        self.rows = 0
        self.columns = 0
        self.walls = 0
        self.player_1_pawns = [[0, 0], [0, 0]]
        self.player_2_pawns = [[0, 0], [0, 0]]
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

        if self.yes_no_prompt("Do you wish to play?"):
            if self.yes_no_prompt("Do you wish to play versus a computer?"):
                if self.yes_no_prompt("Do you wish to play first?"):
                    self.player_1 = Human('X', self.walls, self)
                    self.player_2 = Computer('O', self.walls, self)
                else:
                    self.player_1 = Computer('X', self.walls, self)
                    self.player_2 = Human('O', self.walls, self)
            else:
                self.player_1 = Human('X', self.walls, self)
                self.player_2 = Human('O', self.walls, self)
        else:
            self.player_1 = Computer('X', self.walls, self)
            self.player_2 = Computer('O', self.walls, self)

        self.board = Board(self.rows, self.columns, self.player_1_pawns, self.player_2_pawns)

    # Actual game logic
    def run(self):
        player_cycle = cycle((self.player_1, self.player_2))
        current_player = None
        moves = 0

        while not self.board.game_end():
            current_player = next(player_cycle)
            moves += 1

            self.board.print_board()
            print(f"Move: {moves}")
            current_player.print_player_info()

            # Get the move and test for a draw
            move = current_player.get_move(self.board)
            if move is None:
                print('-' * 50)
                print(f"DRAW IN {moves} MOVES".center(50, '-'))
                print('-' * 50)
                return
            # Check for turn skipping (as a human command)
            elif move != ():
                self.board = current_player.play_move(self.board, move)

        self.board.print_board()
        current_player.print_winner(moves)

    # Input the config from the user
    def input_config(self):
        self.rows = self.integer_prompt("Enter an odd number of rows (3 <= x <= 22): ", lower_bound=3,
                                        upper_bound=22, even=False)
        self.columns = self.integer_prompt("Enter an even number of columns (4 <= x <= 28): ", lower_bound=4,
                                           upper_bound=28, even=True)
        self.walls = self.integer_prompt("Enter the number of walls (0 <= x <= 18): ", lower_bound=0, upper_bound=18)

        while True:
            # Player 1 pawn positions (-1 is because the in-game board coordinates starts from 1)
            self.player_1_pawns[0][0] = self.integer_prompt(
                f"Enter the row number of the first pawn of player 1 (1 <= x <= {self.rows}): ",
                lower_bound=1, upper_bound=self.rows) - 1
            self.player_1_pawns[0][1] = self.integer_prompt(
                f"Enter the column number of the first pawn of player 1 (1 <= x <= {self.columns}): ",
                lower_bound=1, upper_bound=self.columns) - 1
            self.player_1_pawns[1][0] = self.integer_prompt(
                f"Enter the row number of the second pawn of player 1 (1 <= x <= {self.rows}): ",
                lower_bound=1, upper_bound=self.rows) - 1
            self.player_1_pawns[1][1] = self.integer_prompt(
                f"Enter the column number of the second pawn of player 1 (1 <= x <= {self.columns}): ",
                lower_bound=1, upper_bound=self.columns) - 1

            # Player 2 pawn positions
            self.player_2_pawns[0][0] = self.integer_prompt(
                f"Enter the row number of the first pawn of player 2 (1 <= x <= {self.rows}): ",
                lower_bound=1, upper_bound=self.rows) - 1
            self.player_2_pawns[0][1] = self.integer_prompt(
                f"Enter the column number of the first pawn of player 2 (1 <= x <= {self.columns}): ",
                lower_bound=1, upper_bound=self.columns) - 1
            self.player_2_pawns[1][0] = self.integer_prompt(
                f"Enter the row number of the second pawn of player 2 (1 <= x <= {self.rows}): ",
                lower_bound=1, upper_bound=self.rows) - 1
            self.player_2_pawns[1][1] = self.integer_prompt(
                f"Enter the column number of the second pawn of player 2 (1 <= x <= {self.columns}): ",
                lower_bound=1, upper_bound=self.columns) - 1

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

                if key == "rows" and 3 <= val <= 22 and val % 2 == 1:
                    self.rows = val
                elif key == "columns" and 4 <= val <= 28 and val % 2 == 0:
                    self.columns = val
                elif key == "walls" and 0 <= val <= 18:
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
        exit()

    @staticmethod
    def yes_no_prompt(message):
        res = input(message + " (y/n) ")

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
