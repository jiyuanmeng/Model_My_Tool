from tools.FTModel import FTModel
from tools.dclean_tool  import DClean
from tools.dprocess_tool import DProcess
import pandas as pd

da_path = 'data/内蒙古训练集更新数据（234697）3-25.xlsx'
number = '内蒙-1.0.1'
# prediction_path = 'data/增补训练语料11-15(5982).xlsx'

# 1数据清洗
# 1.1 剔除不在意图列表中数据
# res = DClean.clean_intention(da_path=da_path,is_return=True,number=number)
# 1.2 剔除意图重复数据
# da_path = DClean.clean_repeat(df=res,is_return=False,number=number)
# da_path = DClean.clean_repeat(da_path=da_path,is_return=True,number=number)

# 2模型训练-拆分测试集
train_path,test_path,train_data_path,test_data_path = FTModel.fasttext_train_notest(data_path=da_path,is_size=True,test_size=0.03,model_number=number)

# 3模型测试
FTModel.fasttext_test(model_number=number,test_path=test_path,test_data_path=test_data_path)

# 4数据集预测
# res = FTModel.fasttext_prediction(prediction_path=prediction_path,model_number=number,is_return=True)
# print(res)
# DClean.clean_split_prediction(df=res,number='人人对话识别07-4.0.11')
# print(res)
