
class Tilemap():

    def __init__(self, matrix, mutable=False):
        self.matrix = matrix
        self.mutable = mutable

    def update_tile(self, x, y, val):
        if self.mutable:
            self.matrix[x][y] = val
