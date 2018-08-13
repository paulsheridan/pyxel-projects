import os
import pyxel

from random import randint
from itertools import islice
from player import Player
from level import Level


class App:
    def __init__(self):
        pyxel.init(240, 160, caption='test game')
        self.level = Level('map_test2.txt', 16)

        self.offset_x = 0
        self.offset_y = 0
        self.height_in_tiles = pyxel.height // self.level.tile_size
        self.width_in_tiles = pyxel.width // self.level.tile_size

        assets = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'assets'))
        pyxel.image(0).load(0, 0, '{}/tile_test2.png'.format(assets))
        pyxel.image(1).load(0, 0, '{}/anim_test2.png'.format(assets))
        pyxel.image(2).load(0, 0, '{}/bg_test2.png'.format(assets))

        self.player = Player()

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_A):
            self.player.run(-1)
        if pyxel.btn(pyxel.KEY_D):
            self.player.run(1)
        if pyxel.btnp(pyxel.KEY_S, 30, 30):
            self.player.charge()
        if pyxel.btn(pyxel.KEY_SPACE):
            if self.player.grounded:
                self.player.jump()
        if pyxel.btn(pyxel.KEY_ESCAPE):
            pyxel.quit()
        if pyxel.btn(pyxel.KEY_T):
            pyxel.pal(1, 7)
        else:
            pyxel.pal()
        if pyxel.btn(pyxel.KEY_P):
            import pdb; pdb.set_trace()

        self.update_player()

    def draw(self):
        pyxel.cls(1)
        pyxel.blt(0, 0, 2, 0, 0, 240, 100, 1)
        self.level.render(self.offset_x, self.offset_y, self.level.background, 1, self.height_in_tiles, self.width_in_tiles)
        self.level.render(self.offset_x, self.offset_y, self.level.collision, 1, self.height_in_tiles, self.width_in_tiles)
        self.player.render()
        self.level.render(self.offset_x, self.offset_y, self.level.foreground, 1, self.height_in_tiles, self.width_in_tiles)

    def update_player(self):
        if self.player.vx < 0:
            if self.offset_x < abs(self.player.vx):
                self.offset_x = 0
                self.player.x += self.player.vx
            elif self.offset_x > 0 and self.player.x < pyxel.width // 2:
                self.offset_x += self.player.vx
            else:
                self.player.x += self.player.vx
        elif self.player.vx > 0:
            # TODO: make this offset condition dynamic based on tilemap size
            if self.offset_x < 320 and self.player.x > pyxel.width // 2:
                self.offset_x += self.player.vx
            else:
                self.player.x += self.player.vx
        self.player.x_collision(self.offset_x, self.offset_y, self.level.collision.matrix, self.level.tile_size)

        if self.player.vx > 0:
            self.player.vx = self.player.vx - 1
        elif self.player.vx < 0:
            self.player.vx = self.player.vx + 1

        if self.player.vy < 0:
            if self.offset_y < abs(self.player.vy):
                self.offset_y = 0
                self.player.y += self.player.vy
            elif self.offset_y > 0 and self.player.y < pyxel.height // 2:
                self.offset_y += self.player.vy
            else:
                self.player.y += self.player.vy
        elif self.player.vy > 0:
            # TODO: make this offset condition dynamic based on tilemap size
            if self.offset_y < 80 and self.player.y > pyxel.height // 2:
                self.offset_y += self.player.vy
            else:
                self.player.y += self.player.vy
        self.player.y_collision(self.offset_x, self.offset_y, self.level.collision.matrix, self.level.tile_size)

        self.player.vy = min(self.player.vy + 1, 7)


App()
