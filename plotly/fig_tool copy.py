import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from prosess import *
from data import *
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

# 创建Dash应用
app = Dash(__name__)

#主题颜色
custom_template = {
"layout": {
    "paper_bgcolor": "rgb(35, 39, 85)",  # 设置背景颜色为深蓝色
    "plot_bgcolor": "rgb(35, 39, 70)",  # 设置绘图区域的背景颜色为深蓝色
    "title": {
        "font": {
            "color": "#CCFFFF",  # 设置标题文字颜色为白色
            'size':22
        }
    },
    "font": {
        "color": "white"  # 设置其他文字颜色为白色
    },
    "colorway": ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC949", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"]  # 自定义颜色序列
    }
}
pio.templates["dark_dashboard"] = custom_template
pio.templates.default = "dark_dashboard"

# 创建日期、单选组件
app.layout = html.Div([
    html.Div([
        #日期组件
        dcc.DatePickerRange(
            id='date-picker-range',
            start_date='2024-05-01',
            end_date='2024-05-02',
            display_format='YYYY-MM-DD'
        ),
        #地区下拉框
        dcc.Dropdown(
            id='region-filter',
            options=[
                {'label': '北一', 'value': '北方一中心'},
                {'label': '北二', 'value': '北方二中心'},
                {'label': '南一', 'value': '南方一中心'},
                {'label': '南二', 'value': '南方二中心'},
                {'label': '河北', 'value': '河北'},
                {'label': '北京', 'value': '北京'},
                {'label': '吉林', 'value': '吉林'},
                {'label': '江苏', 'value': '江苏'},
                {'label': '内蒙古', 'value': '内蒙古'},
                {'label': '山西', 'value': '山西'}
            ],
            value='北方一中心'
        )
    ]),
    #TOP下拉框
    dcc.Dropdown(
        id='top-filter',
        options=[
            {'label': '筛选TOP15', 'value': 15},
            {'label': '筛选TOP10', 'value': 10}
        ],
        value=15
    ),
     html.Div([
        dcc.Graph(id='bubble-chart')
    ]
    )
])

@app.callback(
    Output('bubble-chart', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('region-filter', 'value'),
    Input('top-filter', 'value')
)

def update_graph(start_date,end_date,region, top):
    #1 获取process数据
    dff = data_cache()
    #1-1筛选日期
    dff = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]
    
    dff = dff[dff['地区'] == '河北']
    #2 计算指标
    filtered_data = data_calculate(df=dff)
    # filtered_data.to_excel('data/数据.xlsx',index=False)
    #2-2筛选地区
    
    #2-3筛选TOP
    filtered_data = dff.groupby(['日期']).head(15)
    #2-4转百分比
    filtered_data['转人工率%'] = filtered_data['转人工率'].apply(lambda x: "{:.2%}".format(x))
    filtered_data['满意度%'] = filtered_data['转人工率'].apply(lambda x: "{:.2%}".format(x))

    #2-4计算转人工、满意度均值
    mean_r = dff['转人工率'].mean()
    dff =  dff[dff['满意度'] != None] #删除分母都是空的行
    dff.dropna(subset=['满意度'], inplace=True)

    # mean_m = dff['满意度'].mean()

    #3 加载气泡图
    bubble_fig = px.scatter(
        filtered_data,
        x='满意度',
        y='转人工率',
        size='末业务意图总通话量',
        color='意图名称',
        animation_frame='日期', #动画字段
        hover_name='意图名称',
        size_max=70,
        labels={
            '满意度': '满意度',
            '转人工率': '转人工率'
        },
        range_x=[0, filtered_data['满意度'].max() if filtered_data['满意度'].max() > 0 else 1],
        range_y=[0, filtered_data['转人工率'].max() if filtered_data['转人工率'].max() > 0 else 1]
    )

    return bubble_fig


if __name__ == '__main__':
    app.run_server(host='172.20.10.5',debug=True)
    # dff = data_cache()
    # filtered_data = data_calculate(df=dff)
    # filtered_data.to_excel('data/数据.xlsx',index=False)