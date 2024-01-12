import os
from enum import Enum

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPainter, QPen, QMovie, QCursor
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from tobii_research_addons import ScreenBasedCalibrationValidation, Point2
import tobii_research as tr

from config import RESOLUTION
from experiment import values
from experiment.Eyetracker import TOBII_PRO_FUSION_DATA
from util import load_ui, repo_root


class ValType(Enum):
    INITIAL = 0
    FINAL = 1


ValidationWidgetUi = load_ui(os.path.join(repo_root, "experiment", "ui", "calibration-validation.ui"))


class ValidationWidget(QWidget, ValidationWidgetUi):
    def __init__(self, parent, val_type):
        super().__init__()
        self.parent = parent
        self.val_type = val_type

        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        # Normalized coordinates (0.0, 0.0) - (1.0, 1.0)
        # Default points: (0.5, 0.5), (0.1, 0.1), (0.9, 0.9), (0.9, 0.1), (0.1, 0.9)
        # Bringing the fixation stimuli closer to the edges of the monitor (better when viewing full screen images)
        self.points_to_collect = [
            # center
            Point2(0.5, 0.5),
            # top left
            Point2(0.05, 0.05),
            # bottom right
            Point2(0.95, 0.95),
            # top right
            Point2(0.95, 0.05),
            # bottom left
            Point2(0.05, 0.95),
        ]
        self.point_pointer = 0

        self.point = QLabel(self)
        self.point_diameter = 30
        self.point.setFixedSize(self.point_diameter, self.point_diameter)
        self.animation = QMovie(os.path.join(repo_root, "experiment", "ui", "animated_dot.gif"))
        self.point.setMovie(self.animation)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.collect_validation_data)
        self.close_timer = QTimer(self)
        self.close_timer.timeout.connect(self.__close)
        self.collect_data_timer = QTimer(self)
        self.collect_data_timer.timeout.connect(self.collect_data)

        self.calib = ScreenBasedCalibrationValidation(self.parent.eyetracker.eyetracker, sample_count=200,
                                                      timeout_ms=3000)

        self.visual_validation_result: dict = dict()
        self.drawing_validation_result = False

        self.result_label = QLabel(self)
        self.__init_result_label()

        self.data_log = None
        self.marker_log = None
        self.__init_log_files()

        self.show()

    def start(self):
        time_until_start = 1000
        self.__log_msg(f"Validation trial {self.val_type.value} starts in {time_until_start} ms")
        self.timer.start(time_until_start)

    def collect_validation_data(self):
        if not self.calib.is_collecting_data:
            self.timer.stop()
            if not self.calib.is_validation_mode:
                self.calib.enter_validation_mode()
                QApplication.setOverrideCursor(QCursor(Qt.BlankCursor))  # Hide cursor
            all_fixation_stimuli_have_been_recorded = self.point_pointer == len(self.points_to_collect)
            if all_fixation_stimuli_have_been_recorded:
                self.calib.leave_validation_mode()
                QApplication.setOverrideCursor(QCursor())  # Show normal cursor
                self.__erase_point()
                res = self.calib.compute()
                self.__log_raw_validation_data()
                validation_successful = self.parent.experiment.set_validation_data(res, self.val_type)
                if validation_successful:
                    self.parent.next()
                    self.__close()
                else:
                    self.__show_validation_result()
            else:
                point = self.points_to_collect[self.point_pointer]
                self.__draw_point(point)
                self.__log_msg(f"Validation {point} online")
                # Wait a little for user to focus (1s)
                self.collect_data_timer.start(1000)

    def collect_data(self):
        point = self.points_to_collect[self.point_pointer]
        self.__log_msg(f"Starting data collection for {point}")
        self.calib.start_collecting_data(point)
        self.point_pointer += 1
        self.collect_data_timer.stop()
        # Wait for 500ms until checking again for is_collecting_data in collect_validation_data
        self.timer.start(500)

    def __show_validation_result(self):
        self.drawing_validation_result = True
        # Set new instruction
        instruction = values.validation_result_instruction
        val_res = self.parent.experiment.get_latest_validation_result()
        instruction = instruction.replace(f"[AAR]", f"AAR: {val_res.average_accuracy_right}")
        instruction = instruction.replace(f"[AAL]", f"AAL: {val_res.average_accuracy_left}")
        instruction = instruction.replace(f"[APR]", f"APR: {val_res.average_precision_right}")
        instruction = instruction.replace(f"[APL]", f"APL: {val_res.average_precision_left}")
        instruction = instruction.replace(f"[APRR]", f"APRR: {val_res.average_precision_rms_right}")
        instruction = instruction.replace(f"[APRL]", f"APRL: {val_res.average_precision_rms_left}")
        self.__paint_validation_result()
        self.result_label.setText(instruction)
        self.result_label.show()

    def keyPressEvent(self, event):
        if self.drawing_validation_result:
            if event.key() == Qt.Key_N and event.modifiers() == Qt.ControlModifier:
                self.parent.next()
                self.__close()
            if event.key() == Qt.Key_R and event.modifiers() == Qt.ControlModifier:
                self.__reset()
                self.start()

    def __reset(self):
        self.setupUi(self)
        self.calib = ScreenBasedCalibrationValidation(self.parent.eyetracker.eyetracker, sample_count=200,
                                                      timeout_ms=3000)
        self.point_pointer = 0
        self.visual_validation_result: dict = dict()
        self.drawing_validation_result = False
        self.result_label.hide()

    def __draw_point(self, point: Point2):
        self.animation.stop()
        w = self.point.width()
        h = self.point.height()
        x = int(int(self.width() * point.x) - (w / 2))
        y = int(int(self.height() * point.y) - (h / 2))
        self.point.setGeometry(x, y, w, h)
        self.point.show()
        self.animation.start()

    def __erase_point(self):
        self.animation.stop()
        self.point.hide()

    def __init_result_label(self):
        self.result_label.setStyleSheet("QLabel{color: white; font-size: 18px;}")
        self.result_label.setAlignment(Qt.AlignCenter)
        width_px = 800
        height_px = 250
        center_x = int(RESOLUTION[0]/2 - width_px/2)
        bottom_padding_px = 25
        bottom_y = int(RESOLUTION[1]-height_px-bottom_padding_px)
        self.result_label.setGeometry(center_x, bottom_y, width_px, height_px)

    def __init_log_files(self):
        pid = str(self.parent.pid)
        data_path = os.path.join(repo_root, "experiment", "results", pid, f"validation_data.tsv")
        marker_path = os.path.join(repo_root, "experiment", "results", pid, f"validation_markers.tsv")
        if self.val_type == ValType.INITIAL:
            self.data_log = open(data_path, 'w')
            self.data_log.write("\t".join(self.__validation_data_header_list()) + "\n")
            self.marker_log = open(marker_path, 'w')
            self.marker_log.write("\t".join(self.__validation_makers_header_list()) + "\n")
        else:
            self.data_log = open(data_path, 'a')
            self.marker_log = open(marker_path, 'a')

    def __log_msg(self, msg):
        timestamp = tr.get_system_time_stamp()
        self.marker_log.write("\t".join([str(timestamp), msg])+"\n")

    @staticmethod
    def __validation_makers_header_list():
        return ["timestamp", "message"]

    @staticmethod
    def __validation_data_header_list():
        return ["validation_trial", "validation_point"]+TOBII_PRO_FUSION_DATA

    def __log_raw_validation_data(self):
        validation_trial = str(self.val_type.value)
        for screen_point, samples in self.calib._ScreenBasedCalibrationValidation__collected_points.items():
            validation_point = str((screen_point.x, screen_point.y))
            for sample in samples:
                device_time_stamp = str(sample.device_time_stamp)
                system_time_stamp = str(sample.system_time_stamp)
                left_eye = sample.left_eye
                left_gaze_point = left_eye.gaze_point
                left_gaze_point_on_display_area = str(left_gaze_point.position_on_display_area)
                left_gaze_point_in_user_coordinate_system = str(left_gaze_point.position_in_user_coordinates)
                left_gaze_point_validity = str(int(left_gaze_point.validity))
                left_pupil = left_eye.pupil
                left_pupil_diameter = str(left_pupil.diameter)
                left_pupil_validity = str(int(left_pupil.validity))
                left_gaze_origin = left_eye.gaze_origin
                left_gaze_origin_in_user_coordinate_system = str(left_gaze_origin.position_in_user_coordinates)
                left_gaze_origin_in_trackbox_coordinate_system = str(left_gaze_origin.position_in_track_box_coordinates)
                left_gaze_origin_validity = str(int(left_gaze_origin.validity))
                right_eye = sample.right_eye
                right_gaze_point = right_eye.gaze_point
                right_gaze_point_on_display_area = str(right_gaze_point.position_on_display_area)
                right_gaze_point_in_user_coordinate_system = str(right_gaze_point.position_in_user_coordinates)
                right_gaze_point_validity = str(int(right_gaze_point.validity))
                right_pupil = right_eye.pupil
                right_pupil_diameter = str(right_pupil.diameter)
                right_pupil_validity = str(int(right_pupil.validity))
                right_gaze_origin = right_eye.gaze_origin
                right_gaze_origin_in_user_coordinate_system = str(right_gaze_origin.position_in_user_coordinates)
                right_gaze_origin_in_trackbox_coordinate_system = str(right_gaze_origin.position_in_track_box_coordinates)
                right_gaze_origin_validity = str(int(right_gaze_origin.validity))
                self.data_log.write("\t".join([validation_trial, validation_point, device_time_stamp, system_time_stamp,
                                               left_gaze_point_on_display_area, left_gaze_point_in_user_coordinate_system,
                                               left_gaze_point_validity, left_pupil_diameter, left_pupil_validity,
                                               left_gaze_origin_in_user_coordinate_system,
                                               left_gaze_origin_in_trackbox_coordinate_system,
                                               left_gaze_origin_validity, right_gaze_point_on_display_area,
                                               right_gaze_point_in_user_coordinate_system, right_gaze_point_validity,
                                               right_pupil_diameter, right_pupil_validity,
                                               right_gaze_origin_in_user_coordinate_system,
                                               right_gaze_origin_in_trackbox_coordinate_system,
                                               right_gaze_origin_validity])+"\n")

    def __close(self):
        self.data_log.close()
        self.marker_log.close()
        self.close()
        self.deleteLater()

    @staticmethod
    def __norm_to_disp_point(normalized_point):
        point = normalized_point
        if isinstance(point, Point2):
            point = point.x, point.y
        return int(point[0] * RESOLUTION[0]), int(point[1] * RESOLUTION[1])

    def __paint_validation_result(self):
        for screen_point, samples in self.calib._ScreenBasedCalibrationValidation__collected_points.items():

            gaze_point_left_all = []
            gaze_point_right_all = []

            for sample in samples:
                right_gaze_point = sample.right_eye.gaze_point
                is_right_eye_valid = right_gaze_point.validity
                left_gaze_point = sample.left_eye.gaze_point
                is_left_eye_valid = left_gaze_point.validity

                if is_right_eye_valid and is_left_eye_valid:
                    gaze_point_right_all.append(
                        ValidationWidget.__norm_to_disp_point(right_gaze_point.position_on_display_area))
                    gaze_point_left_all.append(
                        ValidationWidget.__norm_to_disp_point(left_gaze_point.position_on_display_area))

            self.visual_validation_result[ValidationWidget.__norm_to_disp_point(screen_point)] = (
            gaze_point_right_all, gaze_point_left_all)
        self.update()

    def paintEvent(self, event):
        if self.drawing_validation_result:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.black)

            for stimuli, gaze_point_all in self.visual_validation_result.items():
                gaze_point_radius = 3
                painter.setPen(Qt.black)
                # Paint right eye gaze points
                painter.setBrush(Qt.green)
                for right_gaze_point in gaze_point_all[0]:
                    center_x, center_y = right_gaze_point
                    painter.drawEllipse(center_x - gaze_point_radius, center_y - gaze_point_radius,
                                        gaze_point_radius * 2, gaze_point_radius * 2)
                # Paint left eye gaze points
                painter.setBrush(Qt.blue)
                for left_gaze_point in gaze_point_all[1]:
                    center_x, center_y = left_gaze_point
                    painter.drawEllipse(center_x - gaze_point_radius, center_y - gaze_point_radius,
                                        gaze_point_radius * 2, gaze_point_radius * 2)

            # Have to loop again to print the crosses on top of all gaze points, do not know why
            for stimuli, _ in self.visual_validation_result.items():
                # Paint stimuli
                pen = QPen()
                pen.setColor(Qt.white)  # Set the color of the cross
                pen.setWidth(2)  # Set the width of the cross lines
                painter.setPen(pen)
                x, y = stimuli
                # Draw horizontal line
                painter.drawLine(x - 20, y, x + 20, y)
                # Draw vertical line
                painter.drawLine(x, y - 20, x, y + 20)