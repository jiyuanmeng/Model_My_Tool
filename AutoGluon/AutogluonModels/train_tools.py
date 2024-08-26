import pandas as pd
from autogluon.tabular import TabularDataset, TabularPredictor


df = pd.read_csv("t_train_yw_kb_202404_202408191412.csv")
# 尝试将ques1列转换为数值类型，无法转换的将被设置为NaN  
df['ques1_type'] = pd.to_numeric(df['ques1'], errors='coerce')  
label_column ='ques1_type'  #标签字段
number = '20240820-4'
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
#删除7月数据
dff = df[df['t.month_id'] != 202407]
#负样本(包含集团数据，根据评分划分)
df_1 = dff[dff[label_column] >= 0]
df_neg = df_1[df_1[label_column] < 5].copy()
df_neg[label_column] = 1
#正样本
df_pos = df_1[df_1[label_column] >= 8].copy()
df_pos = df_pos.sample(n=len(df_neg), random_state=42)
df_pos[label_column] = 0
#拼接得到训练数据
df_train = pd.concat([df_neg,df_pos]).sample(frac=1, random_state=22) #随机打乱


#1 模型训练
#1-1创建预测器
predictor = TabularPredictor(label=label_column,
                                 problem_type='binary', #指定二分类问题
                                 path=model_path #指定路径
                            )
#1-2训练
predictor.fit(train_data = df_train,
            presets='best_quality' #花费更多的时间和计算资源来尝试找到最佳的模型
            # time_limits=1200 #最多运行20分钟
            )              

#2 查看性能
leaderboard1 = predictor.leaderboard(df_train, silent=True)  #输出排⾏榜
print(leaderboard1)

#保存
leaderboard1.to_csv(f'{model_path}/model_排⾏榜.csv',index=False)

leaderboard2 = predictor.leaderboard(extra_info=True, silent=True) #输出拓展的每个算法运⾏数据的排⾏榜
print(leaderboard2)
#保存
leaderboard2.to_csv(f'{model_path}/model_运⾏_排⾏榜.csv',index=False)


# 删除其余模型（减少内存开销）
# predictor.delete_models(models_to_keep='best')

# 输出最优模型
#predictor.model_best()

# 输出特征重要程度
# importance=predictor.feature_importance(df_train)
# importance.to_csv(f'{model_path}/参数相关性.csv',index=False)
#4模型保存
#predictor.save(model_path)