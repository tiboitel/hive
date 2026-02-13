import random

class Map:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.tiles:list[str] = []

    def generate(self) -> None:
        for y in range(0, self.height):
            for x in range(0, self.width):
                rand = random.randint(0, 100)

                if (x == 0 or x == self.width - 1) or (y == 0 or y == self.height - 1):
                    self.tiles.append("#")
                elif (rand <= 5):
                    self.tiles.append("#")
                else:
                    self.tiles.append(".")
        return None

