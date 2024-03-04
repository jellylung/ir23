#保存网页快照

import os
import hashlib
from selenium import webdriver
from PIL import Image
from io import BytesIO
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

options = webdriver.ChromeOptions()
options.add_argument('--headless')  # 无头模式，不弹出浏览器窗口
driver = webdriver.Chrome(options=options)
driver.set_window_size(1920, 1080)
page_link = 'https://epaper.gmw.cn/gmrb/html/2009-10/30/nw.D110000gmrb_20091030_2-03.htm?div=-1'
snapshot_dir = 'snapshots'
if not os.path.exists(snapshot_dir):
    os.makedirs(snapshot_dir)

def save_full_screenshot(link):
    filename = hashlib.md5(link.encode('utf-8')).hexdigest() + '.png'
    filepath = os.path.join(snapshot_dir, filename)

    driver.get(link)
    total_height = driver.execute_script("return document.body.scrollHeight")

    part_height = 1000
    screenshot = Image.new('RGB', (1920, total_height))

    for i in range(0, total_height, part_height):
        if i + part_height < total_height:
            driver.execute_script(f"window.scrollTo(0, {i});")
            part = driver.get_screenshot_as_png()
            part = Image.open(BytesIO(part))
            screenshot.paste(part, (0, i))
        else:
            driver.execute_script(f"window.scrollTo(0, {total_height});")
            part = driver.get_screenshot_as_png()
            part = Image.open(BytesIO(part))
            screenshot.paste(part, (0, total_height - part_height))

    screenshot.save(filepath)
    return filepath


screenshot_path = save_full_screenshot(page_link)
print(f'Screenshot saved at: {screenshot_path}')

# 关闭浏览器
driver.quit()
