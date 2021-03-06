import time, math
import numpy as np
import grid as gd
import astar
from typing import Dict
from grid import GridLocation
from grid import NeighborGrid
from grid  import Dir

INTERPOLATION_LIMIT_LENGTH = 15
CENTER_TO_SENSOR_DIST = 11

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
    def __init__(self, len_x, len_y, grid_num_x, grid_num_y, curr_loc, goal_loc, curr_dir, clearance_length = 10):
        self.len_x = len_x  # centimeter (e.g. 100 cm * 100 cm)
        self.len_y = len_y
        self.grid_size_x = len_x / grid_num_x
        self.grid_size_y = len_y / grid_num_y
        self.curr_loc = curr_loc
        self.goal_loc = goal_loc
        self.clearance = round(clearance_length / min(self.grid_size_x, self.grid_size_y))
        self.grid = gd.SquareGrid(grid_num_x, grid_num_y)
        self.curr_dir = curr_dir
        self.route = None
        self.navigation = None
        self.turnpoints = None

    def mark_obstacles(self, angle_distance_list):
        self.clear_map_in_vision()
        obstacles = self._get_obstacles_position(angle_distance_list)
        self._mark(obstacles)
    
    def clear_map_in_vision(self):
        """
        In each time the car scan from +90 ~ -90, the region where the car can see can be reset to 0.
        """
        sensor_loc_x = round(self.curr_loc[0] + CENTER_TO_SENSOR_DIST * math.cos(self.curr_dir.value*45*math.pi/180)/self.grid_size_x)
        sensor_loc_y = round(self.curr_loc[1] + CENTER_TO_SENSOR_DIST * math.sin(self.curr_dir.value*45*math.pi/180)/self.grid_size_y)
        norm_x = math.cos(self.curr_dir.value*45*math.pi/180)
        norm_y = math.sin(self.curr_dir.value*45*math.pi/180)
        # line equation: ax + by + c = 0, clear ax + by + c > 0 part
        eqn_a = norm_x
        eqn_b = norm_y
        eqn_c = (-1) * ( eqn_a * sensor_loc_x + eqn_b * sensor_loc_y)
        self.grid.clear_map_in_vision(eqn_a, eqn_b, eqn_c)

    def get_route_navigation_turnpoints(self):
        self.route, self.navigation, self.turnpoints = astar.a_star_search(self.grid, self.curr_loc, self.goal_loc)

    def mark_route(self):
        for loc in self.route:
            self.grid.map[loc[0],loc[1]] = 2

    def unmark_route(self):
        if self.route == None:
            return
        for loc in self.route:
            self.grid.map[loc[0],loc[1]] = 0
    
    def print_map(self, pause_time=2):
        self.grid.print_map(pause_time)

    def is_reach_goal(self, tolerance):
        del_x = self.goal_loc[0] - self.curr_loc[0]
        del_y = self.goal_loc[1] - self.curr_loc[1]
        dist_grid_num = math.sqrt( del_x*del_x + del_y*del_y )
        return dist_grid_num <= tolerance
            
    def _get_obstacles_position(self, angle_distance_list):
        obstacles = []
        sensor_loc_x = round(self.curr_loc[0] + CENTER_TO_SENSOR_DIST * math.cos(self.curr_dir.value*45*math.pi/180)/self.grid_size_x)
        sensor_loc_y = round(self.curr_loc[1] + CENTER_TO_SENSOR_DIST * math.sin(self.curr_dir.value*45*math.pi/180)/self.grid_size_y)
        for angle, dist in angle_distance_list:
            if dist <= 0:
                obstacles.append(None)
                continue
            radian = (angle + self.curr_dir.value * 45) / 180*math.pi # the angle is from the car's perspective
            obstacle_x = sensor_loc_x + round(dist*math.cos(radian) / self.grid_size_x) 
            obstacle_y = sensor_loc_y + round(dist*math.sin(radian) / self.grid_size_y) 
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
        if dist == 0 or dist > INTERPOLATION_LIMIT_LENGTH:
            self._add_clearance_for_one_point(point1_x, point1_y, clearance)
            return
        
        unit_vector_line = ( (point2_x - point1_x) / dist, (point2_y - point1_y) / dist)
        unit_vector_normal = ( (point1_y - point2_y) / dist, (point2_x - point1_x) / dist)
        
        """
        add 0.5 of the vector per time, otherwise some point will lost.
        0.5 is acceptable, but there are still few points lost
        can add 0.1 of the vector per time as well, almost no points lost
        """
        point_line = vector_add(point1, vector_mul_scalar(unit_vector_line, (-1)*clearance) )
        for i in range( 10*(round(dist) + 2*clearance) + 1):
            point_normal = point_round( vector_add(point_line, vector_mul_scalar(unit_vector_normal, (-1)*clearance)) )
            for j in range( 10*2*clearance + 1 ):
                point = point_round(point_normal)
                if self.grid.in_bounds((point[0], point[1])):
                    self.grid.map[point[0], point[1]] = 1
                point_normal = vector_add( point_normal, vector_mul_scalar(unit_vector_normal, 0.1))
            point_line = vector_add(point_line, vector_mul_scalar(unit_vector_line, 0.1))


    def _add_clearance_for_one_point(self, point_x, point_y, clearance):
        for x in range(point_x - clearance, point_x + clearance + 1):
            for y in range(point_y - clearance, point_y + clearance + 1):
                if self.grid.in_bounds((x,y)):
                    self.grid.map[x][y] = 1

if __name__ == '__main__':
    mapping = Mapping(150,150,100,100, (50,0), (0,50), Dir.N, clearance_length = 5)
    obstacle_list = [(60,40), (50, 45), (40, 80), (30, 50), (20,45) ,  (-30, 60)]
    #obstacle_list = [(0,1)]
    mapping.curr_dir = Dir.N
    mapping.mark_obstacles(obstacle_list)
    #mapping.grid.print_map()
    #mapping.get_route_navigation_turnpoints()
    #mapping.mark_route()
    #mapping.unmark_route()
    mapping.grid.print_map()
    
    mapping.curr_dir = Dir.NE
    obstacle_list = []
    mapping.mark_obstacles(obstacle_list)
    mapping.grid.print_map()
    #print(mapping.navigation)
    #print(mapping.turnpoints)
