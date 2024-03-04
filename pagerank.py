#链接分析

from elasticsearch import Elasticsearch
import networkx as nx
import requests
from bs4 import BeautifulSoup

es = Elasticsearch(host="localhost", port=9200, timeout=3600)

index_name = 'music'

def fetch_data_from_es():
    res = es.search(index=index_name, body={"query": {"match_all": {}}},size=50)
    return res['hits']['hits']

def extract_links_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [link.get('href') for link in soup.find_all('a') if link.get('href').startwith("http")]
        return links
    except Exception as e:
        print(f"Error fetching links from {url}: {e}")
        return []

def build_graph(data):
    graph = nx.DiGraph()

    for item in data:
        link = item['_source']['link']
        graph.add_node(link)
        
        links_in_url = extract_links_from_url(link)
        for link_in_url in links_in_url:
            
            graph.add_edge(link, link_in_url)

    return graph

def calculate_pagerank(graph):
    pagerank = nx.pagerank(graph)
    return pagerank

data_from_es = fetch_data_from_es()
graph_data = build_graph(data_from_es)
pagerank_result = calculate_pagerank(graph_data)

