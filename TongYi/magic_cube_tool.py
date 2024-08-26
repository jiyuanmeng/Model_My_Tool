import requests
import json
from tqdm import tqdm
import pandas as pd

url = "http://183.94.213.143:31530/predictionapi/prediction"

def request(model_name,texts):
    """
    调用接口
    """
    headers = {
      'Content-Type': 'application/json'
    }
    payload = json.dumps({"texts":[texts],"model_name":model_name})
    try:
        response = requests.request("POST", url, headers=headers, data=payload)

        assert response.status_code == 200# 断言200
        res = response.json() #转字典
        return res['msg'][1]
    
    except Exception as e:
        print('except:', e)
        return '提取异常'

def res_out(df,model_name,columns):
    """
    调用方法并处理结果

    model_name:模型名称
    columns:预测数据的列名
    """
    #批量调用
    for idx, row in tqdm(df.iterrows(), desc="处理进度", total=len(df)):
        res = request(model_name=model_name,texts=row[columns])
        df.at[idx, "summary"] = res  # 使用at方法直接在DataFrame中更新值

    return df


if __name__ == '__main__':
   df = pd.read_csv('output/河北数据魔方-结果-2.csv')
   df = df[(df['summary'] == '')|(df['summary'] == '提取异常')]
#    print(df)
#    
   model_name = '内蒙-人人-主要诉求'
   dff = res_out(df=df,model_name=model_name,columns='text')
   dff.to_csv('output/河北数据魔方-结果-3.csv',index=False)
# 