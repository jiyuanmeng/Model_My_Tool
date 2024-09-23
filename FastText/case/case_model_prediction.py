import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
from tools.FTModel import FTModel
from tools.dclean_tool import DClean
pd.set_option('display.max_row', None) #显示全部列字段 不省略
pd.set_option('display.max_colwidth', None) #显示列字段内全部内容 不省略

# 文件调用模型
path = "data/对话-河北-预测.csv"
# df = pd.read_excel(path)
#1调用模型预测结果
res = FTModel.fasttext_prediction(prediction_path=path,model_number='5.1.0',is_return=True,k=1)
res.to_csv('output/河北-结果-8.17.csv',index=False)
print("预测结束，开始处理结果数据")
#2处理结果文件
# res = pd.merge(df,res,on="问题",how='inner')
# r = DClean.clean_split(df=res,is_return=True)
# r.to_excel('output/山西-无意图.xlsx',index=False)
r = DClean.clean_split_prediction(df=res,is_return=True)
r.to_csv('output/河北-标签结果-8.17.csv',index=False)

# 单接口调用模型
# list_data  = ['手机有问题']
# df = pd.DataFrame(list_data, columns=['问题'])

# print(df)
# res = FTModel.fasttext_prediction(dff=df,model_number='5.1.0',is_return=True,k=1)
# r = DClean.clean_split_prediction(df=res,is_return=True)
# print(r)
