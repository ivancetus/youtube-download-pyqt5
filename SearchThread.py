import random
import time

from PyQt5.QtCore import QThread, pyqtSignal
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait


class SearchThread(QThread):
    callback = pyqtSignal(object)
    search_result = pyqtSignal(object)

    def __init__(self, browser, input_text, url_flag):
        super().__init__(None)
        self.browser = browser
        self.text = input_text
        self.url_flag = url_flag

    def run(self):
        links = {}
        # maxretry = 2
        # retry = 0
        while True:
            self.browser.get(f"https://www.youtube.com/results?search_query={self.text}")
            try:
                # 20秒為Timeout, 會觸發except。每隔 5 秒檢查是否有 id 為 video-title
                delay = WebDriverWait(self.browser, 20, 5)
                delay.until(ec.presence_of_element_located((By.ID, 'video-title')))
                tags = self.browser.find_elements(By.TAG_NAME, "a")
                for tag in tags:
                    href = tag.get_attribute('href')
                    if 'watch' in str(href):
                        title = tag.get_attribute('title')
                        if title == '':
                            try:
                                title = tag.find_element(By.ID, 'video-title').get_attribute('title')
                            except Exception as e:
                                pass
                        if title != '':
                            links[href] = f'{title} url={href}'
                            if self.url_flag:
                                break
                if len(links) > 0:
                    self.search_result.emit(f'Search results: {len(links)} ')
                    break
            except Exception as e:
                self.search_result.emit('Search failed, press reset Browser and try again!')
                break
            # retry += 1
            # if retry == maxretry+1:
            #     self.search_result.emit('Search failed, contact Ivan or restart Youtube Download')
            #     break
            # with open('youtube_download.log', 'a', encoding='UTF-8') as f:
            #     log = f'\nConnection failed, cannot access Youtube\ntime failed: {retry}\npage source:\n'
            #     page = self.browser.page_source
            #     f.write(log+page)
            # self.search_result.emit(f'Search failed, retrying {retry}/{maxretry}...')
            # time.sleep(random.randint(5, 8) + random.random())
        self.callback.emit(links)
