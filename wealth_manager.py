# -*- coding: utf-8 -*-
"""
💎 Personal Wealth Command Center - v2.1 Budget Edition
=============================================================
新增功能：
1. 🎯 每月消費預算 (Monthly Budget) 設定
2. 🚥 視覺化預算消耗進度條與超支警告
3. 💸 剩餘可花費 Quota 實時計算

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
        'monthly_budget': 16000,  # 🎯 新增：每月消費預算目標
        'bank_cash': 0,           # 銀行活期存款
        'put_capital': 410000,    # Short Put 初始本金
        'put_profits': 0,         # Short Put 已實現利潤
        'voo_holdings': 0         # 目前 VOO 累積市值
    }

# 2. 初始化逐筆記帳的 DataFrame
if 'expense_df' not in st.session_state:
    st.session_state.expense_df = pd.DataFrame(columns=['日期', '類別', '項目', '金額'])

def update_finances(key, value):
    st.session_state.finances[key] = value

# ============================================
# 📱 主介面 UI & 側邊欄
# ============================================
st.sidebar.title("💎 Wealth Manager")
st.sidebar.caption("v2.1 | 預算控制版")
st.sidebar.divider()

# 計算動態總支出
current_expense_df = st.session_state.expense_df
total_expenses = current_expense_df['金額'].sum() if not current_expense_df.empty else 0

f = st.session_state.finances
total_assets = f['bank_cash'] + f['put_capital'] + f['put_profits'] + f['voo_holdings']

# 計算預算相關數據
budget = f['monthly_budget']
remaining_budget = budget - total_expenses
budget_used_pct = min(total_expenses / budget, 1.0) if budget > 0 else 1.0

# 側邊欄顯示本月財務快照
st.sidebar.markdown("### 🏦 本月財務快照")
st.sidebar.metric("本月總收入", f"HK$ {f['salary']:,.0f}")
st.sidebar.metric("預定月供投資", f"HK$ {f['voo_monthly']:,.0f}")
st.sidebar.divider()

# 🎯 側邊欄預算監控 (視覺化)
st.sidebar.markdown("### 🎯 本月消費預算監控")
st.sidebar.metric("設定總預算", f"HK$ {budget:,.0f}")

# 預算進度條顏色邏輯
if budget_used_pct < 0.8:
    st.sidebar.success(f"已花費: HK$ {total_expenses:,.0f} ({budget_used_pct*100:.0f}%)")
    st.sidebar.progress(budget_used_pct)
    st.sidebar.metric("剩餘可花費 (Quota)", f"HK$ {remaining_budget:,.0f}", delta="狀態健康", delta_color="normal")
elif budget_used_pct < 1.0:
    st.sidebar.warning(f"已花費: HK$ {total_expenses:,.0f} ({budget_used_pct*100:.0f}%)")
    st.sidebar.progress(budget_used_pct)
    st.sidebar.metric("剩餘可花費 (Quota)", f"HK$ {remaining_budget:,.0f}", delta="即將超支", delta_color="off")
else:
    st.sidebar.error(f"已花費: HK$ {total_expenses:,.0f} (100% 爆表!)")
    st.sidebar.progress(1.0)
    st.sidebar.metric("剩餘可花費 (Quota)", f"HK$ {remaining_budget:,.0f}", delta="已經超支", delta_color="inverse")

# 總結每月真實閒置資金 (收入 - 月供 - 實際支出)
real_free_cash = f['salary'] - f['voo_monthly'] - total_expenses
st.sidebar.divider()
st.sidebar.markdown("### 💵 月底結算預估")
st.sidebar.metric("預估可存入銀行現金", f"HK$ {real_free_cash:,.0f}", 
                  help="這是你扣除月供和目前支出後，真正能存下來的錢。")

# ============================================
# 🖥️ 主畫面
# ============================================
st.title("💎 個人財富指揮中心 (Wealth Command Center)")

tabs = st.tabs(["🧾 每月記帳與預算 (Budget Tracker)", "📊 總資產管理 (Asset Manager)", "🚀 8年財富推算 (Projection)"])

# ============================================
# 🧾 TAB 1: 每月記帳與預算 (設定為預設首頁)
# ============================================
with tabs[0]:
    st.header("🧾 每月收支與預算控制")
    
    col_inc, col_exp = st.columns([1, 3])
    
    with col_inc:
        st.subheader("📥 資金流設定")
        st.info("設定你的收入、預定投資，並給自己一個『本月花費上限』。")
        new_salary = st.number_input("本月總薪金 (Income)", value=int(f['salary']), step=1000)
        new_voo_monthly = st.number_input("本月預定月供 (VOO)", value=int(f['voo_monthly']), step=1000)
        
        # 🎯 新增預算輸入框
        st.markdown("---")
        st.markdown("### 🎯 設定消費目標")
        new_budget = st.number_input("本月消費預算上限 (Budget)", value=int(f['monthly_budget']), step=500, 
                                     help="給自己設定一個挑戰，看看能不能把花費控制在這個數字以內！")
        
        if st.button("更新資金設定", type="primary"):
            update_finances('salary', new_salary)
            update_finances('voo_monthly', new_voo_monthly)
            update_finances('monthly_budget', new_budget)
            st.rerun()
    
    with col_exp:
        st.subheader("🛒 逐筆支出紀錄 (Expense Editor)")
        
        # 預算狀態橫幅提示
        if remaining_budget > 0:
            st.success(f"**本月預算還剩 HK$ {remaining_budget:,.0f}，繼續保持！**")
        else:
            st.error(f"**警告！本月已超支 HK$ {abs(remaining_budget):,.0f}！請控制消費！**")
        
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
            num_rows="dynamic",
            use_container_width=True,
            key="expense_editor"
        )
        
        # 將使用者編輯後的表格存回 Session State
        st.session_state.expense_df = edited_df
        
        # 重新計算最新總支出並繪製圖表
        updated_total_expense = edited_df['金額'].sum() if not edited_df.empty else 0
        
        if updated_total_expense > 0:
            st.markdown(f"### 📊 支出結構分析")
            category_group = edited_df.groupby('類別')['金額'].sum().reset_index()
            fig_exp = px.pie(category_group, values='金額', names='類別', hole=0.5, 
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_exp.update_layout(template='plotly_dark', margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig_exp, use_container_width=True)

# ============================================
# 📊 TAB 2: 總資產管理 (Asset Manager)
# ============================================
with tabs[1]:
    st.header("📊 資產配置與編輯")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("💰 目前總資產 (Net Worth)")
        st.markdown(f"<h1 style='color: #00CC96;'>HK$ {total_assets:,.0f}</h1>", unsafe_allow_html=True)
        
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
            
            if st.form_submit_button("💾 儲存並更新總資產"):
                update_finances('bank_cash', new_bank)
                update_finances('put_capital', new_put_cap)
                update_finances('put_profits', new_put_prof)
                update_finances('voo_holdings', new_voo)
                st.rerun()

# ============================================
# 🚀 TAB 3: 8年財富推算 (Projection)
# ============================================
with tabs[2]:
    st.header("🚀 財富軌跡推算 (Road to 6 Million)")
    st.markdown("內建 **2026 至 2029 的加薪藍圖**。調整預期回報率，看看 8 年後的終局。")
    
    col_rate1, col_rate2 = st.columns(2)
    voo_rate = col_rate1.slider("VOO 預期年化回報率 (%)", min_value=4.0, max_value=15.0, value=10.0, step=0.5)
    put_rate = col_rate2.slider("Short Put 預期年化回報率 (%)", min_value=5.0, max_value=20.0, value=12.0, step=0.5)
    
    months = 96
    timeline = []
    
    current_voo = f['voo_holdings']
    current_put_cap = f['put_capital'] + f['put_profits']
    
    for m in range(1, months + 1):
        if m <= 4:            monthly_voo_inv = 20000
        elif m <= 16:         monthly_voo_inv = 23000
        elif m <= 28:         monthly_voo_inv = 24500
        elif m <= 40:         monthly_voo_inv = 26000
        else:                 monthly_voo_inv = 44500
            
        current_voo = current_voo * (1 + (voo_rate / 100 / 12)) + monthly_voo_inv
        current_put_cap = current_put_cap * (1 + (put_rate / 100 / 12))
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
