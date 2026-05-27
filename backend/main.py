import os
from google import genai
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import hashlib
import secrets
import database

load_dotenv()
ai_client = genai.Client()

app = FastAPI(title="AI Wealth Analytics Backend Engine")

# 📊 DATA STRUCTURAL SCHEMAS (Pydantic Models)
class UserRegister(BaseModel):
    username: str
    password: str
    currency: str = "USD"

class UserLogin(BaseModel):
    username: str
    password: str

class TransactionCreate(BaseModel):
    user_id: int
    description: str
    amount: float
    category: str
    type: str 

# 🔐 BULLETPROOF NATIVE ENCRYPTION HELPERS
def hash_password(password: str) -> str:
    """Hashes a password using secure SHA-256 with a built-in salt."""
    # We use a static salt wrapper here to keep the database verification lightweight and simple
    salt = b"wealth_secure_salt_vector_99"
    pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
    return pwd_hash.hex()

# 🔐 AUTHENTICATION ROUTING ENDPOINTS
@app.post("/auth/register")
def register_user(user: UserRegister):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (user.username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="Username is already registered.")
    
    # Securely hash the password natively
    hashed_password = hash_password(user.password)
    
    cursor.execute(
        "INSERT INTO users (username, password_hash, currency) VALUES (?, ?, ?)",
        (user.username, hashed_password, user.currency)
    )
    conn.commit()
    conn.close()
    return {"message": "Account created successfully! Proceed to sign in."}

@app.post("/auth/login")
def login_user(user: UserLogin):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, password_hash, currency FROM users WHERE username = ?", (user.username,))
    db_user = cursor.fetchone()
    conn.close()
    
    # Hash the incoming password attempt to see if it matches our database string
    if not db_user or hash_password(user.password) != db_user["password_hash"]:
        raise HTTPException(status_code=401, detail="Invalid username or password.")
    
    return {
        "message": "Login verified successfully",
        "user_id": db_user["id"],
        "username": user.username,
        "currency": db_user["currency"]
    }

# 💰 TRANSACTION ENGINE ROUTING ENDPOINTS
@app.post("/transactions/")
def add_transaction(tx: TransactionCreate):
    if tx.type not in ["Income", "Expense"]:
        raise HTTPException(status_code=400, detail="Invalid transaction type vector.")
        
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "INSERT INTO transactions (user_id, description, amount, category, type) VALUES (?, ?, ?, ?, ?)",
        (tx.user_id, tx.description, tx.amount, tx.category, tx.type)
    )
    conn.commit()
    conn.close()
    return {"message": "Transaction logged successfully into persistent ledger."}

@app.get("/transactions/{user_id}")
def get_transactions(user_id: int):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY date DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    transactions = [dict(row) for row in rows]
    return transactions


@app.get("/analytics/ai-report/{user_id}")
def generate_ai_report(user_id: int):
    conn = database.get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch user's profile metadata
    cursor.execute("SELECT username, currency FROM users WHERE id = ?", (user_id,))
    user_info = cursor.fetchone()
    
    if not user_info:
        conn.close()
        raise HTTPException(status_code=404, detail="User profile not detected.")
        
    # 2. Fetch all transaction history rows
    cursor.execute("SELECT description, amount, category, type, date FROM transactions WHERE user_id = ?", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    transactions = [dict(row) for row in rows]
    
    if not transactions:
        return {"report": "Your financial ledger is currently empty. Please log income or expenses to unlock AI wealth diagnostics."}
        
    # 3. Format the ledger data cleanly for the AI context model
    ledger_summary = ""
    for tx in transactions:
        ledger_summary += f"- [{tx['date']}] {tx['type']}: {tx['description']} | Category: {tx['category']} | Amount: {tx['amount']} {user_info['currency']}\n"
        
    # 4. Construct a strict, engineering-focused financial prompt
    ai_prompt = f"""
    You are an elite AI Wealth Advisor and Financial Quantitative Strategist. 
    Analyze the personal asset ledger for user '{user_info['username']}' and build a structured financial optimization report.
    
    Here is the live transaction data history:
    {ledger_summary}
    
    Provide your output in clean Markdown formatting with the following structural pillars:
    ### 📊 Executive Summary
    (Provide a quick calculation of total income vs total expenses and a brief health rating of their current liquid cash flow status)
    
    ### ⚠️ Risk Vulnerabilities & Outflow Leakages
    (Identify areas where they are spending heavily or areas of concern based on categories)
    
    ### 🚀 Wealth-Building Action Matrix
    (Give 3 highly strategic, actionable, quantitative recommendations on how they can optimize their savings, lower expenses, or relocate resources to grow their wealth based on their personal base currency: {user_info['currency']})
    """
    
    try:
        # Call the fast, optimized Gemini 2.5 Flash model
        response = ai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=ai_prompt,
        )
        return {"report": response.text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini Engine Error: {str(e)}")