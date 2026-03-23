import streamlit as st
from auth import login_signup_page
from dashboard import dashboard_page
from admin_dashboard import admin_dashboard

st.set_page_config(page_title="Auth System", page_icon="🔐")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.dashboard_data = None
    st.session_state.role = None
    st.session_state.username = None
cddccd
if st.session_state.logged_in:
    if st.session_state.role and st.session_state.role.lower() == "admin":
        admin_dashboard()
    else:
        dashboard_page()
else:
    login_signup_page()