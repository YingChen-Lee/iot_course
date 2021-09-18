import picar_4wd as fc
import part2
import time

THRESHOLD = 150
FINE_TUNE_PWR = fc.TURN_PWR
FINE_TUNE_TIME = fc.TURN_TIME/3  #make it turn 15 degree each time

class fineTune():
    def __init__(self):
        self.ref_points = []
        self.curr_points = []

    def set_ref_points(self):
        ref_angle_dist = part2.get_distances(12, get_median = False)
        #ref_angle_dist = [(90, 200), (75,200), (60, 100), (45,110), (30,90), (15, 300), (0, 400), (-15, 400), (-30, 20), (-45, 10), (-60, 100), (-75, 400), (-90, 400)]  ############  test #############
        self.ref_points = self._LT_threshold(ref_angle_dist)

    def fine_tune(self, del_dir):
        # each elements in list represents 15 degree
        # fine tune +- 30 degree
        is_turn_left = (del_dir >= 0)
        curr_angle_dist = part2.get_distances(12, get_median = False)
        #curr_angle_dist = [(90, 90), (75,300), (60, 400), (45,400), (30,20), (15, 10), (0, 100), (-15, 400), (-30, 400), (-45, 400), (-60, 20), (-75, 10), (-90, 100)]  ############  test  ############
        self.curr_points = self._LT_threshold(curr_angle_dist)

        if is_turn_left == True:
            lhs = self.curr_points
            rhs = self.ref_points
        else:
            lhs = self.ref_points
            rhs = self.curr_points

        ideal_del_i = (abs(del_dir) * 3)  #del_dir = 1 -> 45 degree, displacement = 45/15 = 3
        relevance_list = []
        for del_i in range( ideal_del_i - 2, ideal_del_i + 3):
            avg_relevance = self._cal_relevance(lhs, rhs, del_i) / (len(lhs)-del_i)
            relevance_list.append(avg_relevance)
        fine_tune_displacement = self._get_fine_tune_displacement(relevance_list)
        print("fine tune " + str(fine_tune_displacement*15) + " degree")
        
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
                rel += 0

        return rel

    def _get_fine_tune_displacement(self, relevance_list):
        max_relevance_index = 2
        max_relevance = relevance_list[2]
        for i in range(5):
            if relevance_list[i] > max_relevance:
                max_relevance_index = i
                max_relevance = relevance_list[i]
        return max_relevance_index - 2

if __name__ == '__main__' :
    test_finetuner = fineTune()
    test_finetuner.set_ref_points()
    test_finetuner.fine_tune(-1) #turn right 45 degree
