import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd 
from tools.customer_tool import *

def case_customer(df,out_path='',is_return=False):
    """
    人人对话处理，结果有12列'日期','省份','session_id','contact_id','星级','服务请求列表','服务请求-一级','服务请求-二级','服务请求-三级','服务请求-四级','坐席','客户'
    out_path:结果文件目录
    is_return:是否返回dataframe,默认不返回生成文件
    """
    # 1格式化处理+分列，一共8列：dt_id call_id contact_id service_list convert_text_fm province star_level 0
    df1 = customer_format(df=df)

    # 2处理服务请求，增加4列：service_first service_second service_third service_fourth
    df2 = customer_service(df=df1)

    # 3处理对话明细,一轮对话是一行,增加2列：坐席 客户
    df3 = customer_conversation(df=df2)

    # 4结果处理
    df01 = df3.rename(columns={'contact_id_x':'contact_id','odd_x':'坐席','odd_y':'客户'}) #重命名
    df02 = pd.merge(df2,df01,how='inner',on='contact_id') #关联拼接上全部字段
    df4 = df02.rename(columns={
        'dt_id':'日期',
        'province':'省份',
        'call_id':'session_id',
        'contact_id':'contact_id',
        'service_list':'服务请求列表',
        'star_level':'星级',
        'service_first':'服务请求-一级',
        'service_second':'服务请求-二级',
        'service_third':'服务请求-三级',
        'service_fourth':'服务请求-四级'
    })
    df4 = df4[['日期','省份','session_id','contact_id','星级','服务请求列表','服务请求-一级','服务请求-二级','服务请求-三级','服务请求-四级','坐席','客户']]
    
    if is_return == False:
        df4.to_csv(path,index=False)
    else:
        return df4

if __name__ == '__main__':
    df = pd.read_csv('人人/test1.csv',sep='&')
    print('数据读取完毕，开始处理！')
    path = '人人/结果-全量.csv'
    case_customer(df=df,out_path=path)
    