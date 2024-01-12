import unittest

import numpy as np

from analysis.extractors.ConcurrentHeatSourceEliminationExtractor import MarkerMask, Area, HeatPointVisitor, AxisDirection
from util import Point


class ConcurrentHeatSourceEliminationExtractorTest(unittest.TestCase):

    def test_marker_mask_initialization(self):
        width = 7
        height = 5
        center_split_point = Point(2, 2)
        mm = MarkerMask(center_split_point, width, height)

        # Test lengths
        self.assertEqual(2, mm.py_len)
        self.assertEqual(4, mm.px_len)
        self.assertEqual(2, mm.ny_len)
        self.assertEqual(2, mm.nx_len)

        # Test axis
        self.assertTrue(isinstance(mm.py, Area))
        self.assertEqual(1, mm.py.dimensions)
        self.assertEqual((2, 0), mm.py.global_origin)

        self.assertTrue(isinstance(mm.px, Area))
        self.assertEqual(1, mm.px.dimensions)
        self.assertEqual((3, 2), mm.px.global_origin)

        self.assertTrue(isinstance(mm.ny, Area))
        self.assertEqual(1, mm.ny.dimensions)
        self.assertEqual((2, 3), mm.ny.global_origin)

        self.assertTrue(isinstance(mm.nx, Area))
        self.assertEqual(1, mm.nx.dimensions)
        self.assertEqual((0, 2), mm.nx.global_origin)

        # Test quadrants
        self.assertTrue(isinstance(mm.py_nx, Area))
        self.assertEqual(2, mm.py_nx.dimensions)
        self.assertEqual((0, 0), mm.py_nx.global_origin)

        self.assertTrue(isinstance(mm.py_px, Area))
        self.assertEqual(2, mm.py_px.dimensions)
        self.assertEqual((3, 0), mm.py_px.global_origin)

        self.assertTrue(isinstance(mm.ny_px, Area))
        self.assertEqual(2, mm.ny_px.dimensions)
        self.assertEqual((3, 3), mm.ny_px.global_origin)

        self.assertTrue(isinstance(mm.ny_nx, Area))
        self.assertEqual(2, mm.ny_nx.dimensions)
        self.assertEqual((0, 3), mm.ny_nx.global_origin)

    def test_heat_point_visitor_initialization_py_axis(self):
        width = 7
        height = 5
        center_split_point = Point(2, 2)
        heatmap = np.zeros((height, width))
        heatmap[center_split_point.y, center_split_point.x] = 255
        mm = MarkerMask(center_split_point, width, height)
        axis_direction = AxisDirection.PY
        relevant_points_on_primary_axis = []
        relevant_points_on_support_axis = []
        hpv = HeatPointVisitor(heatmap, mm, axis_direction, relevant_points_on_primary_axis, relevant_points_on_support_axis)

        self.assertTrue(isinstance(hpv.primary_axis, Area))
        self.assertEqual(1, hpv.primary_axis.dimensions)
        self.assertEqual((2, 0), hpv.primary_axis.global_origin)
        axis_len = 2
        self.assertEqual(axis_len, max(hpv.primary_axis.array.shape))

        self.assertTrue(isinstance(hpv.support_axis, Area))
        self.assertEqual(1, hpv.support_axis.dimensions)
        self.assertEqual((3, 2), hpv.support_axis.global_origin)
        axis_len = 4
        self.assertEqual(axis_len, max(hpv.support_axis.array.shape))

        self.assertTrue(isinstance(hpv.quadrant, Area))
        self.assertEqual(2, hpv.quadrant.dimensions)
        self.assertEqual((3, 0), hpv.quadrant.global_origin)
        quadrant_width = 4
        quadrant_height = 2
        self.assertEqual((quadrant_height, quadrant_width), hpv.quadrant.array.shape)

        hpv.run()

    def test_heat_point_visitor_initialization_px_axis(self):
        width = 7
        height = 5
        center_split_point = Point(2, 2)
        heatmap = np.zeros((height, width))
        heatmap[center_split_point.y, center_split_point.x] = 255
        mm = MarkerMask(center_split_point, width, height)
        axis_direction = AxisDirection.PX
        relevant_points_on_primary_axis = []
        relevant_points_on_support_axis = []
        hpv = HeatPointVisitor(heatmap, mm, axis_direction, relevant_points_on_primary_axis,
                               relevant_points_on_support_axis)

        self.assertTrue(isinstance(hpv.primary_axis, Area))
        self.assertEqual(1, hpv.primary_axis.dimensions)
        self.assertEqual((3, 2), hpv.primary_axis.global_origin)
        axis_len = 4
        self.assertEqual(axis_len, max(hpv.primary_axis.array.shape))

        self.assertTrue(isinstance(hpv.support_axis, Area))
        self.assertEqual(1, hpv.support_axis.dimensions)
        self.assertEqual((2, 3), hpv.support_axis.global_origin)
        axis_len = 2
        self.assertEqual(axis_len, max(hpv.support_axis.array.shape))

        self.assertTrue(isinstance(hpv.quadrant, Area))
        self.assertEqual(2, hpv.quadrant.dimensions)
        self.assertEqual((3, 3), hpv.quadrant.global_origin)
        quadrant_width = 4
        quadrant_height = 2
        self.assertEqual((quadrant_height, quadrant_width), hpv.quadrant.array.shape)

        hpv.run()

    def test_heat_point_visitor_initialization_ny_axis(self):
        width = 7
        height = 5
        center_split_point = Point(2, 2)
        heatmap = np.zeros((height, width))
        heatmap[center_split_point.y, center_split_point.x] = 255
        mm = MarkerMask(center_split_point, width, height)
        axis_direction = AxisDirection.NY
        relevant_points_on_primary_axis = []
        relevant_points_on_support_axis = []
        hpv = HeatPointVisitor(heatmap, mm, axis_direction, relevant_points_on_primary_axis,
                               relevant_points_on_support_axis)

        self.assertTrue(isinstance(hpv.primary_axis, Area))
        self.assertEqual(1, hpv.primary_axis.dimensions)
        self.assertEqual((2, 3), hpv.primary_axis.global_origin)
        axis_len = 2
        self.assertEqual(axis_len, max(hpv.primary_axis.array.shape))

        self.assertTrue(isinstance(hpv.support_axis, Area))
        self.assertEqual(1, hpv.support_axis.dimensions)
        self.assertEqual((0, 2), hpv.support_axis.global_origin)
        axis_len = 2
        self.assertEqual(axis_len, max(hpv.support_axis.array.shape))

        self.assertTrue(isinstance(hpv.quadrant, Area))
        self.assertEqual(2, hpv.quadrant.dimensions)
        self.assertEqual((0, 3), hpv.quadrant.global_origin)
        quadrant_width = 2
        quadrant_height = 2
        self.assertEqual((quadrant_height, quadrant_width), hpv.quadrant.array.shape)

        hpv.run()

    def test_heat_point_visitor_initialization_nx_axis(self):
        width = 7
        height = 5
        center_split_point = Point(2, 2)
        heatmap = np.zeros((height, width))
        heatmap[center_split_point.y, center_split_point.x] = 255
        mm = MarkerMask(center_split_point, width, height)
        axis_direction = AxisDirection.NX
        relevant_points_on_primary_axis = []
        relevant_points_on_support_axis = []
        hpv = HeatPointVisitor(heatmap, mm, axis_direction, relevant_points_on_primary_axis, relevant_points_on_support_axis)

        self.assertTrue(isinstance(hpv.primary_axis, Area))
        self.assertEqual(1, hpv.primary_axis.dimensions)
        self.assertEqual((0, 2), hpv.primary_axis.global_origin)
        axis_len = 2
        self.assertEqual(axis_len, max(hpv.primary_axis.array.shape))

        self.assertTrue(isinstance(hpv.support_axis, Area))
        self.assertEqual(1, hpv.support_axis.dimensions)
        self.assertEqual((2, 0), hpv.support_axis.global_origin)
        axis_len = 2
        self.assertEqual(axis_len, max(hpv.support_axis.array.shape))

        self.assertTrue(isinstance(hpv.quadrant, Area))
        self.assertEqual(2, hpv.quadrant.dimensions)
        self.assertEqual((0, 0), hpv.quadrant.global_origin)
        quadrant_width = 2
        quadrant_height = 2
        self.assertEqual((quadrant_height, quadrant_width), hpv.quadrant.array.shape)

        hpv.run()
