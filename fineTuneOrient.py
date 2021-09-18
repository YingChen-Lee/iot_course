import picar_4wd as fc
import part2
import time
import math

FINE_TUNE_STEP_SIZE = 7.5
THRESHOLD = 100 #centimeter
FINE_TUNE_PWR = part2.TURN_PWR
FINE_TUNE_TIME =  part2.TURN_TIME * (FINE_TUNE_STEP_SIZE/45)  #make it turn FINE_TUNE_STEP_SIZE degree each time

class fineTune():
    def __init__(self, del_dir):
        self.ref_points = []
        self.curr_points = []
        self.del_dir = del_dir
        self.tune_range_degree = abs(del_dir) * 15  # turn 45 degree -> fine tune 15 degree; turn 90 degree -> fine tune 30 degree
        self.tune_range = round(self.tune_range_degree / FINE_TUNE_STEP_SIZE)

    def set_ref_points(self):
        ref_angle_dist = part2.get_distances( round(180/FINE_TUNE_STEP_SIZE), get_median = False)
        #ref_angle_dist = [(90, 200), (75,200), (60, 100), (45,110), (30,90), (15, 300), (0, 400), (-15, 400), (-30, 20), (-45, 10), (-60, 100), (-75, 400), (-90, 400)]  ############  test #############
        self.ref_points = self._LT_threshold(ref_angle_dist)

    def fine_tune(self):
        # each elements in list represents FINE_TUNE_STEP_SIZE degree
        # fine tune +- self.tune_range_degree degree
        is_turn_left = (self.del_dir >= 0)
        curr_angle_dist = part2.get_distances( round(180/FINE_TUNE_STEP_SIZE), get_median = False)
        #curr_angle_dist = [(90, 90), (75,300), (60, 400), (45,400), (30,20), (15, 10), (0, 100), (-15, 400), (-30, 400), (-45, 400), (-60, 20), (-75, 10), (-90, 100)]  ############  test  ############
        self.curr_points = self._LT_threshold(curr_angle_dist)
        print(self.ref_points)
        print(self.curr_points)

        if is_turn_left == True:
            lhs = self.curr_points
            rhs = self.ref_points
        else:
            lhs = self.ref_points
            rhs = self.curr_points

        ideal_del_i = (abs(self.del_dir) * round(45/FINE_TUNE_STEP_SIZE))  #del_dir = 1 -> 45 degree, displacement = 45/15 = 3
        relevance_list = []
        for del_i in range( ideal_del_i - self.tune_range, ideal_del_i + self.tune_range + 1):
            relevance = self._cal_relevance(lhs, rhs, del_i)
            #relevance -=  math.sqrt(abs(del_i - ideal_del_i))  ##### test #####
            relevance_list.append(relevance)
        print(relevance_list)
        fine_tune_displacement = self._get_fine_tune_displacement(relevance_list)
        
        if is_turn_left:
            fine_tune_degree = (-1)*fine_tune_displacement*FINE_TUNE_STEP_SIZE
        else:
            fine_tune_degree = fine_tune_displacement*FINE_TUNE_STEP_SIZE
        print("fine tune " + str(fine_tune_degree) + " degree")
        
        # fine_tune_displacement > 0 means overturned, need turn back
        if (is_turn_left and fine_tune_displacement > 0) or (not is_turn_left and fine_tune_displacement < 0):
            fc.turn_right(FINE_TUNE_PWR)
        else:
            fc.turn_left(FINE_TUNE_PWR)
        time.sleep(FINE_TUNE_TIME * abs(fine_tune_displacement))
        fc.stop() 

    def _LT_threshold(self, target_list):
        res = []
        for angle, dist in target_list:
            if dist >= THRESHOLD:
                res.append(0)
            else:
                res.append(1)
        return res

    def _cal_relevance(self, lhs, rhs, del_i):
        rel = 0
        list_len = len(lhs)
        for i in range(list_len - del_i):
            if lhs[del_i + i] == rhs[i]:
                rel += 1
            else:
                rel -= 0.5

        return rel

    def _get_fine_tune_displacement(self, relevance_list):
        max_relevance_index = self.tune_range
        max_relevance = relevance_list[self.tune_range]
        for i in range(2*self.tune_range + 1):
            if relevance_list[i] > max_relevance:
                max_relevance_index = i
                max_relevance = relevance_list[i]
        return max_relevance_index - self.tune_range
