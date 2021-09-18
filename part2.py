import picar_4wd as fc
import traceback
import time
import mapMaking as mp
import objectHelper as obj
import fineTuneOrient as ft
from grid import Dir

X_SIZE = 150 # centimeter  # X_SIZE & Y_SIZE should be the same, X_GRID & Y_GRID should be the same
Y_SIZE = 150 # centimeter
X_GRID = 100
Y_GRID = 100
GRID_SIZE = X_SIZE / X_GRID
TURN_PWR = 35
TURN_TIME = 2  #adjust this parameter, make it turn 45 degree each time 
FORWARD_POWER = 40
GOAL = (25,99)

def get_median_3(dists):
    dists.sort()
    return dists[1]

def get_distances(divisor, get_median=True):
    angle_dist_list = []
    step = 180 / divisor
    fc.current_angle = 90
    servo = fc.Servo(fc.PWM("P0"), offset=fc.ultrasonic_servo_offset) # don't know why, but this seems important!
    servo.set_angle(fc.current_angle)
    time.sleep(0.2)
    
    for i in range(divisor + 1):
        if get_median == True:
            dists = []
            for j in range(3):
                dists.append( fc.get_distance_at(angle = fc.current_angle) )
            distance = get_median_3(dists)
        else:
            distance = fc.get_distance_at(angle = fc.current_angle)

        if distance < 0:  # too far, make the distance very large, indicating it is outside the map
            distance = 10 * max(X_SIZE, Y_SIZE)
        angle_dist_list.append((fc.current_angle, distance))
        fc.current_angle -= step
    fc.current_angle = 0
    servo.set_angle(fc.current_angle)
    return angle_dist_list

def turn_to(target_dir, map_helper):
    del_dir = target_dir.value - map_helper.curr_dir.value
    if del_dir > 4:  # > 180 degree
        del_dir -= 8
    elif del_dir < -4:  # < -180 degree
        del_dir += 8
    
    fine_tuner = ft.fineTune(del_dir)
    fine_tuner.set_ref_points()
    if del_dir > 0:
        fc.turn_left(TURN_PWR)
    elif del_dir < 0:
        fc.turn_right(TURN_PWR)
    time.sleep(TURN_TIME*abs(del_dir))
    fc.stop()

    fine_tuner.fine_tune()
    map_helper.curr_dir = target_dir

def scan_and_set_route(map_helper):
    map_helper.unmark_route()
    angle_dist_list = get_distances(divisor=24)
    map_helper.mark_obstacles(angle_dist_list)
    map_helper.get_route_navigation_turnpoints()
    map_helper.mark_route()
    map_helper.print_map(2)

def get_next_step(map_helper):
    orient_dist = map_helper.navigation[0]  # [ (Dir.NW, 10), (Dir.N, 50), (Dir.W, 30), ... ]
    dir_next = orient_dist[0]
    step_num = orient_dist[1]
    if dir_next == Dir.E or dir_next == Dir.N or dir_next == Dir.W or dir_next == Dir.S:
        dist = 1 * GRID_SIZE * step_num
    else:
        dist = 1.414 * GRID_SIZE * step_num
    return (dir_next, dist)

def go_forward_and_detect_object(target_dist, power=FORWARD_POWER):
    obj.start_detect_object()
    target_dist *= 1.2
    total_dist = 0
    time.sleep(0.2)
    fc.forward(power)
    if 5 <= target_dist < 30:
        total_dist += 3
    else:
        total_dist += 1
    while total_dist < target_dist:
        start_time = time.time()
              
        if obj.need_take_over():
            total_dist += (time.time() - start_time) * fc.speed_val()
            total_dist += obj.take_over(forward_power = FORWARD_POWER)
            start_time = time.time()
        
        time.sleep(0.025)
        total_dist += (time.time() - start_time) * fc.speed_val()

    fc.stop()
    obj.end_detect_object()

def get_scan_dir(map_helper):
    if len(map_helper.navigation) > 1:
        scan_dir = map_helper.navigation[1][0]
    else:
        scan_dir = map_helper.curr_dir
    return scan_dir

if __name__ == '__main__':
    try:
        map_helper = mp.Mapping(X_SIZE, Y_SIZE, X_GRID, Y_GRID, (50,0), GOAL, curr_dir = Dir.N, clearance_length = 3)
        scan_dir = Dir.E
        fc.start_speed_thread()
        time.sleep(1)
        
        turn_to(scan_dir, map_helper) #####test#####
        """
        while not map_helper.is_reach_goal( tolerance =  (10/GRID_SIZE) ):
            ## turn -> scan -> turn -> go
            turn_to(scan_dir, map_helper)
            
            scan_and_set_route(map_helper)
            go_dir, dist = get_next_step(map_helper)
            turn_to(go_dir, map_helper)
            go_forward_and_detect_object(dist)
            map_helper.curr_loc = map_helper.turnpoints[0]

            scan_dir = get_scan_dir(map_helper)
        """
        fc.left_rear_speed.deinit()
        fc.right_rear_speed.deinit()
        
    except Exception as e:
        print(e)
        fc.stop()
        traceback.print_exc()
    except KeyboardInterrupt:
        fc.stop()
        print("KeyboardInterrupt exception is caught.")
