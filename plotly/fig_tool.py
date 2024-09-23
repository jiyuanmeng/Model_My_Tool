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
    ]),
    html.Div([
        dcc.Graph(id='bar-chart',className='six columns',style={'width': '50%', 'display': 'inline-block','height':'30%'}),
        dcc.Graph(id='proportion-chart', className='six columns',style={'width': '50%', 'display': 'inline-block','height':'30%'})
    ], 
    # style={'display': 'grid', 'grid-template-columns': '1fr 1fr 1fr'}
    )
])

@app.callback(
    Output('bubble-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Output('proportion-chart', 'figure'),
    Input('date-picker-range', 'start_date'),
    Input('date-picker-range', 'end_date'),
    Input('region-filter', 'value'),
    Input('top-filter', 'value')
)

def update_graph(start_date, end_date, region, top):
    #1 获取process数据
    df = data_cache()
    #1-1筛选日期
    dff = df[(df['日期'] >= start_date) & (df['日期'] <= end_date)]

    #2 计算指标
    dff = data_calculate(df=dff)
    #2-2筛选地区
    dff = dff[dff['地区'] == region]
    #2-3筛选TOP
    filtered_data = dff.head(top)
    #2-4转百分比
    filtered_data['转人工率%'] = filtered_data['转人工率'].apply(lambda x: "{:.2%}".format(x))
    filtered_data['满意度%'] = filtered_data['转人工率'].apply(lambda x: "{:.2%}".format(x))

    #2-4计算转人工、满意度均值
    mean_r = dff['转人工率'].mean()
    # dff =  dff[dff['满意度'] != None] #删除分母都是空的行
    dff.dropna(subset=['满意度'], inplace=True)

    mean_m = dff['满意度'].mean()

    #3 加载气泡图
    bubble_fig = px.scatter(
        filtered_data,
        x='满意度',
        y='转人工率',
        size='末业务意图总通话量',
        color='意图名称',
        hover_name='意图名称',
        size_max=70,
        labels={
            '满意度': '满意度',
            '转人工率': '转人工率'
        },
        range_x=[0, filtered_data['满意度'].max() if filtered_data['满意度'].max() > 0 else 1],
        range_y=[0, filtered_data['转人工率'].max() if filtered_data['转人工率'].max() > 0 else 1]
    )

    #3-1添加场景名称的标注
    for i in range(len(filtered_data)):
        bubble_fig.add_annotation(
            x=filtered_data['满意度'].iloc[i],
            y=filtered_data['转人工率'].iloc[i],
            text=filtered_data['意图名称'].iloc[i],
            showarrow=False,
            font=dict(
                size=12,
                color="#ffffff"
            )
            # bgcolor="#ffffff",
            # opacity=0.7
        )
    #3-2添加辅助线-指标平均数
    bubble_fig.update_layout(
        xaxis_title='满意度',
        yaxis_title='转人工率',
        shapes=[{
            'type': 'line',
            'x0': mean_m,
            'x1': mean_m,
            'y0': -1,
            'y1': 1,
            'line': {'dash': 'dash', 'width': 1,'color':'yellow'}
        }, {
            'type': 'line',
            'x0': -1,
            'x1': 1,
            'y0': mean_r,
            'y1': mean_r,
            'line': {'dash': 'dash', 'width': 1,'color':'yellow'}
        }],
        xaxis=dict(range=[0.35, 1]),#x轴取值范围
        yaxis=dict(range=[-0.5, 1]),
        xaxis_tickformat=".0%", #更改为百分比格式
        yaxis_tickformat=".0%"
    )

    #3-3添加关于满意度平均值的注释
    bubble_fig.add_annotation(
        x=mean_m,
        y=-0.3,
        text=f"满意度平均值: {mean_m:.2f}",
        # text='1',
        showarrow=False,
        font=dict(size=10, color="yellow")
    )
    #3-4添加关于转人工率平均值的注释
    bubble_fig.add_annotation(
        x=0.37,
        y=mean_r,
        text=f"转人工率平均值: {mean_r:.2f}",
        showarrow=False,
        font=dict(size=10, color="yellow"),
        textangle=-90,  # 注释文本旋转90度
    )
    bubble_fig.update_layout(title={'text': '满意度作战地图', 'x': 0.5, 'font': {'weight': 'bold'}})

    #4 构建柱状图
    #4-1定义满意度的区间
    bins = [-np.inf, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, np.inf]
    labels = ['<=55%', '55-60%', '60-65%', '65-70%', '70-75%', '75-80%', '80-85%', '85-90%', '>90%']
    dff['满意度区间']  = pd.cut(dff['满意度'], bins=bins, labels=labels, right=True) #左开右闭 2<x<=3
    df01 = dff[['满意度区间']]
    
    #4-2根据满意度区间进行计数
    count_data = df01['满意度区间'].value_counts().sort_index().reset_index()
    count_data.columns = ['满意度区间', '计数']

    #4-3创建一个横向柱状图
    bar_fig = px.bar(count_data, x='计数', y='满意度区间', orientation='h', title='满意度区间分布(选定日期范围)',height=270)
    
    #4-4根据满意度区间为每个柱形图手动分配颜色
    colors = ['#339999' if x >= '80-85%' and x != '<=55%'  else '#CC6666' for x in count_data['满意度区间']]
    bar_fig.update_traces(marker_color=colors)
    #4-5设置柱标签
    bar_fig = go.Figure(data=[go.Bar(
        x=count_data['计数'],
        y=count_data['满意度区间'],
        orientation='h',
        marker=dict(color=colors),
        text=count_data['计数'],  # 设置文本显示
        textposition='outside'  # 设置计数显示在外侧
    )])
    #4-6设置图表标题居中、加粗
    bar_fig.update_layout(title={'text': '满意度场景分布', 'x': 0.5, 'font': {'weight': 'bold'}},margin=dict(l=60, r=20, t=58, b=70))

    #5 构建占比图
    df02 = dff.groupby(['满意度区间']).agg({'末业务意图总通话量':sum}).reset_index()
    total = df02['末业务意图总通话量'].sum()
    df02['通话量占比'] = df02['末业务意图总通话量'] / total
    # df02['通话量占比%'] = (df02['末业务意图总通话量'] / total * 100).round(2).astype(str) + '%'
    df02['通话量占比%'] = df02['通话量占比'].apply(lambda x: "{:.2%}".format(x))

    #5-1加载柱状图
    sorted_df = df02.sort_values('通话量占比', ascending=False) #排序
    color_scale = px.colors.sequential.Blugrn #颜色蓝色系列
    proportion_fig = px.bar(sorted_df, x='满意度区间', y='通话量占比', color='通话量占比',color_continuous_scale=color_scale, labels={"通话量占比": "通话量占比(%)"}, hover_data={"通话量占比": ":.2%"},text='通话量占比%')
    proportion_fig.update_layout(title={'text': '满意度通话分布', 'x': 0.5, 'font': {'weight': 'bold'}}#标题加粗
                                 ) 

    return bubble_fig,bar_fig,proportion_fig


if __name__ == '__main__':
    # app.run_server(host='172.20.10.5',debug=True)
    df = data_cache()
    #1-1筛选日期
    dff = df[(df['日期'] >= '2024-05-01') & (df['日期'] <= '2024-05-05')]
    #2 计算指标
    dff = data_calculate(df=dff)
    print(dff)
