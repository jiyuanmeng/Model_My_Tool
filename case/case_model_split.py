import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
from tools.dprocess_tool import DProcess

df = pd.read_excel('data/河北-拆分-8.8.xlsx')

df_train,df_test = DProcess.process_split(df=df,test_size=0.025,number='5.1.0',is_return=True)
# print(df_test)
df_test.to_excel('output/河北-8.8-评估集.xlsx')
df_train.to_excel('output/河北-8.8-训练集.xlsx')