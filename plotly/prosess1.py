import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
from datetime import date, timedelta
from data import data_initialize
import numpy as np

#计算时间段累计的各项指标
# df = pd.read_excel('ceshi2.xlsx')
# start_data = '2024-05-01'
# end_data = '2024-05-02'
# '日期','地区','意图名称','意图总通话量','末业务意图总通话量','末业务意图人工请求量','末业务意图全语音挂机前推送量',
# '末业务意图全语音挂机前参评量','末业务意图全语音挂机前满意量','末业务意图短信推送量','末业务意图短信参评量',
# '末业务意图参评短信满意量','转人工率','满意度'

def data_calculate(df):
    """
    指标计算
    """
    df1 = df

    #计算
    #1 求和

    #2 计算转人工率
    df1['转人工率'] = df1['末业务意图人工请求量']/df1['末业务意图总通话量']

    #3 计算满意度
    #3-1 三种计算公式
    df1['满意度'] = df1.eval('(末业务意图参评短信满意量/末业务意图短信参评量*末业务意图短信推送量 + 末业务意图全语音挂机前满意量/末业务意图全语音挂机前参评量*末业务意图全语音挂机前推送量)/(末业务意图全语音挂机前推送量+末业务意图短信推送量)')
    df1['满意度1'] = df1.eval('(末业务意图全语音挂机前满意量/末业务意图全语音挂机前参评量*末业务意图全语音挂机前推送量)/(末业务意图全语音挂机前推送量+末业务意图短信推送量)')
    df1['满意度2'] = df1.eval('(末业务意图参评短信满意量/末业务意图短信参评量*末业务意图短信推送量 )/(末业务意图全语音挂机前推送量+末业务意图短信推送量)')
    df1.fillna(0, inplace=True) #NaN替换成0
    #3-2逻辑判断取哪个
    df1['满意度x'] = np.where(df1['满意度'] != 0, 
                            df1['满意度'], 
                            np.where(df1['满意度1'] != 0, 
                                     df1['满意度1'], 
                                     np.where( df1['满意度2'] != 0, 
                                              df1['满意度2'], 
                                              None)))
    #3-3删除多余列
    df1.drop(['满意度'], axis=1, inplace=True)
    df1.drop(('满意度1'), axis=1, inplace=True)
    df1.drop(('满意度2'), axis=1, inplace=True)
    #3-4重命名
    df1.rename(columns={'满意度x':'满意度'}, inplace=True)

    #4 填充空
    df1.replace('', 0, inplace=True)

    #5 排序
    df1 = df1.sort_values(['末业务意图总通话量'], ascending=[False])
    df1 = df1.reset_index(drop=True) #重构索引

    return df1

def case(df):
    df1 = df.groupby(['日期','地区','意图名称']).agg({'意图总通话量': 'sum',
                                            '末业务意图总通话量': 'sum',
                                            '末业务意图人工请求量': 'sum',
                                            '末业务意图全语音挂机前推送量': 'sum',
                                            '末业务意图全语音挂机前参评量': 'sum',
                                            '末业务意图全语音挂机前满意量': 'sum',
                                            '末业务意图短信推送量': 'sum',
                                            '末业务意图短信参评量': 'sum',
                                            '末业务意图参评短信满意量': 'sum'
                                      }).reset_index()
    df2 = df.groupby(['地区','意图名称']).agg({'意图总通话量': 'sum',
                                  '末业务意图总通话量': 'sum',
                                  '末业务意图人工请求量': 'sum',
                                  '末业务意图全语音挂机前推送量': 'sum',
                                  '末业务意图全语音挂机前参评量': 'sum',
                                  '末业务意图全语音挂机前满意量': 'sum',
                                  '末业务意图短信推送量': 'sum',
                                  '末业务意图短信参评量': 'sum',
                                  '末业务意图参评短信满意量': 'sum'
                            }).reset_index()
    dff1 = data_calculate(df=df1) #有日期
    dff2 = data_calculate(df=df2)
    dff2 = dff2.head(15)
    dff3 = dff2[['意图名称']]
    dff4 = pd.merge(dff1,dff3,how='inner',on='意图名称')
    return dff4


def data_cache():
    """
    处理数据缓存
    判断是否有数据需要更新
    是→生成新的表，并返回新的dataframe
    否→直接读表并返回dataframe
    """
    #获取日期-昨天
    x = date.today() - timedelta(days=1)
    # x = '2024-05-25'

    #累计表
    file_leiji = [file for file in os.listdir('data/累计表/') if file.endswith('.XLSX')]
    #日表
    file_ri = [file for file in os.listdir('data/日表/') if file.endswith('.XLSX')]
    #结果表
    file_jieguo = [file for file in os.listdir('data/date/') if file.endswith('.csv')]

    #得到各目录下最新日期
    file_leiji = [word.replace("累计-", "").replace('.XLSX','') for word in file_leiji]
    file_ri = [word.replace("日表-", "").replace('.XLSX','') for word in file_ri]
    file_jieguo = [word.replace("process-", "").replace('.csv','') for word in file_jieguo]

    if file_leiji[-1] == file_ri[-1]:
        if str(x) in file_jieguo :
            # 当前日期已存在
            df = pd.read_csv('data/date/process-{}.csv'.format(x))
            return df
        else:
            # 生成最新大宽表
            df = data_initialize()
            # df.to_csv('data/date/process-{}.csv'.format(x))
            return df
        

if __name__ == '__main__':
    df = data_cache()
    # df = df[(df['日期'] >= '2024-05-01') & (df['日期'] <= '2024-05-14')]
    df = df[df['地区'] == '河北']
    dff = case(df=df)
    # dff = dff[dff['地区'] == '河北']
    # dff = dff.groupby(['日期']).head(15)
    # dff.rename(columns={})
    # print(dff)


    # x = date.today() - timedelta(days=1)
    # print('data/date/process-{}.csv'.format(x))
    # print(df)