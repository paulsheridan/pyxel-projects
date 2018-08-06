import pyxel

from itertools import islice


class App:
    def __init__(self):
        pyxel.init(241, 160, caption='test game')
        pyxel.image(0).load(0, 0, 'assets/tile_test2.png')
        pyxel.image(1).load(0, 0, 'assets/anim_test2.png')
        pyxel.image(2).load(0, 0, 'assets/bg_test2.png')

        self.tile_size = 16
        self.tilemap = Tilemap(self.build_tilemap('assets/map_test2.txt', 'layer 0'))
        self.tilemap1 = Tilemap(self.build_tilemap('assets/map_test2.txt', 'layer 1'), True)
        self.tilemap2 = Tilemap(self.build_tilemap('assets/map_test2.txt', 'layer 2'), True)

        self.player = Player()

        self.anim_w = 11
        self.zero_frame = 0

        pyxel.run(self.update, self.draw)

    def build_tilemap(self, map_file, layer):
        l_num = pyxel.height // self.tile_size
        with open(map_file, 'r') as data:
            for line in data:
                if layer in line.strip():
                    return [[int(x) for x in l.strip().rstrip(',').split(',')] for l in islice(data, l_num)] # pylint: disable=C0301
        return False

    def update_player(self):
        if pyxel.btn(pyxel.KEY_A):
            self.player.run(-1)
        if pyxel.btn(pyxel.KEY_D):
            self.player.run(1)
        # if pyxel.btn(pyxel.KEY_W):
        #     pass
        # if pyxel.btn(pyxel.KEY_S):
        #     pass
        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.player.grounded:
                self.player.jump()

        self.player.y_pos += self.player.y_vel
        self.player.y_vel = min(self.player.y_vel + 1, 8)

        self.check_collision()

    def check_collision(self):
        # player coordinates are base 0, so the distance right and down from the 0th element
        # of the player sprite has to be decremented by 1
        player_bottom = self.player.y_pos + self.player.height - 1
        player_right = self.player.x_pos + self.player.width - 1

        if self.player.x_vel < 0:
            for coord in [self.player.x_pos, self.player.y_pos], [self.player.x_pos, player_bottom]:
                left_tile = [
                    (coord[0] + self.player.x_vel) // self.tile_size,
                    coord[1] // self.tile_size
                ]
                if self.tilemap.matrix[left_tile[1]][left_tile[0]] != -1:
                    self.player.x_pos = (left_tile[0] * self.tile_size) + self.tile_size

        elif self.player.x_vel > 0:
            for coord in [player_right, self.player.y_pos], [player_right, player_bottom]:
                right_tile = [
                    (coord[0] + self.player.x_vel) // self.tile_size,
                    coord[1] // self.tile_size
                ]
                if self.tilemap.matrix[right_tile[1]][right_tile[0]] != -1:
                    self.player.x_pos = (right_tile[0] * self.tile_size) - self.player.width

        player_bottom = self.player.y_pos + self.player.height - 1
        player_right = self.player.x_pos + self.player.width - 1

        if self.player.y_pos >= 0 and self.player.y_vel > 0:
            for coord in [self.player.x_pos, player_bottom], [player_right, player_bottom]:
                floor_tile = [
                    coord[0] // self.tile_size,
                    (coord[1] + self.player.y_vel) // self.tile_size
                ]
                if self.tilemap.matrix[floor_tile[1]][floor_tile[0]] != -1:
                    self.player.y_vel = 0
                    self.player.y_pos = (floor_tile[1] * self.tile_size) - self.player.height
                    self.player.grounded = True
                    break
                else:
                    self.player.grounded = False

        elif self.player.y_pos >= 0 and self.player.y_vel < 0:
            for coord in [self.player.x_pos, self.player.y_pos], [player_right, self.player.y_pos]:
                ceiling_tile = [
                    coord[0] // self.tile_size,
                    (coord[1] + self.player.y_vel) // self.tile_size
                ]
                if self.tilemap.matrix[ceiling_tile[1]][ceiling_tile[0]] != -1:
                    self.player.y_vel = 0
                    self.player.y_pos = ceiling_tile[1] * self.tile_size + self.tile_size
                    break

    def render_tiles(self, tilemap, colkey):
        # render the tileset based on information in the tilemap and tileset files loaded on boot.
        for idy, arr in enumerate(tilemap.matrix):
            for idx, val in enumerate(arr):
                if val != -1:
                    x = idx*self.tile_size
                    y = idy*self.tile_size
                    sx = (val % self.tile_size) * self.tile_size
                    sy = (val // (256 // self.tile_size)) * self.tile_size
                    pyxel.blt(x, y, 0, sx, sy, self.tile_size, self.tile_size, colkey)

    def render_player(self):
        frame_x = self.anim_w * 7
        if not self.player.grounded:
            if self.player.y_vel >= 0:
                frame_x = self.anim_w * 13
            else:
                frame_x = self.anim_w * 12
        else:
            if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_D):
                if pyxel.btnp(pyxel.KEY_A) or pyxel.btnp(pyxel.KEY_D):
                    self.zero_frame = pyxel.frame_count
                frame_x = self.anim_w * (((pyxel.frame_count - self.zero_frame) // 4) % 6)
        if self.player.x_vel > 0:
            otn = -1
        else:
            otn = 1

        pyxel.blt(
            self.player.x_pos-(2*otn),
            self.player.y_pos-5, 1, frame_x, 16,
            otn*self.player.width+(3*otn),
            self.player.height+5, 1
        )

    def update(self):
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()

        self.update_player()

    def draw(self):
        pyxel.cls(1)
        pyxel.blt(0, 0, 2, 0, 0, 240, 100, 1)
        self.render_tiles(self.tilemap, 1)
        self.render_tiles(self.tilemap2, 1)
        self.render_player()
        self.render_tiles(self.tilemap1, 1)


class Player():
    def __init__(self):
        self.height = 11
        self.width = 8

        self.x_pos = 72
        self.y_pos = -16
        self.x_vel = 0
        self.y_vel = 0
        self.grounded = False


    def jump(self):
        self.y_vel = -10
        self.grounded = False

    def run(self, m):
        self.x_vel = 2 * m
        if m == -1:
            self.x_pos = max(self.x_pos + self.x_vel, 0)
        else:
            self.x_pos = min(self.x_pos + self.x_vel, pyxel.width - self.width)


class Tilemap():
    def __init__(self, matrix, mutable=False):
        self.matrix = matrix
        self.mutable = mutable

    def update_tile(self, x, y, val):
        if self.mutable:
            self.matrix[x][y] = val


App()
