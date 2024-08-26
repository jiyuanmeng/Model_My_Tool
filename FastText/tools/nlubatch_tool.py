import pandas as pd

def nlu_batch_entity(df):
    """
    批量NLU结果文件再加工
    加工命中的实体结果
    """
    blist = []
    for index,row in df.iterrows():
        if pd.notna(row['实体中匹配结果']):
            a = row['文本'] #词
            b = str(row['实体中匹配结果']).split('。 ')
            bb = [x for x in b if x.strip()]

            for i in bb :
                list = []
                z = str(i).split(',')[1].split('：')[1] #实体名
                zz = str(i).split(',')[2].split('：')[1] #实体值
                list.append(a)
                list.append(z)
                list.append(zz)
                blist.append(list)

    dfa = pd.DataFrame(blist)
    dfa.columns = ['文本','实体名','实体值']
    return dfa

def nlu_batch_identify(df):
    """
    批量NLU结果文件再加工
    加工识别结果，包括识别的意图、置信度、匹配规则
    """
    lists = []
    for index,row in df.iterrows():
        list = []
        a = row['文本']

        #处理第一个返回意图是无意图的情况
        x = str(row['意图中澄清结果']).split('。')[0].split(",")[0].split(':')[1] #意图名称
        y = str(row['意图中澄清结果']).split('。')[1]

        if x == "无意图" and y != "":
            b = str(row['意图中澄清结果']).split('。')[1].split(",")[0].split(':')[1] #意图名称
            c = str(row['意图中澄清结果']).split('。')[1].split(',')[1].split(':')[1] #意图置信度
            d = str(row['意图中澄清结果']).split('。')[1].split(',')[2].split('：')[1] #匹配来源
        else:
            b = str(row['意图中澄清结果']).split(',')[0].split(':')[1]
            c = str(row['意图中澄清结果']).split(',')[1].split(':')[1] #意图置信度
            d = str(row['意图中澄清结果']).split(',')[2].split('：')[1] #匹配来源

        list.append(a)
        list.append(b)
        list.append(c)
        list.append(d)
        lists.append(list)
    
    ddf = pd.DataFrame(lists)
    ddf.columns = ['文本','意图名称','意图置信度','匹配来源']
    return ddf



if __name__ == '__main__':
    df = pd.read_excel('data/nul导出 (2).xls')
    dd = nlu_batch_identify(df=df)
    dd.to_excel('output/北京-人人-用户信息-识别结果.xlsx',index=False)
    # print(dd.columns)