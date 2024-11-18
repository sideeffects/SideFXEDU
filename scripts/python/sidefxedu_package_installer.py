import hou
import sys

if sys.version_info.major >= 3:
    from urllib.request import urlopen, Request
else:
    from urllib2 import urlopen, Request

from hutil.Qt.QtCore import *
from hutil.Qt.QtGui import *
from hutil.Qt.QtWidgets import *

RELEASE_URL = "https://github.com/sideeffects/SideFXEDU/releases/download/20.5.421/SideFXEDU20.5.zip"
PACKAGE_FILE_PATH = "~/Downloads/SideFXEDU20.5.zip"

# --- begin
# Some users ran into this error:
# URLError: <urlopen error [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1006)>
# It might be due to an issue with the configuration of Houdini's Python. We add this bit of code to the top of the script as a workaround
import os
import certifi
os.environ["SSL_CERT_FILE"] = certifi.where()
# --- end


class Downloader(QThread):

    # Signal for the window to establish the maximum value
    # of the progress bar.
    setTotalProgress = Signal(int)
    # Signal to increase the progress.
    setCurrentProgress = Signal(int)
    # Signal to be emitted when the file has been downloaded successfully.
    succeeded = Signal()

    def __init__(self, url, filename):
        super().__init__()
        self._url = url
        self._filename = os.path.expanduser(filename)

    def run(self):
        url = self._url
        filename = self._filename

        readBytes = 0
        chunkSize = 1024
        # Open the URL address.
        with urlopen(url) as r:
            # Tell the window the amount of bytes to be downloaded.
            self.setTotalProgress.emit(int(r.info()["Content-Length"]))
            with open(filename, "ab") as f:
                while True:
                    # Read a piece of the file we are downloading.
                    chunk = r.read(chunkSize)
                    # If the result is `None`, that means data is not
                    # downloaded yet. Just keep waiting.
                    if chunk is None:
                        continue
                    # If the result is an empty `bytes` instance, then
                    # the file is complete.
                    elif chunk == b"":
                        break
                    # Write into the local file the downloaded chunk.
                    f.write(chunk)
                    readBytes += chunkSize
                    # Tell the window how many bytes we have received.
                    self.setCurrentProgress.emit(readBytes)
        # If this line is reached then no exception has ocurred in
        # the previous lines.
        self.succeeded.emit()


class UpdateDialog(QDialog):
    def __init__(self, parent):
        super(UpdateDialog, self).__init__(parent)
        self.setWindowTitle("SideFX EDU Updater")
        self.build_ui()

    def build_ui(self):
        layout = QVBoxLayout()
        self.label = QLabel("Press the button to start downloading.", self)
        self.label.setGeometry(20, 20, 200, 25)
        self.button = QPushButton("Download and Install", self)
        self.button.pressed.connect(self.initDownload)
        self.progressBar = QProgressBar(self)
        self.progressBar.setGeometry(20, 115, 300, 25)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancelbtn_press)

        button_layout = QHBoxLayout()
        # button_layout.addWidget(spacer)
        button_layout.addWidget(self.button)
        button_layout.addWidget(self.cancel_button)


        layout.addWidget(self.label)
        layout.addWidget(self.progressBar)
        # layout.addWidget(self.button)
        # layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)


        self.setLayout(layout)

    def on_cancelbtn_press(self):
        self.close()

    def initDownload(self):
        self.label.setText("Downloading file...")
        # Initialize the progress bar to empty
        self.progressBar.setValue(self.progressBar.minimum())
        # Disable the button while the file is downloading.
        self.button.setEnabled(False)
        # Run the download in a new thread.
        self.downloader = Downloader(RELEASE_URL, PACKAGE_FILE_PATH)
        # Connect the signals which send information about the download
        # progress with the proper methods of the progress bar.
        self.downloader.setTotalProgress.connect(self.progressBar.setMaximum)
        self.downloader.setCurrentProgress.connect(self.progressBar.setValue)
        # Qt will invoke the `succeeded()` method when the file has been
        # downloaded successfully and `downloadFinished()` when the
        # child thread finishes.
        self.downloader.succeeded.connect(self.downloadSucceeded)
        self.downloader.finished.connect(self.downloadFinished)
        self.downloader.start()

    def downloadSucceeded(self):
        # Set the progress at 100%.
        self.progressBar.setValue(self.progressBar.maximum())
        self.label.setText("The file has been downloaded!")

    def downloadFinished(self):
        # Restore the button.
        self.button.setEnabled(True)
        # Delete the thread when no longer needed.
        del self.downloader


class SideFXEDUUpdater(object):
    """ Main updater object, gets called with the shelf button press
    """

    def __init__(self, updater_dialog=False):
        disabling_message = os.getenv("SIDEFXEDU_NOINSTALL_MESSAGE")
        if disabling_message:
            if updater_dialog:
                hou.ui.displayMessage(disabling_message)
                return
            else:
                return disabling_message

        if updater_dialog:
            self.show_updater_dialog()

    def show_updater_dialog(self):
        dialog = UpdateDialog(hou.qt.mainWindow())
        dialog.show()


# hou.ui.loadPackageArchive(package_file_path)
