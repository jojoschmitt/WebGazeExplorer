import sys
import traceback

from PyQt5.QtWidgets import QApplication

from MainWindow import MainWindow


def excepthook(type, value, traceback_obj):
    """
    Custom exception hook to display a detailed error message.
    """
    error_message = "".join(traceback.format_exception(type, value, traceback_obj))
    print(error_message)
    sys.exit(1)


if __name__ == '__main__':
    # Set the custom exception hook
    sys.excepthook = excepthook
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())
