import tkinter as tk

class Map:
    #

    def __init__(self):
        #
        #

        self.root = tk.Tk()
        self.root.title("Game Map")
        self.root.state('zoomed')

        self.selected_regions = None

        self.regions = {
            "North Germany": {
                "population": 5000000,
                "gold": 100,
                "happiness": 80,
                "color": "#5da5da", # Blueish
                # Coordinates (x, y) points to draw the shape
                "coords": [150, 50,  350, 50,  380, 200,  120, 200]
            },
            "South Germany": {
                "population": 4500000,
                "gold": 120,
                "happiness": 90,
                "color": "#faa43a", # Orangey
                "coords": [120, 205, 380, 205, 350, 400,  150, 400]
            }
        }

        self.canvas = tk.Canvas(self.root, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.display()

    def display(self):
        #
        #

        for name, data in self.regions.items():
            # Create the polygon
            # tags=name allows us to identify which shape is clicked later
            self.canvas.create_polygon(
                data["coords"], 
                fill=data["color"], 
                outline="black", 
                width=2,
                tags=name 
            )
            
            # Place a text label in the 'center' (roughly)
            center_x = sum(data["coords"][0::2]) / len(data["coords"][0::2])
            center_y = sum(data["coords"][1::2]) / len(data["coords"][1::2])
            self.canvas.create_text(center_x, center_y, text=name, font=("Arial", 10, "bold"))

            # BIND CLICK EVENT
            # When this specific shape is clicked, run self.on_region_click
            self.canvas.tag_bind(name, "<Button-1>", lambda event, region=name: self.on_region_click(region))