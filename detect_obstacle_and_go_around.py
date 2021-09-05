import picar_4wd as fc
import traceback
import time



def scan_range(max_step=5, ref1=35, ref2=10):
    """
    one step is 18 degree. If max_step = 5, it will scan from -90 degree to 90 degree
    """
    if max_step > 5:
        max_step = 5

    scan_list = []
    fc.current_angle = max_step*(fc.STEP)
    servo = fc.Servo(fc.PWM("P0"), offset=fc.ultrasonic_servo_offset)
    servo.set_angle(fc.current_angle)
    time.sleep(0.1)
    for i in range(max_step*2+1):
        status = fc.get_status_at(angle = fc.current_angle, ref1 = ref1, ref2 = ref2)
        scan_list.append(status)
        fc.current_angle -= fc.STEP
    
    fc.current_angle = 0
    servo.set_angle(fc.current_angle)
    return scan_list


if __name__ == '__main__':
    try:
        fc.forward(10)
        print(fc.scan_range(5))
        print(fc.scan_range(5))
        print(fc.scan_range(5))
        print(fc.scan_range(5))
        time.sleep(2)
        fc.forward(1)
        print(fc.us.get_distance())
        time.sleep(1)
        print(fc.us.get_distance())
        time.sleep(3)
        print(fc.scan_range(5))
        stop()
    except Exception as e:
        print(e)
        stop()
        traceback.print_exc()


