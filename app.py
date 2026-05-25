import streamlit as st
import pandas as pd
from datetime import date
import sqlite3
import json
import hashlib
import os
import plotly.express as px

st.set_page_config(page_title="3D Print Tracker", layout="wide")

# ====================== DATABASE FOLDER ======================
DB_FOLDER = "databases"
os.makedirs(DB_FOLDER, exist_ok=True)

def get_db_path(username):
    return os.path.join(DB_FOLDER, f"data_{username.lower()}.db")

def init_user_db(username):
    conn = sqlite3.connect(get_db_path(username))
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                 id INTEGER PRIMARY KEY,
                 date TEXT,
                 type TEXT,
                 category TEXT,
                 description TEXT,
                 amount REAL,
                 cost REAL,
                 shipping REAL,
                 customer TEXT,
                 details TEXT,
                 notes TEXT)''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(get_db_path(st.session_state.current_user))

# ====================== SESSION ======================
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "form_key" not in st.session_state:
    st.session_state.form_key = 0

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ====================== LOGIN ======================
def login_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🖨️ Printly Made")
        st.subheader("3D Printing Business Tracker")

        tab1, tab2 = st.tabs(["🔑 Login", "📝 Sign Up"])

        with tab1:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login", type="primary", use_container_width=True):
                if username and password:
                    if username.lower() == "adrian" and hash_password(password) == hash_password("adrian123"):
                        st.session_state.current_user = username
                        init_user_db(username)
                        st.success("✅ Login Successful!")
                        st.rerun()
                    else:
                        pass_file = f"pass_{username.lower()}.txt"
                        if os.path.exists(pass_file):
                            with open(pass_file, "r") as f:
                                if f.read().strip() == hash_password(password):
                                    st.session_state.current_user = username
                                    init_user_db(username)
                                    st.success("✅ Login Successful!")
                                    st.rerun()
                st.error("❌ Invalid username or password")

        with tab2:
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Choose Password", type="password")
            new_pass2 = st.text_input("Confirm Password", type="password")
            if st.button("Create Account", type="primary", use_container_width=True):
                if new_pass != new_pass2:
                    st.error("Passwords do not match")
                elif len(new_pass) < 6:
                    st.error("Password must be at least 6 characters")
                else:
                    init_user_db(new_user)
                    with open(f"pass_{new_user.lower()}.txt", "w") as f:
                        f.write(hash_password(new_pass))
                    st.success(f"✅ Account created for **{new_user}**!")
                    st.rerun()

if st.session_state.current_user is None:
    login_page()
else:
    username = st.session_state.current_user
    st.title(f"🖨️ {username}'s 3D Printing Business Tracker")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.current_user = None
        st.rerun()
# ====================== NAVIGATION ======================
    st.sidebar.markdown("## Navigation")
    page = st.sidebar.radio(
        label="",
        options=["Dashboard", "Add Transaction", "View & Edit Transactions", "Analysis"],
        format_func=lambda x: {
            "Dashboard": "📊 Dashboard",
            "Add Transaction": "➕ Add Transaction",
            "View & Edit Transactions": "📋 View & Edit",
            "Analysis": "📈 Analysis"
        }[x]
    )

    products = [
        "Garage", "Dog Bust", "Bowl", "Dog Statue", "Animal Bust", "Animal Statue",
        "Coffee Spoon Holder", "Memory Box", "Dog Holder", "Ring Holder", "Soap Holder",
        "Team Design", "Multi-purpose Pot", "Treat Container", "Knitted Figurine",
        "Fidget Spinner", "Dog Brush", "Dragon", "Magnet", "Waste Bag Holder"
    ]

    # ====================== ADD TRANSACTION ======================
    if page == "Add Transaction":
        st.header("Add New Transaction")
        if "form_key" not in st.session_state:
            st.session_state.form_key = 0

        col1, col2 = st.columns(2)
        with col1:
            trans_date = st.date_input("Date", date.today(), key=f"date_{st.session_state.form_key}")
            trans_type = st.selectbox("Type", ["Income", "Expense"], key=f"type_{st.session_state.form_key}")
        with col2:
            if trans_type == "Income":
                category = st.selectbox("Product", products, key=f"product_{st.session_state.form_key}")
            else:
                exp_categories = ["Filament", "Resin", "Parts & Nozzles", "Electricity", "Shipping", "Equipment", "Marketing", "Other"]
                category = st.selectbox("Expense Category", exp_categories, key=f"exp_{st.session_state.form_key}")

        amount = st.number_input("Selling Price ($)", min_value=0.01, step=0.01, key=f"amt_{st.session_state.form_key}")
        cost = shipping = 0.0
        if trans_type == "Income":
            cost = st.number_input("Cost to Make ($)", min_value=0.0, step=0.01, value=0.0, key=f"cost_{st.session_state.form_key}")
            shipping = st.number_input("Shipping Cost ($)", min_value=0.0, step=0.01, value=0.0, key=f"shipping_{st.session_state.form_key}")

        customer = st.text_input("Customer Name (optional)", key=f"cust_{st.session_state.form_key}") if trans_type == "Income" else ""

        st.subheader("Item Specific Details")
        details = {}
        if trans_type == "Income":
            if category == "Garage":
                details["logo_design"] = st.text_input("Logo Design (optional)", key=f"g_logo_{st.session_state.form_key}")
                details["colors"] = st.text_input("Colors", key=f"g_color_{st.session_state.form_key}")
            elif category == "Dog Bust":
                details["size"] = st.selectbox("Size", ["Small", "Medium", "Large", "Custom"], key=f"db_size_{st.session_state.form_key}")
                details["name"] = st.text_input("Name / Title", key=f"db_name_{st.session_state.form_key}")
                details["colors"] = st.text_input("Colors", key=f"db_color_{st.session_state.form_key}")
                details["breed"] = st.text_input("Breed", key=f"db_breed_{st.session_state.form_key}")
            elif category == "Bowl":
                details["size"] = st.selectbox("Size", ["Small", "Medium", "Large"], key=f"bowl_size_{st.session_state.form_key}")
                details["color"] = st.text_input("Color", key=f"bowl_color_{st.session_state.form_key}")
                details["name"] = st.text_input("Name / Text", key=f"bowl_name_{st.session_state.form_key}")
            elif category == "Dog Statue":
                details["size"] = st.selectbox("Size", ["Small", "Medium", "Large"], key=f"ds_size_{st.session_state.form_key}")
                details["breed"] = st.text_input("Breed", key=f"ds_breed_{st.session_state.form_key}")
            elif category == "Animal Bust" or category == "Animal Statue":
                details["size"] = st.selectbox("Size", ["Small", "Medium", "Large"], key=f"animal_size_{st.session_state.form_key}")
                details["animal"] = st.text_input("Animal Type", key=f"animal_type_{st.session_state.form_key}")
            elif category == "Coffee Spoon Holder":
                details["color"] = st.text_input("Color", key=f"coffee_color_{st.session_state.form_key}")
                details["material"] = st.selectbox("Material", ["PLA", "PETG", "ABS"], key=f"coffee_mat_{st.session_state.form_key}")
            elif category == "Memory Box":
                details["color"] = st.text_input("Color", key=f"memory_color_{st.session_state.form_key}")
                details["lithophanes"] = st.number_input("Number of Lithophanes", min_value=0, step=1, key=f"memory_litho_{st.session_state.form_key}")
            elif category == "Dog Holder":
                details["version"] = st.selectbox("Version", ["V1", "V2"], key=f"dh_ver_{st.session_state.form_key}")
                details["background_color"] = st.text_input("Background Color", key=f"dh_bg_{st.session_state.form_key}")
                details["dog_name"] = st.text_input("Dog Name", key=f"dh_name_{st.session_state.form_key}")
                details["dog_color"] = st.text_input("Dog Color", key=f"dh_dogcol_{st.session_state.form_key}")
                details["breed"] = st.text_input("Breed", key=f"dh_breed_{st.session_state.form_key}")
            elif category == "Ring Holder":
                details["type"] = st.text_input("Type of Ring Holder", key=f"ring_type_{st.session_state.form_key}")
                details["color"] = st.text_input("Color", key=f"ring_color_{st.session_state.form_key}")
            elif category == "Soap Holder":
                details["type"] = st.text_input("Type of Soap Holder", key=f"soap_type_{st.session_state.form_key}")
                details["color"] = st.text_input("Color", key=f"soap_color_{st.session_state.form_key}")
            elif category == "Team Design":
                details["team_name"] = st.text_input("Team Name", key=f"team_name_{st.session_state.form_key}")
                details["design_type"] = st.selectbox("Design Type", ["Name", "Logo"], key=f"team_type_{st.session_state.form_key}")
            elif category == "Knitted Figurine":
                details["animal"] = st.text_input("Animal", key=f"knit_animal_{st.session_state.form_key}")
                details["type"] = st.selectbox("Type", ["Keychain", "Figurine"], key=f"knit_type_{st.session_state.form_key}")
            elif category == "Fidget Spinner":
                details["color"] = st.text_input("Color", key=f"fidget_color_{st.session_state.form_key}")
                details["type"] = st.text_input("Type", key=f"fidget_type_{st.session_state.form_key}")
            elif category == "Dog Brush":
                details["color"] = st.text_input("Color", key=f"brush_color_{st.session_state.form_key}")
                details["name"] = st.text_input("Name", key=f"brush_name_{st.session_state.form_key}")
            elif category == "Magnet":
                details["type"] = st.text_input("Type", key=f"magnet_type_{st.session_state.form_key}")
            elif category == "Waste Bag Holder":
                details["color"] = st.text_input("Color", key=f"waste_color_{st.session_state.form_key}")
                details["name"] = st.text_input("Name", key=f"waste_name_{st.session_state.form_key}")
            elif category == "Dragon":
                details["color"] = st.text_input("Color", key=f"dragon_color_{st.session_state.form_key}")
                details["type"] = st.text_input("Type of Dragon", key=f"dragon_type_{st.session_state.form_key}")

        description = st.text_input("General Description (optional)", key=f"desc_{st.session_state.form_key}")
        notes = st.text_area("Additional Notes", key=f"notes_{st.session_state.form_key}")

        if st.button("💾 Save New Transaction", type="primary"):
            details_json = json.dumps(details)
            conn = get_connection()
            conn.execute("""INSERT INTO transactions
                         (date, type, category, description, amount, cost, shipping, customer, details, notes)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (trans_date.isoformat(), trans_type, category, description,
                          amount, cost, shipping, customer, details_json, notes))
            conn.commit()
            conn.close()
            st.success("✅ Transaction Saved Successfully!")
            st.session_state.form_key += 1
            st.rerun()

        # ====================== DASHBOARD ======================
    elif page == "Dashboard":
        st.header("Business Overview")
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()

        if df.empty:
            st.info("No transactions yet.")
        else:
            for col in ['amount', 'cost', 'shipping']:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            income = df[df['type'] == 'Income']
            expenses = df[df['type'] == 'Expense']
            
            total_revenue = income['amount'].sum()
            total_cogs = income['cost'].sum()
            total_shipping = income['shipping'].sum()
            total_other_operating = expenses['amount'].sum()
            
            gross_profit = total_revenue - total_cogs
            total_operating = total_shipping + total_other_operating
            net_profit = gross_profit - total_operating
            
            gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Revenue", f"${total_revenue:,.2f}")
            col2.metric("Cost of Goods Sold", f"${total_cogs:,.2f}")
            col3.metric("Gross Profit", f"${gross_profit:,.2f}", f"{gross_margin:.1f}%")
            col4.metric("Net Profit", f"${net_profit:,.2f}", f"{net_margin:.1f}%")

            col5, col6, col7 = st.columns(3)
            with col5:
                st.metric("Shipping Cost", f"${total_shipping:,.2f}")
            with col6:
                st.metric("Other Operating Expenses", f"${total_other_operating:,.2f}")
            with col7:
                st.metric("Total Transactions", len(df))

            st.subheader("Recent Transactions")
            recent = df.sort_values(['date', 'id'], ascending=[False, False]).head(20).copy()
            
            # Format the table to show $ amounts
            display_df = recent.copy()
            for col in ['amount', 'cost', 'shipping']:
                if col in display_df.columns:
                    display_df[col] = display_df[col].apply(lambda x: f"${float(x):.2f}" if pd.notna(x) else "$0.00")
            
            # Drop technical columns
            display_df = display_df.drop(columns=['id', 'details'], errors='ignore')
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)

        # ====================== VIEW & EDIT TRANSACTIONS ======================
    elif page == "View & Edit Transactions":
        st.header("View & Edit Transactions")

        # ====================== EDIT FORM ======================
        if 'edit_id' in st.session_state and 'edit_data' in st.session_state:
            st.subheader("✏️ Edit Transaction")
            data = st.session_state.edit_data

            col1, col2 = st.columns(2)
            with col1:
                new_date = st.date_input("Date", pd.to_datetime(data['date']).date(), key="edit_date")
                new_type = st.selectbox("Type", ["Income", "Expense"], 
                                      index=0 if data.get('type') == "Income" else 1, key="edit_type")
            with col2:
                if new_type == "Income":
                    new_category = st.selectbox("Product", products, 
                                              index=products.index(data.get('category', products[0])), key="edit_category")
                else:
                    exp_cat = ["Filament", "Resin", "Parts & Nozzles", "Electricity", "Shipping", "Equipment", "Marketing", "Other"]
                    new_category = st.selectbox("Expense Category", exp_cat, key="edit_exp_cat")

            # Amount, Cost, Shipping formatted as currency
            new_amount = st.number_input("Selling Price ($)", 
                                       value=float(data.get('amount') or 0), 
                                       min_value=0.0, step=0.01, format="%.2f", key="edit_amount")
            
            new_cost = st.number_input("Cost to Make ($)", 
                                     value=float(data.get('cost') or 0), 
                                     min_value=0.0, step=0.01, format="%.2f", key="edit_cost")
            
            new_shipping = st.number_input("Shipping Cost ($)", 
                                         value=float(data.get('shipping') or 0), 
                                         min_value=0.0, step=0.01, format="%.2f", key="edit_shipping")
            
            new_customer = ""
            if new_type == "Income":
                new_customer = st.text_input("Customer Name", value=str(data.get('customer') or ""), key="edit_customer")

            new_description = st.text_input("Description", value=str(data.get('description') or ""), key="edit_desc")
            new_notes = st.text_area("Notes", value=str(data.get('notes') or ""), key="edit_notes")

            col_save, col_cancel, col_delete = st.columns(3)
            with col_save:
                if st.button("💾 Save Changes", type="primary"):
                    conn = get_connection()
                    cur = conn.cursor()
                    cur.execute("""UPDATE transactions 
                                SET date=?, type=?, category=?, description=?, 
                                    amount=?, cost=?, shipping=?, customer=?, notes=?
                                WHERE id=?""",
                        (new_date.isoformat(), new_type, new_category, new_description,
                         new_amount, new_cost, new_shipping, new_customer, new_notes, st.session_state.edit_id))
                    conn.commit()
                    conn.close()
                    st.success("✅ Transaction Updated Successfully!")
                    del st.session_state.edit_id
                    del st.session_state.edit_data
                    st.rerun()

            with col_cancel:
                if st.button("Cancel"):
                    del st.session_state.edit_id
                    del st.session_state.edit_data
                    st.rerun()

            with col_delete:
                if st.button("🗑️ Delete", type="secondary"):
                    if st.checkbox("Confirm Delete?", key="confirm_delete"):
                        conn = get_connection()
                        conn.execute("DELETE FROM transactions WHERE id=?", (st.session_state.edit_id,))
                        conn.commit()
                        conn.close()
                        st.success("✅ Transaction Deleted!")
                        del st.session_state.edit_id
                        del st.session_state.edit_data
                        st.rerun()

        # ====================== LIST OF ALL TRANSACTIONS ======================
        st.subheader("All Transactions")
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM transactions ORDER BY date DESC, id DESC", conn)
        conn.close()

        if df.empty:
            st.info("No transactions yet.")
        else:
            for _, row in df.iterrows():
                emoji = "🟢" if row['type'] == "Income" else "🔴"
                amount_val = float(row.get('amount') or 0)
                
                with st.expander(f"{emoji} {row['date']} — ${amount_val:.2f} — {row['category']}"):
                    if row.get('customer'):
                        st.write(f"**Customer:** {row['customer']}")
                    st.write(f"**Description:** {row.get('description') or '—'}")
                    
                    # Show as currency
                    st.write(f"**Selling Price:** ${float(row.get('amount') or 0):.2f}")
                    st.write(f"**Cost to Make:** ${float(row.get('cost') or 0):.2f}")
                    st.write(f"**Shipping:** ${float(row.get('shipping') or 0):.2f}")
                    
                    profit = amount_val - float(row.get('cost') or 0) - float(row.get('shipping') or 0) if row['type'] == "Income" else -amount_val
                    st.write(f"**Profit:** ${profit:.2f}")
                    
                    if row.get('details'):
                        try:
                            st.json(json.loads(row['details']))
                        except:
                            pass
                    if row.get('notes'):
                        st.write("**Notes:**", row['notes'])
                    
                    if st.button("✏️ Edit This Transaction", key=f"edit_btn_{row['id']}"):
                        st.session_state.edit_id = row['id']
                        st.session_state.edit_data = dict(row)
                        st.rerun()
        # ====================== ANALYSIS ======================
    elif page == "Analysis":
        st.header("📈 Business Analysis")
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM transactions", conn)
        conn.close()

        if df.empty:
            st.info("No data yet.")
        else:
            # Convert numeric columns
            for col in ['amount', 'cost', 'shipping']:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

            # ==================== CUSTOMER ANALYSIS ====================
            st.subheader("Customer Analysis")
            customer_stats = df[df['customer'].notna() & (df['customer'] != '')].groupby('customer').agg(
                transactions=('id', 'count'),
                total_spent=('amount', 'sum')
            ).reset_index()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Unique Customers", len(customer_stats))
            col2.metric("New Customers", len(customer_stats[customer_stats['transactions'] == 1]))
            col3.metric("Repeat Customers", len(customer_stats[customer_stats['transactions'] > 1]))

            # ==================== MONTHLY PERFORMANCE ====================
            st.subheader("Monthly Performance")
            df['date'] = pd.to_datetime(df['date'])
            df['month'] = df['date'].dt.to_period('M').astype(str)
            
            monthly = df.groupby(['month', 'type']).agg({
                'amount': 'sum',
                'cost': 'sum',
                'shipping': 'sum'
            }).reset_index()
            
            revenue = monthly[monthly['type'] == 'Income'].set_index('month')['amount']
            cogs = monthly[monthly['type'] == 'Income'].set_index('month')['cost'].fillna(0)
            shipping = monthly[monthly['type'] == 'Income'].set_index('month')['shipping'].fillna(0)
            op_exp = monthly[monthly['type'] == 'Expense'].groupby('month')['amount'].sum()
            
            monthly_summary = pd.DataFrame({
                'Total Revenue': revenue,
                'Gross Profit': revenue - cogs,
                'Net Profit': revenue - cogs - shipping.fillna(0) - op_exp.fillna(0)
            }).fillna(0).reset_index()
            
            plot_df = monthly_summary.melt(id_vars=['month'], var_name='Metric', value_name='Amount')
            
            fig = px.bar(plot_df, x='month', y='Amount', color='Metric',
                        title="Monthly Revenue, Gross Profit & Net Profit",
                        barmode='group',
                        color_discrete_map={
                            'Total Revenue': '#1f77b4',
                            'Gross Profit': '#2ca02c',
                            'Net Profit': '#ff7f0e'
                        })
            st.plotly_chart(fig, use_container_width=True)

            # ==================== BEST SELLING ITEMS ====================
            st.subheader("🏆 Best Selling Items")
            
            sales_df = df[df['type'] == 'Income'].copy()
            
            if not sales_df.empty:
                top_items = sales_df.groupby('category').agg(
                    total_revenue=('amount', 'sum')
                ).round(2).sort_values('total_revenue', ascending=False).reset_index()
                
                # Top Items by Revenue
                fig_best = px.bar(top_items.head(10), 
                                 x='category', 
                                 y='total_revenue',
                                 text='total_revenue',
                                 title="Top Products by Revenue",
                                 color='total_revenue',
                                 color_continuous_scale='Viridis')
                fig_best.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
                st.plotly_chart(fig_best, use_container_width=True)

                # Simple table
                st.dataframe(top_items, use_container_width=True, hide_index=True)
            else:
                st.info("No sales data yet.")

            # ==================== COST BREAKDOWN ====================
            st.subheader("Cost Breakdown")
            total_cogs = df[df['type']=='Income']['cost'].sum()
            total_ship = df[df['type']=='Income']['shipping'].sum()
            total_op = df[df['type']=='Expense']['amount'].sum()

            cost_df = pd.DataFrame({
                'Category': ['Cost of Goods Sold', 'Shipping Costs', 'Other Operating Expenses'],
                'Amount': [total_cogs, total_ship, total_op]
            })
            fig_cost = px.bar(cost_df, x='Category', y='Amount',
                             title="Total Costs Breakdown",
                             color='Category',
                             color_discrete_sequence=['#d62728', '#ff7f0e', '#9467bd'])
            st.plotly_chart(fig_cost, use_container_width=True)