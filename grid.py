from typing import Tuple, Iterator
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum, auto

class Dir(Enum):
    E  = auto()
    NE = auto()
    N  = auto()
    NW = auto()
    W  = auto()
    SW = auto()
    S  = auto()
    SE = auto()

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
        
    def print_map(self):
        plt.imshow(self.map.transpose(), cmap='Greys')
        plt.gca().invert_yaxis()
        plt.show()


