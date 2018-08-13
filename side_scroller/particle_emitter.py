import pyxel

from random import randint


class ParticleEmitter():
    def __init__(self, x, y, on=False):
        self.on = on
        self.x = x
        self.y = y
        self.spawn_area = 8, 12
        self.particles = []

    def update_position(self, x, y):
        self.x = x
        self.y = y

    def sparkle(self, v):
        if pyxel.frame_count % 2 == 0:
            self.particles.append({
                'end_frame': pyxel.frame_count + 20,
                'x': randint(self.x, self.x+self.spawn_area[0]),
                'y': randint(self.y-2, self.y+self.spawn_area[1]),
                'color': randint(8, 14),
                'v': v
            })

    def render_particles(self):
        for idx, particle in enumerate(self.particles):
            if particle['end_frame'] <= pyxel.frame_count:
                del self.particles[idx]
            else:
                particle['x'] -= particle['v']
            pyxel.pix(particle['x'], particle['y'], particle['color'])
