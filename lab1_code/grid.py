from typing import Tuple, Iterator
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum

import matplotlib.animation as animation

class Dir(Enum):
    E  = 0
    NE = 1
    N  = 2
    NW = 3
    W  = 4
    SW = 5
    S  = 6
    SE = 7

GridLocation = Tuple[int,int]
NeighborGrid = Tuple[Dir, GridLocation]

class SquareGrid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.map = np.zeros( (width, height), dtype = int)
    
    def in_bounds(self, id: GridLocation) -> bool:
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id: GridLocation) -> bool:
        (x, y) = id
        return self.map[x][y] != 1

    def neighbors(self, id: GridLocation) -> Iterator[NeighborGrid]:
        (x, y) = id
        results = []
        neighbors = [(Dir.E,(x+1,y)), (Dir.NE,(x+1,y+1)), (Dir.N,(x,y+1)), (Dir.NW,(x-1,y+1)), (Dir.W,(x-1,y)), (Dir.SW,(x-1,y-1)), (Dir.S,(x,y-1)), (Dir.SE,(x+1,y-1))]
        for nbr in neighbors:
            if self.in_bounds(nbr[1]) and self.passable(nbr[1]):
                results.append(nbr)
        return results
        
    def print_map(self, pause_time=2):
        plt.close()
        plt.imshow(self.map.transpose(), cmap='Greys')
        plt.gca().invert_yaxis()
        plt.show(block=False)
        plt.pause(pause_time)

    def reset_map(self):
        self.map = np.zeros( (self.width, self.height), dtype = int)

    def clear_map_in_vision(self, eqn_a, eqn_b, eqn_c): # clear the region where ax+by+c>0
        for i in range(self.width):
            for j in range(self.height):
                if eqn_a*i + eqn_b*j + eqn_c > 0:
                    self.map[i][j] = 0




