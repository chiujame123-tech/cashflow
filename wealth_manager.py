# -*- coding: utf-8 -*-
"""
💎 Personal Wealth Command Center - v2.8 Blueprint Edition
=============================================================
優化項目：
1. 🗺️ 於推算引擎 (Tab 3) 完美嵌入「8 年加薪與月供專屬藍圖」。
2. 延續實時存檔、預算控制與雙層連動選單的極致體驗。

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

# ============================================
# ⚡ 結構化分類字典 (兩級選單用)
# ============================================
EXPENSE_CATEGORIES = {
    "飲食 🍔": {
        "☕ 買咖啡 ($35)": {"項目": "買咖啡", "金額": 35.0},
        "🍱 食晏/Lunch ($60)": {"項目": "Lunch", "金額": 60.0},
        "🥩 食晚飯/Dinner ($150)": {"項目": "Dinner", "金額": 150.0},
    },
    "交通 🚇": {
        "🚇 搭車/MTR ($15)": {"項目": "搭車", "金額": 15.0},
        "🚕 搭的士 ($80)": {"項目": "搭的士", "金額": 80.0},
    },
    "居住/帳單 🏠": {
        "📱 電話費/上網費 ($100)": {"項目": "電話/上網費", "金額": 100.0},
        "💳 信用卡卡數 ($1000)": {"項目": "信用卡卡數", "金額": 1000.0},
    },
    "購物 🛍️": {
        "🛒 超市買餸 ($200)": {"項目": "超市買餸", "金額": 200.0},
    },
    "其他 ❓": {
        "❓ 其他支出 ($100)": {"項目": "其他支出", "金額": 100.0}
    }
}

# ============================================
# 📱 側邊欄 (Sidebar)
# ============================================
st.sidebar.title("💎 Wealth Manager")
st.sidebar.caption("v2.8 | 專屬藍圖版")
st.sidebar.divider()

total_expenses = st.session_state.expense_df['金額'].sum() if not st.session_state.expense_df.empty else 0
f = st.session_state.finances
total_assets = f['bank_cash'] + f['put_capital'] + f['put_profits'] + f['voo_holdings']
budget = f['monthly_budget']
remaining_budget = budget - total_expenses
budget_used_pct = min(total_expenses / budget, 1.0) if budget > 0 else 1.0

st.sidebar.markdown("### 🏦 本月財務快照")
st.sidebar.metric("本月總收入", f"HK$ {f['salary']:,.0f}")
st.sidebar.metric("預定月供投資", f"HK$ {f['voo_monthly']:,.0f}")
st.sidebar.divider()

st.sidebar.markdown("### 🎯 本月消費預算")
st.sidebar.metric("設定總預算", f"HK$ {budget:,.0f}")

if budget_used_pct < 0.8:
    st.sidebar.success(f"已花費: HK$ {total_expenses:,.0f} ({budget_used_pct*100:.0f}%)")
    st.sidebar.progress(budget_used_pct)
    st.sidebar.metric("剩餘 Quota", f"HK$ {remaining_budget:,.0f}", delta="狀態健康", delta_color="normal")
elif budget_used_pct < 1.0:
    st.sidebar.warning(f"已花費: HK$ {total_expenses:,.0f} ({budget_used_pct*100:.0f}%)")
    st.sidebar.progress(budget_used_pct)
    st.sidebar.metric("剩餘 Quota", f"HK$ {remaining_budget:,.0f}", delta="即將超支", delta_color="off")
else:
    st.sidebar.error(f"已花費: HK$ {total_expenses:,.0f} (爆表!)")
    st.sidebar.progress(1.0)
    st.sidebar.metric("剩餘 Quota", f"HK$ {remaining_budget:,.0f}", delta="已經超支", delta_color="inverse")

real_free_cash = f['salary'] - f['voo_monthly'] - total_expenses
st.sidebar.divider()
st.sidebar.markdown("### 💵 月底結算預估")
st.sidebar.metric("預估可存入銀行現金", f"HK$ {real_free_cash:,.0f}", help="扣除月供和目前支出後，真正能存下來的錢。")

# ============================================
# 🖥️ 主畫面 Tabs
# ============================================
st.title("💎 個人財富指揮中心 (Wealth Command Center)")

tabs = st.tabs(["🧾 每月記帳與預算", "📊 總資產管理", "🚀 8年財富推算"])

# ----------------- TAB 1: 記帳 -----------------
with tabs[0]:
    st.header("🧾 每月收支與預算控制")
    col_inc, col_exp = st.columns([1, 3])
    
    with col_inc:
        st.subheader("📥 資金流設定")
        st.info("💡 輸入數字後按 Enter 即自動保存。請勿輸入逗號。")
        st.number_input("本月總薪金 (Income)", value=int(f['salary']), step=1000, key="in_salary", on_change=update_salary)
        st.number_input("本月預定月供 (VOO)", value=int(f['voo_monthly']), step=1000, key="in_voo", on_change=update_voo_monthly)
        st.markdown("---")
        st.markdown("### 🎯 設定消費目標")
        st.number_input("本月消費預算上限", value=int(f['monthly_budget']), step=500, key="in_budget", on_change=update_budget)
    
    with col_exp:
        st.markdown("### ⚡ 快捷記帳 (Quick Add)")
        c_q1, c_q2, c_q3, c_q4 = st.columns([1.5, 2, 1.2, 1.5])
        
        with c_q1:
            sel_cat = st.selectbox("1️⃣ 消費分類", list(EXPENSE_CATEGORIES.keys()))
        with c_q2:
            sel_item = st.selectbox("2️⃣ 具體項目", list(EXPENSE_CATEGORIES[sel_cat].keys()))
        with c_q3:
            default_amt = float(EXPENSE_CATEGORIES[sel_cat][sel_item]["金額"])
            quick_amt = st.number_input("3️⃣ 金額 (HK$)", value=default_amt, step=10.0)
        with c_q4:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ 寫入表格", type="primary", use_container_width=True):
                new_row = pd.DataFrame([{
                    "日期": datetime.today().date(), 
                    "類別": sel_cat, 
                    "項目": EXPENSE_CATEGORIES[sel_cat][sel_item]["項目"], 
                    "金額": float(quick_amt)
                }])
                st.session_state.expense_df = pd.concat([new_row, st.session_state.expense_df], ignore_index=True)
                save_data()
                st.rerun()

        st.divider()
        st.markdown("### 🛒 逐筆支出紀錄")
        st.info("💡 **如何手動刪除特定項目？** 點擊表格最左側的「灰色行號」（整行會反白），然後按鍵盤的 `Delete` 或 `Backspace` 鍵。")
        
        col_btn1, col_btn2, _ = st.columns([2, 2, 5])
        with col_btn1:
            if st.button("↩️ 復原最後一筆 (Undo)"):
                if not st.session_state.expense_df.empty:
                    st.session_state.expense_df = st.session_state.expense_df.iloc[1:].reset_index(drop=True)
                    save_data()
                    st.rerun()
        with col_btn2:
            if st.button("🗑️ 清空所有紀錄", type="secondary"):
                st.session_state.expense_df = pd.DataFrame(columns=['日期', '類別', '項目', '金額'])
                save_data()
                st.rerun()
        
        if remaining_budget > 0:
            st.success(f"**本月預算還剩 HK$ {remaining_budget:,.0f}，繼續保持！**")
        else:
            st.error(f"**警告！本月已超支 HK$ {abs(remaining_budget):,.0f}！請控制消費！**")
        
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
        
        if not edited_df.equals(st.session_state.expense_df):
            st.session_state.expense_df = edited_df
            save_data()
            
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
    
    # === 🗺️ 新增的專屬藍圖區塊 ===
    with st.expander("🗺️ 展開查看：你的 8 年加薪與投資專屬藍圖", expanded=True):
        st.markdown("""
        * **階段一 (2026.02 - 2026.05 | 4個月)：** 人工 56k ➡️ 每月供 **20k** (共 8萬)
        * **階段二 (2026.06 - 2027.05 | 12個月)：** 人工 62k ➡️ 每月供 **23k** (共 27.6萬)
        * **階段三 (2027.06 - 2028.05 | 12個月)：** 人工 65k ➡️ 每月供 **24.5k** (共 29.4萬)
        * **階段四 (2028.06 - 2029.05 | 12個月)：** 人工 68k ➡️ 每月供 **26k** (共 31.2萬)
        * 🔥 **階段五 (2029.06 - 2034.02 | 56個月)：** 人工 105k ➡️ 每月供高達 **44.5k** (共 249.2萬)
        
        💰 **8 年累積投入 VOO 總本金：約 HK$ 345.4 萬**
        """)
    # ===============================

    st.markdown("調整下方的預期回報率，看看 8 年後的終局：")
    
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
