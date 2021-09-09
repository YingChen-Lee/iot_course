#import picar_4wd as fc
import time, math
import numpy as np
import grid as gd
import astar
from typing import Dict
from grid import GridLocation
from grid import NeighborGrid
from grid  import Dir

def vector_add(lhs, rhs):
    lhs_x, lhs_y = lhs
    rhs_x, rhs_y = rhs
    return (lhs_x + rhs_x, lhs_y + rhs_y)

def vector_mul_scalar(v, a):
    v_x, v_y = v
    return (a*v_x, a*v_y)

def point_round(v):
    v_x, v_y = v
    return (round(v_x), round(v_y))

class Mapping():
    def __init__(self, len_x, len_y, grid_num_x, grid_num_y, curr_loc, goal_loc, clearance_length = 10):
        self.len_x = len_x  # centimeter (e.g. 100 cm * 100 cm)
        self.len_y = len_y
        self.grid_size_x = len_x / grid_num_x
        self.grid_size_y = len_y / grid_num_y
        self.curr_loc = curr_loc
        self.goal_loc = goal_loc
        self.clearance = round(clearance_length / min(self.grid_size_x, self.grid_size_y))
        self.grid = gd.SquareGrid(grid_num_x, grid_num_y)
        self.curr_orient = 0
        self.route = None
        self.navigation = None

    def mark_obstacles(self, angle_distance_list):
        obstacles = self._get_obstacles_position(angle_distance_list)
        self._mark(obstacles)

    def get_route_and_navigation(self):
        self.route, self.navigation = astar.a_star_search(self.grid, self.curr_loc, self.goal_loc)

    def mark_route(self):
        for loc in self.route:
            self.grid.map[loc[0],loc[1]] = 2

    def unmark_route(self):
        for loc in self.route:
            self.grid.map[loc[0],loc[1]] = 0
    
    def print_map(self, pause_time=2):
        self.grid.print_map(pause_time)

    def _get_obstacles_position(self, angle_distance_list):
        obstacles = []
        for angle, dist in angle_distance_list:
            if dist <= 0:
                obstacles.append(None)
                continue
            radian = (angle+90+self.curr_orient) / 180*math.pi #+90: because for servo, -90 degree is right, 90 degree is left, 0 degree is front
            obstacle_x = self.curr_loc[0] + round(dist*math.cos(radian) / self.grid_size_x)
            obstacle_y = self.curr_loc[1] + round(dist*math.sin(radian) / self.grid_size_y)
            if self.grid.in_bounds((obstacle_x, obstacle_y)):
                obstacles.append( (obstacle_x, obstacle_y) )
            else:
                obstacles.append(None)
        return obstacles

    def _mark(self, obstacles):
        obstacles.append(None)
        for i in range(len(obstacles)):
            if obstacles[i] == None:
                continue
            elif obstacles[i+1] != None:
                self._interpolate_add_clearance(obstacles[i], obstacles[i+1], self.clearance)
            else:
                self._interpolate_add_clearance(obstacles[i], obstacles[i], self.clearance)

    def _interpolate_add_clearance(self, point1, point2, clearance, mark_type=1): #maybe we can unmark the obstacles (mark_type=0), but now, we just mark obstacles and don't unmark it.
        point1_x, point1_y = point1
        point2_x, point2_y = point2
        dist = math.sqrt( (point1_x - point2_x) * (point1_x - point2_x) + (point1_y - point2_y) * (point1_y - point2_y))
        if dist == 0:
            self._add_clearance_for_one_point(point1_x, point1_y, clearance)
            return
        
        unit_vector_line = ( (point2_x - point1_x) / dist, (point2_y - point1_y) / dist)
        unit_vector_normal = ( (point1_y - point2_y) / dist, (point2_x - point1_x) / dist)
        
        """
        add 0.5 of the vector per time, otherwise some point will lost.
        0.5 is acceptable, but there are still few points lost
        can add 0.2 of the vector per time as well, almost no points lost
        """
        point_line = vector_add(point1, vector_mul_scalar(unit_vector_line, (-1)*clearance) )
        for i in range( 2*(round(dist) + 2*clearance) + 1):
            point_normal = point_round( vector_add(point_line, vector_mul_scalar(unit_vector_normal, (-1)*clearance)) )
            for j in range( 2*2*clearance + 1 ):
                point = point_round(point_normal)
                if self.grid.in_bounds((point[0], point[1])):
                    self.grid.map[point[0], point[1]] = 1
                point_normal = vector_add( point_normal, vector_mul_scalar(unit_vector_normal, 0.5))
            point_line = vector_add(point_line, vector_mul_scalar(unit_vector_line, 0.5))


    def _add_clearance_for_one_point(self, point_x, point_y, clearance):
        for x in range(point_x - clearance, point_x + clearance + 1):
            for y in range(point_y - clearance, point_y + clearance + 1):
                if self.grid.in_bounds((x,y)):
                    self.grid.map[x][y] = 1

if __name__ == '__main__':
    mapping = Mapping(140,140,100,100, (50,0), (0,50), clearance_length = 3)
    obstacle_list = [(90,20), (60, 10), (0, 120), (-30, 60)]
    mapping.curr_orient = 0
    mapping.mark_obstacles(obstacle_list)
    #mapping.grid.print_map()
    mapping.get_route_and_navigation()
    mapping.mark_route()
    #mapping.unmark_route()
    mapping.grid.print_map()
