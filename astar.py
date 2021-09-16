import grid as gd
from grid import GridLocation
from grid import NeighborGrid
from grid import Dir
import priorityQueue as pq
from typing import Dict, Optional, Tuple, List

PENALTY_FOR_CHANGE_DIR = 50

def heuristic(a: GridLocation, b: GridLocation) -> float:
    (x1, y1) = a
    (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

def build_route_navigation(came_from: Dict[GridLocation, Optional[NeighborGrid]], goal: GridLocation):
    route: List[GridLocation] = []
    navigation: List[Tuple[Dir, int]] = []
    turnpoints: List[GridLocation] = []
    curr = came_from[goal]
    prev_dir = curr[0]
    prev_loc = curr[1]
    dir_count = 0
    curr_dir = None
    turnpoints.append(goal)
    while curr != None:
        route.append(curr[1])
        curr_dir = curr[0]
        if curr_dir != prev_dir:
            navigation.append((prev_dir, dir_count))
            dir_count = 1
            prev_dir = curr_dir
            turnpoints.append(prev_loc)
        else:
            dir_count += 1
        prev_loc = curr[1]
        curr = came_from[curr[1]]
    navigation.append((curr_dir, dir_count))
    navigation.reverse()
    turnpoints.reverse()
    return route, navigation, turnpoints
    

def a_star_search(graph: gd.SquareGrid, start: GridLocation, goal: GridLocation):
    frontier = pq.PriorityQueue()
    frontier.put(start, 0)
    came_from: Dict[GridLocation, Optional[NeighborGrid]] = {}
    cost_so_far: Dict[GridLocation, float] = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current: GridLocation = frontier.get()
        if current == goal:
             break

        for nbr_grid in graph.neighbors(current):
            change_dir_penalty = get_change_dir_penalty(nbr_grid, came_from[current])
            new_cost = cost_so_far[current] + 1 + change_dir_penalty
            if nbr_grid[1] not in cost_so_far or new_cost < cost_so_far[nbr_grid[1]]:
                cost_so_far[nbr_grid[1]] = new_cost
                priority = new_cost + heuristic(nbr_grid[1], goal)
                frontier.put(nbr_grid[1], priority)
                came_from[nbr_grid[1]] = (nbr_grid[0], current)
    route, navigation, turnpoints = build_route_navigation(came_from, goal)
    return route, navigation, turnpoints

def get_change_dir_penalty(nbr_grid: NeighborGrid, came_from_grid: Optional[NeighborGrid]):
    nbr_dir = nbr_grid[0]
    if came_from_grid != None and nbr_dir != came_from_grid[0]:
        change_dir_penalty = PENALTY_FOR_CHANGE_DIR
    else:
        change_dir_penalty = 0
    return change_dir_penalty

