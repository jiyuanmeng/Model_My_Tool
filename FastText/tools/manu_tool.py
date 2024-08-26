import pandas as pd
import os
import re
from tqdm import *
import logger
pd.set_option('display.max_row', None) #显示全部结果行 不省略

# 1整理对话顺序，输出命中本意图对话
def match_the_intent(df,intent_name):
    """
    整理对话顺序，输出命中本意图对话
    """
    df01 = df
    df02 = df01[df01['intent_name']==intent_name]
    set00 = set(df02['session_id'])
    df03 = df01[df01['session_id'].isin(set00)]
    df03.sort_values(by=['session_id','narrative_time','response_time'],inplace=True)
    return df03
    


# 2以本意图开头对话
def function01(x,intent_name):
    list00 = x.index.to_list()
    df03 = x[x['intent_name']==intent_name]
    i = df03.index.to_list()[0]
    j = list00.index(i)-1 # 取前一个索引
    return list00[j:]
def cleanup_the_intent_list(df,intent_name):
    """
    以本意图开头对话
    """
    df01 = df
    tqdm.pandas()
    df02 = df01.groupby('session_id').progress_apply(lambda x:function01(x,intent_name))
    l00 = []

    try:
        for x in df02:
            for y in x:
                l00.append(y)

        df02 = df01.loc[l00]
    except Exception as e:
        print('匹配意图不存在，请检查！')
    return df02



# 3.1对话拼接成行
def combine_in_list(x):
    str00 = '==》'.join(x['intent_name'].astype('str'))
    str01 = '==》'.join(x['customer'].astype('str'))
    str02 = '==》'.join(x['robot'].astype('str'))
    phone = list(x['phone'])[0]
    first_time = list(x['narrative_time'])[0]
    last_time = list(x['narrative_time'])[-1]
    provice = list(x['province'])[0]
    date=pd.to_datetime(first_time).date()
    return [phone,str00,first_time,last_time,str01,str02,date,provice] 
def combine_intent_list(df,is_begin=False):
    """
    对话所有列拼接成行
    """
    df01 = df
    tqdm.pandas()
    df02 = pd.DataFrame()
    #是否需要去除前两轮
    if is_begin == False:
        df02['all'] = df01.groupby('session_id').progress_apply(lambda x: combine_in_list(x.iloc[2:]))
    else:
        df02['all'] = df01.groupby('session_id').progress_apply(lambda x: combine_in_list(x))
    df02.reset_index(names="对话ID") #用索引来存储分组的字段
    df02['对话ID'] = df02.index #索引转为字段
    df02['phone']=[d[0] for d in df02['all']]
    df02['intent_list'] = [d[1] for d in df02['all']]
    df02['customer'] = [d[4] for d in df02['all']]
    df02['reply'] = [d[5] for d in df02['all']]
    df02['first_time'] = [d[2] for d in df02['all']]
    df02['last_time'] = [d[3] for d in df02['all']]
    df02['date'] = [d[6] for d in df02['all']]
    df02['provice'] = [d[7] for d in df02['all']]
    del df02['all']
    return df02
    


def combine_the_label(df):
    df01 = df
    df01.rename(columns={'intent_list': '意图清单'}, inplace=True)
    df02 = pd.read_csv('data/12月19话务通话记录.csv')
    df03 = df02[['对话ID','首句转人工','要求转人工','计数','重复来电次数','是否重复来电']]
    df04 = pd.merge(df01,df03,on='对话ID')


# 3.2获取意图链路
def function06(x,j):
    list=re.split('==》',x)
    if j ==10:
        if len(list)<j:
            return ''
        else:
            return '==》'.join(list[9:])
    elif j<10:
        if len(list)<j:
            return ''
        else:
            return list[j-1]
def menu_intent_label(df):
    """
    获取意图链路,清洗出前10步
    """
    df01 = df
    tqdm.pandas()

    for m in range(1,11):
        df01['第'+str(m)+'步'] = df01['意图清单'].progress_apply(lambda x:function06(str(x),m))
        df01['用户第' + str(m) + '步'] = df01['customer'].progress_apply(lambda x: function06(str(x), m))
        df01['机器人第' + str(m) + '步'] = df01['reply'].progress_apply(lambda x: function06(str(x), m))
    del df01['customer']
    return df01

def get_value(text):
    value = text.split('==》门户自助辅导')[0] #截取门前部分链路
    value = value.split('==》转人工服务')[0] #截取人前部分链路
    values = value.split('==》')
    for i in range(1, len(values) + 1):
        if values[-i] != "门户自助辅导" and values[-i] != "转人工服务":
            return values[-i]
def menu_intent_screen(df,intent_name,is_end): 
    """
    筛选转人工前末意图是本意图
    """
    df01 = df
    df01.rename(columns={'intent_list': '意图清单'}, inplace=True)
    df01 = df01[df01['意图清单'].str.contains('门户自助辅导') | df01['意图清单'].str.contains('转人工')]

    if is_end == False:
        df02 = menu_intent_label(df=df01)
    else:
        df01['末业务意图'] = df01['意图清单'].apply(get_value)
        df01 = df01[df01['末业务意图']==intent_name]
        del df01['末业务意图']
        df02 = menu_intent_label(df=df01)
    return df02