import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd

# 1数据源处理
print('数据读取开始')
df = pd.read_csv('data/人人/结果-6.2-河北-新.csv')
print('数据读取结束，开始处理')

# df = df[df['日期'] == 20240429]
df[['坐席']] = '【坐席】' + df[['坐席']]
df[['客户']] = '【客户】' + df[['客户']]

df['text'] = df['坐席'] + df["客户"]
dff = df.astype(str).groupby('contact_id').agg({'text': ''.join}).reset_index()

# print(dff)
dff.to_excel('output/河北数据魔方预测用户信息.xlsx',index=False)