# -*- coding: utf-8 -*-
"""
💎 Personal Wealth Command Center - 專屬資金管理與資產配置系統
=============================================================
功能：
1. 每月現金流管理 (薪金、支出、月供)
2. 資產分佈可視化 (VOO + Short Put 本金)
3. 財富自由軌跡推算 (動態結合未來的加薪計畫)

Author: Pro Trader AI (Powered by Gemini)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ============================================
# ⚙️ 頁面設定 & Session State 初始化
# ============================================
st.set_page_config(page_title="Wealth Command Center", page_icon="💎", layout="wide")

# 初始化你的財務數據 (可隨時在網頁上修改)
if 'finances' not in st.session_state:
    st.session_state.finances = {
        'salary': 56000,          # 目前月薪
        'expenses': 36000,        # 生活支出 (自動推算: 56k - 20k)
        'voo_monthly': 20000,     # VOO 月供
        'put_capital': 410000,    # Short Put 初始本金
        'voo_holdings': 0,        # 目前 VOO 累積市值
        'put_profits': 0          # Short Put 累積利潤
    }

def update_finances(key, value):
    st.session_state.finances[key] = value

# ============================================
# 📱 主介面 UI
# ============================================
st.title("💎 個人財富指揮中心 (Wealth Command Center)")
st.caption("現金流管控 | 資產配置 | 財富軌跡推算")
st.divider()

# 建立四大分頁
tabs = st.tabs(["📊 總資產看板 (Dashboard)", "💵 現金流與分配 (Cash Flow)", "🚀 8年財富推算引擎 (Projection)"])

# 獲取當前數據
f = st.session_state.finances
total_assets = f['put_capital'] + f['put_profits'] + f['voo_holdings']
free_cash_flow = f['salary'] - f['expenses'] - f['voo_monthly']

# ============================================
# 📊 TAB 1: 總資產看板
# ============================================
with tabs[0]:
    st.header("📊 目前資產狀態")
    
    # 頂部核心指標
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 總資產 (Total Net Worth)", f"HK$ {total_assets:,.0f}")
    col2.metric("🛡️ VOO 核心部位", f"HK$ {f['voo_holdings']:,.0f}")
    col3.metric("💸 Short Put 資本", f"HK$ {f['put_capital'] + f['put_profits']:,.0f}")
    col4.metric("🔄 每月閒置現金", f"HK$ {free_cash_flow:,.0f}", 
                help="如果為正數，代表你有額外資金可獎勵自己或加碼投資；如果為負數，代表支出/月供過高。")
    
    st.divider()
    
    # 資產配置圓餅圖
    st.subheader("🥧 資產配置比例 (Asset Allocation)")
    if total_assets > 0:
        labels = ['VOO 核心部位', 'Short Put 本金', 'Short Put 已實現利潤']
        values = [f['voo_holdings'], f['put_capital'], f['put_profits']]
        
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, 
                                     marker_colors=['#00CC96', '#636EFA', '#EF553B'])])
        fig.update_layout(template='plotly_dark', margin=dict(t=30, b=30, l=0, r=0))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("請前往「現金流與分配」輸入你的初始資產。")

# ============================================
# 💵 TAB 2: 現金流與分配管理
# ============================================
with tabs[1]:
    st.header("💵 每月現金流管理")
    st.markdown("在這裡調整你的收入、支出與月供計畫。當你加人工時，請來這裡更新！")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 收入與支出 (Income & Expenses)")
        new_salary = st.number_input("每月薪金 (Salary)", value=f['salary'], step=1000)
        new_expenses = st.number_input("每月基本支出 (Expenses)", value=f['expenses'], step=1000)
        
        st.subheader("📈 投資分配 (Investments)")
        new_voo = st.number_input("每月供 VOO 金額", value=f['voo_monthly'], step=1000)
        
        if st.button("💾 更新現金流數據", type="primary"):
            update_finances('salary', new_salary)
            update_finances('expenses', new_expenses)
            update_finances('voo_monthly', new_voo)
            st.success("現金流數據已更新！")
            st.rerun()
            
    with col2:
        st.subheader("💼 資產部位更新 (Portfolio Update)")
        st.info("每月月底，請將券商戶口的最新數字填入此處，追蹤財富增長。")
        new_voo_holdings = st.number_input("VOO 目前總市值 (HK$)", value=f['voo_holdings'], step=5000)
        new_put_profits = st.number_input("Short Put 累積已賺取權利金 (HK$)", value=f['put_profits'], step=1000)
        
        if st.button("💾 更新資產市值", type="secondary"):
            update_finances('voo_holdings', new_voo_holdings)
            update_finances('put_profits', new_put_profits)
            st.success("資產市值已更新！")
            st.rerun()

# ============================================
# 🚀 TAB 3: 8年財富推算引擎
# ============================================
with tabs[2]:
    st.header("🚀 財富軌跡推算 (Road to 6 Million)")
    st.markdown("這套引擎已經內建了你 **2026 至 2029 的加薪藍圖**。你可以調整預期回報率，看看 8 年後的終局。")
    
    col_rate1, col_rate2 = st.columns(2)
    voo_rate = col_rate1.slider("VOO 預期年化回報率 (%)", min_value=4.0, max_value=15.0, value=10.0, step=0.5)
    put_rate = col_rate2.slider("Short Put 預期年化回報率 (%)", min_value=5.0, max_value=20.0, value=12.0, step=0.5)
    
    # 建立時間線與加薪邏輯
    months = 96 # 8 年
    
    # 初始化數據列表
    timeline = []
    current_voo = f['voo_holdings']
    current_put_cap = f['put_capital'] + f['put_profits']
    
    # 定義加薪與月供增加邏輯 (50/50 規則)
    for m in range(1, months + 1):
        # 判斷當前是哪一個階段 (假設目前是 2026年初)
        if m <= 4:            # 2026.02 - 2026.05
            monthly_voo_inv = 20000
        elif m <= 16:         # 2026.06 - 2027.05 (人工 62k)
            monthly_voo_inv = 23000
        elif m <= 28:         # 2027.06 - 2028.05 (人工 65k)
            monthly_voo_inv = 24500
        elif m <= 40:         # 2028.06 - 2029.05 (人工 68k)
            monthly_voo_inv = 26000
        else:                 # 2029.06 以後 (人工爆發至 105k)
            monthly_voo_inv = 44500
            
        # 計算複利 (按月)
        # VOO: 上月結餘 * 月回報 + 本月供款
        current_voo = current_voo * (1 + (voo_rate / 100 / 12)) + monthly_voo_inv
        
        # Short Put: 上月結餘 * 月回報
        current_put_cap = current_put_cap * (1 + (put_rate / 100 / 12))
        
        timeline.append({
            'Month': m,
            'Year': 2026 + (m // 12),
            'VOO_Value': current_voo,
            'Put_Value': current_put_cap,
            'Total_Net_Worth': current_voo + current_put_cap,
            'Monthly_Investment': monthly_voo_inv
        })
        
    df_proj = pd.DataFrame(timeline)
    
    # 顯示終局數據
    final_worth = df_proj['Total_Net_Worth'].iloc[-1]
    st.success(f"🎯 **根據此模型，8 年後 (第 96 個月) 你的總資產預計將達到：HK$ {final_worth:,.0f}**")
    
    # 繪製推算圖表
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_proj['Month'], y=df_proj['Total_Net_Worth'], 
                              mode='lines', name='總資產', line=dict(color='cyan', width=3)))
    fig2.add_trace(go.Scatter(x=df_proj['Month'], y=df_proj['VOO_Value'], 
                              mode='lines', name='VOO 累積市值', line=dict(color='#00CC96', width=2)))
    fig2.add_trace(go.Scatter(x=df_proj['Month'], y=df_proj['Put_Value'], 
                              mode='lines', name='Short Put 累積市值', line=dict(color='#636EFA', width=2)))
    
    # 標註重要里程碑 (2029加薪)
    fig2.add_vline(x=40, line_dash="dash", line_color="yellow", 
                   annotation_text="🚀 2029 人工跳升 105k", annotation_position="top left")
    
    fig2.update_layout(template='plotly_dark', title="8 年財富增長雪球圖",
                       xaxis_title="時間 (月)", yaxis_title="港幣 (HK$)", hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)

    # 顯示每年的階段性目標
    st.subheader("📅 年度里程碑 (Yearly Milestones)")
    yearly_df = df_proj[df_proj['Month'] % 12 == 0].copy()
    yearly_df['Year'] = [f"第 {i+1} 年" for i in range(len(yearly_df))]
    
    # 格式化顯示
    display_df = yearly_df[['Year', 'Monthly_Investment', 'VOO_Value', 'Put_Value', 'Total_Net_Worth']].copy()
    for col in ['VOO_Value', 'Put_Value', 'Total_Net_Worth']:
        display_df[col] = display_df[col].apply(lambda x: f"HK$ {x:,.0f}")
    display_df['Monthly_Investment'] = display_df['Monthly_Investment'].apply(lambda x: f"HK$ {x:,.0f}")
    
    display_df.columns = ['年份', '該年月供金額', 'VOO 預估市值', 'Short Put 預估市值', '總資產']
    st.dataframe(display_df, hide_index=True, use_container_width=True)
