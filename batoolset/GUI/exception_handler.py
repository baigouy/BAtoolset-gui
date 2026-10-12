"""Qt-safe global exception handler.

Under PyQt6, an unhandled Python exception that propagates out of a slot, timer
callback or event handler makes Qt call ``qFatal()``/``abort()``. On Windows that
surfaces as a hard crash with exit code ``0xC0000409``
(STATUS_STACK_BUFFER_OVERRUN) — the whole application dies with no message and no
traceback, so it looks like a native stack overflow even though it is just a
Python exception (e.g. a UnicodeEncodeError while autosaving).

The important detail: PyQt only calls ``qFatal()`` when the *default*
``sys.excepthook`` is installed. Installing a non-default hook both suppresses the
abort (the app keeps running) and lets us log the error and warn the user.
"""
import sys
import traceback

from batoolset.tools.logger import TA_logger

logger = TA_logger()

_original_excepthook = sys.excepthook
_reporting = False  # guard against re-entrancy while a dialog is being shown


def _show_dialog(short, details):
    """Best-effort warning dialog; never let the reporter itself raise."""
    try:
        from qtpy.QtWidgets import QApplication, QMessageBox
        if QApplication.instance() is None:
            return
        box = QMessageBox()
        box.setIcon(QMessageBox.Warning)
        box.setWindowTitle('An error occurred')
        box.setText(short)
        box.setInformativeText(
            'The application will keep running, but the last action may not have '
            'completed. Details are in the log.')
        box.setDetailedText(details)
        box.setStandardButtons(QMessageBox.Ok)
        box.exec_()
    except Exception:
        pass


def global_excepthook(exctype, value, tb):
    """Log the exception and warn the user instead of aborting the process."""
    # keep Ctrl+C / normal interpreter-exit behaviour
    if issubclass(exctype, (KeyboardInterrupt, SystemExit)):
        _original_excepthook(exctype, value, tb)
        return

    details = ''.join(traceback.format_exception(exctype, value, tb))
    try:
        logger.error('Unhandled exception (suppressed to keep the app alive):\n' + details)
    except Exception:
        sys.stderr.write(details)

    global _reporting
    if _reporting:
        # already showing a dialog (or we faulted while reporting) — don't stack them
        return
    _reporting = True
    try:
        _show_dialog(f'{exctype.__name__}: {value}', details)
    finally:
        _reporting = False


def install_global_exception_handler():
    """Install the Qt-safe global exception hook. Idempotent."""
    if getattr(sys, '_batoolset_excepthook_installed', False):
        return
    sys.excepthook = global_excepthook
    sys._batoolset_excepthook_installed = True
