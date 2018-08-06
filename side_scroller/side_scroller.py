import pyxel

from itertools import islice
from tilemap import Tilemap


class App:
    def __init__(self):
        pyxel.init(241, 160, caption='test game')
        pyxel.image(0).load(0, 0, 'assets/tile_test2.png')
        pyxel.image(1).load(0, 0, 'assets/anim_test2.png')

        self.tile_size = 16
        self.tilemap = Tilemap(self.build_tilemap('assets/map_test2.txt', 'layer 0'))
        self.tilemap1 = Tilemap(self.build_tilemap('assets/map_test2.txt', 'layer 1'), True)
        self.tilemap2 = Tilemap(self.build_tilemap('assets/map_test2.txt', 'layer 2'), True)

        self.player_h = 11
        self.player_w = 8

        self.player_x = 72
        self.player_y = -16
        self.player_vx = 0
        self.player_vy = 0
        self.grounded = False

        self.zero_frame = 0

        pyxel.run(self.update, self.draw)

    def build_tilemap(self, map_file, layer):
        l_num = pyxel.height // self.tile_size
        with open(map_file, 'r') as data:
            for line in data:
                if layer in line.strip():
                    return [[int(x) for x in l.strip().rstrip(',').split(',')] for l in islice(data, l_num)] # pylint: disable=C0301
        return False

    def player_jump(self):
        self.player_vy = -10
        self.grounded = False

    def player_run(self, m):
        self.player_vx = 2 * m
        if m == -1:
            self.player_x = max(self.player_x + self.player_vx, 0)
        else:
            self.player_x = min(self.player_x + self.player_vx, pyxel.width - self.player_w)

    def update_player(self):
        if pyxel.btn(pyxel.KEY_A):
            self.player_run(-1)
        if pyxel.btn(pyxel.KEY_D):
            self.player_run(1)
        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.grounded:
                self.player_jump()

        self.player_y += self.player_vy
        self.player_vy = min(self.player_vy + 1, 8)

        self.check_collision()

    def check_collision(self):
        # player coordinates are base 0, so the distance right and down from the 0th element
        # of the player sprite has to be decremented by 1
        player_bottom = self.player_y + self.player_h - 1
        player_right = self.player_x + self.player_w - 1

        if self.player_vx < 0:
            for coord in [self.player_x, self.player_y], [self.player_x, player_bottom]:
                left_tile = [
                    (coord[0] + self.player_vx) // self.tile_size,
                    coord[1] // self.tile_size
                ]
                if self.tilemap.matrix[left_tile[1]][left_tile[0]] != -1:
                    self.player_x = (left_tile[0] * self.tile_size) + self.tile_size

        elif self.player_vx > 0:
            for coord in [player_right, self.player_y], [player_right, player_bottom]:
                right_tile = [
                    (coord[0] + self.player_vx) // self.tile_size,
                    coord[1] // self.tile_size
                ]
                if self.tilemap.matrix[right_tile[1]][right_tile[0]] != -1:
                    self.player_x = (right_tile[0] * self.tile_size) - self.player_w

        player_bottom = self.player_y + self.player_h - 1
        player_right = self.player_x + self.player_w - 1

        if self.player_y >= 0 and self.player_vy > 0:
            for coord in [self.player_x, player_bottom], [player_right, player_bottom]:
                floor_tile = [
                    coord[0] // self.tile_size,
                    (coord[1] + self.player_vy) // self.tile_size
                ]
                if self.tilemap.matrix[floor_tile[1]][floor_tile[0]] != -1:
                    self.player_vy = 0
                    self.player_y = (floor_tile[1] * self.tile_size) - self.player_h
                    self.grounded = True
                    break
                else:
                    self.grounded = False

        elif self.player_y >= 0 and self.player_vy < 0:
            for coord in [self.player_x, self.player_y], [player_right, self.player_y]:
                ceiling_tile = [
                    coord[0] // self.tile_size,
                    (coord[1] + self.player_vy) // self.tile_size
                ]
                if self.tilemap.matrix[ceiling_tile[1]][ceiling_tile[0]] != -1:
                    self.player_vy = 0
                    self.player_y = ceiling_tile[1] * self.tile_size + self.tile_size
                    break

    def render_tiles(self, tilemap, colkey):
        # render the tileset based on information in the tilemap and tileset files loaded on boot.
        for idy, arr in enumerate(tilemap.matrix):
            for idx, val in enumerate(arr):
                if val != -1:
                    tile_x = idx*self.tile_size
                    tile_y = idy*self.tile_size
                    sx = (val % self.tile_size) * self.tile_size
                    sy = (val // (256 // self.tile_size)) * self.tile_size
                    pyxel.blt(tile_x, tile_y, 0, sx, sy, self.tile_size, self.tile_size, colkey)

    def render_player(self):
        frame_w = 11
        frame_x = frame_w * 7
        if not self.grounded:
            if self.player_vy >= 0:
                frame_x = frame_w * 13
            else:
                frame_x = frame_w * 12
        else:
            if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_D):
                if pyxel.btnp(pyxel.KEY_A) or pyxel.btnp(pyxel.KEY_D):
                    self.zero_frame = pyxel.frame_count
                frame_x = frame_w * (((pyxel.frame_count - self.zero_frame) // 4) % 6)
        if self.player_vx > 0:
            otn = -1
        else:
            otn = 1

        pyxel.blt(
            self.player_x-(2*otn),
            self.player_y-5, 1, frame_x, 16,
            otn*self.player_w+(3*otn),
            self.player_h+5, 1
        )

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        self.update_player()

    def draw(self):
        pyxel.cls(1)
        self.render_tiles(self.tilemap, 1)
        self.render_tiles(self.tilemap2, 1)
        self.render_player()
        self.render_tiles(self.tilemap1, 1)


App()
