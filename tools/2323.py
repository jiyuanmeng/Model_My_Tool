from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import make_pipeline
from sklearn.cluster import KMeans
import pandas as pd
pd.set_option('display.max_row', None) #显示全部结果行 不省略

df = pd.read_excel('tools/山西-无意图-聚类数据.xlsx')
# 提取话术文本和对应计数
# texts = list(data['文本'])

data = list(df['文本'])

# 创建TF-IDF向量化器
tfidf_vectorizer = TfidfVectorizer()

# 实例化K-means, 假定我们想要聚成3个簇
kmeans = KMeans(n_clusters=200, random_state=42)

# 创建管道，先将文本向量化，然后聚类
pipeline = make_pipeline(tfidf_vectorizer, kmeans)

# 对数据进行拟合，自动完成向量化和聚类的过程
pipeline.fit(data)

# 预测每个对话的簇标签
labels = pipeline.predict(data)

# 将聚类标签和对话组合成数据框
df = pd.DataFrame({'文本': data, '聚类分组': labels})
df.to_excel('tools/试试结果-200.xlsx',index=False)
# print(df)
