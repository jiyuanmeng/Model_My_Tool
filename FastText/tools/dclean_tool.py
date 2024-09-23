import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用

import pandas as pd
import setting
import datetime
from tqdm import tqdm

class DClean:
    def clean_intention(da_dataframe=None,da_path=None,area='河北',is_return=False,number=None):
        """
        筛选数据是否在意图列表中,返回两个结果集：结果集、剔除集
        is_return，true则返回结果集对象，并生成一个剔除数据文件
        is_return，False则生成结果集文件、剔除数据文件

        da_dataframe：传入的是个对象
        da_path：传入的数据源路径
        area:获取的意图列表的地区，默认是河北
        is_return:是否有返回
        number:版本号，用于文件命名
        """

        # 1获取意图列表文件
        if area == '河北':
            list_path = setting.intention_list_hebei
        d1 = pd.read_excel(list_path)
        d1 = d1['意图名称'].values.tolist()

        # 2获取数据原
        if da_dataframe == None:
            da = pd.read_excel(da_path)
        else:
            da = da_dataframe

        # 3数据拆分        
        re0 = []    # 结果集
        re1 = []    # 被剔除的数据

        for line,i in zip(da.意图名称.str.strip(),da.问题):
            if line in d1:
                l_lit = []
                l_lit.append(line)
                l_lit.append(i)
                re0.append(l_lit)
            else:
                l_lit = []
                l_lit.append(line)
                l_lit.append(i)
                re1.append(l_lit)
        #结果数据集
        res = pd.DataFrame(re0,columns=['意图名称','问题'])
        #被剔除的数据集
        eliminate = pd.DataFrame(re1,columns=['意图名称','问题'])

        # 5判断返回的类型
        clean_path = "output/清洗结果集-{}.xlsx".format(number)
        eliminate_path = "output/被剔除意图列表结果集-{}.xlsx".format(number)

        if is_return == False:
            res.to_excel(clean_path,index=False)
            eliminate.to_excel(eliminate_path,index=False)
            print("清洗的结果为：{}".format(clean_path))
            print("剔除的结果为：{}".format(eliminate_path))
        else:
            eliminate.to_excel(eliminate_path,index=False)
            print("剔除的文件路径为：{}".format(eliminate_path))
            print("剔除的数据是：{}".format(eliminate))
            return res

    def clean_repeat(da_path=None,df=None,nrows='',is_return=False,number=None):
        """
        去重，清洗相同的语料但意图标注重复了
        is_return,默认False生成两个文件,并返回结果集文件路径
        is_return,true返回结果集并，只生成被剔除文件

        da_path:加工的文件路径
        df：加工的dataframe对象
        is_return:是否返回，如果默认否，返回的是两个dataframe
        number：版本号，用于输出文件命名

        return
        is_return是true，返回结果集对象，否则返回结果文件路径
        """
        # 读取数据集
        if da_path != None:
            da = da_path.split(".")[-1]   # 得到文件后缀类型
            if da == "xlsx" or da == "xls":
                if nrows == '':
                    df = pd.read_excel(da_path)
                else:
                    df = pd.read_excel(da_path,nrows=nrows)
            elif da == "csv":
                if nrows == '':
                    df = pd.read_csv(da_path)
                else:
                    df = pd.read_csv(da_path,nrows=nrows)
            else:
                    df = pd.read_table(da_path)
        else:
            df = df       

        # 筛选重复数据
        d1 = df.groupby('问题').agg({"意图名称": lambda x: ','.join(x.astype(str).unique())}).reset_index()
        d2 = df.groupby('问题').size().reset_index(name='计数')
        d3 = pd.merge(d1,d2,on='问题',how='inner')

        if  d3[d3['计数']>1].shape[0] == 0:
            res = d3
            res_wrong = pd.DataFrame(columns=['问题','意图名称'])
        else:
            res = pd.merge(df,d3[d3['计数']==1],on='问题',how='inner')
            res = res[['问题','意图名称_x']].rename(columns={'意图名称_x':'意图名称'})

            res_wrong = d3[d3['计数']>1]
        
        # 返回类型
        if is_return != False:
            res_wrong_path = "output/剔除重复集-{}.xlsx".format(number)
            res_wrong.to_excel(res_wrong_path)
            return res
        else:
            res_path = "output/去重后结果集-{}.xlsx".format(number)
            res.to_excel(res_path)
            res_wrong.to_excel("output/剔除重复集-{}.xlsx".format(number))
            print("重后结果集路径：{}".format(res_path))
            return res_path

    def clean_split(da_path=None,df=None,number=None,is_return=False):
        """
        测试结果使用，将预测标签结果进行拆分,默认生成一个结果excel文件；会返回正确、错误

        da_path:加工的文件路径，不传默认不读取文件
        df：加工的dataframe对象
        number：版本号，仅用于输出文件命名
        is_return:默认False，true返回一个对象
        """
        if da_path != None:
            da = pd.read_excel(da_path)
        else:
            da = df

        lists = []
        # 拆分数据 
        # (('__label__反映故障问题', '__label__反映宽带故障'), array([0.78577971, 0.20582965]))
        for index, row in tqdm(da.iterrows(),desc='识别结果是否正确'):
            i = str(row['预测结果'])
            i = eval(i.replace('array','').replace(' ','').replace('__label__',''))
            if len(i[0]) == 1:
                list = []
                a = i[0][0]
                b = i[1][0]
                if a == row['意图名称']:
                    c = '正确'
                else:
                    c = '错误'
                list.append(c)
                list.append(str(row['意图名称']))
                list.append(a)
                list.append(b)
                list.append(row['问题'])
                lists.append(list)
            else:
                 list = []
                 a = i[0][0]
                 b = i[1][0]
                 e = i[0][1]
                 d = i[1][1]
                 if a == row['意图名称']:
                     c = '正确'
                 else:
                     c = '错误'
                 list.append(c)
                 list.append(row['意图名称'])
                 list.append(a)
                 list.append(b)
                 list.append(e)
                 list.append(d)
                 list.append(row['问题'])
                 lists.append(list)       

        df = pd.DataFrame(lists)
        if df.shape[1] == 5:
            df.columns = ['是否正确','原意图','识别意图','置信度','问题']
            df[['置信度']] = df[['置信度']].map(lambda x: f'{x:.2%}')
        else:
            df.columns = ['是否正确','原意图','识别意图1','置信度1','识别意图2','置信度2','问题']
            df[['置信度1']] = df[['置信度1']].map(lambda x: f'{x:.2%}')
            df[['置信度2']] = df[['置信度2']].map(lambda x: f'{x:.2%}')

        if is_return == True:
            return df
        else:
            dpath = "output/result-test{}.xlsx".format(number)
            df.to_excel(dpath, index=False)
            return dpath

    def clean_split_prediction(da_path=None,df=None,number=None,is_return=False):
        """
        预测结果使用，将预测标签结果进行拆分,默认生成一个结果excel文件

        da_path:加工的文件路径，不传默认不读取文件
        df：加工的dataframe对象
        number：版本号，仅用于输出文件命名
        is_return:默认False，true返回一个对象
        """
        if da_path != None:
            da = pd.read_excel(da_path)
        else:
            da = df

        lists = []
        # 拆分数据
        for index, row in tqdm(da.iterrows(), total=da.shape[0]):
            i = str(row['预测结果'])
            i = eval(i.replace('array','').replace(' ','').replace('__label__',''))
            if len(i[0]) == 1:
                list = []
                a = i[0][0]
                b = i[1][0]
                list.append(row['问题'])
                list.append(a)
                list.append(b)
                lists.append(list)
            else:
                #  (('无意图', '反映故障问题'), [0.88337499, 0.05402302])
                 list = []
                 a = i[0][0]
                 b = i[1][0]
                 c = i[0][1]
                 d = i[1][1]
                 list.append(row['问题'])
                 list.append(a)
                 list.append(b)
                 list.append(c)
                 list.append(d)
                 lists.append(list)       

        df = pd.DataFrame(lists)
        if df.shape[1] == 3:
            df.columns = ['问题','识别意图','置信度']
            df[['置信度']] = df[['置信度']].applymap(lambda x: f'{x:.2%}')
        else:
            df.columns = ['问题','识别意图1','置信度1','识别意图2','置信度2']
            df[['置信度1']] = df[['置信度1']].applymap(lambda x: f'{x:.2%}')
            df[['置信度2']] = df[['置信度2']].applymap(lambda x: f'{x:.2%}')

        if is_return == True:
            return df
        else:
            dpath = "output/result-test{}.xlsx".format(number)
            df.to_excel(dpath, index=False)
        
        

if __name__ == '__main__':
    
    da = pd.read_excel("output/test_result2023-10-30.xlsx",nrows=100)
    # clean_intention(da_path=da_path)
    
    res = DClean.clean_split_prediction(df=da,is_return=True)
    print(res)
