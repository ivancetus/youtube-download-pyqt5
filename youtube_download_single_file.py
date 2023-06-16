from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from pytube import YouTube


def chrome_browser():
    opt = Options()
    ser = Service(ChromeDriverManager().install())
    """
    disable headless, enable detach when debugging, if page not loading, try disable user_agent
    """
    opt.add_argument('--headless')
    # opt.add_experimental_option("detach", True)

    user_agent = UserAgent()  # random header info
    opt.add_argument('--user-agent=%s' % user_agent.random)
    opt.add_argument('--disable-gpu')
    opt.add_experimental_option("excludeSwitches", ["enable-logging"])
    opt.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=ser, options=opt)

def search(browser, url, max_retry=5):
    title_href = ""
    retry = 0
    while max_retry+1 > retry :
        try:
            if not browser:
                print("browser restart")
                browser = chrome_browser()
            browser.get(url)
            WebDriverWait(browser, 20, 5).until(ec.presence_of_element_located((By.ID, 'video-title')))
        except Exception as e:
            print("error loading page\nmessage:\n", e)
            retry += 1
            continue
        try:
            tags = browser.find_elements(By.TAG_NAME, "a")
        except:
            print("error no a-tags found")
            retry += 1
            continue
        for tag in tags:
            href = tag.get_attribute('href')
            if 'watch' in str(href):
                title = tag.get_attribute('title')
                if title == '':
                    try:
                        title = tag.find_element(By.ID, 'video-title').get_attribute('title')
                    except:
                        pass
                if title != '':
                    title_href = f'{title} href={href}'
                    break
        if title_href == "":
            print("title_href is empty, retrying...")
            browser.quit()
            retry += 1
        else:
            print("search complete!")
            break
    browser.quit()
    return title_href

def download(title_href, file_format, output_path):
    print("initiate download...")
    if title_href is None:
        return "something went wrong, title and href not found"
    title, href = title_href.split(" href=")
    file_name = title.replace("\\", "").replace("/", "_").replace(":", "_").replace("*", "") \
        .replace("?", "").replace("\"", "").replace("<", "").replace(">", "").replace("|", "").replace(' ', '')
    yt = YouTube(href)
    file_w_extension = f'{file_name}.{file_format.lower()}'
    if file_format == 'MP3':
        yt.streams.filter()\
            .get_audio_only()\
            .download(output_path=output_path, filename=file_w_extension)
    elif file_format == 'MP4':
        yt.streams.filter(progressive=True, file_extension='mp4')\
            .order_by('resolution')\
            .desc()\
            .first()\
            .download(output_path=output_path, filename=file_w_extension)
    else:
        print("something went wrong, not valid file format (MP3 or MP4)")


if __name__ == '__main__':
    youtubeUrl = "https://www.youtube.com/watch?v=Hu3Q9t6H4yw"
    searchUrl = f"https://www.youtube.com/results?search_query={youtubeUrl}"
    fileFormat = 'MP3'
    # fileFormat = 'MP4'
    outputPath = "C:\\youtube_tmp"
    try:
        download(search(chrome_browser(), searchUrl), fileFormat, outputPath)
        print("download finished!")
    except Exception as e:
        print("error\nmessage:\n", e)


