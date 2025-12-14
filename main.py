import map;
import new;

class game_loop():
    #

    def __init__(self):
        #
        #

        print("Game initialized.")

        self.new = new.new()

    def run(self):
        #
        #

        print("Welcome to the Game!")

        next = input("Press Enter for next round")

        if next == "":
            self.new.calculate()
            self.run()
        




game_loop = game_loop()
game_loop.run()