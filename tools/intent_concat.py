import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
from tqdm import tqdm

class IntentConcat:
    def separate_concat(df,sort,id,date1='',date2=''):
        """
        传入一个df
        根据时间字段排序，拼接意图链路并返回结果df
        返回的拼接列命名为 sort-concat
        返回的dataframe只有两个字段：分组的列、拼接的结果列
    
        sort:需要拼接的字段
        date：排序字段
        id：分组字段
        date1:排序字段1
        date2:排序字段2，不传参默认没有
        """
    
        # 判断排序字段是否有值，都没有就不进行排序
        if date2 == '' and date1 != '':
            df = df.sort_values([date1],ascending=True)
        elif date2 == '' and date1 == '':
            pass
        else:
            df = df.sort_values([date1,date2],ascending=[True,True])
    
        df1  = df.astype(str).groupby(id).agg({sort: '==》'.join}).reset_index()
    
        sort_name = '{}-concat'.format(sort)
        df1.columns = [id,sort_name]
    
        return df1
    
    def combine_concat(df,group_sort,date1='',date2=''):
        """
        传入一个df
        根据时间字段排序，将除分组字段外全部列拼接，使用==》拼接
    
        df:除了分组字段，必须全部字段都是要拼接的列
        group_sort:分组字段
        date1:排序字段1
        date2:排序字段2，不传参默认没有
        """
        # 判断排序字段是否有值，都没有就不进行排序
        if date2 == '' and date1 != '':
            df = df.sort_values([date1],ascending=True)
        elif date2 == '' and date1 == '':
            pass
        else:
            df = df.sort_values([date1,date2],ascending=[True,True])
    
        # 需要拼接的列
        columns_list = df.columns.tolist() #获取列
        columns_list =  list(filter(lambda x: x != group_sort, columns_list)) #去除分组字段
    
        # 遍历拼接每个列
        for index,i in enumerate(tqdm(columns_list)):
            if index == 0:
                dff = df.astype(str).groupby(group_sort).agg({i: '==》'.join}).reset_index()
            else:
                dfff = df.astype(str).groupby(group_sort).agg({i: '==》'.join}).reset_index()
                dff = pd.merge(dff,dfff,on=group_sort,how='inner')
    
        return dff

    def function01(x):
        list = str(x).split('==》')
        for i in range(1,len(list) + 1):
            if '门户自助辅导' not in list[-i]   and list[-i] != "转人工服务"  and list[-i] != "挂机服务" and  "菜单" not in list[-i] and '脏话' not in list[-i] and '夜间繁忙' not in list[-i]:
                if list[-i] != '欢迎语通用播报' and list[-i] != '用户类型引导词'  and '无意图' not in list[-i] and 'A' not in list[-i] and 'Y' not in list[-i] and '按键' not in list[-i]:
                    return list[-i]
        return '无'
    def end_intent(df,sort):
        """
        清洗末业务意图-含预判
        sort:意图链路的字段
        """
        df['end_intent'] = df[sort].apply(lambda x:IntentConcat.function01(x)) #获取末业务意图

        return df
    


    def function02(x):
        if '门户' in  x or '转人工服务' in x:
            return "转人工"
        else:
            return "无"
    def is_manu(df,sort):
        """
        增加一个新的字段，判断是否转接人工
        """
        df['是否转人工'] = df[sort].apply(lambda x:IntentConcat.function02(x))
        return df
    




if __name__ == '__main__':

    df1 = pd.read_csv('data/人人/结果-6.2-河北-新.csv')
    df2 = pd.read_csv('output/河北数据魔方-结果.csv')
    df3 = pd.read_csv('output/河北数据魔方-结果-1.csv')
    df4 = pd.read_csv('output/河北数据魔方-结果-2.csv')
    df5 = pd.read_csv('output/河北数据魔方-结果-3.csv')

    df2 = df2[(df2['summary'] != '')&(df2['summary'] != '提取异常')]
    df3 = df3[(df3['summary'] != '')&(df3['summary'] != '提取异常')]
    df4 = df4[(df4['summary'] != '')&(df4['summary'] != '提取异常')]
    df5 = df5[(df5['summary'] != '')&(df5['summary'] != '提取异常')]

    dff = pd.concat([df2,df3])
    dff = pd.concat([dff,df4])   
    dff = pd.concat([dff,df5])

    dfa = pd.merge(dff,df1,how='inner',on='contact_id')
    dfa = dfa.drop_duplicates(subset=['contact_id'],ignore_index=True)
    dfa = dfa[['日期','省份','contact_id','服务请求列表','工单号','工单类型','产品','入网时间','服务请求-一级','服务请求-二级','服务请求-末级','text','summary','全语音意图链']]
    dfa = dfa.rename(columns={'text':'对话','summary':'诉求'})

    dfb = IntentConcat.end_intent(df=dfa,sort='全语音意图链')
    def function001(x):
        if '预判' in x:
            return '是'
        else:
            return '否'
    dfb['是否预判转人工'] = dfb['end_intent'].apply(lambda x: function001(x))

    # print(dfb)
    dfb.to_csv('data/人人/人人-河北-6.2-含诉求结果.csv',index=False)
