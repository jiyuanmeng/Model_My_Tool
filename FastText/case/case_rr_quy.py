import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd 
from tools.intent_concat import IntentConcat

def case_rr_quy(df1,df2):
    """
    人人关联全语音，得到对应的意图链路和末业务意图
    df1 全语音,df2 人人
    
    """
    #获取意图链路
    d1 = IntentConcat.separate_concat(df=df1,id='session_id',sort='识别意图',date1='session_id',date2='话述时间')
    d1 = d1.rename(columns={'识别意图-concat':'全语音-意图链路'})
    d1 = d1.drop_duplicates(subset=['session_id']) #去重

    #关联得到全量数据
    df = pd.merge(df2,d1,how='inner',on='session_id')

    #获人人取末业务意图
    dff = IntentConcat.end_intent(df=df,sort='全语音-意图链路')

    return dff

if __name__ == '__main__':
    df1 = pd.read_csv('data/对话明细/河北-6.2.csv')
    df2 = pd.read_csv('data/结果-6.2-河北-新.csv')

    df = case_rr_quy(df1=df1,df2=df2)
    print(df)
