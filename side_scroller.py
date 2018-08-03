import pyxel

from itertools import islice
from tilemap import Tilemap


class App:
    def __init__(self):
        pyxel.init(241, 160, caption='test game')
        pyxel.image(0).load(0, 0, 'assets/tileset.png')
        pyxel.image(1).load(0, 0, 'assets/alien.png')

        self.tile_size = 16
        self.tilemap = Tilemap(self.build_tilemap('assets/mapfile.txt', 'layer 0'))
        # self.tilemap1 = Tilemap(self.build_tilemap('tileset.txt', 'layer 1'), True)

        self.player_h = 12
        self.player_w = 8
        self.player_x = 72
        self.player_y = -16
        self.player_vy = 0
        self.grounded = False

        pyxel.run(self.update, self.draw)

    def build_tilemap(self, map_file, layer):
        l_num = pyxel.height // self.tile_size
        with open(map_file, 'r') as data:
            for line in data:
                if layer in line.strip():
                    return [[int(x) for x in l.strip().rstrip(',').split(',')] for l in islice(data, l_num)] # pylint: disable=C0301
        return False

    def player_jump(self):
        self.player_vy = min(self.player_vy, -10)
        self.grounded = False

    def player_run(self):
        pass

    def update_player(self):
        if pyxel.btn(pyxel.KEY_A):
            self.player_x = max(self.player_x - 2, 0)
        if pyxel.btn(pyxel.KEY_D):
            self.player_x = min(self.player_x + 2, pyxel.width - 16)
        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.grounded:
                self.player_jump()

        self.player_y += self.player_vy
        self.player_vy = min(self.player_vy + 1, 8)

        self.check_collision()

    def check_collision(self):
        player_bottom = self.player_y + self.player_h
        player_right = self.player_x + self.player_w

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
                ceiling_tile = [coord[0] // self.tile_size, (coord[1] - self.player_vy) // self.tile_size] # pylint: disable=C0301
                if self.tilemap.matrix[ceiling_tile[1]][ceiling_tile[0]] != -1:
                    # import pdb; pdb.set_trace()
                    self.player_vy = 0
                    self.player_y = ceiling_tile[1] * self.tile_size + self.tile_size
                    break

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        self.update_player()

    def draw(self):
        pyxel.cls(12)
        # render the tileset based on information in the tilemap and tileset files loaded on boot.
        for idy, arr in enumerate(self.tilemap.matrix):
            for idx, val in enumerate(arr):
                if val != -1:
                    x = idx*self.tile_size # pylint: disable=C0103
                    y = idy*self.tile_size # pylint: disable=C0103
                    sx = (val % self.tile_size) * self.tile_size # pylint: disable=C0103
                    sy = (val // (256 // self.tile_size)) * self.tile_size # pylint: disable=C0103
                    pyxel.blt(x, y, 0, sx, sy, self.tile_size, self.tile_size)
        pyxel.blt(self.player_x, self.player_y, 0, 0, 16
                  if self.player_vy > 0 else 32, 8, 12, 5)
        pyxel.text(32, 4, 'X: {}'.format(self.player_x), 0)
        pyxel.text(4, 4, 'Y: {}'.format(self.player_y), 0)
        pyxel.text(64, 4, "tile: {}".format(self.player_x // 16), 0)
        pyxel.text(96, 4, "tile: {}".format(self.player_y // 16), 0)


App()
