from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
from qtpy.QtWidgets import QApplication, QDialog, QLabel, QVBoxLayout

class PleaseWaitDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Please wait")
        self.setModal(True)

        label = QLabel("Please wait... The slow process is running.")
        layout = QVBoxLayout()
        layout.addWidget(label)
        self.setLayout(layout)
