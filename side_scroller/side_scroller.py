import os
import pyxel

from itertools import islice


class App:
    def __init__(self):
        pyxel.init(240, 160, caption='test game')

        self.tile_size = 16
        self.offset = 0
        self.map_height = pyxel.height // self.tile_size

        assets = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'assets'))
        pyxel.image(0).load(0, 0, '{}/tile_test2.png'.format(assets))
        pyxel.image(1).load(0, 0, '{}/anim_test2.png'.format(assets))
        pyxel.image(2).load(0, 0, '{}/bg_test2.png'.format(assets))

        self.tilemap = Tilemap(self.build_tilemap('{}/map_test2.txt'.format(assets), 'collision'))
        self.tilemap1 = Tilemap(self.build_tilemap('{}/map_test2.txt'.format(assets), 'foreground'), True)
        self.tilemap2 = Tilemap(self.build_tilemap('{}/map_test2.txt'.format(assets), 'background'), True)

        self.player = Player()

        pyxel.run(self.update, self.draw)

    def build_tilemap(self, map_file, layer):
        with open(map_file, 'r') as data:
            for line in data:
                if layer in line.strip():
                    return [[int(x) for x in l.strip().rstrip(',').split(',')]for l in islice(data, self.map_height)]
        raise IndexError("Tilemap layer {} not found.  Please check tilemap file.".format(layer))

    def set_coll_defaults(self):
        # player coordinates are base 0, so the distance right and down from the 0th element
        # of the player sprite has to be decremented by 1
        player_bottom = self.player.y + self.player.height - 1
        player_right = self.player.x + self.offset + self.player.width - 1
        player_left = self.player.x + self.offset
        return player_bottom, player_right, player_left

    def x_collision(self):
        player_bottom, player_right, player_left = self.set_coll_defaults()

        if self.player.vx < 0:
            for coord in [player_left, self.player.y], [player_left, player_bottom]:
                left_tile = [
                    (coord[0] + self.player.vx) // self.tile_size,
                    coord[1] // self.tile_size
                ]
                if self.tilemap.matrix[left_tile[1]][left_tile[0]] != -1:
                    self.player.x = (left_tile[0] * self.tile_size) + self.tile_size - self.offset
                    break

        elif self.player.vx > 0:
            for coord in [player_right, self.player.y], [player_right, player_bottom]:
                right_tile = [
                    (coord[0] + self.player.vx) // self.tile_size,
                    coord[1] // self.tile_size
                ]
                if self.tilemap.matrix[right_tile[1]][right_tile[0]] != -1:
                    self.player.x = (right_tile[0] * self.tile_size) - self.player.width - self.offset
                    break

    def y_collision(self):
        player_bottom, player_right, player_left = self.set_coll_defaults()

        if self.player.y >= 0 and self.player.vy > 0:
            for coord in [player_left, player_bottom], [player_right, player_bottom]:
                floor_tile = [
                    coord[0] // self.tile_size,
                    (coord[1] + self.player.vy) // self.tile_size
                ]
                if self.tilemap.matrix[floor_tile[1]][floor_tile[0]] != -1:
                    self.player.vy = 0
                    self.player.y = (floor_tile[1] * self.tile_size) - self.player.height
                    self.player.grounded = True
                    break
                else:
                    self.player.grounded = False

        elif self.player.y >= 0 and self.player.vy < 0:
            for coord in [player_left, self.player.y], [player_right, self.player.y]:
                ceiling_tile = [
                    coord[0] // self.tile_size,
                    (coord[1] + self.player.vy) // self.tile_size
                ]
                if self.tilemap.matrix[ceiling_tile[1]][ceiling_tile[0]] != -1:
                    self.player.vy = 0
                    self.player.y = ceiling_tile[1] * self.tile_size + self.tile_size
                    break

    def render_tiles(self, tilemap, colkey):
        # render the tileset based on self.tilemap's matrix.
        base_offset = self.offset // self.tile_size
        mod_offset = self.offset % self.tile_size
        for idy, arr in enumerate(tilemap.matrix):
            for idx, val in enumerate(arr[base_offset:base_offset+16]):
                if val != -1:
                    x = idx*self.tile_size
                    y = idy*self.tile_size
                    sx = (val % self.tile_size) * self.tile_size
                    sy = (val // (256 // self.tile_size)) * self.tile_size
                    pyxel.blt(x-mod_offset, y, 0, sx, sy, self.tile_size, self.tile_size, colkey)

    def update(self):
        if pyxel.btn(pyxel.KEY_A):
            if self.offset > 0 and self.player.x < pyxel.width // 2:
                self.offset += self.player.vx
            else:
                self.player.run(-1)
        if pyxel.btn(pyxel.KEY_D):
            if self.offset < pyxel.width and self.player.x > pyxel.width // 2:
                self.offset += self.player.vx
            else:
                self.player.run(1)
        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.player.grounded:
                self.player.jump()
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_P):
            import pdb; pdb.set_trace()

        self.player.y += self.player.vy
        self.player.vy = min(self.player.vy + 1, 8)

        self.x_collision()
        self.y_collision()

    def draw(self):
        pyxel.cls(1)
        pyxel.blt(0, 0, 2, 0, 0, 240, 100, 1)
        self.render_tiles(self.tilemap2, 1)
        self.player.render()
        self.render_tiles(self.tilemap1, 1)
        self.render_tiles(self.tilemap, 1)


class Player():
    def __init__(self):
        self.height = 11
        self.width = 8

        self.x = 72
        self.y = -16
        self.vx = 0
        self.vy = 0
        self.grounded = False

        self.anim_w = 11
        self.zero_frame = 0

    def jump(self):
        self.vy = -8
        self.grounded = False

    def run(self, m):
        self.vx = 2 * m
        if m == -1:
            self.x = max(self.x + self.vx, 0)
        else:
            self.x = min(self.x + self.vx, pyxel.width - self.width - 6)

    def render(self):
        frame_x = self.anim_w * 7
        if not self.grounded:
            if self.vy >= 0:
                frame_x = self.anim_w * 13
            else:
                frame_x = self.anim_w * 12
        else:
            if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_D):
                if pyxel.btnp(pyxel.KEY_A) or pyxel.btnp(pyxel.KEY_D):
                    self.zero_frame = pyxel.frame_count
                frame_x = self.anim_w * (((pyxel.frame_count - self.zero_frame) // 4) % 6)
            else:
                if pyxel.btnr(pyxel.KEY_A) or pyxel.btnr(pyxel.KEY_D):
                    self.zero_frame = pyxel.frame_count
                frame_x = self.anim_w * (6 + ((pyxel.frame_count - self.zero_frame) // 4) % 6)
        if self.vx > 0:
            otn = -1
        else:
            otn = 1

        pyxel.blt(self.x-(1), self.y-5, 1, frame_x, 16, otn*self.width+(3*otn), self.height+5, 1)
        # pyxel.rectb(self.x, self.y, self.x + self.width, self.y + self.height, 7)


class Tilemap():
    def __init__(self, matrix, mutable=False):
        self.matrix = matrix
        self.mutable = mutable

    def update_tile(self, x, y, val):
        if self.mutable:
            self.matrix[x][y] = val


App()
