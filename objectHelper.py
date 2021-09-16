import picar_4wd as fc
import time
import objectDetect as objD

OBJECT_DETECTION_PERIOD = 1
target_objects = {'person', 'stop sign'}

detected_object_timestamp = {}
need_handle_objects = []
detect_object_flag = True
unfreeze_timestamp = {}
unfreeze_time = 2

def detect_object():
    global detected_object_timestamp
    detector = objD.ObjectDetector()
    while detect_object_flag:
        objects, framerate = detector.get_objects_framerate()
        for obj in objects:
            if obj in target_objects:
                detected_object_timestamp[obj] = time.time()

    detected_object_timestamp = {}

def start_detect_object():
    global detect_object_flag
    detect_object_flag = True
    detect_thread = threading.Thread(target=detect_object, args=()).start()

def end_detect_object():
    global detect_object_flag
    detect_object_flag = False

def check_object(): # timeout: it's meaningless to react to the object that was discovered long time ago
    global need_handle_objects
    need_handle_objects = []
    for obj in detected_object_timestamp:
        timestamp = detected_object_timestamp[obj]
        unfreeze_timestamp_obj = unfreeze_timestamp[obj]
        if time.time() - timestamp < OBJECT_DETECTION_PERIOD and time.time() >= unfreeze_timestamp_obj:
            need_handle_objects.append(obj)

def need_take_over():
    check_object()
    return need_handle_objects != []

def react_to_person(forward_power):
    fc.stop()
    detect_person_timestamp = detected_object_timestamp['person'] 
    while detect_person_timestamp - time.time() < OBJECT_DETECTION_PERIOD:
        time.sleep(0.1)
    
    fc.forward(forward_power)
    unfreeze_timestamp['person'] = time.time() + unfreeze_time

    dist = 4 # in this process, the car actually go a small distance
    return dist

def react_to_stop_sign(forward_power):
    fc.stop()
    time.sleep(2)

    fc.forward(forward_power)
    unfreeze_timestamp['stop sign'] = time.time() + unfreeze_time
    dist = 4 # in this process, the car actually go a small distance
    return dist

def take_over(forward_power=30):
    if 'person' in need_handle_objects:  # priority: person > traffic light
        return react_to_person(forward_power)
    elif 'traffic light' in need_handle_objects :
        return react_to_stop_sign(forward_power)
