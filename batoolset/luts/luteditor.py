# MEGA TODO --> maybe append the newly created LUTs from formula at the end or add a button to append it to the list and then ask for a name an ddo not allow duplication of names -−> TODO --> think about it

from batoolset.GUI.customdialog import CustomDialog
from batoolset.luts.lutcreatorfromformula import PaletteFormulaEditor
from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
import traceback
from batoolset.files.tools import get_home_dir
from batoolset.luts.lut_minimal_test import list_available_luts, PaletteCreator
import sys
from qtpy.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QColorDialog, QLabel, QVBoxLayout, QHBoxLayout, QFileDialog, QMessageBox, QComboBox, QLineEdit, QFormLayout
from qtpy.QtGui import QColor, QPixmap, QImage
from qtpy.QtCore import Qt
from batoolset.pyqts.tools import updateLutLabelPreview
import numpy as np

class PaletteEditor(QWidget):
    def __init__(self, lut=None, parent=None):
        super().__init__(parent)

        self.button_width = 40  # Example button width
        self.button_height = 20  # Example button height
        self.spacing = 2  # Example spacing

        self.rows = 16
        self.columns = 16
        self.buttons = {}

        self.last_used_path = ""  # Store the last used path

        self.initUI()

        if lut:
            self.setLUT(lut)
        else:
            self.setDefaultLUT()

        # self.updatePreview()
        total_length = (self.button_width * self.columns) + (self.spacing * (self.columns - 1))
        updateLutLabelPreview(self.getLUT(), self.previewLabel, total_length)

    def initUI(self):
        mainLayout = QVBoxLayout()

        # Add QComboBox for selecting LUT models with a label
        comboLayout = QHBoxLayout()
        self.lut_label = QLabel("Select LUT:")
        self.lut_combo = QComboBox()
        available_luts = list_available_luts()
        for lll, lut in enumerate(available_luts):
            if lll == 0:
                continue
            self.lut_combo.addItem(lut)

        # Select the "gray" entry by default
        self.lut_combo.setCurrentText("GRAY")

        self.lut_combo.currentIndexChanged.connect(self.setSelectedLUT)
        comboLayout.addWidget(self.lut_label)
        comboLayout.addWidget(self.lut_combo)

        # Set stretch factors to make the combo box occupy more space
        comboLayout.setStretchFactor(self.lut_label, 1)
        comboLayout.setStretchFactor(self.lut_combo, 7)

        mainLayout.addLayout(comboLayout)

        gridLayout = QGridLayout()
        gridLayout.setSpacing(2)

        for row in range(self.rows):
            for col in range(self.columns):
                button = QPushButton()
                button.setFixedSize(self.button_width, self.button_height)
                button.setStyleSheet("background-color: white;")
                button.clicked.connect(lambda _, r=row, c=col: self.openColorDialog(r, c))

                gridLayout.addWidget(button, row, col)
                self.buttons[(row, col)] = button

        self.previewLabel = QLabel()
        gridLayout.addWidget(self.previewLabel, self.rows, 0, 1, self.columns)

        mainLayout.addLayout(gridLayout)

        # Add LO and HI buttons
        buttonLayout = QHBoxLayout()
        self.loButton = QPushButton("LO")
        self.loButton.clicked.connect(self.setFirstButton)
        self.hiButton = QPushButton("HI")
        self.hiButton.clicked.connect(self.setLastButton)
        buttonLayout.addWidget(self.loButton)
        buttonLayout.addWidget(self.hiButton)

        # Add Import and Export buttons
        self.importButton = QPushButton("Import LUT")
        self.importButton.clicked.connect(self.importLUT)
        self.exportButton = QPushButton("Export LUT")
        self.exportButton.clicked.connect(self.exportLUT)
        buttonLayout.addWidget(self.importButton)
        buttonLayout.addWidget(self.exportButton)

        # Add Formula Editor button
        self.formulaEditorButton = QPushButton("New Lut formula")
        self.formulaEditorButton.clicked.connect(self.openFormulaEditor)
        buttonLayout.addWidget(self.formulaEditorButton)

        mainLayout.addLayout(buttonLayout)

        self.setLayout(mainLayout)
        self.setWindowTitle('Palette Editor (256 entries)')
        self.show()

    def openFormulaEditor(self):
        lut_from_formula = PaletteFormulaEditor(self)
        custom_dialog = CustomDialog(title="Edit text", message="Do you want to proceed?", main_widget=lut_from_formula,
                                     parent=self, options=['Ok', 'Cancel'],
                                     auto_adjust=True)  # that is really very good --> I can do it like that
        # custom_dialog.adjustSize()
        result = custom_dialog.exec_()
        if result:
            try:
                lut = lut_from_formula.get_palette()
                self.setLUT(lut)
                total_length = (self.button_width * self.columns) + (self.spacing * (self.columns - 1))
                updateLutLabelPreview(self.getLUT(), self.previewLabel, total_length)
            except:
                traceback.print_exc()
                print('invalid lut')

    def openColorDialog(self, row, col):
        button = self.buttons[(row, col)]
        current_color = button.palette().color(button.backgroundRole())

        color = QColorDialog.getColor(current_color, self)

        if color.isValid():
            button.setStyleSheet(f"background-color: {color.name()};")
            # self.updatePreview()
            total_length = (self.button_width * self.columns) + (self.spacing * (self.columns - 1))
            updateLutLabelPreview(self.getLUT(), self.previewLabel, total_length)

    def getLUT(self):
        lut = []
        for row in range(self.rows):
            for col in range(self.columns):
                button = self.buttons[(row, col)]
                color = button.palette().color(button.backgroundRole())
                lut.append(color.name())
        return lut

    def setLUT(self, lut):
        if len(lut) != 256:
            raise ValueError("LUT must contain exactly 256 entries")

        index = 0
        for row in range(self.rows):
            for col in range(self.columns):
                entry = lut[index]
                if isinstance(entry, str):
                    # Handle string representation of the color
                    color = QColor(entry)
                elif isinstance(entry, (list, np.ndarray)) and len(entry) == 3:
                    # Handle [R, G, B] array
                    color = QColor(entry[0], entry[1], entry[2])
                else:
                    raise ValueError(f"Invalid LUT entry: {entry}")

                if color.isValid():
                    self.buttons[(row, col)].setStyleSheet(f"background-color: {color.name()};")
                index += 1

    def setDefaultLUT(self):
        default_lut = [f"#{i:02x}{i:02x}{i:02x}" for i in range(256)]
        self.setLUT(default_lut)

    def setFirstButton(self):
        self.buttons[(0, 0)].setStyleSheet("background-color: #0000FF;")
        total_length = (self.button_width * self.columns) + (self.spacing * (self.columns - 1))
        updateLutLabelPreview(self.getLUT(), self.previewLabel, total_length)

    def setLastButton(self):
        self.buttons[(self.rows - 1, self.columns - 1)].setStyleSheet("background-color: #FF0000;")
        total_length = (self.button_width * self.columns) + (self.spacing * (self.columns - 1))
        updateLutLabelPreview(self.getLUT(), self.previewLabel, total_length)

    def importLUT(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Import LUT", self.last_used_path if self.last_used_path else get_home_dir(), "Text Files (*.lut);;All Files (*)", options=options)
        if fileName:
            try:
                with open(fileName, 'r') as file:
                    lut = [line.strip() for line in file]
                    if len(lut) != 256:
                        raise ValueError("LUT must contain exactly 256 entries")
                    self.setLUT(lut)
                    total_length = (self.button_width * self.columns) + (self.spacing * (self.columns - 1))
                    updateLutLabelPreview(self.getLUT(), self.previewLabel, total_length)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def exportLUT(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "Export LUT", self.last_used_path if self.last_used_path else get_home_dir(), "Text Files (*.lut);;All Files (*)", options=options)
        if fileName:
            if not fileName.lower().endswith('.lut'):
                fileName=fileName+'.lut'
            try:
                with open(fileName, 'w', encoding='utf-8') as file:
                    lut = self.getLUT()
                    for color in lut:
                        file.write(f"{color}\n")

                # Update the last used path
                self.last_used_path = fileName
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def setSelectedLUT(self):
        selected_lut = self.lut_combo.currentText()
        # lut = list_available_luts()[index + 1]  # Adjust index to skip the first entry
        available_luts = list_available_luts()
        lutcreator = PaletteCreator()
        lut_list = lutcreator.list
        if selected_lut in available_luts:
            try:
                lut = lutcreator.create3(lut_list[selected_lut])
                self.setLUT(lut)
                total_length = (self.button_width * self.columns) + (self.spacing * (self.columns - 1))
                updateLutLabelPreview(self.getLUT(), self.previewLabel, total_length)
            except:
                traceback.print_exc()
                print('invalid LUT')

if __name__ == '__main__':
    # this is the first version of my LUT editor

    app = QApplication(sys.argv)

    # Create PaletteEditor with the default grayscale LUT
    ex = PaletteEditor()

    sys.exit(app.exec_())
