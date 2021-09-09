import picar_4wd as fc
import traceback
import time
import mapMaking as mp

X_SIZE = 150 # centimeter
Y_SIZE = 150 # centimeter
X_GRID = 100
Y_GRID = 100

def get_distances(divisor):
    angle_dist_list = []
    step = 180 / divisor
    fc.current_angle = 90
    servo = fc.Servo(fc.PWM("P0"), offset=fc.ultrasonic_servo_offset) # don't know why, but this seems important!
    servo.set_angle(fc.current_angle)
    time.sleep(0.2)
    
    for i in range(divisor + 1):
        distance = fc.get_distance_at(angle = fc.current_angle)
        if distance < 0:  # too far, make the distance very large, inidicating it is outside the map
            distance = 10 * max(X_SIZE, Y_SIZE)
        angle_dist_list.append((fc.current_angle, distance))
        fc.current_angle -= step
        time.sleep(0.025)
    fc.current_angle = 0
    servo.set_angle(fc.current_angle)
    return angle_dist_list

if __name__ == '__main__':
    try:
        map_helper = mp.Mapping(X_SIZE, Y_SIZE, X_GRID, Y_GRID, (50,0), (99,30), clearance_length=5)
        angle_dist_list = get_distances(divisor=18)
        print(angle_dist_list)        
        map_helper.mark_obstacles(angle_dist_list)
        map_helper.print_map(5)
        map_helper.get_route_and_navigation()
        map_helper.mark_route()
        map_helper.print_map(5)

        
    except Exception as e:
        print(e)
        fc.stop()
        traceback.print_exc()
    except KeyboardInterrupt:
        fc.stop()
        print("KeyboardInterrupt exception is caught.")
