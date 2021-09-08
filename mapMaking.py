#import picar_4wd as fc
import time, math
import numpy as np
import matplotlib.pyplot as plt

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

def add_clearance_for_one_point(target_map, point_x, point_y, clearance):
    x_boundary = len(target_map) - 1
    y_boundary = len(target_map[0]) - 1
    for x in range(point_x - clearance, point_x + clearance + 1):
        for y in range(point_y - clearance, point_y + clearance + 1):
            if x >= 0 and x <= x_boundary and y >= 0 and y <= y_boundary:
                target_map[x][y] = 1

def interpolate_add_clearance(target_map, point1, point2, clearance, mark_type=1): #maybe we can unmark the obstacles (mark_type=0), but now, we just mark obstacles and don't unmark it.
    x_boundary = len(target_map)-1
    y_boundary = len(target_map[0])-1
    point1_x, point1_y = point1
    point2_x, point2_y = point2
    dist = math.sqrt( (point1_x - point2_x) * (point1_x - point2_x) + (point1_y - point2_y) * (point1_y - point2_y))
    if dist == 0:
        add_clearance_for_one_point(target_map, point1_x, point1_y, clearance)
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
            if point[0] >= 0 and point[0] <= x_boundary and point[1] >= 0 and point[1] <= y_boundary:
                target_map[point[0], point[1]] = 1
            point_normal = vector_add( point_normal, vector_mul_scalar(unit_vector_normal, 0.5))
        point_line = vector_add(point_line, vector_mul_scalar(unit_vector_line, 0.5))

def mark_obstacles(target_map, obstacles, clearance):
    obstacles.append(None)
    for i in range(len(obstacles)):
        if obstacles[i] == None:
            continue
        elif obstacles[i+1] != None:
            interpolate_add_clearance(target_map, obstacles[i], obstacles[i+1], clearance)
        else:
            interpolate_add_clearance(target_map, obstacles[i], obstacles[i], clearance)

def print_map(target_map):
    plt.imshow(target_map.transpose(), cmap='Greys')
    plt.gca().invert_yaxis()
    plt.show()

class Mapping():
    def __init__(self, map_size, grid_numbers, curr_x = 50, curr_y = 0, clearance_length = 10):
        self.map_size = map_size  # centimeter (e.g. 100 cm * 100 cm)
        self.grid_numbers = grid_numbers  # number of grids per side
        self.grid_size = map_size/grid_numbers
        self.map = np.zeros( (grid_numbers, grid_numbers), dtype = int)
        self.curr_x = curr_x
        self.curr_y = curr_y
        self.clearance = round(clearance_length / self.grid_size)
    def mark_obstacle(self, angle_distance_list):
        obstacles = []
        for angle, dist in angle_distance_list:
            radian = (angle+90)/180*math.pi  #+90: because for servo, -90 degree is right, 90 degree is left, 0 degree is front
            obstacle_x = self.curr_x + round(dist*math.cos(radian))
            obstacle_y = self.curr_y + round(dist*math.sin(radian))
            if obstacle_x < 0 or obstacle_x >= self.grid_numbers or obstacle_y < 0 or obstacle_y >= self.grid_numbers:
                obstacles.append(None)
            else:
                obstacles.append((obstacle_x, obstacle_y))
        mark_obstacles(self.map, obstacles, self.clearance)


if __name__ == '__main__':
    #mapping = Mapping(140, 100)  #140cm, 100 grids per side
    #mapping.plot_map()
    test_map = np.zeros((20, 20), dtype = int)
    #test_obstacles = [None, (1,1), (5,7), None, (10, 9), (12,15), (15,6)]
    test_obstacles = [(4,4), (4,6),None, (10,9), (12,15), (15,6)]
    mark_obstacles(test_map, test_obstacles, 1)
    print_map(test_map)
