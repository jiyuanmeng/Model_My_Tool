import os, sys
sys.path.append(os.getcwd()) #添加进环境变量，实现跨文件调用
import pandas as pd
# from . import 集团满意度测评
# from . import 王涛手动数据
from . import table_define
from . import OSS
from . import BSS
from . import OSW
from . import 客服数据

def load_all():
    # BSS.dwa_m_cust_percep_predic_mon_text.load()

    #集团满意度测评.固定上网.load()
    #集团满意度测评.移动业务.load()
    #集团满意度测评.固定语音.load()
    #王涛手动数据.光猫不匹配用户清单.load()
    #王涛手动数据.下挂路由不匹配用户清单.load()
    #王涛手动数据.移网网络质量调查.load()
    #王涛手动数据.质量工单.load()
    # OSS.ods_m_speedtest_pass.load()
    # OSS.ods_m_speedtest_nopass.load()
    # OSS.ods_d_speedtest_actual_bandwidth.load()
    # OSS.ods_d_ipnet_banms_pm_onuport.load()
    # BSS.lht_temp_zp_cb_0524_05a.load()
    # BSS.lht_temp_zp_cb_0630_05a.load()
    # OSS.ods_d_ipnet_banms_pm_oltport.load()
    #OSS.ods_d_gk_report_zy_widetable.load()
    # OSS.ods_d_dop_fluxpool_info.load()
    # BSS.ods_m_sa_t7_access_flow.load()
    #BSS.ods_d_seq_mb_user_app.load()
    
    #客服数据.dwd_d_evt_kf_high_quality_report.load()
    #客服数据.dwd_d_evt_kf_high_quality_det.load()
    #客服数据.dwd_d_evt_kf_gd_case_main.load()
    #客服数据.dwd_d_evt_kf_gd_process.load()
    #客服数据.dwd_d_evt_kf_gd_reply.load()
    #客服数据.dwd_d_evt_kf_jc_svc_request.load()
    客服数据.dwd_d_evt_kf_voice_to_text.load()
    #客服数据.dwd_d_evt_kf_jc_manual_seat.load()
    #客服数据.dwd_d_evt_kf_jc_net_cus_msg.load()   
    #客服数据.dwd_d_evt_kf_call_out_detail.load()

    #客服数据.dwd_d_evt_kf_high_quality_report_2.load()
    #客服数据.dwd_d_evt_kf_jc_manual_seat_2.load()
    #客服数据.dwd_d_evt_kf_jc_svc_request_2.load()
    
    # OSW.ods_d_noap_move_net_4g.load()
    # OSW.ods_d_noap_move_net_5g.load()
    # OSW.ods_m_noap_warn.load()
    # OSW.ads_pub_wlsjs_6_npscomplaint_call_w_inc.load()
    # OSW.ads_pub_wlsjs_6_user_npscomplaint_w_inc.load()
    #OSW.ods_d_noap_move_net_4g_2.load()
    #OSW.ods_d_noap_move_net_5g_2.load()
    #OSW.ods_d_noap_move_net_4g_test.load()
    
    # OSW.dws_user_serviceaware_cell_app_exp_d_inc.load()
    
    # OSW.ads_pub_wlsjs_57_hprov_up_user_top_cell_d_inc.load()
    # OSW.ads_pub_wlsjs_14_45g_experience_d_inc.load()
    #OSW.ods_d_noap_move_net_4g.load()
    # BSS.dwa_m_cust_percep_predic_mon.load()

