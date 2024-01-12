import os
import unittest

import numpy as np

from analysis import Analyzer
from config import TEST_RESOURCES_DIR


class DirectedMaskUnitTest(unittest.TestCase):
    def setUp(self):
        dm1_path = os.path.join(TEST_RESOURCES_DIR, '0-directed-mask.npy')
        dm2_path = os.path.join(TEST_RESOURCES_DIR, '1-directed-mask.npy')
        dm3_path = os.path.join(TEST_RESOURCES_DIR, '2-directed-mask.npy')
        self.dm1 = np.load(dm1_path)
        self.dm2 = np.load(dm2_path)
        self.dm3 = np.load(dm3_path)

    def test_accumulation_and_subtraction_integrity(self):
        analyzer = Analyzer.get_default_analyzer()

        def vectors_equal(vector_list):
            assert len(vector_list) == 2
            epsilon = 1e-8
            vect1 = vector_list[0]
            vect2 = vector_list[1]
            direction_v1, strength_v1 = vect1
            direction_v2, strength_v2 = vect2
            equal_direction = abs(direction_v1 - direction_v2) <= epsilon
            equal_strength = abs(strength_v1 - strength_v2) <= epsilon
            zero_vectors = abs(strength_v1) <= epsilon and equal_strength
            equal_vectors = zero_vectors or equal_direction and equal_strength
            if not equal_vectors:
                print(vect1, vect2)
            self.assertTrue(equal_vectors)

        print(f"Generating accumulated directed mask...")
        am = analyzer.accumulator.accumulate_directed_masks([self.dm1, self.dm2])

        print(f"Generating subtracted directed mask 1...")
        sm1 = analyzer.accumulator.subtract_directed_mask(am, self.dm2)
        print(f"Test integrity of subtracted directed mask 1")
        DirectedMaskUnitTest.for_each_element_in_masks_do([self.dm1, sm1], vectors_equal)

        print(f"Generating subtracted directed mask 2...")
        sm2 = analyzer.accumulator.subtract_directed_mask(am, self.dm1)
        print(f"Test integrity of subtracted directed mask 2")
        DirectedMaskUnitTest.for_each_element_in_masks_do([self.dm2, sm2], vectors_equal)

    @staticmethod
    def for_each_element_in_masks_do(masks, function):
        def equal_shapes(masks):
            masks = iter(masks)
            try:
                first_shape = next(masks).shape
            except StopIteration:
                return True
            return all(first_shape == mask.shape for mask in masks)

        assert equal_shapes(masks)

        height, width, _ = masks[0].shape
        for y in range(height):
            for x in range(width):
                function([mask[y, x] for mask in masks])
