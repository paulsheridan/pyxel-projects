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
        self.tile_height = pyxel.height // self.level.tile_size
        self.tile_width = pyxel.width // self.level.tile_size

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
        self.render_tiles(self.level.background, 1)
        self.render_tiles(self.level.collision, 1)
        self.player.render()
        self.render_tiles(self.level.foreground, 1)

    def set_coll_defaults(self):
        # player coordinates are base 0, so the distance right and down from the 0th element
        # of the player sprite has to be decremented by 1
        player_top = self.player.y + self.offset_y
        player_bottom = self.player.y + self.offset_y + self.player.height - 1
        player_right = self.player.x + self.offset_x + self.player.width - 1
        player_left = self.player.x + self.offset_x
        return player_top, player_bottom, player_right, player_left

    def x_collision(self):
        player_top, player_bottom, player_right, player_left = self.set_coll_defaults()

        if self.player.vx < 0:
            for coord in [player_left, player_top], [player_left, player_bottom]:
                left_tile = [
                    (coord[0] + self.player.vx) // self.level.tile_size,
                    coord[1] // self.level.tile_size
                ]
                if self.level.collision.matrix[left_tile[1]][left_tile[0]] != -1:
                    self.player.x = (left_tile[0] * self.level.tile_size) + self.level.tile_size - self.offset_x
                    # self.player.set_test(self.player.x, self.player.y, self.player.x + self.player.width, self.player.y + self.player.height)
                    break

        if self.player.vx > 0:
            for coord in [player_right, player_top], [player_right, player_bottom]:
                right_tile = [
                    (coord[0] + self.player.vx) // self.level.tile_size,
                    coord[1] // self.level.tile_size
                ]
                if self.level.collision.matrix[right_tile[1]][right_tile[0]] != -1:
                    self.player.x = (right_tile[0] * self.level.tile_size) - self.player.width - self.offset_x
                    break

    def y_collision(self):
        player_top, player_bottom, player_right, player_left = self.set_coll_defaults()

        if self.player.y >= 0 and self.player.vy > 0:
            for coord in [player_left, player_bottom], [player_right, player_bottom]:
                floor_tile = [
                    coord[0] // self.level.tile_size,
                    (coord[1] + self.player.vy) // self.level.tile_size
                ]
                if self.level.collision.matrix[floor_tile[1]][floor_tile[0]] != -1:
                    self.player.vy = 0
                    self.player.y = (floor_tile[1] * self.level.tile_size) - self.player.height - self.offset_y
                    self.player.grounded = True
                    # self.player.set_test(self.player.x, self.player.y, self.player.x + self.player.width, self.player.y + self.player.height)
                    break
                else:
                    self.player.grounded = False

        elif self.player.y >= 0 and self.player.vy < 0:
            for coord in [player_left, player_top], [player_right, player_top]:
                ceiling_tile = [
                    coord[0] // self.level.tile_size,
                    (coord[1] + self.player.vy) // self.level.tile_size
                ]
                if self.level.collision.matrix[ceiling_tile[1]][ceiling_tile[0]] != -1:
                    self.player.vy = 0
                    self.player.y = ceiling_tile[1] * self.level.tile_size + self.level.tile_size - self.offset_y
                    break

    def render_tiles(self, tilemap, colkey):
        # render the tileset based on self.level.collision's matrix.
        base_offset_x = self.offset_x // self.level.tile_size
        mod_offset_x = self.offset_x % self.level.tile_size
        base_offset_y = self.offset_y // self.level.tile_size
        mod_offset_y = self.offset_y % self.level.tile_size
        for idy, arr in enumerate(tilemap.matrix[base_offset_y:base_offset_y+self.tile_height+1]):
            for idx, val in enumerate(arr[base_offset_x:base_offset_x+self.tile_width+1]):
                if val != -1:
                    x = idx*self.level.tile_size
                    y = idy*self.level.tile_size
                    sx = (val % self.level.tile_size) * self.level.tile_size
                    sy = (val // (256 // self.level.tile_size)) * self.level.tile_size
                    pyxel.blt(x-mod_offset_x, y-mod_offset_y, 0, sx, sy, self.level.tile_size, self.level.tile_size, colkey)

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
        self.x_collision()
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
        self.y_collision()

        self.player.vy = min(self.player.vy + 1, 7)
        if self.player.jump_chg > 5:
            self.player.jump_charge_emitter.sparkle(-4)


App()
