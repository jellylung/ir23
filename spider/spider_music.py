import requests
import json
import re
import urllib.request, urllib.error  # 制定URL，获取网页数据
from lxml import etree
from elasticsearch import Elasticsearch
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

es = Elasticsearch(host="localhost",port=9200,timeout=3600)

proxies = { "http": None, "https": None}

# 创建一个index（索引），表示存储数据的库
index_name = 'music'  # 假设你想将电影数据存储在名为 "movies" 的index中
# es.indices.create(index=index_name, ignore=400)  # 忽略index已存在的情况

headers = {
    'Referer': 'http://music.163.com',
    'Host': 'music.163.com',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'User-Agent': 'Chrome/10'
}


def getlirics(music_id):
    #我们这里以周杰伦的“布拉格广场”为例，id=210049
    headers={"User-Agent" : "Mozilla/5.0(Windows NT 10.0; WOW64) AppleWebKit/537.36(KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36 ",
    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language" : "zh-CN,zh;q=0.9",
    "Connection" : "keep-alive",
    "Accept-Charset" : "GB2312,utf-8;q=0.7,*;q=0.7"}
    url = 'http://music.163.com/api/song/lyric?'+ 'id=' + music_id + '&lv=1&kv=1&tv=-1'

    r = requests.get(url,headers=headers,allow_redirects=False,proxies=proxies)
    #allow_redirects设置为重定向的参数
    #headers=headers添加请求头的参数，冒充请求头

    #用js将获取的歌词源码进行解析
    json_obj = r.text#.text返回的是unicode 型的数据，需要解析
    j = json.loads(json_obj)#进行json解析
    words = j['lrc']['lyric'] #将解析后的歌词存在words变量中

    #解析后的歌词发现每行歌词前面有时间节点，将它进行美化一下：
    pattern = '\\(.*?\\)|\\{.*?}|\\[.*?]'
    text1 = re.sub(pattern, "", words)#用正则表达式将时间剔除
    return text1

def getmusicid(url):
    # 2.逐一解析数据

    res = requests.request('GET',url,headers=headers)
    # 用xpath 解析热门前50的歌曲信息
    html = etree.HTML(res.text)
    abs_load = html.xpath('//tr[2]')   
    print(abs_load)

# 得到指定一个URL的网页内容
def askURL(url):
    head = {  # 模拟浏览器头部信息，向豆瓣服务器发送消息
        "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 80.0.3987.122  Safari / 537.36"
    }
    # 用户代理，表示告诉豆瓣服务器，我们是什么类型的机器、浏览器（本质上是告诉浏览器，我们可以接收什么水平的文件内容）

    request = urllib.request.Request(url, headers=headers)
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

def get_songs(artist_id):
    page_url = 'https://music.163.com/artist?id=' + artist_id
    # 获取网页 HTML
    res = requests.request('GET',page_url,headers=headers,proxies=proxies)
    # 用xpath 解析热门前50的歌曲信息
    html = etree.HTML(res.text)
    href_xpath = "//*[@id='hotsong-list']//a/@href"
    name_xpath = "//*[@id='hotsong-list']//a/text()"
    # href_xpath = "//*[@id='hotsong-list']//a/@href"
    # name_xpath = "//*[@id='hotsong-list']//a/text()"
    hrefs = html.xpath(href_xpath)
    names = html.xpath(name_xpath)
    # 设置热门歌曲的ID，歌曲名称
    song_ids = []
    song_names = []
    for href,name in zip(hrefs,names):
        song_ids.append(href[9:])
        song_names.append(name)
        # print(href[9:],' ',name)
    return song_ids,song_names    


def save_to_es(datalist):
    for idx, data in enumerate(datalist, start=1):
        es.index(index=index_name, id=idx+11020, document={
            'link': data[0],
            'title': data[1],
            'text': data[2]
        })



id='12487174'
list=get_songs(id)
datalist=[]
for i in range(6,50):
    data=[]
    link="https://music.163.com/#/song?id="+list[0][i]
    data.append(link)#link
    data.append(list[1][i])#title
    lirics=getlirics(list[0][i])
    data.append(lirics)
    datalist.append(data)
    print(data)

save_to_es(datalist)


# url='https://music.163.com/#/playlist?id=542272629'
# data=getmusicid(url)

