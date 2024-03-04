#根据用户点击历史分析兴趣
from urllib.parse import urlparse
from collections import Counter

def get_interest():
    file_path = "search_history.txt" 

    # 读取文件，并提取主机名
    with open(file_path, 'r') as file:
        urls = file.readlines()

    host_names = []
    for url in urls:
        parsed_url = urlparse(url.strip())  # 移除换行符等空白字符
        host_name = parsed_url.netloc
        host_names.append(host_name)

    host_counts = Counter(host_names)

    # print(host_counts)
    sorted_clicks = sorted(host_counts.items(), key=lambda x: x[1], reverse=True)
    return(host_counts)
    # print(host_names)
