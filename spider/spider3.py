import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib import robotparser
from urllib.robotparser import RobotFileParser
from urllib.request import urlopen
import pandas as pd
import urllib.request, urllib.error  # 制定URL，获取网页数据
import newspaper
import ssl
import re
import cchardet
ssl._create_default_https_context = ssl._create_unverified_context

from elasticsearch import Elasticsearch

es = Elasticsearch(host="localhost",port=9200,timeout=3600)

index_name = 'music'
# es.indices.create(index=index_name, ignore=400)  # 忽略index已存在的情况

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

urls = []
visited_urls = set()
new_urls = []
# existing_data = pd.read_csv('data.csv')
datalist=[]
number=38918



# 将爬取的数据逐条存入ES
def save_to_es(data,data_no):
        es.index(index=index_name, doc_type='_doc', id=data_no, body={
            'link': data[0],
            'title': data[1],
            'text': data[2]
        })


def get_page(url):
    global number
    try:
        # 检查 robots.txt 是否允许访问当前 URL
        rp = robotparser.RobotFileParser()
        rp.set_url(url + "/robots.txt")  # 通过 robots.txt 的 URL 设置
        rp.read()
        if rp.can_fetch('*', url)==False:
            print(f"不允许访问 {url}，跳过")
            return
        html = askURL(url)  # 保存获取到的网页源码

        
        soup = BeautifulSoup(html, "html.parser")
        data = []
        if soup.title:
            title_text = soup.title.get_text()
        else:
            return
        data.append(url)
        data.append(title_text)
        intr=""
        tags = soup.find_all('meta')
        for tag in tags :
            content = tag.get('content')
            if content:
                intr += content + " "
        # chinese_characters = re.findall(r'[\u4e00-\u9fff]', intr)
        # # intr=intr.replace('text/html; charset=utf-8', '').strip()
        # chinese_text = ''.join(chinese_characters)
        data.append(intr)

        
        # meta_contents = [meta['content'] for meta in soup.select('meta[content]')]
        # data.append(meta_contents)


        # df = pd.DataFrame(data, columns=['url', 'title'])
        # df.to_csv('data.csv', mode='a', header=False, index=False)
        # new_data = pd.DataFrame(data)
        # updated_data = pd.concat([existing_data, new_data])
        # updated_data.to_csv('data.csv', mode='a', header=False, index=False)
        links = soup.find_all('a')
        for link in links:
            href = link.get('href')  # 获取链接
            if href and href.startswith('https'):
                # href = 'https:'+ href
                urls.append(href)  
        save_to_es(data,number)
        number+=1
        print("data",data)
    except requests.RequestException as e:
        print(f"Error occurred while fetching {url}: {e}")
        # Skip to the next URL in case of an error
        return
    # time.sleep(1)  # 设置延迟时间为1秒



# 得到指定一个URL的网页内容
def askURL(url):
    head = {  # 模拟浏览器头部信息，向豆瓣服务器发送消息
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
    }
    resp = requests.get(url, headers=headers)
    data = resp.content

    # 使用 chardet 检测编码
    encoding = cchardet.detect(data)['encoding']

    # 解码文本
    html = data.decode(encoding)

    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html

    # request = urllib.request.Request(url, headers=head)
    # html = ""
    # try:
    #     resp = requests.get(url, headers=headers, stream=True)
    #     if resp.encoding == 'utf-8':
    #         try:
    #             html = resp.text.encode('utf8').decode('utf8')
    #         except Exception:
    #             if resp.encoding == 'gbk':
    #                 try:
    #                     html = resp.text.encode('gbk').decode('gbk')
    #                 except Exception:
    #                     return
    #     else:
    #         html = resp.text.encode(resp.encoding, 'ignore').decode(resp.encoding, 'ignore')
    # except urllib.error.URLError as e:
    #     if hasattr(e, "code"):
    #         print(e.code)
    #     if hasattr(e, "reason"):
    #         print(e.reason)

    return html

def crawl_recursive(urls_to_crawl, max_depth, visited):
    if max_depth <= 0 or not urls_to_crawl:
        return
    
    for url in urls_to_crawl:
        if url in visited:
            continue
        visited.add(url)
        if(url):
            links = get_page(url)
            if links:
                new_urls.extend(links)

    crawl_recursive(new_urls, max_depth - 1, visited)


start_url = 'https://news.nankai.edu.cn/'
urls.append(start_url)
crawl_recursive(urls, max_depth=2, visited=visited_urls)


# def main():
#     start_url = 'https://www.bilibili.com/'
#     urls.append(start_url)
#     crawl_recursive(urls, max_depth=2, visited=visited_urls)
#     baseurl = "https://movie.douban.com/top250?start="
#     datalist = getData(baseurl)
#     save_to_es(datalist)

# if __name__ == "__main__":
#     main()

# df = pd.DataFrame(urls)

# df.to_csv('search_results.csv', index=False)
