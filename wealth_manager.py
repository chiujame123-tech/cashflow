# -*- coding: utf-8 -*-
"""
💎 Personal Wealth Command Center - v2.4 Smooth UX Edition
=============================================================
修復與優化：
1. 🛠️ 修復表格無法編輯的問題 (移除干擾的 rerun，重構渲染順序)
2. ⚡ 快捷記帳升級：選擇項目後，可自由修改金額再新增
3. 💾 保持完美的 JSON 本地自動存檔

Author: Pro Trader AI (Powered by Gemini)
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# ============================================
# 💾 資料庫存取系統 (JSON Local Storage)
# ============================================
DATA_FILE = "wealth_data.json"

def save_data():
    """無感實時存檔"""
    exp_df = st.session_state.expense_df.copy()
    if not exp_df.empty:
        exp_df['日期'] = pd.to_datetime(exp_df['日期']).dt.strftime('%Y-%m-%d')
    
    data_to_save = {
        'finances': st.session_state.finances,
        'expenses': exp_df.to_dict('records')
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('finances', {}), data.get('expenses', [])
        except Exception:
            pass
    return None, None

# ============================================
# ⚙️ 頁面設定 & Session State 初始化
# ============================================
st.set_page_config(page_title="Wealth Command Center", page_icon="💎", layout="wide")

saved_finances, saved_expenses = load_data()

if 'finances' not in st.session_state:
    if saved_finances:
        st.session_state.finances = saved_finances
    else:
        st.session_state.finances = {
            'salary': 56000,          
            'voo_monthly': 20000,     
            'monthly_budget': 16000,  
            'bank_cash': 0,           
            'put_capital': 410000,    
            'put_profits': 0,         
            'voo_holdings': 0         
        }

if 'expense_df' not in st.session_state:
    if saved_expenses:
        df = pd.DataFrame(saved_expenses)
        df['日期'] = pd.to_datetime(df['日期']).dt.date
        st.session_state.expense_df = df
    else:
        st.session_state.expense_df = pd.DataFrame(columns=['日期', '類別', '項目', '金額'])

# --- Callback 函數 ---
def update_salary(): st.session_state.finances['salary'] = st.session_state.in_salary; save_data()
def update_voo_monthly(): st.session_state.finances['voo_monthly'] = st.session_state.in_voo; save_data()
def update_budget(): st.session_state.finances['monthly_budget'] = st.session_state.in_budget; save_data()
def update_bank(): st.session_state.finances['bank_cash'] = st.session_state.in_bank; save_data()
def update_put_cap(): st.session_state.finances['put_capital'] = st.session_state.in_put_cap; save_data()
def update_put_prof(): st.session_state.finances['put_profits'] = st.session_state.in_put_prof; save_data()
def update_voo_hold(): st.session_state.finances['voo_holdings'] = st.session_state.in_voo_hold; save_data()

# 常用開銷字典
COMMON_EXPENSES = {
    "☕ 買咖啡 (預設 $35)": {"類別": "飲食 🍔", "項目": "買咖啡", "金額": 35.0},
    "🍱 食晏/Lunch (預設 $60)": {"類別": "飲食 🍔", "項目": "Lunch", "金額": 60.0},
    "🥩 食晚飯/Dinner (預設 $150)": {"類別": "飲食 🍔", "項目": "Dinner", "金額": 150.0},
    "🚇 搭車/MTR (預設 $15)": {"類別": "交通 🚇", "項目": "搭車", "金額": 15.0},
    "🚕 搭的士 (預設 $80)": {"類別": "交通 🚇", "項目": "搭的士", "金額": 80.0},
    "🛒 超市買餸 (預設 $200)": {"類別": "購物 🛍️", "項目": "超市買餸", "金額": 200.0}
}

# ============================================
# 🖥️ 主畫面 Tabs 渲染
# ============================================
st.title("💎 個人財富指揮中心 (Wealth Command Center)")

f = st.session_state.finances
tabs = st.tabs(["🧾 每月記帳與預算", "📊 總資產管理", "🚀 8年財富推算"])

# ----------------- TAB 1: 記帳 -----------------
with tabs[0]:
    st.header("🧾 每月收支與預算控制")
    col_inc, col_exp = st.columns([1, 3])
    
    with col_inc:
        st.subheader("📥 資金流設定")
        st.number_input("本月總薪金 (Income)", value=int(f['salary']), step=1000, key="in_salary", on_change=update_salary)
        st.number_input("本月預定月供 (VOO)", value=int(f['voo_monthly']), step=1000, key="in_voo", on_change=update_voo_monthly)
        st.markdown("---")
        st.markdown("### 🎯 設定消費目標")
        st.number_input("本月消費預算上限", value=int(f['monthly_budget']), step=500, key="in_budget", on_change=update_budget)
    
    with col_exp:
        # ✅ 修復 2: 快捷記帳加入「可修改金額」欄位
        st.markdown("### ⚡ 快捷記帳 (Quick Add)")
        c_q1, c_q2, c_q3 = st.columns([2, 1, 1])
        with c_q1:
            quick_selection = st.selectbox("選擇預設項目", list(COMMON_EXPENSES.keys()))
        with c_q2:
            default_amt = float(COMMON_EXPENSES[quick_selection]["金額"])
            # 讓用戶可以在按下新增前，自由修改金額
            quick_amt = st.number_input("修改金額 (HK$)", value=default_amt, step=10.0)
        with c_q3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ 寫入表格", type="primary", use_container_width=True):
                new_row = pd.DataFrame([{
                    "日期": datetime.today().date(), 
                    "類別": COMMON_EXPENSES[quick_selection]["類別"], 
                    "項目": COMMON_EXPENSES[quick_selection]["項目"], 
                    "金額": float(quick_amt)
                }])
                st.session_state.expense_df = pd.concat([new_row, st.session_state.expense_df], ignore_index=True)
                save_data()
                st.rerun()

        st.divider()
        st.markdown("### 🛒 逐筆支出紀錄 (直接點擊表格編輯)")
        
        # 顯示預算警告
        current_total = st.session_state.expense_df['金額'].sum() if not st.session_state.expense_df.empty else 0
        rem_budget = f['monthly_budget'] - current_total
        if rem_budget >= 0:
            st.success(f"**本月預算還剩 HK$ {rem_budget:,.0f}，繼續保持！**")
        else:
            st.error(f"**警告！本月已超支 HK$ {abs(rem_budget):,.0f}！**")
        
        # ✅ 修復 1: 互動式表格 (移除了干擾編輯的 rerun)
        edited_df = st.data_editor(
            st.session_state.expense_df,
            column_config={
                "日期": st.column_config.DateColumn("日期", default=datetime.today()),
                "類別": st.column_config.SelectboxColumn("消費類別", options=["飲食 🍔", "交通 🚇", "居住/帳單 🏠", "娛樂/社交 🎮", "購物 🛍️", "其他 ❓"], required=True),
                "項目": st.column_config.TextColumn("項目描述", required=True),
                "金額": st.column_config.NumberColumn("金額 (HK$)", min_value=0.0, format="$%d", required=True)
            },
            num_rows="dynamic",
            use_container_width=True,
            key="expense_editor"
        )
        
        # 只有當數據真的發生變化時，才在背景存檔 (不觸發 rerun，保護鼠標焦點)
        if not edited_df.equals(st.session_state.expense_df):
            st.session_state.expense_df = edited_df
            save_data()
            
        # 即時繪製圓餅圖 (使用最新的 edited_df)
        updated_total = edited_df['金額'].sum() if not edited_df.empty else 0
        if updated_total > 0:
            st.markdown(f"### 📊 支出結構分析 (總花費: HK$ {updated_total:,.0f})")
            cat_group = edited_df.groupby('類別')['金額'].sum().reset_index()
            fig_exp = px.pie(cat_group, values='金額', names='類別', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
            fig_exp.update_layout(template='plotly_dark', margin=dict(t=0, b=0, l=0, r=0), height=300)
            st.plotly_chart(fig_exp, use_container_width=True)

# ----------------- TAB 2: 總資產 -----------------
with tabs[1]:
    st.header("📊 資產配置與編輯")
    col1, col2 = st.columns([2, 1])
    
    total_assets = f['bank_cash'] + f['put_capital'] + f['put_profits'] + f['voo_holdings']
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
        st.info("💡 直接更改數字，按 Enter 即自動存檔。請勿輸入逗號。")
        st.number_input("🏦 銀行活期存款 (HK$)", value=int(f['bank_cash']), step=5000, key="in_bank", on_change=update_bank)
        st.number_input("💸 Short Put 資本 (HK$)", value=int(f['put_capital']), step=10000, key="in_put_cap", on_change=update_put_cap)
        st.number_input("📈 Short Put 累積利潤 (HK$)", value=int(f['put_profits']), step=1000, key="in_put_prof", on_change=update_put_prof)
        st.number_input("🛡️ VOO 累積總市值 (HK$)", value=int(f['voo_holdings']), step=5000, key="in_voo_hold", on_change=update_voo_hold)

# ----------------- TAB 3: 8年推算 -----------------
with tabs[2]:
    st.header("🚀 財富軌跡推算 (Road to 6 Million)")
    col_rate1, col_rate2 = st.columns(2)
    voo_rate = col_rate1.slider("VOO 預期年化回報率 (%)", min_value=4.0, max_value=15.0, value=10.0, step=0.5)
    put_rate = col_rate2.slider("Short Put 預期年化回報率 (%)", min_value=5.0, max_value=20.0, value=12.0, step=0.5)
    
    timeline = []
    current_voo = f['voo_holdings']
    current_put_cap = f['put_capital'] + f['put_profits']
    
    for m in range(1, 97):
        if m <= 4: monthly_voo_inv = 20000
        elif m <= 16: monthly_voo_inv = 23000
        elif m <= 28: monthly_voo_inv = 24500
        elif m <= 40: monthly_voo_inv = 26000
        else: monthly_voo_inv = 44500
            
        current_voo = current_voo * (1 + (voo_rate / 100 / 12)) + monthly_voo_inv
        current_put_cap = current_put_cap * (1 + (put_rate / 100 / 12))
        proj_net_worth = current_voo + current_put_cap + f['bank_cash']
        
        timeline.append({'Month': m, 'Year': 2026 + (m // 12), 'VOO_Value': current_voo, 'Put_Value': current_put_cap, 'Total_Net_Worth': proj_net_worth, 'Monthly_Investment': monthly_voo_inv})
        
    df_proj = pd.DataFrame(timeline)
    st.success(f"🎯 **根據此模型，8 年後 (第 96 個月) 你的總資產預計將達到：HK$ {df_proj['Total_Net_Worth'].iloc[-1]:,.0f}**")
    
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df_proj['Month'], y=df_proj['Total_Net_Worth'], mode='lines', name='總資產', line=dict(color='cyan', width=3)))
    fig2.add_trace(go.Scatter(x=df_proj['Month'], y=df_proj['VOO_Value'], mode='lines', name='VOO 累積市值', line=dict(color='#00CC96', width=2)))
    fig2.add_trace(go.Scatter(x=df_proj['Month'], y=df_proj['Put_Value'], mode='lines', name='Short Put 累積市值', line=dict(color='#636EFA', width=2)))
    fig2.add_vline(x=40, line_dash="dash", line_color="yellow", annotation_text="🚀 2029 加薪", annotation_position="top left")
    fig2.update_layout(template='plotly_dark', title="8 年財富增長雪球圖", xaxis_title="時間 (月)", yaxis_title="港幣 (HK$)", hovermode="x unified")
    st.plotly_chart(fig2, use_container_width=True)

# ============================================
# 📱 側邊欄 (Sidebar) - 放最後渲染以確保讀取最新數據
# ============================================
st.sidebar.title("💎 Wealth Manager")
st.sidebar.caption("v2.4 | 極致流暢版")
st.sidebar.divider()

final_total_exp = st.session_state.expense_df['金額'].sum() if not st.session_state.expense_df.empty else 0
budget = f['monthly_budget']
rem_budget = budget - final_total_exp
used_pct = min(final_total_exp / budget, 1.0) if budget > 0 else 1.0

st.sidebar.markdown("### 🏦 本月財務快照")
st.sidebar.metric("本月總收入", f"HK$ {f['salary']:,.0f}")
st.sidebar.metric("預定月供投資", f"HK$ {f['voo_monthly']:,.0f}")
st.sidebar.divider()

st.sidebar.markdown("### 🎯 預算消耗進度")
st.sidebar.metric("設定總預算", f"HK$ {budget:,.0f}")

if used_pct < 0.8:
    st.sidebar.success(f"已花費: HK$ {final_total_exp:,.0f} ({used_pct*100:.0f}%)")
    st.sidebar.progress(used_pct)
    st.sidebar.metric("剩餘 Quota", f"HK$ {rem_budget:,.0f}", delta="狀態健康", delta_color="normal")
elif used_pct < 1.0:
    st.sidebar.warning(f"已花費: HK$ {final_total_exp:,.0f} ({used_pct*100:.0f}%)")
    st.sidebar.progress(used_pct)
    st.sidebar.metric("剩餘 Quota", f"HK$ {rem_budget:,.0f}", delta="即將超支", delta_color="off")
else:
    st.sidebar.error(f"已花費: HK$ {final_total_exp:,.0f} (爆表!)")
    st.sidebar.progress(1.0)
    st.sidebar.metric("剩餘 Quota", f"HK$ {rem_budget:,.0f}", delta="已經超支", delta_color="inverse")

st.sidebar.divider()
st.sidebar.markdown("### 💵 月底結算預估")
st.sidebar.metric("預估可存入銀行現金", f"HK$ {f['salary'] - f['voo_monthly'] - final_total_exp:,.0f}", help="扣除月供和目前支出後，真正能存下來的錢。")
