from tools.FTModel import FTModel
from tools.dclean_tool import DClean
from tools.dprocess_tool import DProcess
import pandas as pd

# 调用模型得到预测意图标签

tra_path = 'data/北京-训练集4-11.xlsx'
tes_path = 'data/北京-评估集4-11.xlsx'
model_number = '北京-2.1.2'
number = '北京-2.1.2'
# 1数据清洗
# 1.1 剔除不在意图列表中数据
# res_tra = DClean.clean_intention(da_path=tra_path,is_return=True,number=number)
# res_tes = DClean.clean_intention(da_path=tes_path,is_return=True,number=number)
# 1.2 剔除意图重复数据
# da_tra = DClean.clean_repeat(df=res_tra,is_return=False,number=number)
# da_tes = DClean.clean_repeat(df=tes_path,is_return=False,number=number)

# 2模型训练-不拆分
train_path,test_path = FTModel.fasttext_train_notest(datatrain_path=tra_path,datatest_path=tes_path,is_size=False,model_number=number)

# 3模型测试
#加工训练集格式 更换测试集
# df = pd.read_excel(tes_path)
# test_path = DProcess.process_fasttext(type='test',model_number=model_number,df=df)

FTModel.fasttext_test(model_number=number,test_path=test_path,test_data_path=tes_path)