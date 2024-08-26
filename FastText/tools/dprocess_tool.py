import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
from sklearn.model_selection import train_test_split

class DProcess:
    def process_fasttext(type,model_number,df):
        """
        处理加工fasttext需要的格式,返回加工结果文件路径

        type：train或test
        model_number：模型版本号
        df：传入的dataframe，必须存在“意图名称”、“问题”
        """
        path = "process/{}-{}.txt".format(type,model_number)
        f = open(path, 'w')

        for line,lines in zip(df.意图名称,df.问题):
            line = line.strip()
            label01 = '__label__' + line
            txt00 = lines
            f.write(label01 + ' ')
            f.write(' '.join(list(txt00)))
            f.write('\n')
        f.close()

        return path
    
    def process_split(test_size,number,da_path=None,df=None,nrows='',is_return=False,is_output=False):
        """
        等比拆分训练集与测试集

        da_path:拆分数据集路径，默认不传
        df：拆分数据的dataframe类，默认不传
        test_size：测试集占比，如果是整数的话就是样本的数量
        nrows:拆分数据集的读取行数
        number:版本号,用于结果数据的文件命名
        is_return:是否返回
        is_output:是否生成结果文件
        如果都是true，那么会生成文件同时返回对象

        return:先返回训练集、再返回测试集
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

        # 得到训练集的x、y集数据    x:问题 y:标签
        train_data = df[['问题']]
        train_target = df[['意图名称']]

        # 调用方法
        X_train,X_test, y_train, y_test =train_test_split(train_data,train_target,test_size=test_size, random_state=0)
            # print(test_df)
            # train_data：所要划分的样本特征集  问题x
            # train_target：所要划分的样本结果  标签y
            # test_size：样本占比，如果是整数的话就是样本的数量
            # random_state：是随机数的种子。
            # 随机数种子：其实就是该组随机数的编号，在需要重复试验的时候，保证得到一组一样的随机数。比如你每次都填1，其他参数一样的情况下你得到的随机数组是一样的。但填0或不填，每次都会不一样。
        
        # 结果输出
        test_df = pd.concat([y_test,X_test],axis=1) # axis:0行拼接 1列拼接
        train_df = pd.concat([y_train,X_train],axis=1) # axis:0行拼接 1列拼接
        test_data_path = "data/测试数据集-{}.xlsx".format(number)
        train_data_path = "data/训练数据集-{}.xlsx".format(number)
        
        if is_output == True and is_return == False:
            test_df.to_excel(test_data_path,index=False)
            train_df.to_excel(train_data_path,index=False)
        elif is_return == True and is_output == True:
            test_df.to_excel(test_data_path,index=False)
            train_df.to_excel(train_data_path,index=False)
            return train_df,test_df,train_data_path,test_data_path
        else:
            return train_df,test_df


if __name__ == '__main__':

    df = pd.read_excel("data/测试数据集-1.0.1.xlsx",nrows=1000)
    DProcess.process_split(test_size=100,number='1.0.2',df=df)
