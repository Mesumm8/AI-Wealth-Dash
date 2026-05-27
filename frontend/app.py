import streamlit as str_ui  # Using 'str_ui' for layout configuration
import requests

# 1. Base URL configuration pointing to our FastAPI server
API_URL = "http://127.0.0.1:8000"

# Set up clean browser tab settings
str_ui.set_page_config(page_title="AI Wealth Dashboard", page_icon="💰", layout="wide")

# 2. INITIALIZE SESSION STATE VARIABLES
# This allows Streamlit to remember if we are logged in across page refreshes
if "logged_in" not in str_ui.session_state:
    str_ui.session_state.logged_in = False
if "user_id" not in str_ui.session_state:
    str_ui.session_state.user_id = None
if "username" not in str_ui.session_state:
    str_ui.session_state.username = ""
if "currency" not in str_ui.session_state:
    str_ui.session_state.currency = "USD"

# ==========================================
# GATEWAY VIEW: LOGIN & REGISTRATION
# ==========================================
if not str_ui.session_state.logged_in:
    str_ui.title("💰 AI Personal Wealth Dashboard")
    str_ui.markdown("Welcome! Please securely authenticate to access your financial tracking network and AI analytics panel.")
    
    # Create two interactive tabs for the user entry portal
    tab_login, tab_register = str_ui.tabs(["🔒 Secure Login", "✨ Create Account"])
    
    # --- LOGIN SYSTEM ---
    with tab_login:
        str_ui.subheader("Member Sign In")
        login_user = str_ui.text_input("Username", key="login_user_input")
        login_pass = str_ui.text_input("Password", type="password", key="login_pass_input")
        
        if str_ui.button("Sign In", type="primary"):
            if login_user and login_pass:
                payload = {"username": login_user, "password": login_pass}
                try:
                    response = requests.post(f"{API_URL}/auth/login", json=payload)
                    if response.status_code == 200:
                        data = response.json()
                        # Lock authentication data into session memory
                        str_ui.session_state.logged_in = True
                        str_ui.session_state.user_id = data["user_id"]
                        str_ui.session_state.username = data["username"]
                        str_ui.session_state.currency = data["currency"]
                        str_ui.success(f"Welcome back, {data['username']}!")
                        str_ui.rerun() # Refresh layout to load dashboard
                    else:
                        error_detail = response.json().get("detail", "Authentication failed.")
                        str_ui.error(error_detail)
                except requests.exceptions.ConnectionError:
                    str_ui.error("Cannot connect to FastAPI backend engine. Make sure Uvicorn is running!")
            else:
                str_ui.warning("Please fill out all credential inputs.")

    # --- REGISTRATION SYSTEM ---
    with tab_register:
        str_ui.subheader("Register New Account")
        reg_user = str_ui.text_input("Choose Username", key="reg_user_input")
        reg_pass = str_ui.text_input("Choose Password", type="password", key="reg_pass_input")
        reg_curr = str_ui.selectbox("Preferred Currency Base", ["USD", "EUR", "GBP", "OMR", "INR"], index=0)
        
        if str_ui.button("Create System Ledger"):
            if reg_user and reg_pass:
                payload = {"username": reg_user, "password": reg_pass, "currency": reg_curr}
                try:
                    response = requests.post(f"{API_URL}/auth/register", json=payload)
                    if response.status_code == 200:
                        str_ui.success("Account compiled successfully! Please switch to the Login tab.")
                    else:
                        error_detail = response.json().get("detail", "Registration failed.")
                        str_ui.error(error_detail)
                except requests.exceptions.ConnectionError:
                    str_ui.error("Cannot connect to FastAPI backend engine.")
            else:
                str_ui.warning("Please complete all registration parameters.")

# ==========================================
# PREMIUM VIEW: AUTHENTICATED USER DASHBOARD
# ==========================================
else:
    # Top Action Row Header
    col_header, col_logout = str_ui.columns([0.85, 0.15])
    with col_header:
        str_ui.title(f"📊 Welcome, {str_ui.session_state.username}!")
        str_ui.markdown(f"Live Ledger System Core active • Base Currency: **{str_ui.session_state.currency}**")
    with col_logout:
        if str_ui.button("Log Out System", use_container_width=True):
            str_ui.session_state.logged_in = False
            str_ui.session_state.user_id = None
            str_ui.session_state.username = ""
            # Clear report state on logout
            if "ai_report" in str_ui.session_state:
                str_ui.session_state.ai_report = ""
            str_ui.rerun()

    str_ui.divider()
    
    # 🏃‍♂️ 1. FETCH LIVE TRANSACTION DATA FROM BACKEND
    try:
        response = requests.get(f"{API_URL}/transactions/{str_ui.session_state.user_id}")
        if response.status_code == 200:
            transactions = response.json()
        else:
            transactions = []
            str_ui.error("Could not load transaction matrix records.")
    except requests.exceptions.ConnectionError:
        transactions = []
        str_ui.error("Backend connection offline.")

    # 📊 2. CALCULATE LIVE METRICS
    total_income = sum(t["amount"] for t in transactions if t["type"] == "Income")
    total_expense = sum(t["amount"] for t in transactions if t["type"] == "Expense")
    net_wealth = total_income - total_expense

    # Display Metrics Visual Cards
    m_col1, m_col2, m_col3 = str_ui.columns(3)
    m_col1.metric("Total Inflow (Income)", f"{total_income:,.2f} {str_ui.session_state.currency}", delta_color="normal")
    m_col2.metric("Total Outflow (Expenses)", f"{total_expense:,.2f} {str_ui.session_state.currency}", delta_color="inverse")
    m_col3.metric("Net Liquid Wealth", f"{net_wealth:,.2f} {str_ui.session_state.currency}")

    str_ui.divider()

    # 🛠️ 3. DUAL COLUMN WORKSPACE: INPUT FORM & LEDGER VIEW
    left_panel, right_panel = str_ui.columns([0.4, 0.6])

    with left_panel:
        str_ui.subheader("📝 Log Asset Transaction")
        
        with str_ui.form("transaction_form", clear_on_submit=True):
            tx_desc = str_ui.text_input("Transaction Description", placeholder="e.g., Freelance Project, Rent, Groceries")
            tx_amount = str_ui.number_input("Amount Value", min_value=0.01, step=0.50, format="%.2f")
            
            tx_type = str_ui.radio("Transaction Vectors", ["Income", "Expense"], horizontal=True)
            
            categories = ["Salary", "Investments", "Freelance", "Housing", "Food", "Transport", "Utilities", "Tech Gear", "Other"]
            tx_cat = str_ui.selectbox("Category Classification", categories)
            
            submit_button = str_ui.form_submit_button("Commit to Ledger", type="primary")
            
            if submit_button:
                if tx_desc:
                    payload = {
                        "user_id": str_ui.session_state.user_id,
                        "description": tx_desc,
                        "amount": tx_amount,
                        "category": tx_cat,
                        "type": tx_type
                    }
                    tx_res = requests.post(f"{API_URL}/transactions/", json=payload)
                    if tx_res.status_code == 200:
                        str_ui.success("Transaction successfully committed to ledger!")
                        str_ui.rerun()  # Refresh dashboard metrics and table instantly
                    else:
                        str_ui.error("Failed to execute ledger storage entry.")
                else:
                    str_ui.warning("Please supply a descriptive name.")

    with right_panel:
        str_ui.subheader("📜 Historical Ledger Network")
        if transactions:
            # Display clear data table grid
            import pandas as pd
            df = pd.DataFrame(transactions)
            # Re-arrange columns for presentation cleanliness
            df = df[["date", "description", "category", "type", "amount"]]
            df.columns = ["Timestamp", "Description", "Category", "Vector Type", "Amount"]
            str_ui.dataframe(df, use_container_width=True, hide_index=True)
        else:
            str_ui.info("No records detected. Commit an asset transaction on the left to initialize the data engine stream.")

    # ==========================================
    # 🤖 GEMINI AI FINANCIAL ADVISORY ENGINE
    # ==========================================
    str_ui.divider()
    str_ui.subheader("🤖 Gemini AI Financial Advisory Engine")
    str_ui.markdown("Deploy our generative quantitative intelligence layer to audit your transaction streams and synthesize a custom wealth management playbook.")
    
    # Check if a report session state exists so it doesn't disappear when the page reruns
    if "ai_report" not in str_ui.session_state:
        str_ui.session_state.ai_report = ""

    col_btn, _ = str_ui.columns([0.25, 0.75])
    with col_btn:
        generate_btn = str_ui.button("🚀 Synthesize Wealth Strategy", use_container_width=True, type="secondary")
        
    if generate_btn:
        with str_ui.spinner("Analyzing ledger dynamics and generating strategy..."):
            try:
                ai_res = requests.get(f"{API_URL}/analytics/ai-report/{str_ui.session_state.user_id}")
                if ai_res.status_code == 200:
                    str_ui.session_state.ai_report = ai_res.json()["report"]
                    str_ui.success("Strategy compiled successfully!")
                    str_ui.rerun()
                else:
                    str_ui.error("The AI engine ran into an error processing your data streams.")
            except requests.exceptions.ConnectionError:
                str_ui.error("Backend offline. Unable to reach analytics microservice.")
                
    # If a report exists, render it beautifully inside a premium markdown container
    if str_ui.session_state.ai_report:
        str_ui.markdown("---")
        with str_ui.container(border=True):
            str_ui.markdown(str_ui.session_state.ai_report)