from elasticsearch import Elasticsearch
from spider import getData,askURL

es = Elasticsearch(host="localhost",port=9200,timeout=3600)

index_name = 'music'

# 将爬取的数据逐条存入ES
def save_to_es(data):
    for idx, data in enumerate(data, start=3670):
        es.index(index=index_name, doc_type='_doc', id=idx, body={
            'link': data[0],
            'title': data[1],
            'text': data[2]
        })

def main():
    baseurl = "https://movie.douban.com/top250?start="
    datalist = getData(baseurl)
    save_to_es(datalist)

if __name__ == "__main__":
    main()