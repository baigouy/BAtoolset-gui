import os
from batoolset.settings.global_settings import set_UI  # set the UI to qtpy
set_UI()
import sys
from qtpy.QtWidgets import QApplication, QFileDialog,QCheckBox, QComboBox
from os.path import expanduser

# parent_window = None, extensions = "Supported Files (*.jpg *.tif *.png);;All Files (*)",
# path = expanduser('~'),
# almost there just add the possibility to chose the extensions by default and the alike stuff!!
class SaveFileDialogWithOptions(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

    def get_widget_values(self):
        return [widget.isChecked() for widget in self.widgets]

    def getOpenFileName(self, parent=None,
                        caption="Select a File",
                        dir=expanduser('~'),
                        filter="All files (*.*)",
                        selectedFilter="",
                        options=None):

        # configuration of the dialog window: make sure it's complete!
        self.setWindowTitle(caption)
        self.setDirectory(dir)
        self.setNameFilter(filter)
        self.setFileMode(QFileDialog.AnyFile)
        self.setAcceptMode(QFileDialog.AcceptOpen)  # "Open" button
        if selectedFilter != "":
            self.selectNameFilter(selectedFilter)
        if options != None:
            self.setOptions(options)

        self.setOption(QFileDialog.DontUseNativeDialog, True)

        layout = self.layout()

        if self.widgets:
            for iii, widget in enumerate(self.widgets):
                layout.addWidget(widget, 4+iii, 0, 1, 4)

        # user interaction and result return
        if self.exec_():
            widget_values = self.get_widget_values()
            return widget_values, list(self.selectedFiles())[0]
        else:
            return ""


class OpenFileDialogWithOptions(QFileDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.widgets = []

    def add_widget(self, widget):
        self.widgets.append(widget)

    def get_widget_values(self):
        return [widget.isChecked() for widget in self.widgets]

    def getSaveFileName(self, parent=None,
                        caption="Save a File",
                        dir=expanduser('~'),
                        filter="All files (*.*)",
                        selectedFilter="",
                        options=None):

        # configuration of the dialog window: make sure it's complete!
        self.setWindowTitle(caption)
        self.setDirectory(dir)
        self.setNameFilter(filter)
        self.setFileMode(QFileDialog.AnyFile)
        self.setAcceptMode(QFileDialog.AcceptSave)  # "Save" button
        if selectedFilter != "":
            self.selectNameFilter(selectedFilter)
        if options != None:
            self.setOptions(options)

        self.setOption(QFileDialog.DontUseNativeDialog, True)

        layout = self.layout()

        if self.widgets:
            for iii, widget in enumerate(self.widgets):
                layout.addWidget(widget, 4+iii, 0, 1, 4)

        # user interaction and result return
        if self.exec_():
            widget_values = self.get_widget_values()
            return widget_values, self.selectedFiles()[0]
        else:
            return ""

def saveFileWithOptions():
    fileDialog = SaveFileDialogWithOptions()

    # Add checkboxes
    fileDialog.add_widget(QCheckBox("consolidate"))
    fileDialog.add_widget(QCheckBox("blabla_bli"))

    return fileDialog.getOpenFileName()
    # print("Widget values:", result[0])
    # print("Selected file:", result[1])

def openFileNameDialog(parent_window=None, extensions="Supported Files (*.jpg *.tif *.png);;All Files (*)",
                       path=expanduser('~')):
    """
    Opens a file dialog to select a single file.

    Args:
        parent_window (object): Parent window object. Default is None.
        extensions (str): File extension filters for the dialog. Default is "Supported Files (*.jpg *.tif *.png);;All Files (*)".
        path (str): Initial path for the dialog. Default is user's home directory.

    Returns:
        str: Selected file name.

    # Examples:
    #     >>> filename = openFileNameDialog()
    """
    if not os.path.exists(path):
        path = expanduser('~')
    fileName, _ = QFileDialog.getOpenFileName(parent_window, "Select a File", path, extensions,
                                              options=QFileDialog.DontUseNativeDialog)
    return fileName


def openFileNamesDialog(parent_window=None, extensions="Supported Files (*.jpg *.tif *.png);;All Files (*)",
                        path=expanduser('~')):
    """
    Opens a file dialog to select multiple files.

    Args:
        parent_window (object): Parent window object. Default is None.
        extensions (str): File extension filters for the dialog. Default is "Supported Files (*.jpg *.tif *.png);;All Files (*)".
        path (str): Initial path for the dialog. Default is user's home directory.

    Returns:
        list: List of selected file names.

    # Examples:
    #     >>> files = openFileNamesDialog()
    """
    if not os.path.exists(path):
        path = expanduser('~')
    files, _ = QFileDialog.getOpenFileNames(parent_window, "Select Files", path, extensions,
                                            options=QFileDialog.DontUseNativeDialog)
    return files


def saveFileDialog(parent_window=None, path=expanduser('~'), extensions="All Files (*);;Text Files (*.txt)",
                    default_ext=None):
    """
    Opens a file dialog to save a file.

    Args:
        parent_window (object): Parent window object. Default is None.
        path (str): Initial path for the dialog. Default is user's home directory.
        extensions (str): File extension filters for the dialog. Default is "All Files (*);;Text Files (*.txt)".
        default_ext (str): Default file extension. Default is None.

    Returns:
        str: Selected file name to save.

    # Examples:
    #     >>> filename = saveFileDialog(default_ext='.tif')
    """
    try:
        if not os.path.exists(path) and not os.path.exists(os.path.dirname(path)):
            path = expanduser('~')
    except:
        path = expanduser('~')
    fd = QFileDialog(parent_window, "Save a File", path, extensions, options=QFileDialog.DontUseNativeDialog)
    if default_ext is not None:
        fd.setDefaultSuffix(default_ext)
    fd.setAcceptMode(QFileDialog.AcceptSave)
    selected = fd.exec()
    if selected:
        fileName = fd.selectedFiles()[0]
        return fileName
    else:
        return


def openDirectoryDialog(parent_window=None, path=expanduser('~')):
    """
    Opens a dialog to select a directory.

    Args:
        parent_window (object): Parent window object. Default is None.
        path (str): Initial path for the dialog. Default is user's home directory.

    Returns:
        str: Selected directory path.

    # Examples:
    #     >>> folder = openDirectoryDialog()
    """
    if not os.path.exists(path):
        path = expanduser('~')
    folderName = QFileDialog.getExistingDirectory(parent_window, "Select a Directory", path,
                                                  options=QFileDialog.DontUseNativeDialog)
    if folderName is not None:
        if not folderName.strip():
            return None
        if not folderName.endswith("/") and not folderName.endswith("\\"):
            folderName += '/'
    return folderName


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # filename = saveFileDialog(default_ext='.tif')

    filename = saveFileWithOptions() # I can add options to this stuff and the content of the options is saved

    # TODO --> finalize that to make it really usable
    # or pop a widow first for parameters then for saving or vice versa -−> maybe simpler for now
    # try that on windows to see if that works

    print(filename)
    sys.exit(0)
