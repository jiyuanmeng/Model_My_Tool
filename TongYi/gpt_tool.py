import pandas as pd
import time
import os
from gradio_client import Client
from tqdm import tqdm

#内网地址
# client = Client("http://172.16.52.63:31133")
#外网地址
client = Client("http://183.94.213.143:9012/")


def read_prompt(prompt_title):
    """
    读取提示要求
    """
    file_path = os.path.join(prompt_title)
    if not os.path.exists(file_path):
        # return "$HOLDER$"
        return "提示：要求文件读取错误！"
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
    
def gpt_info(prompt_title, text):
    """
    发起请求
    """
    try:
        prompt = read_prompt(prompt_title)
        result = client.predict(
            "jimeng", # 需把"账号"处换成自己申请的账号名称
            prompt,  # str  in 'prompt文本' Textbox component
            text,  # str  in '文本' Textbox component
            0,  # int | float (numeric value between 0.0 and 1.0) in 'temperature' Slider component
            api_name='/predict'
        )
        return result[0]
    except Exception as e:
        print('except:', e)
        return '提取异常'


def predtest(df,columns,prompt_path='gpt/全语音_诉求.txt',is_retrun=False,out_path=''):
    """
    调用方法后处理结果

    columns:需要传给gpt的字段
    prompt_path:提示要求的路径
    is_retrun:是否需要返回，默认不反悔生成csv文件
    out_path:生成文件的路径
    """
    predictData = df

    #批量调用
    for idx, row in tqdm(predictData.iterrows(), desc="处理进度", total=len(predictData)):
        # time.sleep(3.5)  # 保持原样，尽管这会显著影响实际进度条的平滑度
        res = gpt_info(prompt_path, row[columns])
        predictData.at[idx, "summary"] = res  # 使用at方法直接在DataFrame中更新值

    #是否生成结果文件  
    if is_retrun == False:
        predictData.to_csv(out_path, index=False, encoding='utf-8')
    else:
        return predictData

def gpt_case(df,id,customer,robot,is_rg=False):
    """
    返回的dataframe有4列 id 主诉求 次诉求 末诉求

    id:分组字段
    is_rg:是否在处理人人,默认否→全语音
    """
    #1 处理数据格式 一通对话是一行
    if is_rg == False:
        # 全语音
        df = df[[id,customer,robot]]
        df['对话'] = df[customer]+'|'+df[robot]
        df.drop([customer,robot],axis=1,inplace=True)
        df = df.astype(str).groupby([id]).agg({'对话': '|'.join}).reset_index()   
    else:
        df = df[[id,robot,customer]]
        df['对话'] = df[robot]+'|'+df[customer]
        df.drop([customer,robot],axis=1,inplace=True)
        df = df.astype(str).groupby([id]).agg({'对话': '|'.join}).reset_index()

    #2 调用接口方法
    dff = predtest(df=df,columns='对话',is_retrun=True)
    
    # 3处理结果
    # 主要诉求：，次要诉求：，末级诉求：。
    # 主要诉求：查询联通畅越会员领取方法。\n次要诉求：确认套餐生效日期与领取时间。\n末级诉求：了解电子券使用规则（如充值抵扣）。
    dff.drop(['对话'],axis=1,inplace=True)
    #取出三级诉求
    # dff['末诉求'] = dff['summary'].str.split('末级诉求：').str[1]
    # dff['summary'] = dff['summary'].str.split('末级诉求：').str[0]
    # dff['次诉求'] = dff['summary'].str.split('次要诉求：').str[1]
    # dff['summary'] = dff['summary'].str.split('次要诉求：').str[0]
    # dff['主诉求'] = dff['summary'].str.split('主要诉求：').str[1]

    # dff.drop(['summary'],axis=1,inplace=True)
    # dff = dff.replace('\n', '', regex=True) #删除换行

    return dff


if __name__ == '__main__':
    client = Client("http://183.94.213.143:9012/")
    result = client.predict(
    "jimeng", # 需把"账号w
    '你好',  # str  in 'p
    '请回答我',  # str  in '文
    0,
    api_name='/predict')

    print(result[0])