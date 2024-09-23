import pandas as pd
import numpy as np
import plotly
import plotly.graph_objects as go   #存放图的对象的组件
import chart_studio.plotly as py  #在线画图
import plotly.express as px   #离线画图
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from prosess import *
from data import *
import plotly.io as pio

# 创建Dash应用
# app = Dash(__name__)

df_cnt = px.data.gapminder()
# fig = px.scatter(df_cnt,x='gdpPercap',y='lifeExp',color='continent',log_x=True,hover_name='country')
fig = px.scatter(df_cnt,x='gdpPercap',y='lifeExp',
           color='continent',log_x=True,
           hover_name='country',
           animation_frame='year',
           range_x=[100,100000],
           range_y=[25,90],
           size_max=90,
           size='pop'
          )

# 更新 updatemenus 以添加自定义的播放/暂停按钮
fig.update_layout(
    updatemenus=[
        {
            "type": "buttons",
            "buttons": [
                {
                    "args": [None, {"frame": {"duration": 500, "redraw": True},
                                    "fromcurrent": True,
                                    "transition": {"duration": 300}}],
                    "label": "Play",
                    "method": "animate"
                },
                {
                    "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                      "mode": "immediate",
                                      "transition": {"duration": 0}}],
                    "label": "Pause",
                    "method": "animate"
                }
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top"
        }
    ]
)

# 设置初始帧，并将自动播放的配置作为默认
fig.layout.sliders[0]['active'] = 0
fig['layout']['sliders'][0]['steps'][0]['args'][1]['mode'] = 'immediate'


fig.show()

if __name__ == '__main__':
    # app.run_server()
    pass
