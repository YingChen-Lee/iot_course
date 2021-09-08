from typing import Tuple, Iterator
import numpy as np
import matplotlib.pyplot as plt

GridLocation = Tuple[int,int]
NeighborGrid = Tuple[int, GridLocation]

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
        neighbors = [(1,(x+1,y)), (2,(x+1,y+1)), (3,(x,y+1)), (4,(x-1,y+1)), (5,(x-1,y)), (6,(x-1,y-1)), (7,(x,y-1)), (8,(x+1,y-1))]
        for nbr in neighbors:
            if self.in_bounds(nbr[1]) and self.passable(nbr[1]):
                results.append(nbr)
        return results
        
    def print_map(self):
        plt.imshow(self.map.transpose(), cmap='Greys')
        plt.gca().invert_yaxis()
        plt.show()


