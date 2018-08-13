import os
import pyxel

from random import randint
from itertools import islice


class Tilemap():
    def __init__(self, matrix, mutable=False):
        self.matrix = matrix
        self.mutable = mutable

    def update_tile(self, x, y, val):
        if self.mutable:
            self.matrix[x][y] = val


class Level():
    def __init__(self, map_file, tile_size):
        assets = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__), 'assets'))
        self.collision = Tilemap(build_tilemap('{}/{}'.format(assets, map_file), 'layer 1'))
        self.foreground = Tilemap(build_tilemap('{}/{}'.format(assets, map_file), 'layer 2'), True)
        self.background = Tilemap(build_tilemap('{}/{}'.format(assets, map_file), 'layer 0'), True)
        self.tile_size = tile_size
        self.map_width = len(self.collision.matrix[0])
        self.map_height = len(self.collision.matrix)

        # TODO: Create one more layer for spawns and checkpoints, then read those into memory and set
        # spawn and checkpoints for the player.

    def render(self, offset_x, offset_y, tilemap, colkey, height_in_tiles, width_in_tiles):
        # render the tileset based on collision's matrix.
        base_offset_x = offset_x // self.tile_size
        mod_offset_x = offset_x % self.tile_size
        base_offset_y = offset_y // self.tile_size
        mod_offset_y = offset_y % self.tile_size
        for idy, arr in enumerate(tilemap.matrix[base_offset_y:base_offset_y+height_in_tiles+1]):
            for idx, val in enumerate(arr[base_offset_x:base_offset_x+width_in_tiles+1]):
                if val != -1:
                    x = idx*self.tile_size
                    y = idy*self.tile_size
                    sx = (val % self.tile_size) * self.tile_size
                    sy = (val // (256 // self.tile_size)) * self.tile_size
                    pyxel.blt(x-mod_offset_x, y-mod_offset_y, 0, sx, sy, self.tile_size, self.tile_size, colkey)

def build_tilemap(map_file, layer):
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
