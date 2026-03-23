import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from sklearn.linear_model import LinearRegression
from db import get_connection
from admin_dashboard import admin_dashboard
import bcrypt


# Helper function for "K" formatting
def format_k(value):
    return f"₹{value / 1000:.2f}K"


def get_data():
    if "data" not in st.session_state:
        st.session_state.data = pd.DataFrame(
            columns=["Date", "Product", "Sales", "Expenses", "Quantity"]
        )
    return st.session_state.data


def dashboard_page():
    df = get_data()

    # --- CSS: FIXED SIDEBAR & UI ---
    st.markdown("""
        <style>
        [data-testid="stSidebar"] { background-color: #1a1c2c !important; }
        [data-testid="stSidebar"] * { color: white !important; }
        .kpi-card {
            background: white; padding: 20px; border-radius: 15px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1); border-top: 5px solid #6c63ff;
            text-align: center; margin-bottom: 20px;
        }
        .kpi-title { font-size: 14px; color: #888; font-weight: 600; text-transform: uppercase; }
        .kpi-value { font-size: 24px; color: #333; font-weight: 800; }
        </style>
    """, unsafe_allow_html=True)

    with st.sidebar:
        st.markdown("## 🚀 SmartBiz AI")
        st.write(f"Welcome, **{st.session_state.get('username', 'User')}**")
        st.divider()
        menu = st.radio("Select a Page",
                        ["Dashboard", "Add Transaction", "Upload File", "AI Prediction", "Profile", "Logout"])

    # ================= DASHBOARD LOGIC =================
    if menu == "Dashboard":
        st.title("📊 Monthly Business Intelligence")

        if df.empty:
            st.info("Your dashboard is empty. Please add data or upload a file.")
        else:
            # Data Preparation
            df["Date"] = pd.to_datetime(df["Date"])
            df["Profit"] = df["Sales"] - df["Expenses"]
            df['Month_Year'] = df['Date'].dt.strftime('%B %Y')

            # --- 1. MONTHLY FILTER ---
            available_months = df['Month_Year'].unique()
            selected_month = st.selectbox("📅 Select Month to Analyze", available_months)

            # Filtered Data for the selected month
            m_df = df[df['Month_Year'] == selected_month].sort_values("Date")

            # --- 2. KPI METRICS (Monthly) ---
            ts, te, tp = m_df["Sales"].sum(), m_df["Expenses"].sum(), m_df["Profit"].sum()

            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(
                    f'<div class="kpi-card"><div class="kpi-title">Monthly Sales</div><div class="kpi-value">{format_k(ts)}</div></div>',
                    unsafe_allow_html=True)
            with c2:
                st.markdown(
                    f'<div class="kpi-card" style="border-top-color:#ff4b4b"><div class="kpi-title">Monthly Expenses</div><div class="kpi-value">{format_k(te)}</div></div>',
                    unsafe_allow_html=True)
            with c3:
                profit_color = "#00c853" if tp >= 0 else "#ff4b4b"
                st.markdown(
                    f'<div class="kpi-card" style="border-top-color:{profit_color}"><div class="kpi-title">Monthly Profit</div><div class="kpi-value">{format_k(tp)}</div></div>',
                    unsafe_allow_html=True)

            # --- 3. DAILY PROFIT/LOSS GRAPH ---
            st.subheader(f"📈 Daily Profit Trend - {selected_month}")
            daily_data = m_df.groupby("Date")["Profit"].sum().reset_index()

            fig_daily = px.area(daily_data, x="Date", y="Profit",
                                title="Daily Profitability Path",
                                line_shape="spline",
                                color_discrete_sequence=["#6c63ff"])
            fig_daily.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break-even point")
            st.plotly_chart(fig_daily, use_container_width=True)

            # --- 4. PRODUCT PROFITABILITY & RATIOS ---
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("📦 Most Profitable Products")
                product_profit = m_df.groupby("Product")["Profit"].sum().sort_values(ascending=False).reset_index()
                fig_prod = px.bar(product_profit, x="Profit", y="Product",
                                  orientation='h', color="Profit",
                                  color_continuous_scale="RdYlGn",
                                  title="Profit by Product")
                st.plotly_chart(fig_prod, use_container_width=True)

            with col2:
                st.subheader("⚖️ Expense vs Revenue Ratio")
                fig_pie = go.Figure(data=[go.Pie(labels=['Revenue', 'Expenses'],
                                                 values=[ts, te],
                                                 hole=.5,
                                                 marker_colors=['#00c853', '#ff4b4b'])])
                st.plotly_chart(fig_pie, use_container_width=True)

            st.markdown("### 📝 Monthly Transaction Details")
            st.dataframe(m_df[["Date", "Product", "Sales", "Expenses", "Profit", "Quantity"]].sort_values("Date",
                                                                                                          ascending=False),
                         use_container_width=True)

    # --- REST OF THE FUNCTIONS (KEEP YOUR ORIGINAL CODE FOR THESE) ---
    elif menu == "Add Transaction":
        st.title("➕ Manual Data Entry")
        with st.form("input_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            d = col1.date_input("Transaction Date")
            p = col2.text_input("Product/Service Name")
            s = col1.number_input("Sales Revenue (₹)", min_value=0.0)
            e = col2.number_input("Cost/Expense (₹)", min_value=0.0)
            q = st.number_input("Quantity Sold", min_value=1)

            if st.form_submit_button("Submit Transaction"):
                new_entry = pd.DataFrame([{"Date": d, "Product": p, "Sales": s, "Expenses": e, "Quantity": q}])
                st.session_state.data = pd.concat([st.session_state.data, new_entry], ignore_index=True)
                st.success("Data successfully saved!")

    elif menu == "Upload File":
        st.title("📂 CSV Data Import")
        file = st.file_uploader("Choose File", type="csv")
        if file:
            up_df = pd.read_csv(file)
            st.session_state.data = pd.concat([st.session_state.data, up_df], ignore_index=True)
            st.success(f"Successfully imported {len(up_df)} rows!")

        # ================= AI PREDICTION LOGIC =================

    elif menu == "AI Prediction":

        st.title("🔮 AI Profit Predictor & Product Forecast")

        if len(df) >= 5:  # AI works better with more data

            st.markdown("### 🔍 Product-Wise Future Profit Potential")

            # 1. AI Logic for Product Analysis

            unique_products = df["Product"].unique()

            predictions = []

            for prod in unique_products:

                prod_df = df[df["Product"] == prod]

                if len(prod_df) >= 2:  # At least 2 records per product to predict

                    X_prod = prod_df[["Sales", "Expenses", "Quantity"]]

                    y_prod = prod_df["Sales"] - prod_df["Expenses"]

                    model = LinearRegression().fit(X_prod, y_prod)

                    # Predict based on that product's average performance

                    avg_s = prod_df["Sales"].mean()

                    avg_e = prod_df["Expenses"].mean()

                    avg_q = prod_df["Quantity"].mean()

                    pred_val = model.predict([[avg_s, avg_e, avg_q]])[0]

                    predictions.append({"Product": prod, "Predicted_Profit": pred_val})

            if predictions:
                pred_df = pd.DataFrame(predictions).sort_values(by="Predicted_Profit", ascending=False)

                # 2. Show Best Product Recommendation

                best_prod = pred_df.iloc[0]["Product"]

                best_val = pred_df.iloc[0]["Predicted_Profit"]

                st.success(
                    f"🌟 **AI Recommendation:** Future mein **{best_prod}** aapko sabse zyada profit (Approx {format_k(best_val)}) de sakta hai.")

                # 3. AI Prediction Graph

                st.markdown("### 📊 Predicted Profit Potential by Product")

                fig_ai_prod = px.bar(pred_df, x="Product", y="Predicted_Profit",

                                     color="Predicted_Profit",

                                     color_continuous_scale="Viridis",

                                     text_auto='.2s',

                                     title="AI Forecast: Which Product will earn more?")

                fig_ai_prod.update_layout(template="plotly_white")

                st.plotly_chart(fig_ai_prod, use_container_width=True)

            st.divider()

            # --- Individual Prediction Tool ---

            st.markdown("### 🧮 Manual Scenario Testing")

            col_in1, col_in2, col_in3 = st.columns(3)

            ps = col_in1.number_input("Sales Prediction (₹)", min_value=0.0, value=float(df["Sales"].mean()))

            pe = col_in2.number_input("Expenses Prediction (₹)", min_value=0.0, value=float(df["Expenses"].mean()))

            pq = col_in3.number_input("Quantity Prediction", min_value=1, value=int(df["Quantity"].mean()))

            if st.button("Run AI Scenario"):
                X = df[["Sales", "Expenses", "Quantity"]]

                y = df["Sales"] - df["Expenses"]

                reg = LinearRegression().fit(X, y)

                res = reg.predict([[ps, pe, pq]])[0]

                st.metric("Expected Profit for this Scenario", f"₹{res:,.2f}")

                st.balloons()

        else:

            st.warning("⚠️ AI ko analyze karne ke liye kam se kam 5 transactions ki zaroorat hai.")
    elif menu == "Profile":
        st.title("👤 My Account")
        st.info(f"Currently logged in as: {st.session_state.username}")


        db = get_connection()
        cursor = db.cursor()

        # Fetch current user details
        cursor.execute("SELECT username, email FROM users WHERE username=%s", (st.session_state.username,))
        user_data = cursor.fetchone()

        if user_data:
            current_username, current_email = user_data

            # Editable form
            with st.form("edit_profile_form"):
                new_username = st.text_input("Username", value=current_username)
                new_email = st.text_input("Email", value=current_email)
                new_password = st.text_input("New Password", type="password",
                                             placeholder="Leave blank to keep current password")

                if st.form_submit_button("Save Changes"):
                    try:
                        # Update username and email
                        cursor.execute(
                            "UPDATE users SET username=%s, email=%s WHERE username=%s",
                            (new_username, new_email, current_username)
                        )

                        # Update password if provided
                        if new_password:
                            hashed_pw = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
                            cursor.execute(
                                "UPDATE users SET password=%s WHERE username=%s",
                                (hashed_pw, new_username)
                            )

                        db.commit()

                        # Update session state
                        st.session_state.username = new_username
                        st.success("Profile updated successfully!")

                    except Exception as e:
                        st.error("Error updating profile. Please try again.")
        else:
            st.error("Unable to fetch user details.")
    elif menu == "Logout":
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()


if __name__ == "__main__":
    dashboard_page()