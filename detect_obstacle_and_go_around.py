import picar_4wd as fc
import traceback
import time

def periodly_check_status_change(curr_status, ref1=40, ref2=15):
    count = 1
    status = min(scan_range(3, ref1, ref2))
    while(status != 0 and status == curr_status):
        time.sleep(0.1)
        if count % 3 == 0: # -54~54 degree -> 0 degree -> 0 degree -> -54~54 degree -> ...
            status = min(scan_range(3, ref1, ref2))
        else:
            status = min(scan_range(0, ref1, ref2))
        count += 1
    return status

def scan_range(max_step=5, ref1=40, ref2=15):
    """
    one step is 18 degree. If max_step = 5, it will scan from -90 degree to 90 degree
    """
    if max_step > 5:
        max_step = 5

    scan_list = []
    fc.current_angle = max_step*(fc.STEP)
    servo = fc.Servo(fc.PWM("P0"), offset=fc.ultrasonic_servo_offset) # don't know why, but this seems important!
    servo.set_angle(fc.current_angle)
    if max_step >= 3:
        time.sleep(0.2)
    else:
        time.sleep(0.1)

    for i in range(max_step*2+1):
        status = fc.get_status_at(angle = fc.current_angle, ref1 = ref1, ref2 = ref2)
        scan_list.append(status)
        fc.current_angle -= fc.STEP
    
    fc.current_angle = 0
    servo.set_angle(fc.current_angle)
    return scan_list

def run_and_stop(power_fast, power_slow):
    status = -1
    while status != 0:
        status = periodly_check_status_change(status)
        if status == 2:
            fc.forward(power_fast)
        elif status == 1:
            fc.forward(power_slow)
        else:
            break
    fc.stop()
    time.sleep(0.1)

def add_clearance_for_scan_list(scan_list):
    add_0_index = []
    tmp_list = scan_list.copy()
    if tmp_list[0] == 0 and len(tmp_list) > 1:
        add_0_index.append(1)
    if tmp_list[len(tmp_list)-1] == 0 and len(tmp_list) > 1:
        add_0_index.append(len(tmp_list)-2)
    for i in range(1, len(tmp_list)-1):
        if tmp_list[i] == 0:
            add_0_index.append(i-1)
            add_0_index.append(i+1)
    for i in add_0_index:
        tmp_list[i] = 0
    return tmp_list

def find_near_middle_index(scan_list ,status=2):
    for i in range(1, 6): # +-18 degree -> +- 36 degree -> ...
        if scan_list[5+i] == status:
            return i #turn left
        elif scan_list[5-i] == status:
            return -i #turn right
    return 0 #no status matched

def scan_and_turn_left_or_right(status):
    scan_list = add_clearance_for_scan_list( scan_range(5, 100, 25) )
    index = find_near_middle_index(scan_list, status)
    if index > 0:
        fc.turn_right(50)
        time.sleep(index)  #larger index needs more time to turn
    elif index < 0:
        fc.turn_left(50)
        time.sleep(-index)
    else:
        if status == 2:
            scan_and_turn_left_or_right(1)
        elif status == 1:
            fc.backward(10)
            time.sleep(2)
            fc.stop()
            scan_and_turn_left_or_right(2)
    fc.stop()
        
if __name__ == '__main__':
    try:
        while True:
            run_and_stop(power_fast=50, power_slow=5)
            fc.backward(10)
            time.sleep(2)
            fc.stop()
            scan_and_turn_left_or_right(2)
    except Exception as e:
        print(e)
        fc.stop()
        traceback.print_exc()
    except KeyboardInterrupt:
        fc.stop()
        print("KeyboardInterrupt exception is caught")


