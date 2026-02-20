# -*- coding: utf-8 -*-
"""
💎 Personal Wealth Command Center - v2.2 Pro Storage Edition
=============================================================
新增與優化功能：
1. 💾 自動存檔機制 (JSON Local Storage)：重整網頁/關閉電腦，資料不再流失！
2. ⚡ 快捷記帳面板 (Quick Add)：內建常用開銷，一鍵自動填入記帳表。
3. 🎯 預算控制與資產管理完美融合。

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
# 💾 資料庫存取系統 (Data Persistence)
# ============================================
DATA_FILE = "wealth_data.json"

def save_data():
    """將目前的狀態存入 JSON 檔案"""
    exp_df = st.session_state.expense_df.copy()
    if not exp_df.empty:
        # 將日期格式轉換為字串以便存入 JSON
        exp_df['日期'] = pd.to_datetime(exp_df['日期']).dt.strftime('%Y-%m-%d')
    
    data_to_save = {
        'finances': st.session_state.finances,
        'expenses': exp_df.to_dict('records')
    }
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)

def load_data():
    """從 JSON 檔案讀取資料"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                finances = data.get('finances', {})
                expenses = data.get('expenses', [])
                
                exp_df = pd.DataFrame(expenses)
                if not exp_df.empty:
                    exp_df['日期'] = pd.to_datetime(exp_df['日期']).dt.date
                else:
                    exp_df = pd.DataFrame(columns=['日期', '類別', '項目', '金額'])
                    
                return finances, exp_df
        except Exception as e:
            st.error(f"讀取存檔失敗: {e}")
            pass
    return None, None

# ============================================
# ⚙️ 頁面設定 & Session State 初始化
# ============================================
st.set_page_config(page_title="Wealth Command Center", page_icon="💎", layout="wide")

# 啟動時自動讀取存檔
saved_finances, saved_expenses = load_data()

if 'finances' not in st.session_state:
    if saved_finances:
        st.session_state.finances = saved_finances
    else:
        # 預設初始值
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
    if saved_expenses is not None:
        st.session_state.expense_df = saved_expenses
    else:
        st.session_state.expense_df = pd.DataFrame(columns=['日期', '類別', '項目', '金額'])

def update_finances(key, value):
    """更新財務數據並立即存檔"""
    st.session_state.finances[key] = value
    save_data()

# 常用開銷字典 (給 Quick Add 使用)
COMMON_EXPENSES = {
    "☕ 買咖啡 ($35)": {"類別": "飲食 🍔", "項目": "買咖啡", "金額": 35.0},
    "🍱 食晏/Lunch ($60)": {"類別": "飲食 🍔", "項目": "Lunch", "金額": 60.0},
    "🥩 食晚飯/Dinner ($150)": {"類別": "飲食 🍔", "項目": "Dinner", "金額": 150.0},
    "🚇 搭車/MTR ($15)": {"類別": "交通 🚇", "項目": "搭車", "金額": 15.0},
    "🚕 的士/的士 ($80)": {"類別": "交通 🚇", "項目": "搭的士", "金額": 80.0},
    "🛒 超市買餸 ($200)": {"類別": "購物 🛍️", "項目": "超市買餸", "金額": 200.0},
    "📱 電話費/月費 ($100)": {"類別": "居住/帳單 🏠", "項目": "電話/上網費", "金額": 100.0}
}

# ============================================
# 📱 側邊欄 (Sidebar)
# ============================================
st.sidebar.title("💎 Wealth Manager")
st.sidebar.caption("v2.2 | 自動存檔 & 預算控制版")
st.sidebar.divider()

# 計算動態總支出
current_expense_df = st.session_state.expense_df
total_expenses = current_expense_df['金額'].sum() if not current_expense_df.empty else 0

f = st.session_state.finances
total_assets = f['bank_cash'] + f['put_capital'] + f['put_profits'] + f['voo_holdings']
budget = f['monthly_budget']
remaining_budget = budget - total_expenses
budget_used_pct = min(total_expenses / budget, 1.0) if budget > 0 else 1.0

st.sidebar.markdown("### 🏦 本月財務快照")
st.sidebar.metric("本月總收入", f"HK$ {f['salary']:,.0f}")
st.sidebar.metric("預定月供投資", f"HK$ {f['voo_monthly']:,.0f}")
st.sidebar.divider()

# 🎯 側邊欄預算監控 (視覺化)
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
# 🖥️ 主畫面
# ============================================
st.title("💎 個人財富指揮中心 (Wealth Command Center)")

tabs = st.tabs(["🧾 每月記帳與預算 (Budget Tracker)", "📊 總資產管理 (Asset Manager)", "🚀 8年財富推算 (Projection)"])

# ============================================
# 🧾 TAB 1: 每月記帳與預算
# ============================================
with tabs[0]:
    st.header("🧾 每月收支與預算控制")
    
    col_inc, col_exp = st.columns([1, 3])
    
    with col_inc:
        st.subheader("📥 資金流設定")
        new_salary = st.number_input("本月總薪金 (Income)", value=int(f['salary']), step=1000)
        new_voo_monthly = st.number_input("本月預定月供 (VOO)", value=int(f['voo_monthly']), step=1000)
        new_budget = st.number_input("本月消費預算 (Budget)", value=int(f['monthly_budget']), step=500)
        
        if st.button("更新設定與存檔", type="primary"):
            update_finances('salary', new_salary)
            update_finances('voo_monthly', new_voo_monthly)
            update_finances('monthly_budget', new_budget)
            st.success("✅ 設定已更新並存檔！")
            st.rerun()
    
    with col_exp:
        # ⚡ 快捷記帳 UI
        st.markdown("### ⚡ 快捷記帳 (Quick Add)")
        c_quick1, c_quick2 = st.columns([3, 1])
        with c_quick1:
            quick_selection = st.selectbox("選擇常用開銷 (一鍵加入表格)", list(COMMON_EXPENSES.keys()) + ["-- 手動在下方表格輸入 --"])
        with c_quick2:
            st.markdown("<br>", unsafe_allow_html=True) # 排版對齊
            if st.button("➕ 新增", type="primary", use_container_width=True):
                if quick_selection != "-- 手動在下方表格輸入 --":
                    item_data = COMMON_EXPENSES[quick_selection]
                    new_row = pd.DataFrame([{
                        "日期": datetime.today().date(),
                        "類別": item_data["類別"],
                        "項目": item_data["項目"],
                        "金額": item_data["金額"]
                    }])
                    # 把新的一筆加到最上面
                    st.session_state.expense_df = pd.concat([new_row, st.session_state.expense_df], ignore_index=True)
                    save_data() # 立即存檔
                    st.rerun()

        st.divider()
        st.markdown("### 🛒 逐筆支出紀錄 (手動編輯區)")
        if remaining_budget > 0:
            st.success(f"**本月預算還剩 HK$ {remaining_budget:,.0f}，繼續保持！**")
        else:
            st.error(f"**警告！本月已超支 HK$ {abs(remaining_budget):,.0f}！請控制消費！**")
        
        # 互動式數據表
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
        
        # 檢測是否有手動編輯，若有則自動存檔
        if not edited_df.equals(st.session_state.expense_df):
            st.session_state.expense_df = edited_df
            save_data() # 手動修改後自動存檔
            st.rerun()
            
        updated_total_expense = edited_df['金額'].sum() if not edited_df.empty else 0
        if updated_total_expense > 0:
            st.markdown(f"### 📊 支出結構分析")
            category_group = edited_df.groupby('類別')['金額'].sum().reset_index()
            fig_exp = px.pie(category_group, values='金額', names='類別', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
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
        st.info("請在此更新你的銀行與券商最新結餘，總資產將自動計算並永久保存。")
        
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
                st.success("✅ 資產資料已成功存檔！")
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
