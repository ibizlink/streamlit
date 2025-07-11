import streamlit as st
from utils.auth_utils import (
    init_authenticator,
    check_auth_and_redirect,
    load_and_sync_localstorage
)
st.set_page_config(page_title="📊 Dashboard")



st.markdown("""
  <style>
        [data-testid="stSidebarNav"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)


# --- 인증 및 초기화 ---
init_authenticator()
check_auth_and_redirect()
load_and_sync_localstorage()

# --- UI ---
st.title("📊 Dashboard")
st.write(f"Welcome, {st.session_state.get('user_email', '')}!")

st.markdown(f"""
<div style='font-size: 16px; color: grey; margin-bottom: 20px;'>
    Domain: <b>{st.session_state.get('domain_code')}</b> |
    Database: <code>{st.session_state.get('target_database')}</code> |
    Admin: <b>{'Yes' if st.session_state.get('is_admin', False) else 'No'}</b>
</div>
""", unsafe_allow_html=True)



# 2. 내가 원하는 사이드바 직접 만들기
with st.sidebar:
    st.image("assets/logo.png", width=200)
    st.markdown("### 내 커스텀 메뉴")
    if st.button("Dashboard", key="sidebar_dashboard"):
        st.switch_page("pages/dashboard.py")
    if st.button("리포트", key="sidebar_reports"):
        st.switch_page("pages/reports.py")
    if st.button("설정", key="sidebar_settings"):
        st.switch_page("pages/settings.py")
    st.markdown("---")
    if st.button("로그아웃", key="sidebar_logout"):
        st.session_state["logout_flag"] = True
        st.rerun()