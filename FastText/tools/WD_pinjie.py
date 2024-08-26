import pandas as pd
import os
import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用


def WD_pinjie(outpunt_path='',path='',classi='.xlsx',skiprows=0,is_return=False):
    """
    outpunt_path:输出路径
    path:读取文件夹的路径，默认当前文件下
    classi:读取的文件类型，默认.xlsx
    skiprows:是否忽略行，默认没有
    is_return:是否返回dataframe
    """
    file_list = [file for file in os.listdir(path) if file.endswith(classi)]
    # print(file_list)

    dfs = pd.DataFrame()
    for file in file_list:
        print(file)
        if dfs.empty:
            if classi == '.xlsx' or classi == '.xls':
                dfs = pd.read_excel(path+file,skiprows=skiprows, encoding='utf-8')
            else:
                dfs = pd.read_csv(path+file,skiprows=skiprows, encoding='utf-8')
        else:
            if classi == '.xlsx' or classi == '.xls':
                dff = pd.read_excel(path+file,skiprows=skiprows, encoding='utf-8')
            else:
                dff = pd.read_csv(path+file,skiprows=skiprows, encoding='utf-8')
            dfs = pd.concat([dfs,dff])

    if is_return == False:
        if  classi == '.xlsx' or classi == '.xls':
            dfs.to_excel(outpunt_path, index=False)
        else:
            dfs.to_csv(outpunt_path, index=False)
    else:
        return dfs

if __name__ == '__main__':
# 
    path = 'data/对话明细/5bj/5bj/'
    out = 'data/对话明细/5bj/5bj/jieguo.csv'
    df = WD_pinjie(outpunt_path=out,path=path,classi='.csv',is_return=True)
    # df = pd.read_csv('data/对话明细/5bj/5bj/全量话务（全国）1716946832027sss.csv')
    # print(df)
    df.to_csv(out,index=False)
