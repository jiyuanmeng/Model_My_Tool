import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd 

class Lianlu:
    def yitu_count(df,intent_name,is_return=False):
        """
        调用的dataframe需要是意图链路结果，用==》连接
        给出意图链路中某个意图下的途经意图、转人工意图、挂机前意图TOP计数

        df:传入的dataframe，意图链路的列名必须是【意图清单】，对话id列名必须是【session_id】
        intent_name:加工的意图名
        is_return:是否有返回值，默认fase会生成结果文件，否则返回dataframe对象
        """
        # 1挂机前最后一个意图
        a_list = []
        for i,row in df.iterrows():
            list = []
            a = str(row['意图清单']).split("==》")[-1]
            list.append(row['session_id'])
            list.append(a)
            a_list.append(list)
        
        df1 = pd.DataFrame(a_list)
        df1.columns = ['对话ID','挂机前意图']


        # 2转人工前意图
        #2.1筛选转人工 ['用户类型引导词', '欢迎语通用播报', 'Y1一级菜单', '门户自助辅导']
        d2 = df[(df['意图清单'].str.contains('门户自助辅导')) | (df['意图清单'].str.contains('转人工服务'))]
        d2 = d2[['session_id','意图清单']]

        #2.2循环判断每一行，并取出转人工前最后一个意图
        b_list = []
        for i,row in d2.iterrows():
            list = []
            # 只包含'门户自助辅导'
            if '门户自助辅导' in row['意图清单'] and '转人工服务' not in row['意图清单']:
                b = row['意图清单'].split('==》门户自助辅导')[0].split("==》")[-1]
                list.append(row['session_id'])
                list.append(b)
                b_list.append(list)
            # 只包含'转人工服务'
            elif '转人工服务' in row['意图清单'] and '门户自助辅导' not in row['意图清单']:
                b = row['意图清单'].split('==》转人工服务')[0].split("==》")[-1]
                list.append(row['session_id'])
                list.append(b)
                b_list.append(list)
            # 都包含
            else:
                b = row['意图清单'].split('==》转人工服务')[0]
                if '门户自助辅导' in b:
                    bb = b.split('==》门户自助辅导')[0].split('==》')[-1]
                    list.append(row['session_id'])
                    list.append(bb)
                    b_list.append(list)
                else:
                    bb = b.split("==》")[-1]
                    list.append(row['session_id'])
                    list.append(bb)
                    b_list.append(list)
        df2 = pd.DataFrame(b_list)
        df2.columns = ['对话ID','转人工前意图']

        # 3关联得到全量数据
        dff = pd.merge(df2,df1,on='对话ID')

        # 4聚合统计
        #4.1挂机前意图
        dfa = dff.groupby(['挂机前意图']).size().reset_index(name='挂机前计数')
        dfa = dfa.loc[dfa['挂机前意图'] != intent_name ]  #剔除意图自己
        dfa = dfa.sort_values('挂机前计数',ascending=[False]) #倒序排列
        dfa['意图'] = intent_name #本次加工意图名
        dfa['排序'] = dfa.groupby(['意图']).cumcount() + 1 #组内排序
        dfa = dfa.head(10) #取前10
        dfa = dfa[['意图','排序','挂机前意图','挂机前计数']]
        dfa = dfa.reset_index(drop=True)

        #4.2转人工前意图
        dfb = dff.groupby(['转人工前意图']).size().reset_index(name='转人工前意图计数')
        dfb = dfb.loc[dfb['转人工前意图'] != intent_name] #剔除意图自己
        dfb = dfb.sort_values(['转人工前意图计数'],ascending=[False])
        dfb['意图'] = intent_name #本次加工意图名 
        dfb['转人工排序'] = dfb.groupby(['意图']).cumcount()+1
        dfb = dfb.head(10)
        dfb = dfb[['转人工前意图','转人工前意图计数']]
        dfb = dfb.reset_index(drop=True)

        #4.3途径意图
        d_list = []
        for i,row in df.iterrows():
            z = row['session_id']
            y_list = row['意图清单'].split(intent_name)[1:]
            for j in y_list:
                j_list = j.split('==》')
                for jj in j_list:
                    if jj != '':
                        list = []
                        list.append(z)
                        list.append(jj)
                        d_list.append(list)
        df3 = pd.DataFrame(d_list)
        df3.columns = ['对话ID','途经意图']
        df3 = df3.drop_duplicates(subset=['对话ID','途经意图']) #去重
        dfc = df3.groupby(['途经意图']).size().reset_index(name='途经意图计数')
        dfc = dfc.loc[dfc['途经意图']!= intent_name ] #剔除自己
        dfc = dfc.sort_values(['途经意图计数'],ascending=[False]) #倒序
        dfc['意图'] = intent_name #本次加工意图名    
        dfc['途经排序'] = dfc.groupby(['意图']).cumcount()+1
        dfc = dfc.head(10)
        dfc = dfc[['途经意图','途经意图计数']]
        dfc = dfc.reset_index(drop=True)

        #5导出
        df = pd.concat([dfa,dfb,dfc],axis=1) 
        if is_return == True:
            return df
        else:
            url_name = '{}意图链路计数.xlsx'.format(intent_name)
            df.to_excel(url_name,index=False)
            print("已生成链路计数结果：{}".format(url_name))

if __name__ == '__main__':

    df = pd.read_csv('开通流量包开头通话12.csv')
    Lianlu.yitu_count(df=df,intent_name='开通流量包')