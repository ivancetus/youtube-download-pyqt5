import os
import time

from PyQt5.QtCore import QThread, pyqtSignal
from pytube import YouTube


class DownloadThread(QThread):
    callback = pyqtSignal(object)
    finished = pyqtSignal(object)

    def __init__(self, browser, chks, path, style):
        super().__init__(None)
        self.browser = browser
        self.chks = chks
        self.path = path
        self.style = style

    def increment_filename(self, f):
        fnew = f
        root, ext = os.path.splitext(f)
        i = 1
        while os.path.exists(fnew):
            i += 1
            fnew = '%s_%i%s' % (root, i, ext)
        return fnew

    def get_filename(self, file, style):
        return os.path.basename(self.increment_filename(os.path.join(self.path, f'{file}.{style.lower()}')))

    def run(self):
        for i, chk in enumerate(self.chks):
            file, url = chk.split(' url=')
            file = file.replace("\\", "").replace("/", "_").replace(":", "_").replace("*", "") \
                .replace("?", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "").replace(' ', '')
            self.callback.emit(f'Downloading {file}...')
            yt = YouTube(url)
            if self.style == 'MP3':
                file = self.get_filename(file, self.style)
                yt.streams.filter().get_audio_only()\
                    .download(output_path=self.path, filename=file)
            elif self.style == 'MP4':
                file = self.get_filename(file, self.style)
                yt.streams.filter(progressive=True, file_extension='mp4')\
                    .order_by('resolution')\
                    .desc().first()\
                    .download(output_path=self.path, filename=file)
            self.callback.emit(f'{file} Done. ({i + 1}/{len(self.chks)})...')
            time.sleep(2)
            if i + 1 != len(self.chks):
                self.callback.emit('Downloading next...')
                time.sleep(2)
            else:
                self.finished.emit('Download finished.')
