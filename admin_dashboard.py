import streamlit as st
import pandas as pd
import plotly.express as px
from db import get_connection
import bcrypt

st.set_page_config(page_title="Admin Dashboard", page_icon="🛠", layout="wide")


def admin_dashboard():

    # --- STYLING ---
    st.markdown("""
    <style>

    .block-container {
        padding: 1rem 2rem !important;
        max-width: 100% !important;
    }

    .stApp {
        background: #f4f6fb;
    }

    .metric-card {
        background: white;
        padding: 25px;
        border-radius: 18px;
        box-shadow: 0 6px 18px rgba(0,0,0,0.08);
        border-left: 6px solid #6c63ff;
        text-align: center;
        transition: 0.3s;
    }

    .metric-card:hover {
        transform: translateY(-6px);
    }

    .metric-value {
        font-size: 36px;
        font-weight: bold;
        color: #1e1e2f;
    }

    .metric-label {
        font-size: 13px;
        color: #888;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .section-header {
        font-weight: 700;
        font-size: 20px;
        margin-top: 40px;
        border-left: 5px solid #6c63ff;
        padding-left: 10px;
    }

    </style>
    """, unsafe_allow_html=True)

    # --- HEADER ---
    st.title("🛠 Admin Dashboard")
    st.caption("Monitor users, analytics & system health")

    db = get_connection()
    cursor = db.cursor()

    # --- METRICS ---
    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
    total_admins = cursor.fetchone()[0]

    active_users = total_users  # demo

    col1, col2, col3 = st.columns(3)

    col1.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Total Users</div>
        <div class="metric-value">{total_users}</div>
    </div>
    """, unsafe_allow_html=True)

    col2.markdown(f"""
    <div class="metric-card" style="border-left-color:#00b894;">
        <div class="metric-label">Admins</div>
        <div class="metric-value">{total_admins}</div>
    </div>
    """, unsafe_allow_html=True)

    col3.markdown(f"""
    <div class="metric-card" style="border-left-color:#ff7675;">
        <div class="metric-label">Active Users</div>
        <div class="metric-value">{active_users}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- USER DATA ---
    st.markdown('<p class="section-header">👥 User Directory</p>', unsafe_allow_html=True)

    cursor.execute("SELECT id, username, email, role FROM users")
    users = cursor.fetchall()
    df = pd.DataFrame(users, columns=["ID", "Username", "Email", "Role"])

    st.dataframe(df, use_container_width=True, hide_index=True)

    # --- CHARTS SECTION ---
    st.markdown('<p class="section-header">📊 Analytics</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    # --- ROLE BAR CHART ---
    role_count = df["Role"].value_counts().reset_index()
    role_count.columns = ["Role", "Count"]

    fig_bar = px.bar(
        role_count,
        x="Role",
        y="Count",
        text="Count",
        title="Users by Role"
    )
    c1.plotly_chart(fig_bar, use_container_width=True)

    # --- PIE CHART ---
    fig_pie = px.pie(
        role_count,
        values="Count",
        names="Role",
        hole=0.5,
        title="Role Distribution"
    )
    c2.plotly_chart(fig_pie, use_container_width=True)

    # --- USER GROWTH (DUMMY DATA) ---
    st.markdown('<p class="section-header">📈 User Growth</p>', unsafe_allow_html=True)

    # Dummy data (baad me DB se la sakte ho)
    growth_data = pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "Users": [5, 12, 20, 35, 50, total_users]
    })

    fig_line = px.line(
        growth_data,
        x="Month",
        y="Users",
        markers=True,
        title="User Growth Over Time"
    )
    st.plotly_chart(fig_line, use_container_width=True)

    # --- PASSWORD RESET ---
    st.markdown('<p class="section-header">🔐 Security</p>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])

    with c1:
        uid = st.number_input("User ID", min_value=1)

    with c2:
        new_pass = st.text_input("New Password", type="password")

    with c3:
        st.write("")
        st.write("")
        if st.button("Update Password"):
            if new_pass:
                hashed = bcrypt.hashpw(new_pass.encode(), bcrypt.gensalt())
                cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed, uid))
                db.commit()
                st.success("Password updated")
            else:
                st.warning("Enter password")

    st.markdown("---")
    st.caption("Admin Panel • v4.0 🚀")


if __name__ == "__main__":
    admin_dashboard()