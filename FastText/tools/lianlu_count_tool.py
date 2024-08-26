import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd 
import numpy as np

class Lianlu:
    def get_value01(text):
        values = text.split('==》')
        for i in range(0,len(values)):
            if values[i] != "用户类型引导词" and values[i] != "欢迎语通用播报":
                return values[i]
    def get_value02(text):
        values = text.split('==》')
        for i in range(1,len(values)+1):
            if values[-i] != "门户自助辅导" and values[-i] != "转人工服务" and values[-i] != "无意图":
                return values[-i]
    def get_value03(text):
        if "门户自助辅导" in text or "转人工服务" in text:
            values = text.split('==》门户自助辅导')[0] #截取门前部分链路
            values = values.split('==》转人工服务')[0] #截取人前部分链路
            value = values.split('==》')[-1]
            return value
        else:
            value = ""
            return value
    def initialize_lianlu(df):
        """
        初始化设置,并获取每行的首意图、末意图、转人工前意图
        传入的df必须只有两列:对话id、意图链路,链路需要使用==》连接
        """
        df01 = df
        if len(df.columns) == 2:
            df01.columns = ['session_id','意图清单']
            df01['首意图'] = df01['意图清单'].apply(Lianlu.get_value01)
            df01['末业务意图'] = df01['意图清单'].apply(Lianlu.get_value02) #去除转人工和无意图
            df01['人工前意图'] = df01['意图清单'].apply(Lianlu.get_value03)
            return df01
        else:
            print("传入字段数量错误，请检查！")   


    def process_lianlu(df):
        """
        处理途经意图
        """
        lists = []
        for i,row in df.iterrows():
            z = row['session_id']
            y_list = row['意图清单'].split('==》')
            for j in y_list:
                list = []
                list.append(z)
                list.append(j)
                lists.append(list)
        dff = pd.DataFrame(lists)
        dff.columns = ['session_id','途经意图']
        dff = dff.drop_duplicates(subset=['session_id','途经意图']) #去重
        dff = dff[(dff['途经意图'] != '用户类型引导词')&(dff['途经意图'] != '欢迎语通用播报')&(dff['途经意图'] != '门户自助辅导')] #去除
        return dff   


    def get_value04(df,top,column1,out_column,column2=None):
        """
        分组聚合计数，并整理格式并生成ID字段为后续做关联

        top:组内保留前几个
        column1:group by的第一个字段 首意图
        out_column:分组计数的字段名
        column2:group by的第二个字段,默认无
        """
        if column2 == None:
            df = df.groupby([column1]).size().reset_index(name=out_column)
            df = df.sort_values([out_column],ascending=[False]) #倒序排列
            df['排序'] = df.cumcount() + 1 #排序
            df = df.head(top) #取top
            df['排序'] = df['排序'].astype(int) #转整数
        else:
            df = df.groupby([column1,column2]).size().reset_index(name=out_column)
            df = df[df[column2] != ''] #去空
            df = df[df[column1] != df[column2]] #去除自己
            df = df.sort_values([column1,out_column],ascending=[True,False]) #倒序排列
            df = df.groupby([column1]).head(top) #取每组top
            df['排序'] = df.groupby([column1]).cumcount() + 1 #组内排序
            df['排序'] = df['排序'].astype(int) #转整数
            df['ID'] = df["排序"].map(str) +"-"+ df[column1].map(str) #拼接两列
            del df[column1]
            del df['排序']
        return df
    def count_lianlu(df,top=5,is_first=True):
        """
        计算整理

        top:展示前top多少，默认展示前5
        is_first:是否首意图(预判)分组，默认是
        """
        df02 = Lianlu.initialize_lianlu(df=df) #初始化 获取首意图、人工、末意图
        df03 = Lianlu.process_lianlu(df=df02) #获取途经意图
        df04 = pd.merge(df02,df03,how='inner',on='session_id') #获取首意图
        del df02['意图清单']
        del df04['意图清单']

        #session_id 首意图 末业务意图 人工前意图
        #session_id 首意图 末业务意图 人工前意图 途经意图

        #开始计算
        if is_first == True:
            #首意图 排序 末业务意图 挂机前计数 人工前意图 转人工前计数 途经意图 途经计数
            #1 挂机前意图
            dfa = Lianlu.get_value04(df=df02,top=top,column1='首意图',column2='末业务意图',out_column='挂机前计数')
            #2 转人工前意图
            dfb = Lianlu.get_value04(df=df02,top=top,column1='首意图',column2='人工前意图',out_column='转人工前计数')
            #3 途径意图
            dfc = Lianlu.get_value04(df=df04,top=top,column1='首意图',column2='途经意图',out_column='途经计数')

            #4.1 得到索引列 ID
            dfd = df02.groupby(['首意图']).size().reset_index(name='计数')
            del dfd['计数']
            dfd = dfd.reindex(dfd.index.repeat(top)) #得到组内top行
            dfd['排序'] = dfd.groupby(['首意图']).cumcount() + 1 #组内排序
            dfd["ID"] = dfd["排序"].map(str) +"-"+ dfd["首意图"].map(str)  

            #4.2 通过索引列关联
            dff = pd.merge(dfd,dfa,on='ID',how='left')
            dff = pd.merge(dff,dfb,on='ID',how='left')
            dff = pd.merge(dff,dfc,on='ID',how='left')
            dff = dff.fillna(0) #空转成0，为修改整数类型
            dff[['挂机前计数','转人工前计数','途经计数']] = dff[['挂机前计数','转人工前计数','途经计数']].astype(int)
            dff = dff[['首意图','排序','末业务意图','挂机前计数','人工前意图','转人工前计数','途经意图','途经计数']]
            dff = dff.replace(0,'') #0换成空
        else:
            #排序 末业务意图 挂机前计数 人工前意图 转人工前计数 途经意图 途经计数
            #挂机前意图
            dfa = Lianlu.get_value04(df=df02,top=top,column1='末业务意图',out_column='挂机前计数')
            # 转人工前意图
            dfb = Lianlu.get_value04(df=df02,top=top,column1='人工前意图',out_column='转人工前计数')
            #途径意图
            dfc = Lianlu.get_value04(df=df04,top=top,column1='途经意图',out_column='途经计数')

            #合并
            dff = pd.concat([dfa,dfb,dfc],axis=1)
            dff = dff[['排序','末业务意图','挂机前计数','人工前意图','转人工前计数','途经意图','途经计数']]
        return dff


if __name__ == '__main__':

    df = pd.read_csv('开通流量包开头通话12.csv')
    Lianlu.yitu_count(df=df,intent_name='开通流量包')