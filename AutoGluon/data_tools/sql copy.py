import pandas as pd
import requests

dic = [['202405','雄安']]
zk = 't_train_yw_kb_202405'
z4 = 't_train_yw_kb_202405_1_4'
z7 = 't_train_yw_kb_202405_1_7'
z10 = 't_train_yw_kb_202405_1_10'


def read_txt(path,i):
    """
    读sql txt
    """
    with open(path, "r", encoding="utf-8") as f:
        sql = f.read()
    sql = sql.format(month_id=dic[i][0], area_name=dic[i][1])
    return sql


def get_request(sql_text: str):
    """
    请求数据库接口
    """
    # 通过requests库调用clickhouse的http接口。
    url = 'http://db:8123/'
    response = requests.post(url, data=(sql_text).encode('utf-8'))
    res = response.text
    code = response.status_code
    print(res)
    return res,code


def sql_url(sql_text: str,is_retrun=False):
    """
    调用请求
    """
    if is_retrun == True:
        #调用校验sql，主要执行查询语句并获取结果值
        res,code = get_request(sql_text=sql_text)
        return res
    else:
        #调用执行sql，主要执行insert语句
        for i in range(1,11):
            #如果执行失败再次尝试，一共尝试10次
            res,code = get_request(sql_text=sql_text)
            if code == 200:
                return 0
            else:
                print(print(f"-------------------------执行第{i}次执行错误，再次尝试-------------------------------------------------"))
        #10次都失败，返回错误1
        return 1

def process_ver():
    """
    校验过程表是否清空
    """
    test1 = f'select count(*) from hb.{z4}'
    test2 = f'select count(*) from hb.{z7}'
    test3 = f'select count(*) from hb.{z10}'

    rlist = []

    #获取count结果
    r1 = function01(text=test1)
    if r1 != 0:
        rlist.append(z4)
    r2 = function01(text=test2)
    if r2 != 0:
        rlist.append(z7)
    r3 = function01(text=test3)
    if r3 != 0:
        rlist.append(z10)
    
    #判断是否都清空了
    if len(rlist) == 0:
        return 0
    else:
        return rlist


def function01(text):
    res = int(sql_url(sql_text=text,is_retrun=True))
    return res
    

def case():
    for i in range(0,len(dic)):
        print(f"-------------------------第{dic[i]}个文件开始执行！-----------------------------")

        #1 校验宽表数据重复
        # ss = f"select count(*) from hb.{zk} where t.area_name = '{dic[i][1]}' and t.month_id = '{dic[i][0]}'"   
        # sr = function01(text=ss)
        # if sr != 0:
            # print(f"宽表数据未清空：{sr}")
            # break
        
        #2 校验中间表是否清空
        res_pro = process_ver()
        if res_pro !=0:
            print(f"-------------------------中间表未清空：{res_pro}-----------------------------")
            break


        #3 获取sql语句
        s1 = read_txt(path='sql1.txt',i=i)
        s2 = read_txt(path='sql2.txt',i=i)
        s3 = read_txt(path='sql3.txt',i=i)
        s4 = read_txt(path='sql4.txt',i=i)


        #4 执行inser中间表
        #4-1第一部分
        re1 = sql_url(sql_text=s1)
        if re1 == 1:
            print(f"---------------------------------erro:第{dic[i]}个文件第一部分执行错误！----------------------------------------------------------")
            break
        else:
            print(f"---------------------------------第{dic[i]}个文件第一部分执行完毕！----------------------------------------------------------")
        #4-2第二部分
        re2 = sql_url(sql_text=s2)
        if re2 == 1:
            #清空1中间表
            flag = sql_url(sql_text=f'TRUNCATE TABLE hb.{z4}')
            print(f"---------------------------------erro:第{dic[i]}个文件第二部分执行错误！----------------------------------------------------------")
            break
        else:
            print(f"---------------------------------第{dic[i]}个文件第二部分执行完毕！----------------------------------------------------------") 
        #4-3第三部分
        re3 = sql_url(sql_text=s3)
        if re3 == 1:
            #清空2中间表
            flag = sql_url(sql_text=f'TRUNCATE TABLE hb.{z7}')
            print(f"---------------------------------erro:第{dic[i]}个文件第三部分执行错误！----------------------------------------------------------")
            break
        else:
            print(f"---------------------------------第{dic[i]}个文件第三部分执行完毕！----------------------------------------------------------")

        #5 insert宽表
        flag = sql_url(sql_text=s4)
        print(f"---------------------------------第{dic[i]}个文件插入宽表执行完毕！----------------------------------------------------------")


        #6 清空中间表
        flag = sql_url(sql_text=f'TRUNCATE TABLE hb.{z4}')
        flag = sql_url(sql_text=f'TRUNCATE TABLE hb.{z7}')
        flag = sql_url(sql_text=f'TRUNCATE TABLE hb.{z10}')
        print(f"---------------------------第{dic[i]}个文件中间表清空完毕！----------------------------------------------------------")

        #7 校验中间表是否清空
        res_pro = process_ver()
        if res_pro !=0:
            print(f"-------------------------中间表未清空：{res_pro}-----------------------------")
            break


        print(f"-------------------------第{dic[i]}个文件已执行完毕！-----------------------------")


if __name__ == '__main__':
    case()