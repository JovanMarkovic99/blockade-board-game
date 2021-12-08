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

    def get_move(self, board):
        pass


class Human(Player):
    def __init__(self, player, walls):
        super().__init__(player, walls)

    def get_move(self, board):
        pass


class Computer(Player):
    def __init__(self, player, walls):
        super().__init__(player, walls)

    def get_move(self, board):
        pass
