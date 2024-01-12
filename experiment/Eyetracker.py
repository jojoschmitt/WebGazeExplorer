# This code is adapted from the TobiiProTracker class as part of PyGaze,
# https://github.com/esdalmaijer/PyGaze/
#
# PyGaze is an open-source toolbox for eye tracking
#
#    PyGaze is a Python module for easily creating gaze contingent experiments
#    or other software (as well as non-gaze contingent experiments/software)
#    Copyright (C) 2012-2013  Edwin S. Dalmaijer
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>

import os.path
import time

import tobii_research as tr

from config import RESOLUTION
from util import repo_root

DEFAULT_RAW_FILE = os.path.join(repo_root, "experiment", "results", "raw-recording.tsv")
DEFAULT_EXPLORATION_FILE = os.path.join(repo_root, "experiment", "results", "exploration.tsv")

TOBII_PRO_FUSION_DATA = ['device_time_stamp',
                         'system_time_stamp',
                         'left_gaze_point_on_display_area',
                         'left_gaze_point_in_user_coordinate_system',
                         'left_gaze_point_validity',
                         'left_pupil_diameter',
                         'left_pupil_validity',
                         'left_gaze_origin_in_user_coordinate_system',
                         'left_gaze_origin_in_trackbox_coordinate_system',
                         'left_gaze_origin_validity',
                         'right_gaze_point_on_display_area',
                         'right_gaze_point_in_user_coordinate_system',
                         'right_gaze_point_validity',
                         'right_pupil_diameter',
                         'right_pupil_validity',
                         'right_gaze_origin_in_user_coordinate_system',
                         'right_gaze_origin_in_trackbox_coordinate_system',
                         'right_gaze_origin_validity'
                         ]


class Eyetracker:
    def __init__(self, disp_size=RESOLUTION, raw_file=DEFAULT_RAW_FILE, exploration_file=DEFAULT_EXPLORATION_FILE):
        eyetrackers = tr.find_all_eyetrackers()
        if eyetrackers:
            self.eyetracker = eyetrackers[0]
        else:
            raise Exception("No eyetracker found!")

        self._write_enabled = True
        self.raw_datafile = open(raw_file, 'w')
        self.exploration_file = open(exploration_file, 'w')
        self._write_raw_header()
        self._write_exploration_header()
        self.disp_size = disp_size

        self.recording = False

    def _write_raw_header(self):
        header = '\t'.join(TOBII_PRO_FUSION_DATA)+"\n"
        self.raw_datafile.write(header)

    def _write_exploration_header(self):
        header = f"Timestamp\tMessage"
        self.exploration_file.write(header+"\n")

    def _on_gaze_data(self, gaze_data):
        if self._write_enabled:
            self._write_raw_data(gaze_data)

    def start_recording(self, trial_nr, img_name):
        if self.recording:
            print("WARNING: Recording is ongoing. Cannot start second recording from same device.")
        else:
            self.eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, self._on_gaze_data, as_dictionary=True)
            # Make sure that the eyetracker is recording properly when the image is shown
            time.sleep(1)
            self.recording = True
            self.log_msg(f"TRIALSTART {trial_nr}")
            self.log_msg(f"IMAGENAME {img_name}")

    def stop_recording(self, trial_nr):
        if self.recording:
            self.log_msg(f"TRIALEND {trial_nr}")
            self.eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA)
            self.recording = False
            return True
        else:
            print("WARNING: No recording ongoing. Cannot stop recording.")
            return False

    def _write_raw_data(self, gaze_data):
        _write_buffer = ""
        for data in TOBII_PRO_FUSION_DATA:
            _write_buffer += str(gaze_data[data])+'\t'
        if _write_buffer.endswith('\t'):
            # Remove the trailing tab
            _write_buffer = _write_buffer[:-1]
        self.raw_datafile.write(_write_buffer + "\n")

    def log_msg(self, msg):
        # Timestamp in microseconds (us)
        timestamp = tr.get_system_time_stamp()
        self.exploration_file.write("{}\t{}\n".format(timestamp, msg))

    def close(self):
        self.raw_datafile.close()
        self.exploration_file.close()
