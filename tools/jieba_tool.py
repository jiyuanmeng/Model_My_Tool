import pandas as pd
from collections import Counter
import jieba
from tqdm import tqdm

def jieba_fenci(df,sort):
    """
    jieba分词后统计数量并排序
    """

    # 分词
    words = []
    # print(df)
    for sentence in tqdm(df[sort]):
        # seg_list = jieba.cut(sentence) #精准模式
        seg_list = jieba.cut_for_search(sentence)# 使用搜索引擎模式
        for word in seg_list:
            words.append(word)
    
    # 统计每个分词的个数
    word_counter = dict(Counter(words))

    # 格式转为dataframe
    word_counter = [[key, value] for key, value in word_counter.items()]    

    df = pd.DataFrame(word_counter)
    df.columns = [sort,'次数']
    df = df.sort_values('次数', ascending=False)
    # print(df)

    # df.to_csv('tool/结果.txt', sep='\t', index=False)
    # print(df)

    return df

if __name__ == '__main__':

    # df = pd.read_excel('tools/山西-无意图-聚类数据.xlsx')
    df = pd.read_table('tools/分词.txt')
    dff = jieba_fenci(df=df,sort='问题')
    # print(dff)
    dff.to_excel('tools/河北-Y1无意图分词.xlsx',index=False)
