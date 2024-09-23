import pandas as pd
from autogluon.tabular import TabularDataset, TabularPredictor
import numpy as np
import os
from sklearn.metrics import precision_recall_fscore_support

df = pd.read_csv("t_train_yw_kb_202404_202408191412.csv")
# 尝试将ques1列转换为数值类型，无法转换的将被设置为NaN  
df['ques1_type'] = pd.to_numeric(df['ques1'], errors='coerce')  
label_column ='ques1_type'  #标签字段
number = '20240820-2_selected_features/new'
model_path = f"./model/{number}"


#将‘\N’转换为空
df = df.map(lambda x: None if x=='\\N' else x )
#删除多余字段
df = df.drop(columns=[
                    'cust_no','cust_type','city_no','user_name','brand_no','CONTACT_NBR','channel_no',
                    'cust_name',
                    'ques1',
                    'ques2',
                    'ques3',
                    'ques4',
                    'nps_call.month_id',
                    'nps_call.device_number',
                    'nps_user.month_id',
                    'nps_user.device_number',
                    'gd.device_number',
                    'gd.month_id',
                    'JCJL.device_number',
                    'JCJL.month_id',
                    'fwqq.device_number',
                    'fwqq.month_id',
                    'gaoj.device_number',
                    'gaoj.month_id',
                    'XQXN.device_number',
                    'XQXN.month_id',
                    'gz.month_id',
                    'gz.device_number',
                    'cell_app.month_id',
                    'cell_app.device_number',
                    'area_no',
                    't.device_number',
                    'depart_name',
                    'product_id',
                    "app_cs",
                    "app_sc",
                    "app_cs_1",
                    "app_cs_2",
                    "app_cs_3",
                    "app_cs_4",
                    "app_cs_5",
                    "app_sc_1",
                    "app_sc_2",
                    "app_sc_3",
                    "app_sc_4",
                    "app_sc_5"
                    ])
#删除全部是空的列
df.dropna(axis=1, how='all',inplace=True)
#处理标签值-语音质量
#删除空值行-19031
df.dropna(subset=[label_column], inplace=True)
# 筛选ques1_numeric列中值在0到10之间的行  
df= df[df[label_column].between(0, 10) & (~df[label_column].isna())]

df_test = df[df['t.month_id'] == 202407].copy()
df001 = df_test[label_column].copy()

#取验证集
df_test.loc[(df_test[label_column] >= 0) & (df_test[label_column] < 5), label_column] = 1  
df_test.loc[df_test[label_column] >= 5, label_column] = 0  
df_test[label_column] = df_test[label_column].astype(int)  #转整数

#验证集目标值
y_test = df_test[label_column].copy() #因变量
#验证集预测值
x_test = df_test.drop([label_column], axis=1).copy()  #删除目标列，剩下的是自变量

# 导⼊预测数据
test_data = TabularDataset(x_test)
# 导⼊模型
predictor = TabularPredictor.load(model_path)
# 得到预测值
y_pred = predictor.predict(test_data)

# 输出最优模型
print(predictor.model_best)

# 输出6种评估指标，以及预测结果
perf = predictor.evaluate_predictions(y_true=y_test, y_pred=y_pred, auxiliary_metrics=True)# 结果评估
print(perf)
# accuracy 准确率
# balanced_accuracy 平衡精度 针对不平衡数据集，计算每个类别的准确率，然后取平均值。这有助于在类别分布不均的情况下更公平地评估模型性能
# mcc 相关系数 用于衡量二分类问题中模型预测性能的相关系数，MCC 的值范围从 -1 到 1，其中 1 表示完美预测，-1 表示完全不一致的预测，0 表示随机预测
# f1 精确率和召回率的调和平均数，用于综合评估模型的精确性和完整性
# precision 精确率 预测为正类的样本中，真正为正类的样本所占的比例
# recall 在所有实际为正类的样本中，被正确预测为正类的样本所占的比例

with open(f'{model_path}/评估指标.txt', 'w') as file:  
    # 写入变量中的值  
    file.write(str(perf))  

print(f"{model_path}/评估指标.txt 已创建并写入内容。")


# 假设y_pred是预测标签（0和1）  
precision, recall, fscore, support = precision_recall_fscore_support(y_test, y_pred, average=None) 
print(f"负类样本Precision: {precision[0]:.4f}")
print(f"负类样本Recall: {recall[0]:.4f}")


df002 = pd.concat([df001,y_pred],axis=1)
#预测结果的置信度
pred_proba = predictor.predict_proba(test_data)
pred_rea = pd.concat([df002,pred_proba],axis=1)
pred_rea.columns = ['原-因变量','预测结果','0置信度','1置信度']
pred_rea.to_csv(f'{model_path}/-5预测结果.csv',index=False)