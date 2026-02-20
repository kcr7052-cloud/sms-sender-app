import streamlit as st
import sqlite3
import hashlib
import time
from datetime import datetime
from streamlit_option_menu import option_menu
import pandas as pd
import plotly.express as px

# --------------------------------------------------------------------------------
# 1. CONFIGURATION, CSS & DATA STRUCTURE
# --------------------------------------------------------------------------------
st.set_page_config(page_title="Expense Tracker Pro", page_icon="💰", layout="wide")

# --- CATEGORY DATA STRUCTURE (Main Categories only) ---
MAIN_CATEGORIES = [
    "1. Food & Beverages (खाना–पीना)",
    "2. Travel (यात्रा)",
    "3. Bills & Utilities (बिल)",
    "4. Shopping (खरीदारी)",
    "5. Groceries (राशन)",
    "6. Entertainment",
    "7. Health & Fitness",
    "8. Education",
    "9. Rent & EMIs",
    "10. Personal Care",
    "11. Savings & Investments",
    "12. Miscellaneous (अन्य)",
]

st.markdown("""
    <style>
    /* General Styling */
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* --- NOTIFICATION BAR STYLES (Header) --- */
    .notification-bar {
        padding: 15px;
        margin-bottom: 20px;
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        animation: slideDown 0.5s ease-out;
    }
    .notif-red { background-color: #d32f2f; border-left: 10px solid #b71c1c; }
    .notif-yellow { background-color: #fbc02d; color: #333; border-left: 10px solid #f57f17; }
    .notif-blue { background-color: #1976d2; border-left: 10px solid #0d47a1; }
    @keyframes slideDown { 0% { transform: translateY(-20px); opacity: 0; } 100% { transform: translateY(0); opacity: 1; } }

    /* Login Box & Title Fix */
    .login-box {
        animation: slideUp 0.8s ease-out;
        background-color: white;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        text-align: center;
        border-top: 5px solid #ff4b4b;
        margin-top: 10px; /* Reduced margin */
    }
    /* New Title Style for Auth Page */
    .auth-page-title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ff4b4b;
        text-align: center;
        margin-bottom: 20px;
        margin-top: 30px;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }

    /* Metric Cards */
    .metric-container {
        background: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
        text-align: center;
        border: 1px solid #eee;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------------------------------------------------------------
# 2. DATABASE FUNCTIONS
# --------------------------------------------------------------------------------
DB_NAME = "expense_tracker_final.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (username TEXT PRIMARY KEY, password TEXT, full_name TEXT, 
                      email TEXT, phone TEXT, currency TEXT, budget REAL, signup_date TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS profiles
                     (username TEXT PRIMARY KEY, occupation TEXT, monthly_income REAL, 
                      salary REAL, spendable REAL, savings_goal REAL, current_savings REAL,
                      emergency_fund REAL, other_income REAL)''')
        
        # Transactions table without subcategory
        c.execute('''CREATE TABLE IF NOT EXISTS transactions
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, name TEXT, amount REAL, category TEXT, date TEXT)''')
        conn.commit()

def make_hash(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def register_user_db(username, password, fullname, email, phone, currency, budget):
    try:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute('INSERT INTO users VALUES (?,?,?,?,?,?,?,?)', 
                      (username, make_hash(password), fullname, email, phone, currency, budget, date))
            conn.commit()
            return True
    except sqlite3.IntegrityError:
        return False

def login_user_db(username, password):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', 
                  (username, make_hash(password)))
        return c.fetchone()
    
def update_profile_db(username, spendable, current_savings, emergency_fund, savings_goal=None):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        
        current_profile = get_profile_db(username)
        if not current_profile:
             return False

        if savings_goal is None:
            savings_goal = current_profile[5]

        updated_data = list(current_profile)
        updated_data[4] = spendable
        updated_data[6] = current_savings
        updated_data[7] = emergency_fund
        updated_data[5] = savings_goal
        
        c.execute('INSERT OR REPLACE INTO profiles VALUES (?,?,?,?,?,?,?,?,?)', tuple(updated_data))
        conn.commit()
        return True

def save_profile_db(data_tuple):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('INSERT OR REPLACE INTO profiles VALUES (?,?,?,?,?,?,?,?,?)', data_tuple)
        conn.commit()

def get_profile_db(username):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM profiles WHERE username = ?', (username,))
        return c.fetchone()

# Updated add_expense_db to remove subcategory
def add_expense_db(username, name, amount, category, date):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('INSERT INTO transactions (username, name, amount, category, date) VALUES (?,?,?,?,?)', 
                  (username, name, amount, category, date))
        conn.commit()

def get_total_expenses(username):
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute('SELECT SUM(amount) FROM transactions WHERE username = ?', (username,))
        result = c.fetchone()[0]
        return result if result else 0.0

def get_recent_transactions(username):
    # Query: date, name, category, amount
    with sqlite3.connect(DB_NAME) as conn:
        df = pd.read_sql_query(f"SELECT date, name, category, amount FROM transactions WHERE username='{username}' ORDER BY date DESC", conn)
        return df

init_db()

# --------------------------------------------------------------------------------
# 3. SESSION STATE
# --------------------------------------------------------------------------------
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'page' not in st.session_state:
    st.session_state['page'] = 'auth'
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = {}

# --------------------------------------------------------------------------------
# 4. AUTH & ONBOARDING PAGES
# --------------------------------------------------------------------------------

def show_auth():
    # Main title above the box
    st.markdown('<div class="auth-page-title">EXPENSE TRACKER SYSTEM</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        # Inner title removed as requested
        
        st.markdown("### 💰 User Access") # Changed to a generic title for the box

        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            username = st.text_input("Username", key="l_user")
            password = st.text_input("Password", type="password", key="l_pass")
            if st.button("Log In", use_container_width=True):
                user = login_user_db(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = {'username': user[0], 'name': user[2], 'currency': user[5]}
                    if get_profile_db(username):
                        st.session_state['page'] = 'dashboard'
                    else:
                        st.session_state['page'] = 'onboarding'
                    st.rerun()
                else:
                    st.error("Invalid Credentials")

        with tab2:
            with st.form("reg_form"):
                f_name = st.text_input("Full Name")
                u_name = st.text_input("Username")
                email = st.text_input("Email")
                phone = st.text_input("Phone")
                p1 = st.text_input("Password", type="password")
                p2 = st.text_input("Confirm Password", type="password")
                curr = st.selectbox("Currency", ["₹ INR", "$ USD"])
                # Amount Step Fix: Set step=50.0
                budg = st.number_input("Monthly Budget", min_value=0.0, step=50.0)
                tnc = st.checkbox("I agree to Terms & Conditions")
                
                if st.form_submit_button("Register"):
                    if p1 == p2 and tnc and u_name:
                        if register_user_db(u_name, p1, f_name, email, phone, curr, budg):
                            # --- New Logic: Log in and redirect to onboarding ---
                            st.session_state['logged_in'] = True
                            st.session_state['user_info'] = {'username': u_name, 'name': f_name, 'currency': curr}
                            st.session_state['page'] = 'onboarding'
                            st.success("Registration Successful! Please complete your profile setup.")
                            time.sleep(1) 
                            st.rerun()
                            # --- End New Logic ---
                        else:
                            st.error("Username exists.")
        st.markdown('</div>', unsafe_allow_html=True)

def show_onboarding():
    st.title("🚀 Setup Profile")
    with st.form("onboard"):
        occ = st.selectbox("Occupation", ["Student", "Job", "Business", "Other"])
        c1, c2 = st.columns(2)
        with c1:
            # Amount Step Fix: Set step=50.0
            salary = st.number_input("Salary", min_value=0.0, step=50.0)
            other = st.number_input("Other Income", min_value=0.0, step=50.0)
            spendable = st.number_input("Spendable Budget (Limit)", min_value=0.0, step=50.0)
        with c2:
            # Amount Step Fix: Set step=50.0
            curr_sav = st.number_input("Current Savings", min_value=0.0, step=50.0)
            emerg = st.number_input("Emergency Fund", min_value=0.0, step=50.0)
            goal = st.number_input("Savings Goal", min_value=0.0, step=50.0)
        
        total_inc = salary + other
        if st.form_submit_button("Save & Continue"):
            uname = st.session_state['user_info']['username']
            save_profile_db((uname, occ, total_inc, salary, spendable, goal, curr_sav, emerg, other))
            st.session_state['page'] = 'dashboard'
            st.rerun()

# --------------------------------------------------------------------------------
# 5. DASHBOARD
# --------------------------------------------------------------------------------

def show_dashboard():
    user_name = st.session_state['user_info']['name']
    u_curr = st.session_state['user_info']['currency'].split()[0]
    username = st.session_state['user_info']['username']
    
    today_date = datetime.now().strftime("%A, %B %d, %Y")
    
    # --- STEP 1: GET DATA ---
    profile = get_profile_db(username)
    total_spent = get_total_expenses(username)
    
    # --- STEP 2: DISPLAY NOTIFICATION BAR (TOP HEADER) ---
    if profile:
        spendable_limit = profile[4]
        if spendable_limit > 0:
            percent_used = (total_spent / spendable_limit) * 100
            
            if percent_used >= 90:
                st.markdown(f"""
                    <div class="notification-bar notif-red">
                        🚨 CRITICAL ALERT: Budget 90% Exhausted! ({u_curr}{total_spent} / {u_curr}{spendable_limit})
                    </div>
                """, unsafe_allow_html=True)
            elif percent_used >= 75:
                st.markdown(f"""
                    <div class="notification-bar notif-yellow">
                        ⚠ WARNING: You have crossed 75% of your budget. Spend wisely.
                    </div>
                """, unsafe_allow_html=True)
            elif percent_used >= 50:
                st.markdown(f"""
                    <div class="notification-bar notif-blue">
                        ℹ REMINDER: 50% of budget utilized.
                    </div>
                """, unsafe_allow_html=True)
    
    # --- STEP 3: HEADER MENU ---
    selected = option_menu(
        menu_title=None, 
        options=["Overview", "Add Expense", "Analytics", "Logout"], 
        icons=["house", "wallet", "bar-chart-line", "box-arrow-right"], 
        menu_icon="cast", 
        default_index=0, 
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "orange", "font-size": "18px"}, 
            "nav-link": {"font-size": "15px", "text-align": "center", "margin":"5px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#ff4b4b"},
        }
    )
    
    if selected == "Logout":
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'auth'
        st.rerun()

    # --- STEP 4: CONTENT BASED ON MENU SELECTION ---
    
    if profile:
        spendable_limit = profile[4]
        remaining = spendable_limit - total_spent
        
        # === TAB 1: OVERVIEW ===
        if selected == "Overview":
            st.markdown(f"### 👋 Welcome, *{user_name}*")
            st.markdown(f"*Today's Date:* {today_date}")
            st.caption("YOUR FINANCIAL OVERVIEW")
            
            # --- EDITABLE PROFILE SECTION ---
            with st.expander("⚙ Edit Profile Limits (Limit, Savings, Emergency Fund)", expanded=False):
                with st.form("edit_profile_form"):
                    st.markdown("##### Update key financial limits:")
                    c1, c2, c3 = st.columns(3)
                    
                    with c1:
                        # Amount Step Fix: Set step=50.0
                        new_spendable = st.number_input("Spendable Limit (Budget)", min_value=0.0, value=spendable_limit, key='edit_spend', step=50.0)
                    with c2:
                        # Amount Step Fix: Set step=50.0
                        new_savings = st.number_input("Current Savings", min_value=0.0, value=profile[6], key='edit_savings', step=50.0)
                    with c3:
                        # Amount Step Fix: Set step=50.0
                        new_emergency = st.number_input("Emergency Fund", min_value=0.0, value=profile[7], key='edit_emergency', step=50.0)
                    
                    if st.form_submit_button("Update Profile"):
                        if update_profile_db(username, new_spendable, new_savings, new_emergency):
                             st.success("Profile updated successfully!")
                             time.sleep(0.5)
                             st.rerun()
                        else:
                             st.error("Error updating profile.")
            
            st.markdown("---")

            # METRICS (5 Columns)
            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                st.markdown(f"<div class='metric-container'><h5>Limit</h5><h3>{u_curr}{spendable_limit}</h3></div>", unsafe_allow_html=True)
            with c2:
                st.markdown(f"<div class='metric-container'><h5>Spent</h5><h3>{u_curr}{total_spent}</h3></div>", unsafe_allow_html=True)
            with c3:
                color = "#d32f2f" if remaining < 0 else "#388e3c"
                st.markdown(f"<div class='metric-container'><h5>Remaining</h5><h3 style='color:{color}'>{u_curr}{remaining:.0f}</h3></div>", unsafe_allow_html=True)
            with c4:
                st.markdown(f"<div class='metric-container'><h5>Current Savings</h5><h3>{u_curr}{profile[6]}</h3></div>", unsafe_allow_html=True) 
            with c5:
                st.markdown(f"<div class='metric-container'><h5>Emergency Fund</h5><h3>{u_curr}{profile[7]}</h3></div>", unsafe_allow_html=True) 
            
            st.write("")
            
            if spendable_limit > 0 and percent_used >= 90:
                 st.error("🚨 CRITICAL SPENDING ALERT: Your budget is almost exhausted! Immediate action needed.")
            
            st.subheader("📊 Budget vs Spent")
            # BAR CHART
            chart_data = {"Category": ["Limit", "Spent", "Remaining"], "Value": [spendable_limit, total_spent, max(0, remaining)]}
            st.bar_chart(chart_data, x="Category", y="Value", color="#ff4b4b") 


        # === TAB 2: ADD EXPENSE (MAIN CATEGORY ONLY) ===
        elif selected == "Add Expense":
            st.subheader("➕ Add Transaction")
            st.write("Add your daily spending here. Choose the most relevant category.")
            
            with st.form("exp_form"):
                
                st.markdown("##### 1. Select Main Category")
                
                # --- MAIN CATEGORY SELECTION ---
                main_category = st.selectbox(
                    "Select Main Category", 
                    MAIN_CATEGORIES,
                    key="main_cat"
                )
                
                st.markdown("---")
                st.markdown("##### 2. Transaction Details")
                
                c1, c2 = st.columns(2)
                with c1:
                    # 'name' field corresponds to the item/place description
                    name = st.text_input("Description (e.g., KFC meal, Amazon purchase, Bus fare)")
                    # Amount Step Fix: Set step=50.0
                    amt = st.number_input("Amount (₹50 step)", min_value=0.0, step=50.0) 
                with c2:
                    date = st.date_input("Date")
                
                if st.form_submit_button("Add Expense", use_container_width=True):
                    
                    if not main_category:
                        st.warning("Please select a Main Category.")
                    elif amt <= 0 or not name:
                        st.warning("Please enter a valid Amount and Description.")
                    else:
                        # Extract clean Main Category name for DB storage
                        try:
                            clean_main_category = main_category.split(". ")[1].split(" (")[0].strip()
                        except IndexError:
                            clean_main_category = main_category
                        
                        add_expense_db(username, name, amt, clean_main_category, str(date)) 
                        st.toast(f"Expense added to '{clean_main_category}'!", icon="✅")
                        time.sleep(0.5) 
                        st.rerun() 

        # === TAB 3: ANALYTICS ===
        elif selected == "Analytics":
            st.subheader("📈 Detailed Analysis")
            
            df_transactions = get_recent_transactions(username)
            
            if not df_transactions.empty:
                st.write("")
                col_pie, col_recent = st.columns([1, 1])

                # PIE CHART (Use Main Category for grouping)
                with col_pie:
                    st.markdown("#### Category Spending Breakdown (Pie Chart)")
                    df_category = df_transactions.groupby('category')['amount'].sum().reset_index()
                    fig = px.pie(df_category, values='amount', names='category', title='Spending by Main Category', hole=0.3)
                    fig.update_traces(textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)

                # RECENT ACTIVITY TABLE 
                with col_recent:
                    st.markdown("#### Recent Activity (Downloadable)")
                    # df_transactions columns: date, name, category, amount
                    df_display = df_transactions[['date', 'name', 'category', 'amount']].head(10)
                    df_display.columns = ['Date', 'Item/Description', 'Category', f'Amount ({u_curr})']
                    st.dataframe(df_display, use_container_width=True, hide_index=True)
                    
                    # Option to Download Data
                    csv = df_transactions.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Download All Data as CSV",
                        data=csv,
                        file_name='expense_activity.csv',
                        mime='text/csv',
                        help='Download all your transaction data.'
                    )
            else:
                st.info("No transactions recorded yet. Add expenses in the 'Add Expense' tab.")

    else:
        st.error("Profile data missing. Please re-login.")

# --------------------------------------------------------------------------------
# 6. MAIN APP EXECUTION
# --------------------------------------------------------------------------------
if not st.session_state['logged_in']:
    show_auth()
else:
    if st.session_state['page'] == 'onboarding':
        show_onboarding()
    elif st.session_state['page'] == 'dashboard':
        show_dashboard()
