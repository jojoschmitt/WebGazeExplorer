import os.path

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QCursor, QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QApplication, QProgressBar, QRadioButton, \
    QCheckBox, QFrame

from experiment.Image import Image, SPECIFICATIONS
from experiment.Observation import Answer
from experiment.Phase import Phase
from util import load_ui, repo_root

import tobii_research as tr

ExperimentWidgetUi = load_ui(os.path.join(repo_root, "experiment", "ui", "experiment.ui"))


class FullscreenWidget(QWidget, ExperimentWidgetUi):

    instruction_lb: QLabel
    warning_lb: QLabel
    navigation_header_lb: QLabel
    navigation_task_lb: QLabel
    correct_lb: QLabel
    yes_bt: QPushButton
    no_bt: QPushButton
    progress_bar: QProgressBar

    reference_img: QFrame

    radio_bt1: QRadioButton
    radio_bt2: QRadioButton
    radio_bt3: QRadioButton
    radio_bt4: QRadioButton
    radio_bt5: QRadioButton
    radio_bt6: QRadioButton
    radio_bt7: QRadioButton
    radio_bt8: QRadioButton

    seen_cb: QCheckBox

    def __init__(self, parent):
        super().__init__()
        self.parent = parent

        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.showFullScreen()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.img_layer = QLabel()
        self.timer = QTimer(self)

        self.radio_buttons: list[QRadioButton] = [self.radio_bt1, self.radio_bt2, self.radio_bt3, self.radio_bt4,
                                                  self.radio_bt5, self.radio_bt6, self.radio_bt7, self.radio_bt8]

        self.warning_lb.hide()
        self.progress_bar.setMaximum(self.parent.experiment.workflow.qsize())
        self.yes_toggled = False
        self.yes_bt.clicked.connect(self.__toggle_yes)
        self.no_toggled = False
        self.no_bt.clicked.connect(self.__toggle_no)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_N:
            self.next()

    def __enabled_keyPressEvent(self, event):
        if event.key() == Qt.Key_N:
            self.next()

    def __disabled_keyPressEvent(self, event):
        return

    def __enable_key_press(self):
        self.keyPressEvent = self.__enabled_keyPressEvent
        if self.timer.isActive():
            self.timer.stop()

    def __disable_key_press(self):
        self.keyPressEvent = self.__disabled_keyPressEvent

    def __disable_next_for(self, time):
        self.__disable_key_press()
        self.timer.timeout.connect(self.__enable_key_press)
        self.timer.start(time)

    def next(self):
        if self.parent.experiment.state.phase == Phase.STATEMENT:
            assert self.parent.experiment.state.task.id in [1, 2, 3]
            answer = Answer(None, None)
            if self.parent.experiment.state.task.id == 1:
                for rb in self.radio_buttons[:4]:
                    if rb.isChecked():
                        answer.user_selection = rb.text()
                        break
                if answer.user_selection is None:
                    self.warning_lb.setText("Bitte wähle eine Kategorie aus um fortzufahren.")
                    self.warning_lb.show()
                    return
                answer.website_known = str(self.seen_cb.isChecked())
                self.warning_lb.hide()
                self.parent.next(answer=answer)
            elif self.parent.experiment.state.task.id == 2:
                for rb in self.radio_buttons:
                    if rb.isChecked():
                        answer.user_selection = rb.text()
                        break
                if answer.user_selection is None:
                    self.warning_lb.setText("Bitte wähle eine Funktionalität aus um fortzufahren.")
                    self.warning_lb.show()
                    return
                answer.website_known = str(self.seen_cb.isChecked())
                self.warning_lb.hide()
                self.parent.next(answer=answer)
            elif self.parent.experiment.state.task.id == 3:
                if self.yes_toggled ^ self.no_toggled:
                    if self.yes_toggled:
                        answer.user_selection = self.yes_bt.text()
                    else:
                        answer.user_selection = self.no_bt.text()
                else:
                    self.warning_lb.setText("Bitte gib an, ob Du das selbe Element identifiziert hast um fortzufahren.")
                    self.warning_lb.show()
                    return
                answer.website_known = str(self.seen_cb.isChecked())
                self.warning_lb.hide()
                self.parent.next(answer=answer)
        else:
            self.parent.next()

    def show_introduction(self, introduction):
        self.__prepare_instruction_alignment()
        self.__reference_img_elements(False)
        # Show normal cursor
        QApplication.setOverrideCursor(QCursor())
        # Remove image
        self.img_layer.close()
        self.layout.removeWidget(self.img_layer)
        # Set new instruction
        self.instruction_lb.setText(introduction)
        # Update progress bar
        self.__update_progress_bar()
        self.__disable_next_for(1000)

    def show_instruction(self, instruction, navigation_task=None):
        self.__prepare_instruction_alignment()
        self.__reference_img_elements(False)
        if navigation_task:
            self.navigation_task_lb.setText(navigation_task)
            self.navigation_task_lb.show()
            self.navigation_header_lb.show()
        # Show normal cursor
        QApplication.setOverrideCursor(QCursor())
        # Remove image
        self.img_layer.close()
        self.layout.removeWidget(self.img_layer)
        # Set new instruction
        self.instruction_lb.setText(instruction)
        # Update progress bar
        self.__update_progress_bar()

    def show_image(self, img: Image):
        self.__reference_img_elements(False)
        # Hide cursor
        QApplication.setOverrideCursor(QCursor(Qt.BlankCursor))
        # Prepare image
        img_pixmap = QPixmap(img.url)
        self.img_layer = QLabel()
        self.img_layer.setPixmap(img_pixmap)
        # Add img layer to the layout
        self.layout.addWidget(self.img_layer)
        if not self.parent.debug:
            self.parent.eyetracker.log_msg("image online")
            self.parent.view_start = tr.get_system_time_stamp()

    def show_statement(self, statement):
        self.__prepare_statement_alignment()
        if self.parent.experiment.state.task.id == 3:
            self.__reference_img_elements(True)
        else:
            self.__reference_img_elements(False)
        # Show normal cursor
        QApplication.setOverrideCursor(QCursor())
        # Remove image
        self.img_layer.close()
        self.layout.removeWidget(self.img_layer)
        if not self.parent.debug:
            self.parent.eyetracker.log_msg("image offline")
            self.parent.view_end = tr.get_system_time_stamp()
        # Set new instruction
        self.instruction_lb.setText(statement)
        # Update progress bar
        self.__update_progress_bar()

    def __toggle_yes(self):
        assert self.yes_toggled ^ self.no_toggled or not (self.yes_toggled and self.no_toggled)
        self.yes_toggled = True
        self.no_toggled = False
        self.__replace_button_color(self.yes_bt, "#D8D9DA", "#99FF99")
        self.__replace_button_color(self.no_bt, "#FF9999", "#D8D9DA")
        assert self.yes_toggled ^ self.no_toggled or not (self.yes_toggled and self.no_toggled)

    def __toggle_no(self):
        assert self.yes_toggled ^ self.no_toggled or not (self.yes_toggled and self.no_toggled)
        self.yes_toggled = False
        self.no_toggled = True
        self.__replace_button_color(self.yes_bt, "#99FF99", "#D8D9DA")
        self.__replace_button_color(self.no_bt, "#D8D9DA", "#FF9999")
        assert self.yes_toggled ^ self.no_toggled or not (self.yes_toggled and self.no_toggled)

    def __deactivate_buttons(self):
        if self.yes_toggled:
            self.yes_toggled = False
            self.__replace_button_color(self.yes_bt, "#99FF99", "#D8D9DA")
        elif self.no_toggled:
            self.no_toggled = False
            self.__replace_button_color(self.no_bt, "#FF9999", "#D8D9DA")

    @staticmethod
    def __replace_button_color(button, old_color, new_color):
        style = button.styleSheet()
        if style.count(new_color) > 0:
            # We are not replacing anything here. In our case this means that the button already has the correct color.
            # In other cases, if we would still replace the color here, it could lead to duplicates.
            return
        if style.count(old_color) == 1:
            style = style.replace(old_color, new_color)
            button.setStyleSheet(style)

    def __prepare_instruction_alignment(self):
        self.navigation_task_lb.hide()
        self.navigation_header_lb.hide()
        for rb in self.radio_buttons:
            rb.hide()
        self.seen_cb.hide()

    def __reference_img_elements(self, enabled):
        if enabled:
            pixmap = QPixmap(self.parent.experiment.get_reference_img().url)
            scaled_pixmap = pixmap.scaled(self.reference_img.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.reference_img.setPixmap(scaled_pixmap)
            self.reference_img.show()
            self.correct_lb.show()
            self.yes_bt.show()
            self.no_bt.show()
        else:
            self.reference_img.hide()
            self.correct_lb.hide()
            self.yes_bt.hide()
            self.no_bt.hide()
            self.__deactivate_buttons()

    def __prepare_statement_alignment(self):
        self.navigation_task_lb.hide()
        self.navigation_header_lb.hide()
        task_id = self.parent.experiment.state.task.id
        task_specifications = SPECIFICATIONS[task_id]
        if task_id == 1:
            for i in range(len(task_specifications)):
                rb = self.radio_buttons[i]
                if rb.isChecked():
                    self.__uncheck_radio_button(rb)
                rb.setText(task_specifications[i])
                rb.show()
        elif task_id == 2:
            for i in range(len(task_specifications)):
                rb = self.radio_buttons[i]
                if rb.isChecked():
                    self.__uncheck_radio_button(rb)
                rb.setText(task_specifications[i])
                rb.show()
        self.seen_cb.setChecked(False)
        self.seen_cb.setText(f"Ich habe {self.parent.experiment.get_img().get_host()} schon einmal besucht.")
        self.seen_cb.show()

    @staticmethod
    def __uncheck_radio_button(button: QRadioButton):
        # https://stackoverflow.com/questions/9372992/qradiobutton-check-uncheck-issue-in-qt
        button.setAutoExclusive(False)
        button.setChecked(False)
        button.setAutoExclusive(True)

    def __update_progress_bar(self):
        max = self.progress_bar.maximum()
        current_size = self.parent.experiment.workflow.qsize()
        self.progress_bar.setValue(max-current_size)
