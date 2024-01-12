import cProfile
import os
from pstats import SortKey

import numpy as np


from analysis import Analyzer
from config import TEST_RESOURCES_DIR

if __name__ == '__main__':

    analyzer = Analyzer.get_default_analyzer()

    dm1_path = os.path.join(TEST_RESOURCES_DIR, '0-directed-mask.npy')
    dm2_path = os.path.join(TEST_RESOURCES_DIR, '1-directed-mask.npy')
    dm1 = np.load(dm1_path)
    dm2 = np.load(dm2_path)

    with cProfile.Profile() as pr:
        analyzer.accumulator.accumulate_directed_masks([dm1, dm2])

        pr.print_stats(sort=SortKey.CUMULATIVE)
