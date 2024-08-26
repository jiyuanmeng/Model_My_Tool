a = '用户类型引导词==》查询余额或欠费==》预判高频自助服务==》查询余额或欠费==》查询余额或欠费==》预判高频自助服务==》查询余额或欠费==》办理停机业务'

list = str(a).split('查询余额或欠费==》')[1:] #根据意图名截取，不要第一个元素
lists = []
for i in list:
    j = i.split('==》')[0]
    lists.append(j)
lists = [x for x in lists if x != ""] #去空元素
print(lists)

import pandas as pd

# 假设这是你的原始DataFrame
data = {'A': [1, 2, 3], 'B': [['预判高频自助服务', '预判高频自助服务'], ['预判高频自助服务'], ['办理停机业务']]}
df = pd.DataFrame(data)
print(df)

# 使用explode方法拆分B列
# df_exploded = df.explode('B')

df['B'] = df['B'].apply(lambda x: x.split(', ') if isinstance(x, str) else x)
df_exploded = df.explode('B')

# print(df_exploded)