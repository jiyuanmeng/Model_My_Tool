import pandas as pd
import re
import sys
import numpy as np
from tqdm import *
pd.set_option('display.max_row', None) #显示全部结果列 不省略

def function02(y):
    """
    校验每行的字段数量
    """
    list = str(y).split('|')
    if len(list) != 9:
        print(y)
        sys.exit() # 停止程序的继续往下执行
    else:
        return y
def customer_format(df,header='|a.dt_id|a.call_id|a.contact_id|b.service_type_name1|c.convert_text_fm|province|a.star_level|'):
    """
    格式化处理+分列
    """
    # 1去空
    df.dropna(how='all',inplace=True) #空行
    df.columns = df.columns.str.replace(' ', '') #列名空格
    df = df.replace(' ','',regex=True) #全部空格

    tqdm.pandas()
    # 2校验每行字段数
    h = header #表头
    df[h] = df[h].progress_apply(lambda x:function02(x))
    df = df[df[h] != h] #去除多余列名行
    
    # 3分列
    df1 = pd.DataFrame()
    df1['dt_id'] = df[h].apply(lambda x:str(x).split('|')[1])
    df1['call_id'] = df[h].apply(lambda x:str(x).split('|')[2])
    df1['contact_id'] = df[h].apply(lambda x:str(x).split('|')[3])
    df1['service_list'] = df[h].apply(lambda x:str(x).split('|')[4])
    df1['convert_text_fm'] = df[h].apply(lambda x:str(x).split('|')[5])
    df1['province'] = df[h].apply(lambda x:str(x).split('|')[6])
    df1['star_level'] = df[h].apply(lambda x:str(x).split('|')[7])

    # 3.1获取倒数第一个元素，判断是否换行
    df1['0'] = df[h].apply(lambda x:str(x).split('|')[-1])
    df1.replace('NULL', np.nan, inplace=True) #NULL转nan
    df1.dropna(subset=['convert_text_fm'], inplace=True) #去除对话是空行
    return df1


def function01(x,i):
    list = str(x).split('>>')
    if len(list) < i+1: #0是【服务请求】不要
        res = None
    else:
        res = list[i]
    return res
def customer_service(df):
    """
    处理服务请求链,拆成4级
    """
    tqdm.pandas()
    df['service_first'] = df['service_list'].progress_apply(lambda x:function01(x,1))
    df['service_second'] = df['service_list'].progress_apply(lambda x:function01(x,2))
    df['service_third'] = df['service_list'].progress_apply(lambda x:function01(x,3))
    df['service_fourth'] = df['service_list'].progress_apply(lambda x:function01(x,4))
    return df


# 4.1处理对话
#【坐席】很高兴为您服务【客户】哎你好你们那这么晚还【客户】排队打电话呢【坐席】啊对遇到什么问题了【客户】他这个就是我们这个网1到12点他他就慢点的
def function03(id,x):
    #处理取出括号内外
    result = re.findall(r'【(.*?)】|([^【】]+)', x)
    list = [item[0] if item[0] else item[1] for item in result]
    #索引分列
    even_index_list = list[::2] #偶数-分类
    odd_index_list = list[1::2] #奇数-内容
    d = pd.DataFrame({'even':even_index_list,'odd':odd_index_list})
    #如果even多行相同，拼接成一行
    result_df = (d.groupby((d['even'] != d['even'].shift(1)).cumsum()).agg({'even': 'first', 'odd': lambda x: '; '.join(x)}))
    result_df['contact_id'] = id #拼接上对话id
    return result_df
def customer_conversation(df):
    """
    处理对话明细,将对话清洗成一轮是一行的形式
    """
    #处理对话明细
    tqdm.pandas()
    df1 = df
    df2 = df1.progress_apply(lambda row: function03(row['contact_id'], row['convert_text_fm']), axis=1) #将对话拆分，形式为：标签列-坐席 话术内容 标签列-客户 话术内容
    df2 = pd.concat([df for df in df2], ignore_index=True) #将调用function03后的DataFrame进行竖直拼接

    #处理坐席
    df01 = df2[df2['even'] == '坐席'] 
    df01 = df01.reset_index(drop=True) #索引重构
    df01['id'] = df01.groupby(['contact_id']).cumcount() #组内排序
    df01['id'] = df01['id'].astype(str) #转字符串
    df01['ids'] = df01['contact_id'] + '-' + df01['id'] #构建辅助列
    df01 = df01[['even','odd','contact_id','ids']]

    #处理客户
    df02 = df2[df2['even'] == '客户']
    df02 = df02.reset_index(drop=True) #索引重构
    df02['id'] = df02.groupby(['contact_id']).cumcount() #组内排序
    df02['id'] = df02['id'].astype(str) #转字符串
    df02['ids'] = df02['contact_id'] + '-' + df02['id'] #构建辅助列
    df02 = df02[['even','odd','contact_id','ids']]

    #将坐席、客户关联起来，形成一轮对话是一行
    #通过唯一索引，contact_id-组内索引，进行关联，保证对话一一对应
    df03 = pd.merge(df01,df02,how='outer',on='ids') #有可能在坐席或客户那挂机断掉，所以用全外关联
    df03 = df03[['contact_id_x','odd_x','odd_y']] #保留3列
    return df03