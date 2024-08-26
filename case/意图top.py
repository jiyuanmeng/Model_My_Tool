import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd 
from tools.intent_concat import IntentConcat


def function01(x,a):
    list = str(x).split(a)[1:] #根据意图名截取，不要第一个元素
    lists = []
    for i in list:
        j = str(i.split('==》')[0])
        lists.append(j)
    lists = [y for y in lists if y != ""] #去空元素
    return lists
def case(df,intent):
    """
    intent:本次的top意图
    """
    dff = df
    #得到top意图拼接结果
    a = '{}==》'.format(intent)

    #2-1 筛选本意图的行
    df01 = dff[dff['识别意图-concat'].str.contains(a)]
    df01['后续意图'] = df01['识别意图-concat'].apply(lambda x:function01(x,a)) #调用得到多个后续意图
    df01 = df01.drop(['识别意图-concat'],axis=1)
    #2-2一通对话拆分多个后续意图
    df02 = df01.explode('后续意图')
    #2-3统计计数
    df03 = df02.groupby(['后续意图']).size().reset_index(name='计数')
    df03 = df03.sort_values('计数',ascending=False)
    df03['意图'] = intent

    #2-4去除无效值
    df03 = df03[df03['后续意图'] != intent] #去除自己
    df03 = df03[(df03['后续意图'] != '门户自助辅导')&(df03['后续意图'] != '无意图')&(~df03['后续意图'].str.contains('菜单')&(~df03['后续意图'].str.contains('预判')))] #去除非业务意图


    return df03

if __name__ == '__main__':
    df = pd.read_csv('data/对话明细/河北-5月对话.csv')
    print("数据读取完毕，开始处理！")

    yitu = ["查询余额或欠费",
            "查询本机套餐",
            "反映宽带故障",
            "查询流量使用情况",
            "反映故障问题",
            "查询话费及流量",
            "查询本机号码及归属地",
            "咨询宽带安装办理方法",
            "话费释疑",
            "开通流量包"]
    #1 获取意图链路
    dff = IntentConcat.separate_concat(df=df,sort='识别意图',id='session_id',date1='session_id',date2='话述时间')
    #1-1筛选包含top意图的对话
    dff = dff[dff['识别意图-concat'].str.contains('|'.join(yitu))]

    #2 处理
    dfs = pd.DataFrame()
    for i in yitu:
        dd = case(df=dff,intent=i)
        dfs = pd.concat([dfs,dd])
    # dfs = case(df=dff,intent=yitu[0])
    # print(dfs)
    
    dfs = dfs[['意图','后续意图','计数']]
    dfs = dfs.reset_index(drop=True) #索引重构
    dfs = dfs.groupby('意图').head(5) #取top5

    # print(dfs)
    dfs.to_excel('data/对话明细/河北-意图统计-业务意图版.xlsx',index=False)
