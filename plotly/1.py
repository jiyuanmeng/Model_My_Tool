import plotly.graph_objects as go
import numpy as np

# 生成100个随机数作为x轴数据
x = np.random.rand(100)

# 生成100个随机数作为y轴数据
y = np.random.rand(100)

# 创建一个空的散点图
scatter = go.Scatter(
    x=x,
    y=y,
    mode='markers'
)

layout = go.Layout(
    xaxis=dict(range=[0, 1], autorange=False),
    yaxis=dict(range=[0, 1], autorange=False),
    title="动态绘图示例",
    updatemenus=[dict(
        type="buttons",
        buttons=[dict(label="开始",
                      method="animate",
                      args=[None, {"frame": {"duration": 200, "redraw": False},
                                   "fromcurrent": True,
                                   "transition": {"duration": 0}}]),
                 dict(label="停止",
                      method="animate",
                      args=[[None], {"frame": {"duration": 0, "redraw": False},
                                     "mode": "immediate",
                                     "transition": {"duration": 0}}])])]
)

frames = [go.Frame(data=[go.Scatter(
    x=x[:k+1],
    y=y[:k+1])],
    layout=go.Layout(
        xaxis=dict(range=[0, 1], autorange=False),
        yaxis=dict(range=[0, 1], autorange=False)))
    for k in range(1, len(x))]

animation = go.Figure(data=[scatter], frames=frames, layout=layout)

animation.show()
