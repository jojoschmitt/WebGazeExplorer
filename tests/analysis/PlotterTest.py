import unittest

from analysis import Analyzer


class PlotterTest(unittest.TestCase):

    def test_plot_cross_validation_result(self):
        # Sample data in three dictionaries
        dm_correlations = {"Task1": [0.1, 0.2, 0.3, 0.4, 0.5],
                           "Task2": [0.2, 0.3, 0.4, 0.5, 0.6]}
        hm_correlations = {"Task1": [0.3, 0.4, 0.5, 0.6, 0.7],
                           "Task2": [0.4, 0.5, 0.6, 0.7, 0.8]}
        avg_correlations = {"Task1": [0.2, 0.3, 0.4, 0.5, 0.6],
                            "Task2": [0.3, 0.4, 0.5, 0.6, 0.7]}
        analyzer = Analyzer.get_default_analyzer()
        analyzer.plotter.plot_cross_validation_analysis_results(dm_correlations, hm_correlations, avg_correlations)