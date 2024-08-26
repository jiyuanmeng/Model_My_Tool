import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
from tools.manu_tool import *

def case_regong(df,intent_name,out_path='',is_return=False,is_begin=False,is_end=False):
    """
    intent_name:本次处理的意图
    out_path:输出路径
    is_return:是否返回dataframe，默认不返回直接生成文件
    is_begin:是否要求以本意图开头，默认全量
    is_end:是否要求转人工前意图为本意图

    会返回两个df:处理结果、命中的对话明细
    """
    # 1整理对话顺序，输出命中本意图对话
    df01 = match_the_intent(df=df,intent_name=intent_name) 
    

    # 2以本意图开头对话
    df02 = cleanup_the_intent_list(df=df01,intent_name=intent_name)

    # 3.1对话拼接成行
    if is_begin == False:
        df03 = combine_intent_list(df=df01) #全量
    else:
        df03 = combine_intent_list(df=df02,is_begin=True) #已本意图开头
    # 3.2获取意图链路
    df04 = menu_intent_screen(df=df03,intent_name=intent_name,is_end=is_end)


    # 4命中本意图且转人工的全量对话

    df05 = df04['对话ID']
    df05.columns = ['session_id']
    df05 = pd.merge(df01,df05,how='inner',on='session_id')


    if is_return == False:
        df01.to_excel(out_path+'-全量对话.xlsx',index=False)
        df05.to_excel(out_path+'-全量对话-人工.xlsx',index=False)
        df04.to_excel(out_path+'-结果.xlsx',index=False)
        if is_begin == False:
            pass
        else:
            df02.to_excel(out_path+'-开头对话.xlsx',index=False)
    else:
        if is_begin == False:
            return df01,df04,df05
        else:
            return df01,df04,df05,df02
    


if __name__ == '__main__':
    
    print("数据读取开始！")
    # df1 = pd.read_csv('data/对话明细/河北-5.1.csv')
    # df2 = pd.read_csv('data/对话明细/河北-5.2.csv')
    df = pd.read_csv('data/对话明细/转人工诉求-北一1718586452962.csv')
    # df4 = pd.read_csv('data/对话明细/内蒙-5.15.csv')
    # df5 = pd.read_csv('data/对话明细/内蒙-5.16.csv')
    # df6 = pd.read_csv('data/对话明细/内蒙-5.13.csv')
    # df7 = pd.read_csv('data/对话明细/内蒙-5.12.csv')
    # df8 = pd.read_csv('data/对话明细/河北-5.13.csv')
    # df9 = pd.read_csv('data/对话明细/河北-5.12.csv')
    # df10 = pd.read_csv('data/对话明细/河北-5.11.csv')
    # df11 = pd.read_csv('data/对话明细/河北-5.10.csv')

    # df = pd.concat([df1,df2])
    # df = pd.concat([df,df3])
    # df = pd.concat([df3,df4])
    # df = pd.concat([df,df5])
    # df = pd.concat([df,df6])
    # df = pd.concat([df,df7])
    # df = pd.concat([df,df8])
    # df = pd.concat([df,df9])
    # df = pd.concat([df,df10])
    # df = pd.concat([df,df11])
    print("数据读取完毕，开始处理！")

    # 列重命名
    df = df.rename(columns={'识别意图':'intent_name',
                            'session_id':'session_id',
                            '话述时间':'narrative_time',
                            '应答时间':'response_time',
                            '用户话述':'customer',
                            '应答话述':'robot',
                            '省份':'province',
                            '用户号码':'phone'})
    intent_name = '预判修改密码'
    out_path = 'output/人工/佳老师'+intent_name
    case_regong(df=df,intent_name=intent_name,out_path=out_path,is_begin=True)