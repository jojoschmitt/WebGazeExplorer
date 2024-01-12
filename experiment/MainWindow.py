import os.path
from typing import Optional

from PyQt5.QtWidgets import QMainWindow, QLabel, QLineEdit, QPushButton, QTextEdit, QApplication, QCheckBox
from PyQt5.QtCore import Qt

from experiment.ValidationWidget import ValidationWidget, ValType
from experiment.Eyetracker import Eyetracker
from experiment.FullscreenWidget import FullscreenWidget
from experiment.Experiment import Experiment
from experiment.Observation import Assignment
from experiment.Phase import Phase
from util import *
from version import version


MainWindowUi = load_ui(os.path.join(repo_root, "experiment", "ui", "main-window.ui"))


class MainWindow(QMainWindow, MainWindowUi):

    exit_bt: QPushButton
    pid_lb: QLabel
    pid_le: QLineEdit
    pwd_lb: QLabel
    pwd_le: QLineEdit
    start_bt: QPushButton
    debug_cb: QCheckBox
    status: QTextEdit
    status_lb: QLabel
    version: QLabel

    def __init__(self):
        super().__init__()
        #####
        # Init experiment based attributes
        #####
        self.RESULT_DIR = os.path.join(repo_root, "experiment", "results")

        self.pid: int = self.__get_next_pid()
        self.experiment: Optional[Experiment] = None

        self.participant_dir = os.path.join(self.RESULT_DIR, str(self.pid))

        self.debug = False

        self.eyetracker = None

        self.gaze_validation_data = {ValType.INITIAL: None, ValType.FINAL: None}

        #####
        # Init UI based attributes
        #####
        self.setWindowFlags(Qt.FramelessWindowHint)  # Set the frameless window hint
        self.setupUi(self)

        self.version.setText(version)
        self.pid_le.setText(str(self.pid))

        self.view_start = None
        self.view_end = None

        # Setup start button
        self.start_bt.clicked.connect(self.start_clicked)
        # Setup exit button
        self.exit_bt.clicked.connect(self.exit_clicked)

        self.fullscreen_widget: Optional[FullscreenWidget] = None
        self.validation_widget: Optional[ValidationWidget] = None

    def next(self, answer=None):

        if self.experiment.state.phase == Phase.N_FINAL:
            if not self.debug:
                self.experiment.evaluate_validation_success()
                self.experiment.observation.completed = True
                self.experiment.save_observation_to_file(self.__generate_pid_based_file_path("observation", ".json"))
            exit(0)

        # Save user input to observation
        if answer:
            task_id = self.experiment.state.task.id
            round = self.experiment.state.round
            img_url = absolute_to_repo_relative_path(self.experiment.get_img().url)
            img_specification = self.experiment.get_img().specification
            user_selection = answer.user_selection
            if user_selection in ["Ja", "Nein"]:
                answer_correct = "NA"
            else:
                answer_correct = str(user_selection == img_specification)
            website_known = answer.website_known
            assignment = Assignment(task_id, round, img_url, img_specification, user_selection, answer_correct, website_known)
            self.experiment.observation.add_assignment(assignment)

        # Get next state
        self.experiment.next_state()

        # Handle GUI for next state
        match self.experiment.state.phase:
            case Phase.N_INITIAL_VALIDATION_INSTRUCTION:
                self.fullscreen_widget.show_instruction(self.experiment.get_initial_validation_instruction())
            case Phase.N_INITIAL_VALIDATION:
                if not self.debug:
                    self.validation_widget = ValidationWidget(self, ValType.INITIAL)
                    self.validation_widget.start()
            case Phase.T_INTRODUCTION:
                self.fullscreen_widget.show_introduction(self.experiment.get_introduction())
            case Phase.INSTRUCTION:
                if self.experiment.state.task.id == 3:
                    self.fullscreen_widget.show_instruction(self.experiment.get_instruction(),
                                                            self.experiment.get_navigation_task())
                else:
                    self.fullscreen_widget.show_instruction(self.experiment.get_instruction())
            case Phase.EXPLORATION:
                self.__start_recording(self.experiment.trial_nr())
                self.fullscreen_widget.show_image(self.experiment.get_img())
            case Phase.STATEMENT:
                self.fullscreen_widget.show_statement(self.experiment.get_statement())
            case Phase.N_FINAL_VALIDATION_INSTRUCTION:
                self.fullscreen_widget.show_instruction(self.experiment.get_final_validation_instruction())
            case Phase.N_FINAL_VALIDATION:
                if not self.debug:
                    self.validation_widget = ValidationWidget(self, ValType.FINAL)
                    self.validation_widget.start()
            case Phase.N_FINAL:
                self.fullscreen_widget.show_instruction(self.experiment.get_instruction())
            case _:
                raise ValueError(f"This phase does not exist: {self.experiment.state.phase}")

        if self.experiment.state.phase != Phase.EXPLORATION:
            # Stop recording after the image is no longer visible
            self.__stop_recording(self.experiment.trial_nr())

    def closeEvent(self, event):
        # Close all other windows
        for widget in QApplication.topLevelWidgets():
            if widget != self:
                widget.close()
        if not self.debug and self.experiment:
            self.__stop_recording(self.experiment.trial_nr())
            self.experiment.save_observation_to_file(self.__generate_pid_based_file_path("observation", ".json"))
        event.accept()

    def __start_recording(self, trial_nr):
        if not self.debug:
            self.eyetracker.start_recording(trial_nr, self.experiment.get_img().get_name())

    def __stop_recording(self, trial_nr):
        if not self.debug:
            self.eyetracker.stop_recording(trial_nr)

    def start_clicked(self):
        self.debug = self.debug_cb.isChecked()
        if not self.debug:
            pwd = self.pwd_le.text()
            if pwd != 'john':
                if pwd == '':
                    self.print_status('WARNING: Password missing.')
                else:
                    self.pwd_le.setText('')
                    self.print_status('WARNING: Password wrong.')
                return

        self.print_status(f'Starting experiment for PID {self.pid}.')
        self.experiment = Experiment(self.pid)
        self.fullscreen_widget = FullscreenWidget(self)
        if not self.debug:
            self.__create_participant_dir()
            self.eyetracker = Eyetracker(raw_file=self.__generate_pid_based_file_path("tobii_data", ".tsv"),
                                         exploration_file=self.__generate_pid_based_file_path("explorations", ".tsv"))
        self.next()

    def exit_clicked(self):
        self.close()

    def print_status(self, status):
        self.status.append(status)
        status_scroll_bar = self.status.verticalScrollBar()
        status_scroll_bar.setValue(status_scroll_bar.maximum())

    def __get_next_pid(self):
        pid = 0
        for item in os.listdir(self.RESULT_DIR):
            if os.path.isdir(os.path.join(self.RESULT_DIR, item)):
                pid += 1
        next_pid = pid + 1
        assert 1 <= next_pid <= 16
        return next_pid

    def __create_participant_dir(self):
        part_dir_exists = os.path.exists(self.participant_dir)
        if part_dir_exists:
            raise FileExistsError(f"Cannot create result directory for PID {self.pid}. Result for PID already exists.")
        else:
            os.makedirs(self.participant_dir)

    def __generate_pid_based_file_path(self, filename="", extension=""):
        return os.path.join(self.participant_dir, f"{filename}{extension}")

