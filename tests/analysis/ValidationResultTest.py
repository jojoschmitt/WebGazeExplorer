import os
import unittest

from analysis.ValidationResult import DirectedMaskScore, HeatMapScore, ValidationScore, ValidationResult
from config import TEST_DIR


class ValidationResultTest(unittest.TestCase):

    def test_save_and_load_validation_result(self):
        file_path = os.path.join(TEST_DIR, 'analysis', 'validation_result.pickle')

        mapping1 = "task-1"
        pid1 = 1
        eid1 = 1
        dm_score1 = DirectedMaskScore(0.5, 0.5)
        hm_score1 = HeatMapScore(0.5, 0.5)
        v_score1 = ValidationScore(mapping1, pid1, eid1, dm_score1, hm_score1)

        mapping2 = "task-1"
        pid2 = 1
        eid2 = 2
        dm_score2 = DirectedMaskScore(0.8, 0.8)
        hm_score2 = HeatMapScore(0.8, 0.8)
        v_score2 = ValidationScore(mapping2, pid2, eid2, dm_score2, hm_score2)

        vr = ValidationResult()
        vr.set_scores([v_score1, v_score2])

        vr.save(file_path)
        try:
            loaded_vr = ValidationResult()
            loaded_vr.load(file_path)
            self.assertTrue(isinstance(loaded_vr, ValidationResult))
            loaded_vs_list = loaded_vr.validation_scores
            self.assertEqual(2, len(loaded_vs_list))
            s1 = loaded_vs_list[0]
            self.assertTrue(isinstance(s1, ValidationScore))
            s2 = loaded_vs_list[1]
            self.assertTrue(isinstance(s2, ValidationScore))
            self.assertEqual(v_score1, s1)
            self.assertEqual(v_score2, s2)
        finally:
            os.remove(file_path)
