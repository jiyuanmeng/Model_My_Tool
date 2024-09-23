import pandas as pd
import os

#日期 地区 意图名称 一级分类名称 二级分类名称 意图总通话量 末业务意图总通话量 末业务意图人工请求量 
#末业务意图全语音挂机前推送量 末业务意图全语音挂机前参评量 末业务意图全语音挂机前满意量 末业务意图短信推送量
#末业务意图短信参评量 末业务意图参评短信满意量

def function01(list):
    #处理累计表
    dfs = pd.DataFrame()
    for file in list:
        #获取日期
        file = 'data/累计表/' + file
        df = pd.read_excel(file,nrows=1)
        x = df.columns[1] #表日期
        df = pd.read_excel(file,header=2)
        df['日期'] = x #增加日期列

        df = df[['日期','区域','省份','意图名称','末业务意图全语音挂机前推送量','末业务意图全语音挂机前参评量','末业务意图全语音挂机前满意量','末业务意图短信推送量','末业务意图短信参评量','末业务意图参评短信满意量']]
        df['ID'] = df['日期'] + df['意图名称'] + df['省份'] #辅助列
        #全部文件拼接
        if dfs.empty:   
            dfs = df
        else:
            dfs = pd.concat([dfs,df])
    return dfs
def function02(list):
    #处理日表
    dfs = pd.DataFrame()
    for file in list:
        file = 'data/日表/' + file
        df = pd.read_excel(file,header=2)
        df = df[['日期','区域名称','省分名称','意图名称','一级分类名称','二级分类名称','意图总通话量','末业务意图总通话量','末业务意图人工请求量']]
        df['ID'] = df['日期'] + df['意图名称'] + df['省分名称'] #辅助列
        #全部文件拼接
        if dfs.empty:
            dfs = df
        else:
            dfs = pd.concat([dfs,df])
    return dfs

def data_initialize():
    #读取文件目录
    file_leiji = [file for file in os.listdir('data/累计表/') if file.endswith('.XLSX')]
    file_ri = [file for file in os.listdir('data/日表/') if file.endswith('.XLSX')]
               
    #两个目录下文件拼接
    df_leiji = function01(list=file_leiji)
    df_ri = function02(list=file_ri)

    dff = pd.merge(df_leiji,df_ri,how='inner',on='ID')
    dff = dff[['日期_x','区域名称','省分名称','意图名称_x','一级分类名称','二级分类名称','意图总通话量','末业务意图总通话量','末业务意图人工请求量','末业务意图全语音挂机前推送量','末业务意图全语音挂机前参评量','末业务意图全语音挂机前满意量','末业务意图短信推送量','末业务意图短信参评量','末业务意图参评短信满意量','ID']]
    dff = dff.rename(columns={'日期_x':'日期','意图名称_x':'意图名称','省分名称':'地区'})
    dff['日期'] = pd.to_datetime(dff['日期']) #转日期格式

    #处理区域数据
    df1 = dff.groupby(['日期', '区域名称','意图名称','一级分类名称','二级分类名称']).agg({'意图总通话量': 'sum', 
                                                            '末业务意图总通话量': 'sum',
                                                            '末业务意图人工请求量': 'sum',
                                                            '末业务意图全语音挂机前推送量': 'sum',
                                                            '末业务意图全语音挂机前参评量': 'sum',
                                                            '末业务意图全语音挂机前满意量': 'sum',
                                                            '末业务意图短信推送量': 'sum',
                                                            '末业务意图短信参评量': 'sum',
                                                            '末业务意图参评短信满意量': 'sum'
                                                        }).reset_index()
    df1 = df1.rename(columns={'区域名称':'地区'})

    #合并省份和区域
    df2 = pd.concat([df1,dff])
    return df2
