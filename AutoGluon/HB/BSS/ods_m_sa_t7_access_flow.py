import pandas as pd
from data.table_define import FileTable

# 宽带测速未达标数据结果明细（月全量）
#root_dir = '/home/big_data1/app/data/BSS'
root_dir = '/home/bigdata2/data/BSS/target_dir07'
# match_pattern = r'HE_M_SA_T7_ACCESS_FLOW_202408.zip'
match_pattern = r'bd78a7d74f524650ae74524e974fb335'
"""建表语句参考
CREATE TABLE "ods_m_sa_t7_access_flow"(
"month_id"varchar(6) DEFAULT NULL COMMENT'账期月'，
"account"varchar(100) DEFAULT NULL COMMENT'宽带账号',
"app_name"varchar(800)DEFAULT NULL COMMENT'应用名称',
"app_times" decimal(18,0)DEFAULT NULL COMMENT '应用使用时长(分钟)',
"total_bytes" decimal(18,0)DEFAULT NULL COMMENT'应用使用流量(MB)',
"new_flows" decimal(18,0)DEFAULT NULL COMMENT'应用使用次数',
"online_days" decimal(18,0)DEFAULT NULL COMMENT '应用使用天数',
"up_avg"decimal(18,2)DEFAULT NULL COMMENT'应用下行平均速率(mbps)',
"down_avg"decimal(18,2)DEFAULT NULL COMMENT'应用上行平均速率(mbps)',
"field1" decimal(18,2)DEFAULT NULL COMMENT'应用平均时延(ms)',
"field2"decimal(18,0)DEFAULT NULL COMMENT'应用质差次数',
"field3"decimal(18,0)DEFAULT NULL COMMENT'应用卡顿次数
)
"""
schema = {
    'table_name': 'ods_m_sa_t7_access_flow',
    'order_key': 'month_id',
    'cols': [
        {
            'name': 'month_id',
            'type': 'str',
            'comment': '账期月'
        },
        {
            'name': 'account',
            'type': 'str',
            'comment': '宽带账号'
        },
        {
            'name': 'app_name',
            'type': 'str',
            'comment': '应用名称'
        },
        {
            'name': 'app_times',
            'type': 'float',
            'comment': '应用使用时长(分钟)'
        },
        {
            'name': 'total_bytes',
            'type': 'float',
            'comment': '应用使用流量(MB)'
        },
        {
            'name': 'new_flows',
            'type': 'float',
            'comment': '应用使用次数'
        },
        {
            'name': 'online_days',
            'type': 'float',
            'comment': '应用使用天数'
        },
        {
            'name': 'up_avg',
            'type': 'float',
            'comment': '应用下行平均速率(mbps)'
        },
        {
            'name': 'down_avg',
            'type': 'float',
            'comment': '应用上行平均速率(mbps)'
        },
        {
            'name': 'field1',
            'type': 'float',
            'comment': '应用平均时延(ms)'
        },
        {
            'name': 'field2',
            'type': 'float',
            'comment': '应用质差次数'
        },
        {
            'name': 'field3',
            'type': 'float',
            'comment': '应用卡顿次数'
        },
        {
            'name': 'unknow',
            'type': 'str',
            'comment': ''
        }

    ]
}


def load():
    tab = FileTable(
        dir_path=root_dir,
        match_pattern=match_pattern,
        #sep='\001', 初表
        sep='\u0005',
        schema=schema,
    )
    tab.dump_to_ck()
