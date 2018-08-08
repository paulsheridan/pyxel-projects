import pyxel

class App:
    def __init__(self):
        pyxel.init(160, 240, caption='seesaw motherfucker')
        pyxel.run(self.update, self.draw)

    def update(self):
        pass

    def draw(self):
        pyxel.cls(1)

App()
