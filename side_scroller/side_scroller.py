import os
import pyxel

from itertools import islice


class App:
    def __init__(self):
        pyxel.init(240, 160, caption='test game')

        self.tile_size = 16
        self.offset_x = 0
        self.offset_y = 0
        self.map_height = pyxel.height // self.tile_size
        self.map_width = pyxel.width // self.tile_size

        assets = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'assets'))
        pyxel.image(0).load(0, 0, '{}/tile_test2.png'.format(assets))
        pyxel.image(1).load(0, 0, '{}/anim_test2.png'.format(assets))
        pyxel.image(2).load(0, 0, '{}/bg_test2.png'.format(assets))

        self.tilemap = Tilemap(self.build_tilemap('{}/map_test2.txt'.format(assets), 'layer 1'))
        self.tilemap1 = Tilemap(self.build_tilemap('{}/map_test2.txt'.format(assets), 'layer 2'), True)
        self.tilemap2 = Tilemap(self.build_tilemap('{}/map_test2.txt'.format(assets), 'layer 0'), True)

        self.player = Player()

        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btn(pyxel.KEY_A):
            self.player.run(-1)
        if pyxel.btn(pyxel.KEY_D):
            self.player.run(1)
        if pyxel.btnp(pyxel.KEY_SPACE):
            if self.player.grounded:
                self.player.jump()
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            pyxel.quit()
        if pyxel.btn(pyxel.KEY_T):
            pyxel.pal(1, 7)
        else:
            pyxel.pal()
        if pyxel.btnp(pyxel.KEY_P):
            import pdb; pdb.set_trace()

        self.x_collision()
        self.y_collision()

        self.update_player()

    def draw(self):
        pyxel.cls(1)
        pyxel.blt(0, 0, 2, 0, 0, 240, 100, 1)
        self.render_tiles(self.tilemap2, 1)
        self.player.render()
        self.render_tiles(self.tilemap1, 1)
        self.render_tiles(self.tilemap, 1)
        # pyxel.line(0, 0, pyxel.width, pyxel.height, 7)

    def build_tilemap(self, map_file, layer):
        matrix = []
        with open(map_file, 'r') as data:
            for line in data:
                if layer in line:
                    break
            for line_after in data:
                if not line_after.strip():
                    break
                else:
                    matrix.append([int(x) for x in line_after.strip().rstrip(',').split(',')])
        return matrix


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
                    (coord[0] + self.player.vx) // self.tile_size,
                    coord[1] // self.tile_size
                ]
                if self.tilemap.matrix[left_tile[1]][left_tile[0]] != -1:
                    self.player.x = (left_tile[0] * self.tile_size) + self.tile_size - self.offset_x - 1
                    break

        elif self.player.vx > 0:
            for coord in [player_right, player_top], [player_right, player_bottom]:
                right_tile = [
                    (coord[0] + self.player.vx) // self.tile_size,
                    coord[1] // self.tile_size
                ]
                if self.tilemap.matrix[right_tile[1]][right_tile[0]] != -1:
                    self.player.x = (right_tile[0] * self.tile_size) - self.player.width - self.offset_x + 1
                    break

    def y_collision(self):
        player_top, player_bottom, player_right, player_left = self.set_coll_defaults()

        if self.player.y >= 0 and self.player.vy > 0:
            for coord in [player_left, player_bottom], [player_right, player_bottom]:
                floor_tile = [
                    coord[0] // self.tile_size,
                    (coord[1] + self.player.vy) // self.tile_size
                ]
                if self.tilemap.matrix[floor_tile[1]][floor_tile[0]] != -1:
                    self.player.vy = 0
                    self.player.y = (floor_tile[1] * self.tile_size) - self.player.height - self.offset_y
                    self.player.grounded = True
                    break
                else:
                    self.player.grounded = False

        elif self.player.y >= 0 and self.player.vy < 0:
            for coord in [player_left, player_top], [player_right, player_top]:
                ceiling_tile = [
                    coord[0] // self.tile_size,
                    (coord[1] + self.player.vy) // self.tile_size
                ]
                if self.tilemap.matrix[ceiling_tile[1]][ceiling_tile[0]] != -1:
                    self.player.vy = 0
                    self.player.y = ceiling_tile[1] * self.tile_size + self.tile_size - self.offset_y
                    break

    def render_tiles(self, tilemap, colkey):
        # render the tileset based on self.tilemap's matrix.
        base_offset_x = self.offset_x // self.tile_size
        mod_offset_x = self.offset_x % self.tile_size
        base_offset_y = self.offset_y // self.tile_size
        mod_offset_y = self.offset_y % self.tile_size
        for idy, arr in enumerate(tilemap.matrix[base_offset_y:base_offset_y+self.map_height+1]):
            for idx, val in enumerate(arr[base_offset_x:base_offset_x+self.map_width+1]):
                if val != -1:
                    x = idx*self.tile_size
                    y = idy*self.tile_size
                    sx = (val % self.tile_size) * self.tile_size
                    sy = (val // (256 // self.tile_size)) * self.tile_size
                    pyxel.blt(x-mod_offset_x, y-mod_offset_y, 0, sx, sy, self.tile_size, self.tile_size, colkey)

    def update_player(self):
        if self.player.vx < 0:
            if self.offset_x > 0 and self.player.x < pyxel.width // 2:
                self.offset_x += self.player.vx
            else:
                self.player.x += self.player.vx
        elif self.player.vx > 0:
            if self.offset_x < pyxel.width and self.player.x > pyxel.width // 2:
                self.offset_x += self.player.vx
            else:
                self.player.x += self.player.vx
        self.player.vx = 0

        if self.player.vy < 0:
            if self.offset_y < abs(self.player.vy):
                self.offset_y = 0
                self.player.y += self.player.vy
            elif self.offset_y > 0 and self.player.y < pyxel.height // 2:
                self.offset_y += self.player.vy
            else:
                self.player.y += self.player.vy
        elif self.player.vy > 0:
            if self.offset_y < 80 and self.player.y > pyxel.height // 2:
                self.offset_y += self.player.vy
            else:
                self.player.y += self.player.vy

        self.player.vy = min(self.player.vy + 1, 8)


class Player():
    def __init__(self):
        self.height = 11
        self.width = 8

        self.x = 72
        self.y = -16
        self.vx = 0
        self.vy = 0
        self.grounded = False
        self.direction = 1

        self.anim_w = 11
        self.zero_frame = 0

    def jump(self):
        self.vy = -10
        self.grounded = False

    def run(self, direction):
        self.direction = direction
        self.vx = 2 * direction

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

        pyxel.blt(self.x-1, self.y-5, 1, frame_x, 16, -self.direction*self.width+(3*-self.direction), self.height+5, 1)
        pyxel.rectb(self.x, self.y, self.x + self.width - 1, self.y + self.height - 1, 7)


class Tilemap():
    def __init__(self, matrix, mutable=False):
        self.matrix = matrix
        self.mutable = mutable

    def update_tile(self, x, y, val):
        if self.mutable:
            self.matrix[x][y] = val


App()
