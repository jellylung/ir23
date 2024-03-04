from flask import Flask, request, render_template, redirect, url_for
from search import select,select2,select3
import logging
import os
import hashlib
from flask import send_from_directory

# 配置日志记录器
logging.basicConfig(
    filename='app.log',  
    level=logging.INFO,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'  
)

app = Flask(__name__)
start_page=0

@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'POST' and request.form.get('query') and request.form.get('webdns'):
        query = request.form['query']
        webdns= request.form['webdns']
        logging.info(f"User searched for: {query} limit in:{webdns} Mode: In Station Query")
        return redirect(url_for('search', query=query,limit=webdns))
    if request.method == 'POST' and request.form.get('wildcard'):
        wildcard=request.form['wildcard']
        logging.info(f"User searched for: {wildcard} Mode: wildcard Query")
        return redirect(url_for('search_wild', wildcard=wildcard))
    else : 
        if request.method == 'POST' and request.form.get('query'):
            query = request.form['query']
            logging.info(f"User searched for: {query} Mode: Phrase Query")
            return redirect(url_for('search1', query=query))
    return render_template('index.html')

# 用户信息收集页面
@app.route('/collect-info', methods=['GET', 'POST'])
def collect_info():
    if request.method == 'POST':
        age = request.form['age']
        gender = request.form['gender']
        
        print(f"User age: {age}, User gender: {gender}")

        return redirect(url_for('index'))

    return render_template('collect_info.html')

#站内查询
@app.route('/search', methods=['POST','GET'])
def search():
    query = request.args.get('query')  # 获取查询词
    dns= request.args.get('limit')  
    res=select2(query,dns)
    result=res[0]
    leng=res[1]
    # print(leng)
    return render_template('search.html', result=result['hits']['hits'], value=query, length=leng)

#短语查询
@app.route('/search1', methods=['POST','GET'])
def search1():
    query = request.args.get('query')  # 获取查询词
    res=select(query)
    result=res[0]
    leng=res[1]
    # print(leng)
    return render_template('search.html', result=result, value=query, length=leng)

@app.route('/search_wild', methods=['POST','GET'])
def search_wild():
    wildcard = request.args.get('wildcard')  # 获取查询词

    res=select3(wildcard)
    result=res[0]
    leng=res[1]
    # print(leng)
    return render_template('search.html', result=result['hits']['hits'], value=wildcard, length=leng)

@app.route('/snapshot/<path:weblink>')
def show_snapshot(weblink):
    file_path = 'search_history.txt'
    # 写入 weblink 到文件
    with open(file_path, 'a') as file:
        file.write(weblink + '\n')
    imagename = hashlib.md5(weblink.encode('utf-8')).hexdigest()
    filepath = f'snapshots/{imagename}.png'
    if os.path.exists(filepath):
        return send_from_directory('snapshots', f'{imagename}.png')
    else:
        # 如果文件不存在，则重定向到链接
        return redirect(weblink)


@app.route('/next-page', methods=['POST'])
def next_page():
    query = request.args.get('query')
    limit = request.args.get('limit')
    start_page = int(request.form.get('page', 1))
    print("Received start_page:", start_page) 
    start_page = (start_page - 1) * 10  
    print("Transformed start_page:", start_page) 
    res = select(query, start_page)
    result = res[0]
    leng = res[1]
    return render_template('search.html', result=result, value=query, length=leng)

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080,debug=True)