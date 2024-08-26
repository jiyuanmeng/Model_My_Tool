import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import os
import re
import time
import csv
import pandas as pd
import hashlib
import requests
import warnings
warnings.simplefilter("ignore", UserWarning)

# mapping pandas data types to Clickhouse data types
CTM = {
    'str': 'String',
    'int': 'Int32',
    'float': 'Float64',
    'datetime': 'DateTime',
    'bool': 'UInt8',
    'date': 'Date',
}


class FileTable():

    def __init__(self,
                 *,
                 dir_path,
                 match_pattern,
                 sep=',',
                 schema=None,
                 ):
        self.dir_path = dir_path
        self.schema = schema
        self.sep = sep
        self.match_pattern = match_pattern

    @staticmethod
    def _md5(s):
        return hashlib.md5(str(s).encode()).hexdigest()

    @staticmethod
    def _list_all_files(dir_path, pattern):
        all_files = []
        for root, dirs, files in os.walk(dir_path):
            for file in files:
                if re.search(pattern, file) and '~' not in file:
                    file_path = os.path.join(root, file)
                    all_files.append(file_path)
            for dir in dirs:
                all_files.extend(FileTable._list_all_files(dir, pattern))
        return all_files

    @staticmethod
    def _get_cols_from_schema(schema, has_compute=True):
        # 从schema中获取列名, has_compute=True表示获取有compute的列
        schema_cols = schema['cols']
        schema_cols = [
            col for col in schema_cols if 'compute' not in col or col['compute'] == has_compute]
        return schema_cols

    def _read_excel_or_csv(self, file, **kwargs):
        """
        数据文件读取,返回的是一个dataframe类型
        """
        print(f'Reading {file}')
        schema = self.schema
        schema_cols = FileTable._get_cols_from_schema(
            schema, has_compute=False)
        # 指定列名
        cols_names = [col['name'] for col in schema_cols]
        # 指定列的数据类型
        column_types = {col['name']: col['type'] for col in schema_cols}
        if file.endswith('.xlsx') or file.endswith('.xls'):
            df = pd.read_excel(file,
                               usecols=cols_names, dtype=column_types, ** kwargs)
        elif file.endswith('.csv'):
            df = pd.read_csv(file, sep=self.sep,
                             names=cols_names,  dtype=column_types, **kwargs)
        elif file.endswith('.txt'):
            df = pd.read_csv(file, sep=self.sep,
                             names=cols_names,  dtype=column_types, **kwargs)
        elif file.endswith('.zip'):
            df = pd.read_csv(file, sep=self.sep,compression='zip',on_bad_lines='skip',quoting=csv.QUOTE_NONE,
                             names=cols_names,  dtype=column_types, encoding_errors='ignore', **kwargs)
        elif file.endswith('_0'):
            df = pd.read_csv(file,sep=self.sep,names=cols_names, dtype=column_types,**kwargs)
        #elif 'DWA_M_CUST_PERCEP_PREDIC_MON_202404_' in file:
        #    df = pd.read_csv(file,sep=self.sep,names=cols_names, dtype=column_types,on_bad_lines='skip',encoding_errors='ignore',quoting=csv.QUOTE_NONE,**kwargs)
        #else:
        #    raise ValueError('Unsupported file type')
        else:
        # 尝试用csv类型读取
            try:
                df = pd.read_csv(file, sep=self.sep, names=cols_names, dtype=column_types, on_bad_lines='skip',
                              quoting=csv.QUOTE_NONE, **kwargs)
            except Exception as e:
                print('except:', e)
                raise ValueError(f'Unsupported file type. Original error: {e}')
        
        #df1 = pd.DataFrame()
        #for chunk in df:
        #df1 = pd.concat([chunk for chunk in df])
            #df1 = chunk[cols_names]
            #yield df1
        df = df[cols_names]

        if 'md5_key' in schema:
            md5_key = schema['md5_key']
            df[f'{md5_key}_md5'] = df[md5_key].apply(FileTable._md5)
        if 'md5_key_2' in schema:
            md5_key_2 = schema['md5_key_2']
            df[f'{md5_key_2}_md5'] = df[md5_key_2].apply(FileTable._md5)
        return df

    def list_all_files(self):
        return self._list_all_files(self.dir_path, self.match_pattern)

    def read(self, **kwargs) -> pd.DataFrame: # type: ignore
        """
        循环执行数据表读取，并返回一个生成器
        """
        #df_result = pd.DataFrame()
        for file in self.list_all_files():
            df = self._read_excel_or_csv(file, **kwargs)
            #df_result = pd.concat([df_result, df])
            yield df #返回一个生成器

    def create_columns_sql(self):
        """
        生成建表语句中,字段的定义
        """
        schema_cols = FileTable._get_cols_from_schema(self.schema)
        order_key = self.schema['order_key']
        cols = []
        for col in schema_cols:
            col_name = col['name']
            col_type = col['type']
            # 判断是order_key
            col_sql = f'"{col_name}" {CTM[col_type]}' if col_name == order_key else f'"{col_name}" Nullable({CTM[col_type]})'
            # 添加注释
            if 'comment' in col:
                col_sql += ' COMMENT \'{}\''.format(col['comment'])
            cols.append(col_sql)
        if 'md5_key' in self.schema:
            md5_key = self.schema['md5_key']
            cols.append(f'"{md5_key}_md5" {CTM["str"]}')

        if 'md5_key_2' in self.schema:
            md5_key_2 = self.schema['md5_key_2']
            cols.append(f'"{md5_key_2}_md5" {CTM["str"]}')
        
        return ', \n'.join(cols)

    def create_table_sql(self):
        """
        生成建表sql,返回的是一个字符串
        """
        table_name = self.schema['table_name']
        order_key = self.schema['order_key']
        sql = '''
                CREATE TABLE hb."{}"
                (
                {}
                ) ENGINE = MergeTree()
                ORDER BY ("{}")
                '''.format(
                            table_name,
                            self.create_columns_sql(),
                            order_key
                        )
        return sql

    def dump_to_ck(self,**kwargs):
        """
        控制台执行流程
        """
        # 把数据结构和数据内容导出clickhouse的目录中
        ck_data_dir = '/var/log/clickhouse-server'
        host_data_dir = '/home/big_data1/app/clickhouse/log'
        table_name = self.schema.get('table_name')

        # 1读取数据文件列，创建建表sql语句
        #sql = self.create_table_sql()

        # 2加载sql初始化
        # 2-1如果本表已存在就删除
        #FileTable._exec_sql("DROP TABLE IF EXISTS hb.\"{}\"".format(table_name))
        # 2-2加载数据库接口
        #FileTable._exec_sql(sql)

        # 3读取文件数据，导入数据库
        # 3-1读取文件数据
        df = self.read(**kwargs)

        # 用生成器分批处理df,文件数仅1个每次处理1000000行
        print("---------数据长度---------",len(self.list_all_files()))

        # 3-2判断是否多文件读取
        if len(self.list_all_files())>1:
            for i in range(len(self.list_all_files())):
                df1 = next(df)
                #print(df)
                #print(type(df))
                FileTable._exec_data_sql(table_name, df1)
                print(f'------------------第{i}个文件处理完毕！！！------------------')
        else:
            df = next(df)
            temp = 0
            length = 1000000
            # 3-2-1判断文件大小，过大则分隔处理
            if len(df)<=length:
                # 执行一次
                FileTable._exec_data_sql(table_name, df)
            else:
                for chunksize in range(length,len(df),length):
                    try:
                        if len(df)-chunksize>length:
                            df_1 = df[temp:chunksize]
                            FileTable._exec_data_sql(table_name, df_1)
                            temp += length
                        else:
                            df_1 = df[chunksize:]
                            FileTable._exec_data_sql(table_name, df_1)
                    except Exception as se:
                        print(se)


    @staticmethod
    def _exec_sql(sql: str):
        """
        调用数据库接口，执行sql语句
        """
        # 通过requests库调用clickhouse的http接口。
        print(sql)
        url = 'http://db:8123/'
        # data encode utf-8
        response = requests.post(url, data=sql.encode('utf-8'))
        print(response.text)

    @staticmethod
    def _exec_data_sql(table_name: str, df: pd.DataFrame):
        """
        生成insert语句,并调用数据库接口执行
        """
        # 通过requests库调用clickhouse的http接口。
        print(df)
        url = 'http://db:8123/'
        data = df.to_csv(index=False)
        response = requests.post(url, data=(
            f'INSERT INTO hb."{table_name}" FORMAT CSVWithNames\n' + data).encode('utf-8'))
        print(response.text)
