import pandas as pd
import requests
from io import StringIO

def get_request(sql_text: str):
    """
    请求数据库接口
    """
    # 通过requests库调用clickhouse的http接口。
    url = 'http://db:8123/'
    print("-------------------------------开始执行sql语句--------------------------------------------")
    response = requests.post(url, data=(sql_text).encode('utf-8'))
    res = response.text
    print(res)
    return res

if __name__ == '__main__':
    sql = "select * from hb.t_train_yw_kb_202404"
    res = get_request(sql_text=sql)
    print("-------------------------开始处理sql结果--------------------------------------------------")
    data = StringIO(res.strip())
    df = pd.read_csv(data, sep='\t', header=None)
    print("-------------------------开始生成结果csv--------------------------------------------------")
    df.to_csv('./宽表训练数据.csv',index=False)
