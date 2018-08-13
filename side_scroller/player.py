import pyxel

from random import randint
from particle_emitter import ParticleEmitter


class Player():
    def __init__(self):
        self.height = 11
        self.width = 8

        self.test_left = 0
        self.test_right = 0
        self.test_up = 0
        self.test_down = 0

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
        self.jump_charge_emitter.render_particles()

        # TODO: make the rendering offset between player collision box
        # and the image blt dynamic based on frame size and hit box size
        pyxel.blt(self.x-1, self.y-5, 1, frame_x, 16, -self.direction*self.width+(3*-self.direction), self.height+5, 1)
        # pyxel.rectb(self.test_left, self.test_up, self.test_right, self.test_down, 7)
