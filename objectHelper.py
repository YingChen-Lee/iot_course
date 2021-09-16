import picar_4wd as fc
import time
import threading
import objectDetect as objD

OBJECT_DETECTION_PERIOD = 1
target_objects = {'person', 'stop sign'}

detected_object_timestamp = {}
need_handle_objects = []
detect_object_flag = True
unfreeze_timestamp = {'person': 0, 'stop sign': 0}
unfreeze_time = 2
detector = None

def detect_object():
    global detected_object_timestamp, detector
    detector = objD.ObjectDetector()
    while detect_object_flag:
        objects, framerate = detector.get_objects_framerate()
        for obj in objects:
            if obj in target_objects:
                detected_object_timestamp[obj] = time.time()
                #print(obj + ": "+str(time.time()))   ###### test ######

    detected_object_timestamp = {}

def start_detect_object():
    global detect_object_flag
    detect_object_flag = True
    detect_thread = threading.Thread(target=detect_object, args=()).start()

def end_detect_object():
    global detect_object_flag
    detect_object_flag = False
    detector.stop_camera()
    

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
    print("Handle person")
    while time.time() - detected_object_timestamp['person'] < OBJECT_DETECTION_PERIOD:
        time.sleep(0.1)
    
    fc.forward(forward_power)
    unfreeze_timestamp['person'] = time.time() + unfreeze_time

    dist = -2 # in this process, the car actually go a small distance
    return dist

def react_to_stop_sign(forward_power):
    fc.stop()
    print("Handle stop sign")
    time.sleep(2)

    fc.forward(forward_power)
    unfreeze_timestamp['stop sign'] = time.time() + unfreeze_time
    dist = -2 # in this process, the car actually go a small distance
    return dist

def take_over(forward_power=30):
    if 'person' in need_handle_objects:  # priority: person > traffic light
        return react_to_person(forward_power)
    elif 'stop sign' in need_handle_objects :
        return react_to_stop_sign(forward_power)
