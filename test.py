from gensim.models import KeyedVectors

# 加载预训练的Word2Vec模型
# 请将路径替换为您下载的模型文件路径
path_to_model = 'path/to/your/word2vec_model.bin'
word2vec_model = KeyedVectors.load_word2vec_format(path_to_model, binary=True)

# 用户输入的词语
user_input_word = "apple"

# 查找与用户输入词语相关的词语
similar_words = word2vec_model.most_similar(user_input_word)

# 打印相关词语
for word, similarity in similar_words:
    print(f"{word}: {similarity}")
