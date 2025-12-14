import json

import map
import new

class game_loop():
    #

    def __init__(self):
        #
        #

        print("Game initialized.")

        with open ("storage/players.json", "r") as f:
            self.player_data = json.load(f)

        self.new = new.new()
        self.map = map.Map()

    def run(self):
        #
        #

        for i in range(self.player_data["participants"]):

            


        self.map.display()

        next = input("Press Enter for next round")

        if next == "":
            self.new.calculate()
            self.run()
        




game_loop = game_loop()
game_loop.run()
