from decimal import Decimal
import pandas as pd

d1 = pd.read_excel("output/result-Y1.1二级查询菜单.xlsx")

x_list = []
y_list = []
z_list = []
h_list = []
k_list = []
d_list = []


for index, row in d1.iterrows():
    d = row["问题"]
    # e = row["原意图"]
    a = str(row["预测结果"])
    b = a.replace("'__label__","").replace("array","").replace("[","").replace("]","")
    x = b.split("',")[0].split("((")[1]
    y = b.split(",")[1].split("')")[0]
    z = Decimal(b.split(",")[2].split("(")[1])  # 概率列科学计数法转小数
    h = Decimal(b.split(",")[3].split("))")[0]) # 概率列科学计数法转小数
    k = z-h
    x_list.append(x)
    y_list.append(y)
    z_list.append(z)
    h_list.append(h)
    k_list.append(k)
    d_list.append(d)
    

d2 = pd.DataFrame({"用户问题":d_list,"意图1":x_list,"意图2":y_list,"概率1":z_list,"概率2":h_list,"概率差值":k_list})
d3 = d2[d2["概率差值"]<=0.4]    # 筛选数双意图
d2[["概率1","概率2"]] = d2[["概率1","概率2"]].applymap(lambda x: f'{x:.1%}')    # 转百分比保留1位小数
d3[["概率1","概率2"]] = d3[["概率1","概率2"]].applymap(lambda x: f'{x:.1%}')

d2.to_excel("output/拆分结果-Y1.1二级查询菜单.xlsx",index=False)
print("拆分结果已导出！")

d3.to_excel("output/双意图结果-Y1.1二级查询菜单.xlsx",index=False)
print("双意图已导出！")
# print(d3)