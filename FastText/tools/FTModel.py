import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用

import pandas as pd
import fasttext
import datetime
from tools.dclean_tool import DClean    
from tools.dprocess_tool import DProcess
from tqdm import tqdm

class FTModel:
    def fasttext_train_notest(data_path=None,datatrain_path=None,datatest_path=None,nrows='',model_number=None,is_size=True,test_size=None):
             """
             训练模型、可以选择是否需要拆分测试、训练集

             data_path:数据集路径，需要拆分测试、训练集时使用
             datatrain_path：训练集路径
             datatest_path：测试集路径
             model_number:模型版本号
             is_size:是否拆分测试集与训练集
             test_size:测试集占比，整数时认为是样本的数量

             return 
             is_size 是true
             返回4个路径：训练带标签 训练不带 测试带标签 测试不带
             is_size 是fase
             返回2个路径：训练带标签 测试带标签
             """
        
         # 0训练集、测试集拆分
             if is_size == True:
                #等比拆分
                df_train,df_test,df_train_path,df_test_path = DProcess.process_split(test_size=test_size,number=model_number,da_path=data_path,is_return=True,is_output=True)

         # 1练集数据加工
             if datatrain_path != None:
                da = datatrain_path.split(".")[-1]   # 得到文件后缀类型
                if da == "xlsx" or da == "xls":
                    if nrows == '':
                        df01 = pd.read_excel(datatrain_path)
                    else:
                        df01 = pd.read_excel(datatrain_path,nrows=nrows)
                elif da == "csv":
                    if nrows == '':
                        df01 = pd.read_csv(datatrain_path)
                    else:
                        df01 = pd.read_csv(datatrain_path,nrows=nrows)
                else:
                        df01 = pd.read_table(datatrain_path)
                print("1、训练集数据读取完毕！")
             else:
                  df01 = df_train  

            # 加工训练集格式 返回的是带标签的文件路径
             train_path = DProcess.process_fasttext(type='train',model_number=model_number,df=df01)


         # 2测试集数据加工
             if datatest_path != None:
                da = datatest_path.split(".")[-1]   # 得到文件后缀类型
                if da == "xlsx" or da == "xls":
                    if nrows == '':
                        df02 = pd.read_excel(datatest_path)
                    else:
                        df02 = pd.read_excel(datatest_path,nrows=nrows)
                elif da == "csv":
                    if nrows == '':
                        df02 = pd.read_csv(datatest_path)
                    else:
                        df02 = pd.read_csv(datatest_path,nrows=nrows)
                else:
                        df02 = pd.read_table(datatest_path)
                print("1、测试集数据读取完毕！")  
             else:
                 df02 = df_test

            # 加工测试集格式
             test_path = DProcess.process_fasttext(type='test',model_number=model_number,df=df02)

        # 3模型训练
             model = fasttext.train_supervised(input=train_path,lr=0.08,epoch=25,wordNgrams=3)
             model.save_model("model/model-{}.bin".format(model_number)) #保存模型
             print("4、模型训练完毕请查收！：output/model-{}.bin".format(model_number))        
             
             if is_size == True:
                  return train_path,test_path,df_train_path,df_test_path
             else:
                  return train_path,test_path
                  


    def fasttext_train(data_path,model_path,nrows=''):
            """
            训练意图标签识别模型，需要注意：输入的数据源必须只有两列，"问题"列、"意图"列
            data_path:训练数据源路径
            model_path:模型保存路径
            nrows:训练数据源的指定读取行数
            """
        # 1读取训练数据
            da = data_path.split(".")[-1]   # 得到文件后缀类型
            if da == "xlsx" or da == "xls":
                if nrows == '':
                    df01 = pd.read_excel(data_path)
                else:
                    df01 = pd.read_excel(data_path,nrows=nrows)
            elif da == "csv":
                if nrows == '':
                    df01 = pd.read_csv(data_path)
                else:
                    df01 = pd.read_csv(data_path,nrows=nrows)
            else:
                    df01 = pd.read_table(data_path)
            print("1、训练数据读取完毕！")
        
        # 2过滤意图正确数据
            # da = clean_is(da_dataframe=da)

        # 3拆分测试集与训练集
            train_path = "process/train-{}.txt".format(datetime.date.today()) #训练集结果文件
            testdata_path = "process/testdata-{}.txt".format(datetime.date.today()) #测试集纯数据结果
            with open(train_path,"w") as file:
                pass
            with open(testdata_path,"w") as file:
                pass
            file01 = open(train_path,'w') # 训练集
            file02 = open(testdata_path,'w')  # 测试集-纯数据
            file02.write('问题	意图')
            file02.write('\n')

            i=0
            for line1,line2 in zip(df01.问题,df01.意图名称):
                i=i+1
                if i%10<9: # 9:1拆分
                    file01.write(line1)
                    file01.write(' ')
                    file01.write(line2)
                    file01.write('\n')
                else:
                    file02.write(line1)
                    file02.write('	')
                    file02.write(line2)
                    file02.write('\n')
            file01.close()
            file02.close()
            print("2、测试数据拆分完毕！{}".format(testdata_path))

        # 4数据加工
            # 4.1加工训练集
            f1 = open(train_path, 'r')
            f2 = open('process/temp.txt', 'w')

            lines = f1.readlines()
            for line in lines:
                line = line.strip()
                data = line.split(' ')
                if len(data) == 2:
                    label00 = data[1]
                    label01 = '__label__' + label00
                    txt00 = data[0]
                    f2.write(label01 + ' ')
                    f2.write(' '.join(list(txt00)))
                    f2.write('\n')

            f1.close()
            f2.close()
            os.remove(train_path)
            os.rename('process/temp.txt', train_path)

            # 4.2加工测试集
            test_path = "process/test-{}.txt".format(datetime.date.today()) # 测试集结果文件
            f3 = open(testdata_path, 'r')
            f4 = open(test_path, 'w')

            lines = f3.readlines()
            for i,line in enumerate(lines):
                if i == 0:
                     continue
                line = line.strip()
                data = line.split('	')
                if len(data) == 2:
                    label00 = data[1]
                    label01 = '__label__' + label00
                    txt00 = data[0]
                    f4.write(label01 + ' ')
                    f4.write(' '.join(list(txt00)))
                    f4.write('\n')
            f3.close()
            f4.close()
            print("3、训练集与测试集加工完毕！训练集:{}测试集{}".format(train_path,test_path))

        # 5模型训练
            model = fasttext.train_supervised(input=train_path,lr=0.04,epoch=100,wordNgrams=5)
            model.save_model(model_path) #保存模型
            print("4、模型训练完毕请查收！：{}".format(model_path))


    def fasttext_test(model_number,test_path,test_data_path=None):
            """
            调用模型进行测试,输出两个文件，test_path准确率结果，test_data_path预测的标签结果
            test_data_path不传参，默认不调用测试集预测结果

            model_path:调用的模组路径
            test_path:测试集路径（带标签的文件）
            test_data_path:测试集预测数据路径,不传默认不调用
            """
         
        # 1加载模型
            model = fasttext.load_model('model/model-{}.bin'.format(model_number))
            parameter = str(model.test(test_path))  #准确率
            parameter_label = model.test_label(test_path) #各标签准确率

            # 加工标签结果为
            label = list(parameter_label.keys())
            value = list(parameter_label.values())
            values = []
            for i in value:
                 values.append(i['precision'])
            parameter_label = pd.DataFrame({"意图":label,"准确率":values})
            parameter_label['意图'] = parameter_label['意图'].str.replace('__label__','')
            parameter_label[['准确率']] = parameter_label[['准确率']].applymap(lambda x: f'{x:.2%}')


        # 2得到测试参数结果
            test_result_parameter = "output/test_parameter{}.txt".format(model_number)
            test_result_parameter_lable = "output/test_parameter_lable{}.xlsx".format(model_number)
            
            with open(test_result_parameter,'w') as file:
                 file.write(parameter)
            print("模型测试参数结果请查收！:{}".format(test_result_parameter))

            parameter_label.to_excel(test_result_parameter_lable,index=False)

        
        #  3调用模型得到测试集的识别结果
            if test_data_path !=None:
                # test_result = "output/test_result{}.xlsx".format(model_number)
                res = FTModel.fasttext_prediction(prediction_path=test_data_path,model_number=model_number,k=1,is_return=True)
                # 返回的res是一个DataFrame

                # 判断测试集的文件类型
                da = test_data_path.split(".")[-1]
                if da == "xlsx" or da == "xls":
                     dt = pd.read_excel(test_data_path)
                else:
                    dt = pd.read_table(test_data_path)

                # 得到原意图
                res = pd.merge(dt,res,on="问题",how='inner')

                # 调用加工结果集文件
                test_result = DClean.clean_split(number=model_number,df=res)
                # res.to_excel(test_result)
                print("模型测试集预测结果请查收：{}".format(test_result))

    def fasttext_prediction(model_number,prediction_path=None,dff=pd.DataFrame(),k=1,is_return=False):
        """
        调用模型进行预测，需要注意，预测集的预测字段必须叫"问题"

        prediction_path:预测集路径
        model_number:模型版本号
        k:标签个数 默认生成前2个标签
        is_return:是否给一个返回值，默认false会生成一个结果excel文件；否则将会把结果的DataFrame返回
        df:传入预测的dataframe，默认是空则传入的是一个文件
        """

    # 1读取预测集数据
        if dff.empty:
            da = prediction_path.split(".")[-1]   # 得到文件后缀类型
            if da == "xlsx" or da == "xls":
                df = pd.read_excel(prediction_path)
            elif da == "csv":
                df = pd.read_csv(prediction_path)
            else:
                df = pd.read_table(prediction_path)
            print("预测集数据读取完毕！")
        else:
             df = dff

    # 2调用模型
        results = []  # 用于存储预测结果的列表
        model_path = "model/model-{}.bin".format(model_number)
        model = fasttext.load_model(model_path) #加载模型
        for line in tqdm(df.问题):
            re = model.predict(' '.join(list(line)),k=k)
            results.append((line, re))

    # 3将结果输出
        df_results = pd.DataFrame(results, columns=['问题', '预测结果'])
        if is_return == False:
             df_results.to_excel('output/result_prediction{}'.format(model_number), index=False)
             print("预测成功，请查收！:output/result_prediction{}".format(model_number))
        else:
             return df_results

if __name__ == '__main__':

    model_path = "意图识别-测试.bin"
    data_path = "训练集.xlsx"
    
    FTModel.fasttext_train(model_path=model_path,data_path=data_path,nrows=1000)

