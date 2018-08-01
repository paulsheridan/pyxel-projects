import pyxel

from itertools import islice

from tilemap import Tilemap

def xclamp(n):
    return max(min(224, n), 0)

def yclamp(n):
    return max(min(144, n), 0)

def read_map_lines(map_file, l_num):
    return [[int(x) for x in l.strip().rstrip(',').split(',')] for l in islice(map_file, l_num)]

class App:
    def __init__(self):
        pyxel.init(240, 160, caption='test game')
        pyxel.image(0).load(0, 0, 'tileset.png')

        self.tile_size = 16
        self.tilemap0 = Tilemap(self.build_tilemap('tileset.txt', 'layer 0'))
        self.tilemap1 = Tilemap(self.build_tilemap('tileset.txt', 'layer 1'), True)

        self.player_x = 72
        self.player_y = -16
        self.player_vy = 0
        self.player_is_alive = True

        # first number is the height (0 is empty) second number is type of block
        # self.floor = [(1, 6), (2, 7), (0, 3), (2, 9),
        #               (2, 1), (2, 3), (1, 1), (1, 1),
        #               (0, 4), (0, 3), (1, 6), (2, 7),
        #               (0, 3), (2, 9), (1, 6), (2, 7)]

        pyxel.run(self.update, self.draw)

    def build_tilemap(self, map_file, layer):
        l_num = pyxel.height // self.tile_size
        with open(map_file, 'r') as data:
            for line in data:
                if layer in line.strip():
                    return [[int(x) for x in l.strip().rstrip(',').split(',')] for l in islice(data, l_num)] # pylint: disable=C0301
        return False

    def update_player(self):
        if pyxel.btn(pyxel.KEY_LEFT):
            self.player_x = max(self.player_x - 2, 0)
        if pyxel.btn(pyxel.KEY_RIGHT):
            self.player_x = min(self.player_x + 2, pyxel.width - 16)
        if pyxel.btn(pyxel.KEY_SPACE):
            self.player_jump()

        self.player_y += self.player_vy
        self.player_vy = min(self.player_vy + 1, 8)

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        self.update_player()

    def draw(self):
        pyxel.cls(12)
        # for idx, val in enumerate(self.current_floor()):
        #     pyxel.rect(idx*16, pyxel.height - val[0]*16, idx*16+15, pyxel.height, val[1])
        pyxel.blt(self.player_x, self.player_y, 0, 0, 0
                  if self.player_vy > 0 else 0, 16, 16, 5)
        pyxel.text(32, 4, 'X: {}'.format(self.player_x), 1)
        pyxel.text(4, 4, 'Y: {}'.format(self.player_y), 7)

    def player_jump(self):
        self.player_vy = min(self.player_vy, -8)

    # def current_floor(self):
    #     return self.floor


App()
