import pyxel

def xclamp(n):
    return max(min(224, n), 0)

def yclamp(n):
    return max(min(144, n), 0)

class App:
    def __init__(self):
        pyxel.init(240, 160, caption='test game')
        pyxel.image(0).load(0, 0, 'assets/test.png')

        self.speed = 2
        self.player_x = 100
        self.player_y = 100
        self.facing_left = True
        self.heart = False

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        self.update_player()

    def update_player(self):
        if pyxel.btn(pyxel.KEY_A):
            self.player_x = xclamp(self.player_x - self.speed)
            self.facing_left = True
        if pyxel.btn(pyxel.KEY_D):
            self.player_x = xclamp(self.player_x + self.speed)
            self.facing_left = False
        if pyxel.btn(pyxel.KEY_W):
            self.player_y = yclamp(self.player_y - self.speed)
        if pyxel.btn(pyxel.KEY_S):
            self.player_y = yclamp(self.player_y + self.speed)
        if pyxel.btnp(pyxel.KEY_L):
            if self.heart:
                self.heart = False
            else:
                self.heart = True

    def draw(self):
        pyxel.cls(5)

        if self.facing_left:
            m = 1
        else:
            m = -1

        if self.heart == False:
            pyxel.blt(self.player_x, self.player_y, 0, 0, 0, 16*m, 16, 5)
        else:
            pyxel.blt(self.player_x, self.player_y, 0, 0, 16, 16*m, 16, 5)


App()
