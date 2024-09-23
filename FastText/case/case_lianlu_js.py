import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
from tools.lianlu_count_tool import Lianlu
from tools.intent_concat import IntentConcat

pd.set_option('display.max_row', None) #显示全部结果行 不省略

df1 = pd.read_csv('data/预判按键/河北-4.26.csv')
df2 = pd.read_csv('data/预判按键/河北-4.27.csv')
df3 = pd.read_csv('data/预判按键/河北-4.28.csv')
df4 = pd.read_csv('data/预判按键/河北-4.29.csv')
df5 = pd.read_csv('data/预判按键/河北-4.30.csv')
print('数据读取完毕！')

df = pd.concat([df1,df2])
df = pd.concat([df,df3])
df = pd.concat([df,df4])
df = pd.concat([df,df5])

# 处理对话拼接成一行
dfa = IntentConcat.combine_concat(df=df,group_sort='session_id')
dfa = dfa[['session_id','识别意图']]

# 根据预判取各类别前top
dfb = Lianlu.count_lianlu(df=dfa,top=5)
dfb = dfb[dfb['首意图'].str.startswith('预判')] #取预判
# print(df2)
dfb.to_excel('output/预判按键/河北-预判按键-月末.xlsx',index=False)

# 取全量数据各类别前top
# df02 = Lianlu.count_lianlu(df=df1,is_first=False)