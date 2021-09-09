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
    
    for i in range(divisor + 1):
        distance = fc.get_distance_at(angle = fc.current_angle)
        if distance < 0:  # too far, make the distance very large, inidicating it is outside the map
            distance = 10 * max(X_SIZE, Y_SIZE)
        angle_dist_list.append((fc.current_angle, distance))
        fc.current_angle -= step
    fc.current_angle = 0
    servo.set_angle(fc.current_angle)
    return angle_dist_list

if __name__ == '__main__':
    try:
        map_helper = mp.Mapping(X_SIZE, Y_SIZE, X_GRID, Y_GRID, (50,0), (0,0), clearance=10)
        angle_dist_list = get_distances(divisor=18)
        print(angle_dist_list)        

        
    except Exception as e:
        print(e)
        fc.stop()
        traceback.print_exc()
    except KeyboardInterrupt:
        fc.stop()
        print("KeyboardInterrupt exception is caught.")
