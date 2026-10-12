from batoolset.pyqts.tools import updateLutLabelPreview
from batoolset.settings.global_settings import set_UI # set the UI to qtpy
set_UI()
import sys
import random
from qtpy.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QGroupBox, QMessageBox, QScrollArea, QSizePolicy,
)
from qtpy.QtCore import Qt
from qtpy.QtGui import QFont
from batoolset.luts.lut_minimal_test import PaletteCreator, list_available_luts, apply_lut, lsm_LUT_to_numpy


class PaletteFormulaEditor(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.palette = None

        # Initialize the UI components
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Preview Panel
        self.preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout()
        # Align the QLabel to the center

        self.previewLabel = QLabel()
        # self.previewLabel.setFixedSize(750,16)
        preview_layout.addWidget(self.previewLabel)
        preview_layout.setAlignment(self.previewLabel, Qt.AlignCenter)
        self.preview_group.setLayout(preview_layout)
        layout.addWidget(self.preview_group)

        # Formula Panel
        self.formula_group = QGroupBox("Formula")
        formula_layout = QVBoxLayout()

        h_layout1 = QHBoxLayout()
        h_layout2 = QHBoxLayout()

        # Red Formula
        self.redLabel = QLabel("Red Formula:")
        self.redFormula = QLineEdit("34")
        self.redFormula.textChanged.connect(self.update_palette)

        # Green Formula
        self.greenLabel = QLabel("Green Formula:")
        self.greenFormula = QLineEdit("35")
        self.greenFormula.textChanged.connect(self.update_palette)

        # Blue Formula
        self.blueLabel = QLabel("Blue Formula:")
        self.blueFormula = QLineEdit("36")
        self.blueFormula.textChanged.connect(self.update_palette)

        # Add to layout
        h_layout1.addWidget(self.redLabel)
        h_layout1.addWidget(self.redFormula)
        h_layout1.addWidget(self.greenLabel)
        h_layout1.addWidget(self.greenFormula)
        h_layout1.addWidget(self.blueLabel)
        h_layout1.addWidget(self.blueFormula)


        # Equation Text Fields
        self.eqLabel1 = QLabel("Eq. #1:")
        self.eq1 = QLineEdit("x")
        self.eq1.textChanged.connect(self.update_palette)

        self.eqLabel2 = QLabel("Eq. #2:")
        self.eq2 = QLineEdit("x")
        self.eq2.textChanged.connect(self.update_palette)

        self.eqLabel3 = QLabel("Eq. #3:")
        self.eq3 = QLineEdit("x")
        self.eq3.textChanged.connect(self.update_palette)

        # Random Button
        self.randomButton = QPushButton("Random")
        self.randomButton.clicked.connect(self.randomize_formulas)

        # Update Button
        # self.updateButton = QPushButton("Update")
        # self.updateButton.clicked.connect(self.update_palette)

        if False:  # TODO --> really connect this in the future but ok for now
            h_layout2.addWidget(self.eqLabel1)
            h_layout2.addWidget(self.eq1)
            h_layout2.addWidget(self.eqLabel2)
            h_layout2.addWidget(self.eq2)
            h_layout2.addWidget(self.eqLabel3)
            h_layout2.addWidget(self.eq3)
        h_layout2.addWidget(self.randomButton)
        # h_layout2.addWidget(self.updateButton)

        # Text Area
        self.textArea = QTextEdit()
        self.textArea.setReadOnly(True)
        self.textArea.setText(
            "0: 0\t\t\t1: 0.5\t\t\t2: 1\n"
            "3: x\t\t\t4: x^2\t\t\t5: x^3\n"
            "6: x^4\t\t\t7: sqrt(x)\t\t8: sqrt(sqrt(x))\n"
            "9: sin(90*x)\t\t10: cos(90*x)\t\t11: |x-0.5|\n"
            "12: (2*x-1)^2\t\t13: sin(180*x)\t\t14: |cos(180*x)|\n"
            "15: sin(360*x)\t\t16: cos(360*x)\t\t17: |sin(360*x)|\n"
            "18: |cos(360*x)|\t\t19: |sin(720*x)|\t\t20: |cos(720*x)|\n"
            "21: 3*x\t\t\t22: 3*x-1\t\t23: 3*x-2\n"
            "24: |3*x-1|\t\t25: |3*x-2|\t\t26: (3*x-1)/2\n"
            "27: (3*x-2)/2\t\t28: |(3*x-1)/2|\t\t29: |(3*x-2)/2|\n"
            "30: x/0.32-25/32\t\t31: 2*x-0.84\t\t32: x\n"
            "33: |2*x - 0.5|\t\t34: 2*x\t\t\t35: 2*x - 0.5\n"
            "36: 2*x - 1\t\t37: eq. #1\t\t38: eq. #2\n"
            "39: eq. #3\n\n"
            "NB: negative numbers --> returns the negative of the generated palette\n"
            "NB2: I used Gnuplot numbering for equations to promote compatibility between the 2 softwares\n"
            "NB3: the idea of using formulas to create LUTs is coming from Gnuplot"
        )
        # Set the font to monospace
        font = QFont("Courier New", 12)  # You can adjust the font size as needed
        self.textArea.setFont(font)

        # Disable scrollbars
        self.textArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.textArea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # Resize QTextEdit to fit its content
        self.textArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.textArea.setMinimumHeight(360)  # Set a minimum height to ensure it's usable

        formula_layout.addLayout(h_layout1)
        formula_layout.addLayout(h_layout2)
        formula_layout.addWidget(self.textArea)

        self.formula_group.setLayout(formula_layout)
        layout.addWidget(self.formula_group)

        self.setLayout(layout)

        self.update_palette()


    def randomize_formulas(self):
        rand = int(self.randomSign(random.uniform(0, 39)))
        self.redFormula.setText(str(rand))
        rand = int(self.randomSign(random.uniform(0, 39)))
        self.greenFormula.setText(str(rand))
        rand = int(self.randomSign(random.uniform(0, 39)))
        self.blueFormula.setText(str(rand))
        self.update_palette()

    def randomSign(self, nb):
        return nb if random.random() > 0.5 else -nb

    def update_palette(self):
        if self.check_validity():
            # Here, you would call your function to create and update the palette
            self.palette = self.create_palette(
                self.redFormula.text(),
                self.greenFormula.text(),
                self.blueFormula.text(),
                self.eq1.text(),
                self.eq2.text(),
                self.eq3.text()
            )
            self.show_palette()
    def check_validity(self):
        return all([self.redFormula.text(), self.greenFormula.text(), self.blueFormula.text()])

    def create_palette(self, red_formula, green_formula, blue_formula, eq1, eq2, eq3):
        # print('red_formula, green_formula, blue_formula, eq1, eq2, eq3', red_formula, green_formula, blue_formula, eq1, eq2, eq3)
        pc = PaletteCreator()
        # lut = pc.create2(None, str(red_formula)+str(eq1), str(green_formula)+str(eq2), str(blue_formula)+str(eq3))
        lut = pc.create2(f'{str(red_formula)},{ str(green_formula)},{str(blue_formula)}', eq1,eq2, eq3)

        # print('lut', lut)

        # self.show_palette()
        return lut  # Return the LUT for preview

    def show_palette(self):
        if self.palette is not None:
            # print('show_palette called')
            # Compute the total length based on your button dimensions and spacing
            total_length = 760#(button_width * 16) + (spacing * 15)  # Adjust based on columns and spacing
            updateLutLabelPreview(self.palette, self.previewLabel, total_length, height=32)
        else:
            if self.check_validity():
                QMessageBox.warning(self, "No Palette", "No palette to display. Please generate a palette first.")

    def get_palette(self):
        """
        Returns the current LUT.

        :return: The current LUT or None if no LUT has been generated.
        """
        return self.palette


if __name__ == '__main__':
    app = QApplication(sys.argv)
    jar_folder = ""  # Provide the correct path if needed
    ex = PaletteFormulaEditor()
    ex.setWindowTitle('Palette Formula Editor')
    ex.show()
    sys.exit(app.exec_())
