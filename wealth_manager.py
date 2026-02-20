# -*- coding: utf-8 -*-
"""
💎 Personal Wealth Command Center - v2.0 Pro Edition
=============================================================
功能：
1. 互動式動態記帳系統 (逐筆記錄支出)
2. 資產配置自由編輯與可視化 (現金、VOO、期權)
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

# 1. 初始化資產與現金流設定
if 'finances' not in st.session_state:
    st.session_state.finances = {
        'salary': 56000,          # 目前月薪
        'voo_monthly': 20000,     # 每月預定定投 VOO
        'bank_cash': 0,           # 銀行活期存款 (新增)
        'put_capital': 410000,    # Short Put 初始本金
        'put_profits': 0,         # Short Put 已實現利潤
        'voo_holdings': 0         # 目前 VOO 累積市值
    }

# 2. 初始化逐筆記帳的 DataFrame
if 'expense_df' not in st.session_state:
    # 建立一個空的記帳表，帶有預設欄位
    st.session_state.expense_df = pd.DataFrame(columns=['日期', '類別', '項目', '金額'])

def update_finances(key, value):
    st.session_state.finances[key] = value

# ============================================
# 📱 主介面 UI & 側邊欄
# ============================================
st.sidebar.title("💎 Wealth Manager")
st.sidebar.caption("v2.0 | 個人資產與收支管理")
st.sidebar.divider()

# 計算動態總支出
current_expense_df = st.session_state.expense_df
total_expenses = current_expense_df['金額'].sum() if not current_expense_df.empty else 0

f = st.session_state.finances
total_assets = f['bank_cash'] + f['put_capital'] + f['put_profits'] + f['voo_holdings']
free_cash_flow = f['salary'] - total_expenses - f['voo_monthly']

st.sidebar.markdown("### 🏦 本月財務快照")
st.sidebar.metric("本月總收入", f"HK$ {f['salary']:,.0f}")
st.sidebar.metric("已紀錄支出", f"HK$ {total_expenses:,.0f}", delta=f"-{total_expenses:,.0f}", delta_color="inverse")
st.sidebar.metric("預定月供投資", f"HK$ {f['voo_monthly']:,.0f}")
st.sidebar.divider()
st.sidebar.metric("💵 剩餘閒置現金", f"HK$ {free_cash_flow:,.0f}", 
                  help="正數代表可加碼投資或儲蓄；負數代表本月超支！", 
                  delta="安全" if free_cash_flow >= 0 else "赤字警告", 
                  delta_color="normal" if free_cash_flow >= 0 else "inverse")

st.title("💎 個人財富指揮中心 (Wealth Command Center)")

# 建立四大分頁
tabs = st.tabs(["📊 總資產管理 (Asset Manager)", "🧾 每月記帳與開銷 (Expense Tracker)", "🚀 8年財富推算 (Projection)"])

# ============================================
# 📊 TAB 1: 總資產管理 (Asset Manager)
# ============================================
with tabs[0]:
    st.header("📊 資產配置與編輯")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💰 目前總資產 (Net Worth)")
        st.markdown(f"<h1 style='color: #00CC96;'>HK$ {total_assets:,.0f}</h1>", unsafe_allow_html=True)
        
        # 資產分佈圓餅圖
        if total_assets > 0:
            labels = ['VOO 核心部位', 'Short Put 本金', 'Short Put 已實現利潤', '銀行活期存款']
            values = [f['voo_holdings'], f['put_capital'], f['put_profits'], f['bank_cash']]
            colors = ['#00CC96', '#636EFA', '#EF553B', '#FFA15A']
            
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4, marker_colors=colors)])
            fig.update_layout(template='plotly_dark', margin=dict(t=30, b=30, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
    with col2:
        st.subheader("📝 編輯資產部位")
        st.info("請在此更新你的銀行與券商最新結餘，總資產將自動計算。")
        
        with st.form("asset_update_form"):
            new_bank = st.number_input("🏦 銀行活期存款 (HK$)", value=int(f['bank_cash']), step=5000)
            new_put_cap = st.number_input("💸 Short Put 資本 (HK$)", value=int(f['put_capital']), step=10000)
            new_put_prof = st.number_input("📈 Short Put 累積利潤 (HK$)", value=int(f['put_profits']), step=1000)
            new_voo = st.number_input("🛡️ VOO 累積總市值 (HK$)", value=int(f['voo_holdings']), step=5000)
            
            if st.form_submit_button("💾 儲存並更新總資產", type="primary"):
                update_finances('bank_cash', new_bank)
                update_finances('put_capital', new_put_cap)
                update_finances('put_profits', new_put_prof)
                update_finances('voo_holdings', new_voo)
                st.rerun()

# ============================================
# 🧾 TAB 2: 每月記帳與開銷 (Expense Tracker)
# ============================================
with tabs[1]:
    st.header("🧾 每月收支記帳板")
    
    col_inc, col_exp = st.columns([1, 3])
    
    with col_inc:
        st.subheader("📥 收入與定投設定")
        new_salary = st.number_input("本月總薪金 (Income)", value=int(f['salary']), step=1000)
        new_voo_monthly = st.number_input("本月預定月供 (VOO)", value=int(f['voo_monthly']), step=1000)
        
        if st.button("更新設定"):
            update_finances('salary', new_salary)
            update_finances('voo_monthly', new_voo_monthly)
            st.rerun()
            
        st.divider()
        st.markdown(f"**可用於支出的預算:**\nHK$ {f['salary'] - f['voo_monthly']:,.0f}")
    
    with col_exp:
        st.subheader("🛒 逐筆支出紀錄 (Expense Editor)")
        st.caption("點擊表格即可新增、修改或刪除支出項目。系統會自動儲存與計算。")
        
        # 互動式數據表 (st.data_editor)
        edited_df = st.data_editor(
            st.session_state.expense_df,
            column_config={
                "日期": st.column_config.DateColumn("日期", default=datetime.today()),
                "類別": st.column_config.SelectboxColumn(
                    "消費類別", 
                    options=["飲食 🍔", "交通 🚇", "居住/帳單 🏠", "娛樂/社交 🎮", "購物 🛍️", "其他 ❓"],
                    required=True
                ),
                "項目": st.column_config.TextColumn("項目描述 (例如: 買咖啡)", required=True),
                "金額": st.column_config.NumberColumn("金額 (HK$)", min_value=0.0, format="$%d", required=True)
            },
            num_rows="dynamic", # 允許使用者隨意增加或刪除行數
            use_container_width=True,
            key="expense_editor"
        )
        
        # 將使用者編輯後的表格存回 Session State
        st.session_state.expense_df = edited_df
        
        # 重新計算最新總支出
        updated_total_expense = edited_df['金額'].sum() if not edited_df.empty else 0
        
        if updated_total_expense > 0:
            st.markdown(f"### 📊 本月支出分析 (總計: HK$ {updated_total_expense:,.0f})")
            
            # 將分類進行加總並繪製圓餅圖
            category_group = edited_df.groupby('類別')['金額'].sum().reset_index()
            fig_exp = px.pie(category_group, values='金額', names='類別', hole=0.5, 
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_exp.update_layout(template='plotly_dark', margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig_exp, use_container_width=True)

# ============================================
# 🚀 TAB 3: 8年財富推算 (Projection)
# ============================================
with tabs[2]:
    st.header("🚀 財富軌跡推算 (Road to 6 Million)")
    st.markdown("這套引擎已經內建了你 **2026 至 2029 的加薪藍圖**。調整預期回報率，看看 8 年後的終局。")
    
    col_rate1, col_rate2 = st.columns(2)
    voo_rate = col_rate1.slider("VOO 預期年化回報率 (%)", min_value=4.0, max_value=15.0, value=10.0, step=0.5)
    put_rate = col_rate2.slider("Short Put 預期年化回報率 (%)", min_value=5.0, max_value=20.0, value=12.0, step=0.5)
    
    months = 96 # 8 年
    timeline = []
    
    current_voo = f['voo_holdings']
    # 預設把 41 萬本金和利潤算進去開始滾
    current_put_cap = f['put_capital'] + f['put_profits']
    
    for m in range(1, months + 1):
        if m <= 4:            monthly_voo_inv = 20000
        elif m <= 16:         monthly_voo_inv = 23000
        elif m <= 28:         monthly_voo_inv = 24500
        elif m <= 40:         monthly_voo_inv = 26000
        else:                 monthly_voo_inv = 44500
            
        current_voo = current_voo * (1 + (voo_rate / 100 / 12)) + monthly_voo_inv
        current_put_cap = current_put_cap * (1 + (put_rate / 100 / 12))
        
        # 加上銀行現金 (不計息) 作為總資產的一部分
        proj_net_worth = current_voo + current_put_cap + f['bank_cash']
        
        timeline.append({
            'Month': m,
            'Year': 2026 + (m // 12),
            'VOO_Value': current_voo,
            'Put_Value': current_put_cap,
            'Total_Net_Worth': proj_net_worth,
            'Monthly_Investment': monthly_voo_inv
        })
        
    df_proj = pd.DataFrame(timeline)
    
    final_worth = df_proj['Total_Net_Worth'].iloc[-1]
    st.success(f"🎯 **根據此模型，8 年後 (第 96 個月) 你的總資產預計將達到：HK$ {final_worth:,.0f}**")
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_proj['Month'], y=df_proj['Total_Net_Worth'], mode='lines', name='總資產', line=dict(color='cyan', width=3)))
    fig2.add_trace(go.Scatter(x=df_proj['Month'], y=df_proj['VOO_Value'], mode='lines', name='VOO 累積市值', line=dict(color='#00CC96', width=2)))
    fig2.add_trace(go.Scatter(x=df_proj['Month'], y=df_proj['Put_Value'], mode='lines', name='Short Put 累積市值', line=dict(color='#636EFA', width=2)))
    
    fig2.add_vline(x=40, line_dash="dash", line_color="yellow", annotation_text="🚀 2029 人工跳升 105k", annotation_position="top left")
    
    fig2.update_layout(template='plotly_dark', title="8 年財富增長雪球圖", xaxis_title="時間 (月)", yaxis_title="港幣 (HK$)", hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("📅 年度里程碑 (Yearly Milestones)")
    yearly_df = df_proj[df_proj['Month'] % 12 == 0].copy()
    yearly_df['Year'] = [f"第 {i+1} 年" for i in range(len(yearly_df))]
    
    display_df = yearly_df[['Year', 'Monthly_Investment', 'VOO_Value', 'Put_Value', 'Total_Net_Worth']].copy()
    for col in ['VOO_Value', 'Put_Value', 'Total_Net_Worth']:
        display_df[col] = display_df[col].apply(lambda x: f"HK$ {x:,.0f}")
    display_df['Monthly_Investment'] = display_df['Monthly_Investment'].apply(lambda x: f"HK$ {x:,.0f}")
    
    display_df.columns = ['年份', '該年月供金額', 'VOO 預估市值', 'Short Put 預估市值', '總資產']
    st.dataframe(display_df, hide_index=True, use_container_width=True)
