import unittest

from experiment.Phase import Phase
from experiment.State import State
from experiment.Task import Task


class RandomImageUnitTest(unittest.TestCase):

    def test_random_img_orders(self):
        for id in range(1, 17):
            for task_id in range(1, 4):
                for round in range(1, 5):
                    for phase_id in range(1, 4):
                        state = State(task=Task(task_id, id), round=round, phase=Phase(phase_id))
                        self.assertTrue(self.check_list(state.task._get_img_order()))

    def check_list(self, l):
        return self.check_len(l) and self.check_duplicates(l) and self.check_order(l)

    def check_len(self, l):
        return len(l) == 32

    def check_duplicates(self, l):
        for i in range(len(l)):
            if l.count(i) > 1:
                return False
        return True

    def check_order(self, l):
        for i in range(len(l)):
            if i not in l:
                return False
        return True


if __name__ == '__main__':
    unittest.main()
