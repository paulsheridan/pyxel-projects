import pyxel

from random import randint
from particle_emitter import ParticleEmitter


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
        self.jump_chg = 0

        self.anim_w = 11
        self.anim_zero_frame = 0

        self.jump_charge_emitter = ParticleEmitter(self.x, self.y)

    def charge(self):
        self.jump_chg = min(self.jump_chg + 1, 6)

    def jump(self):
        self.vy = -self.jump_chg - 8
        self.grounded = False
        self.jump_chg = 0

    def run(self, direction):
        self.direction = direction
        self.vx = 2 * direction

    def set_test(self, left, up, right, down):
        self.test_left = left
        self.test_right = right
        self.test_up = up
        self.test_down = down


    def set_coll_defaults(self, offset_x, offset_y):
        # player coordinates are base 0, so the distance right and down from the 0th element
        # of the player sprite has to be decremented by 1
        player_top = self.y + offset_y
        player_bottom = self.y + offset_y + self.height - 1
        player_right = self.x + offset_x + self.width - 1
        player_left = self.x + offset_x
        return player_top, player_bottom, player_right, player_left

    def x_collision(self, offset_x, offset_y, coll_matrix, tile_size):
        player_top, player_bottom, player_right, player_left = self.set_coll_defaults(offset_x, offset_y)

        if self.vx < 0:
            for coord in [player_left, player_top], [player_left, player_bottom]:
                left_tile = [
                    (coord[0] + self.vx) // tile_size,
                    coord[1] // tile_size
                ]
                if coll_matrix[left_tile[1]][left_tile[0]] != -1:
                    self.x = (left_tile[0] * tile_size) + tile_size - offset_x
                    break

        if self.vx > 0:
            for coord in [player_right, player_top], [player_right, player_bottom]:
                right_tile = [
                    (coord[0] + self.vx) // tile_size,
                    coord[1] // tile_size
                ]
                if coll_matrix[right_tile[1]][right_tile[0]] != -1:
                    self.x = (right_tile[0] * tile_size) - self.width - offset_x
                    break

    def y_collision(self, offset_x, offset_y, coll_matrix, tile_size):
        player_top, player_bottom, player_right, player_left = self.set_coll_defaults(offset_x, offset_y)

        if self.y >= 0 and self.vy > 0:
            for coord in [player_left, player_bottom], [player_right, player_bottom]:
                floor_tile = [
                    coord[0] // tile_size,
                    (coord[1] + self.vy) // tile_size
                ]
                if coll_matrix[floor_tile[1]][floor_tile[0]] != -1:
                    self.vy = 0
                    self.y = (floor_tile[1] * tile_size) - self.height - offset_y
                    self.grounded = True
                    break
                else:
                    self.grounded = False

        elif self.y >= 0 and self.vy < 0:
            for coord in [player_left, player_top], [player_right, player_top]:
                ceiling_tile = [
                    coord[0] // tile_size,
                    (coord[1] + self.vy) // tile_size
                ]
                if coll_matrix[ceiling_tile[1]][ceiling_tile[0]] != -1:
                    self.vy = 0
                    self.y = ceiling_tile[1] * tile_size + tile_size - offset_y
                    break

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
                    self.anim_zero_frame = pyxel.frame_count
                frame_x = self.anim_w * (((pyxel.frame_count - self.anim_zero_frame) // 4) % 6)
            else:
                if pyxel.btnr(pyxel.KEY_A) or pyxel.btnr(pyxel.KEY_D):
                    self.anim_zero_frame = pyxel.frame_count
                frame_x = self.anim_w * (6 + ((pyxel.frame_count - self.anim_zero_frame) // 4) % 6)
        self.jump_charge_emitter.update_position(self.x, self.y)
        if self.jump_chg > 5:
            self.jump_charge_emitter.sparkle(-4)
        self.jump_charge_emitter.render_particles()

        # TODO: make the rendering offset between player collision box
        # and the image blt dynamic based on frame size and hit box size
        pyxel.blt(self.x-1, self.y-5, 1, frame_x, 16, -self.direction*self.width+(3*-self.direction), self.height+5, 1)
