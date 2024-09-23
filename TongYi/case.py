import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
from gpt_tool import *
# pd.set_option('display.max_colwidth', None) #显示列字段内全部内容 不省略
# pd.set_option('display.max_columns', None) #显示全部结果列 不省略
from gpt.gpt_tool import *


# 1数据源处理
print('数据读取开始')
df = pd.read_csv('data/人人/结果-6.2-北京-新.csv')
print('数据读取结束，开始处理')

# df = df[df['日期'] == 20240429]
df[['坐席']] = '【坐席】' + df[['坐席']]
df[['客户']] = '【客户】' + df[['客户']]

df['text'] = df['坐席'] + df["客户"]
dff = df.astype(str).groupby('contact_id').agg({'text': ''.join}).reset_index()

# df.drop(['summary'],axis=1,inplace=True)
print(dff)
# 2调用接口
# dff1 = gpt_case(df=df,id='contact_id',customer='客户',robot='坐席',is_rg=True)

# 3关联原数据
# dd1 = pd.merge(df,dff1,how='inner',on='contact_id')
# dff.to_csv('gpt/内蒙-4.29-预测.csv',index=False)

# print(dff)