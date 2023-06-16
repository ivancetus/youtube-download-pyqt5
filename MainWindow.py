import ctypes
import json
import os
import os.path
import platform
import sys

from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, QCheckBox, QListWidgetItem, QFileDialog
from BrowserThread import BrowserThread
from DownloadThread import DownloadThread
from SearchThread import SearchThread
from img.pic_string import favicon_ico
from ui.ui_mainwindow import Ui_MainWindow


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowTitle('Youtube Download -Ivan')
        self.resize(1280, 720)
        self.url_flag = False
        self.input_text = None
        self.browser = None
        self.browserThread = None
        self.searchThread = None
        self.downloadThread = None
        self.titles = []
        self.urls = []
        self.checkOs = self.win_or_mac()
        if os.path.exists("path.json"):
            with open("path.json", 'r') as f:
                self.path = json.load(f)
        else:
            if self.checkOs == 'Windows':
                self.path = "C:\\youtube_tmp"
            elif self.checkOs == 'Darwin':
                self.path = "/Users/youtube_tmp"
            else:
                self.lblStatus.setText("OS not supported!")
        self.lblPath.setText(self.path)
        if not os.path.exists(self.path):
            os.mkdir(self.path)
        self.disable_gui()
        # BrowserThread
        self.browserThread = BrowserThread(self.path)
        self.browserThread.callback.connect(self.browser_thread_callback)
        self.browserThread.start()

        self.btnReset.clicked.connect(self.btn_reset_clicked)
        self.btnSearch.clicked.connect(self.btn_search_clicked)
        self.btnDownload.clicked.connect(self.btn_download_clicked)
        self.btnPath.clicked.connect(self.btn_path_clicked)

        # press Enter to search
        self.txtInput.installEventFilter(self)

    def btn_reset_clicked(self):
        self.listWidget.clear()
        self.browser.quit()
        self.disable_gui()
        self.browserThread = BrowserThread(self.path)
        self.browserThread.callback.connect(self.browser_thread_callback)
        self.browserThread.start()

    def btn_search_clicked(self):
        self.listWidget.clear()
        self.input_text = self.txtInput.text()
        if self.input_text == '':
            dialog = QMessageBox()
            dialog.setWindowTitle('Youtube Download')
            dialog.setText("Search bar is empty!")
            dialog.exec()
            return
        self.lblStatus.setText('Searching...')
        self.disable_gui()
        # SearchThread
        if self.input_text.startswith('https://www.youtube.com/watch?v='):
            self.url_flag = True
        self.searchThread = SearchThread(self.browser, self.input_text, self.url_flag)
        self.searchThread.callback.connect(self.search_thread_callback)
        self.searchThread.search_result.connect(self.search_thread_result)
        self.searchThread.start()

    def btn_download_clicked(self):
        style = ''
        if self.rbtnMP3.isChecked():
            style = 'MP3'
        elif self.rbtnMP4.isChecked():
            style = 'MP4'
        count = self.listWidget.count()
        if count < 1:
            dialog = QMessageBox()
            dialog.setWindowTitle("Youtube Download")
            dialog.setText("Search some stuff first!")
            dialog.exec()
            return
        boxes = [self.listWidget.itemWidget(self.listWidget.item(i)) for i in range(count)]
        checked = []
        for i, box in enumerate(boxes):
            if box.isChecked():
                file = f'{box.text()} url={self.urls[i]}'
                checked.append(file)
        self.disable_gui()
        # DownloadThread
        self.downloadThread = DownloadThread(self.browser, checked, self.path, style)
        self.downloadThread.callback.connect(self.download_thread_callback)
        self.downloadThread.finished.connect(self.download_thread_finished)
        self.downloadThread.start()

    def btn_path_clicked(self):
        path = QFileDialog.getExistingDirectory()
        if path != '':
            # if file cannot be saved, try different path slashes
            if self.checkOs == 'Windows':
                self.path = path.replace("/", "\\")
            elif self.checkOs == 'Darwin':
                self.path = path
            with open("path.json", 'w') as f:
                json.dump(self.path, f)
            self.lblPath.setText(self.path)

    def browser_thread_callback(self, browser):
        self.browser = browser
        self.lblStatus.setText('Search as if using Youtube or just URL.')
        self.enable_gui()
        self.url_flag = False

    def search_thread_result(self, msg):
        self.lblStatus.setText(msg)

    def search_thread_callback(self, links):
        self.enable_gui()
        self.setStyleSheet('''
            QCheckBox::indicator{
                width: 18px;
                height: 18px;
            }
        ''')
        if links is not None:
            for key in links.keys():
                item = QListWidgetItem()
                title, url = links[key].split(' url=')
                box = QCheckBox(title)
                self.listWidget.addItem(item)
                self.titles.append(title)
                self.urls.append(url)
                self.listWidget.setItemWidget(item, box)

    def download_thread_callback(self, msg):
        self.lblStatus.setText(msg)

    def download_thread_finished(self, msg):
        self.lblStatus.setText(msg)
        self.enable_gui()

    def eventFilter(self, source, event):
        if event.type() == QEvent.KeyPress and source is self.txtInput:
            if event.text() == '\r':
                self.btn_search_clicked()
        return super(MainWindow, self).eventFilter(source, event)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, "Youtube Download", "Quit app?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.browser.quit()
            event.accept()
        else:
            event.ignore()

    def disable_gui(self):
        self.txtInput.setDisabled(True)
        self.btnSearch.setDisabled(True)
        self.btnDownload.setDisabled(True)
        self.btnPath.setDisabled(True)
        self.btnReset.setDisabled(True)
        self.rbtnMP3.setDisabled(True)
        self.rbtnMP4.setDisabled(True)

    def enable_gui(self):
        self.txtInput.setEnabled(True)
        self.btnSearch.setEnabled(True)
        self.btnDownload.setEnabled(True)
        self.btnPath.setEnabled(True)
        self.btnReset.setEnabled(True)
        self.rbtnMP3.setEnabled(True)
        self.rbtnMP4.setEnabled(True)

    @staticmethod
    def icon_from_base64(base64):
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(QtCore.QByteArray.fromBase64(base64))
        icon = QtGui.QIcon(pixmap)
        return icon

    @staticmethod
    def win_or_mac():
        return platform.system()


if __name__ == '__main__':
    if MainWindow.win_or_mac() == 'Windows':
        myAppId = u'myCompany.myProduct.subProduct.version'  # arbitrary string, unicode
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myAppId)

    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon(MainWindow.icon_from_base64(favicon_ico)))
    mainWindow = MainWindow()
    mainWindow.show()
    app.exec()
