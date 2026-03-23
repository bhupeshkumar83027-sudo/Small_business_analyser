import streamlit as st
import jwt
import datetime
import bcrypt
from db import get_connection

SECRET_KEY = "MY_SECRET_KEY_123456"


def create_token(username):
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def login_signup_page():
    # Page Config
    st.set_page_config(page_title="Smart Business | Login", layout="wide")

    # --- CUSTOM CSS ---
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #1e1e2f 0%, #4e54c8 100%);
    }

    .main-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border-radius: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 40px;
        box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        color: white;
    }

    .hero-section {
        padding-right: 20px;
        border-right: 1px solid rgba(255, 255, 255, 0.1);
    }

    .hero-title {
        font-family: 'Inter', sans-serif;
        font-weight: 800;
        font-size: 42px;
        background: -webkit-linear-gradient(#fff, #a5a5a5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 10px;
    }

    .stTextInput input {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 10px !important;
    }

    div.stButton > button {
        width: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 0px;
        font-weight: bold;
        border-radius: 12px;
        transition: 0.3s;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(118, 75, 162, 0.4);
        color: white;
    }

    div[data-testid="stMarkdownContainer"] p {
        color: #e0e0e0;
    }
    </style>
    """, unsafe_allow_html=True)

    # Database setup
    db = get_connection()
    cursor = db.cursor()

    # Layout
    _, central_col, _ = st.columns([0.1, 0.8, 0.1])

    with central_col:
        st.markdown('<div class="main-container">', unsafe_allow_html=True)
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown('<div class="hero-section">', unsafe_allow_html=True)
            st.markdown('<h1 class="hero-title">🚀 Smart<br>Business</h1>', unsafe_allow_html=True)
            st.markdown("""
                <p style="font-size: 1.1rem; opacity: 0.8; line-height: 1.6;">
                Unleash the power of AI-driven analytics. <br><br>
                ✓ Real-time Data Tracking<br>
                ✓ Predictive Insights<br>
                ✓ Growth Automation
                </p>
                <br>
                <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px;">
                    <small>“The best way to predict the future is to create it.”</small>
                </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            menu = st.tabs(["🔑 Login", "📝 Create Account"])

            # --- LOGIN TAB ---
            with menu[0]:
                role = st.selectbox("I am an", ["User", "Admin"])
                user_input = st.text_input("Username / Email", placeholder="johndoe@biz.com")
                password = st.text_input("Password", type="password", placeholder="••••••••")

                if st.button("Access Dashboard"):

                    # ✅ FIX 1: lowercase role
                    role_filter = role.lower()

                    cursor.execute(
                        # ✅ FIX 2: LOWER(role)
                        "SELECT username, password, role FROM users WHERE (email=%s OR username=%s) AND LOWER(role)=%s",
                        (user_input, user_input, role_filter)
                    )
                    result = cursor.fetchone()

                    if result:
                        db_username, db_password, db_role = result
                        if isinstance(db_password, str):
                            db_password = db_password.encode()

                        if bcrypt.checkpw(password.encode(), db_password):
                            token = create_token(db_username)
                            st.session_state.logged_in = True
                            st.session_state.username = db_username

                            # ✅ FIX 3: store lowercase role
                            st.session_state.role = db_role.lower()

                            st.session_state.token = token
                            st.success(f"Welcome back, {db_username}!")

                            # ✅ FIX 4: only rerun needed
                            st.rerun()

                    else:
                        st.error("Authentication failed. Check credentials.")

            # --- SIGNUP TAB ---
            with menu[1]:
                new_user = st.text_input("Full Name")
                new_email = st.text_input("Work Email")
                new_pass = st.text_input("Create Password", type="password")
                new_role = st.radio("Account Type", ["User", "Admin"], horizontal=True)

                if st.button("Join Now"):
                    hashed_pw = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt())
                    try:
                        cursor.execute(
                            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                            (new_user, new_email, hashed_pw, new_role.lower())
                        )
                        db.commit()
                        st.balloons()
                        st.success("Account created! You can now login.")
                    except Exception as e:
                        st.error("Error creating account. Email might already exist.")

        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    login_signup_page()