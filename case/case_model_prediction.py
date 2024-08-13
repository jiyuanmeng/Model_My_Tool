import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
from tools.FTModel import FTModel
from tools.dclean_tool import DClean
pd.set_option('display.max_row', None) #显示全部列字段 不省略
pd.set_option('display.max_colwidth', None) #显示列字段内全部内容 不省略

# 文件调用模型
# path = "data/山西-无意图.xlsx"
# df = pd.read_excel(path)
#1调用模型预测结果
# res = FTModel.fasttext_prediction(prediction_path=path,model_number='江苏-3.1.1',is_return=True,k=2)
#2处理结果文件
# res = pd.merge(df,res,on="问题",how='inner')
# r = DClean.clean_split(df=res,is_return=True)
# r.to_excel('output/山西-无意图.xlsx',index=False)

# 单接口调用模型
list_data  = ['手机有问题']
df = pd.DataFrame(list_data, columns=['问题'])

# print(df)
res = FTModel.fasttext_prediction(dff=df,model_number='吉林-2.1.1',is_return=True,k=3)
print(res)
