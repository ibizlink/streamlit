# ✅ common/auth_utils.py
import streamlit as st
import streamlit_authenticator as stauth
from utils.auth import get_authenticator_data
from utils.localstorage import save_to_localstorage, clear_localstorage
from streamlit_js_eval import streamlit_js_eval
import json
import time

def init_authenticator():
    if "credentials" not in st.session_state or "authenticator" not in st.session_state:
        st.session_state["credentials"] = get_authenticator_data()
        st.session_state["authenticator"] = stauth.Authenticate(
            st.session_state["credentials"],
            "ibizlinkauth_cookie", "ibizlinkauth_signature", cookie_expiry_days=1,
            preauthorized=[]
        )
        st.rerun()
    return st.session_state["authenticator"]

def check_auth_and_redirect():
    # 인증 상태가 None이면 잠시 대기 후 재확인
    for _ in range(5):
        auth_status = st.session_state.get("authentication_status")
        if auth_status is not None:
            break
        time.sleep(0.1)
    auth_status = st.session_state.get("authentication_status")
    if auth_status in [None, False]:
        st.switch_page("home.py")
    return auth_status

def load_and_sync_localstorage():
    result_json = streamlit_js_eval(
        js_expressions="""
            JSON.stringify([
                localStorage.getItem('domain_code'),
                localStorage.getItem('target_database')
            ])
        """,
        key="load_localstorage"
    )
    if result_json:
        try:
            domain_code, target_database = json.loads(result_json)
            if domain_code and domain_code != "null":
                st.session_state["domain_code"] = domain_code
            if target_database and target_database != "null":
                st.session_state["target_database"] = target_database
        except Exception as e:
            st.warning("⚠️ Failed to parse localStorage data.")
            st.exception(e)

    if all(k in st.session_state for k in ["domain_code", "target_database"]):
        js_code = f"""
            localStorage.setItem('domain_code', '{st.session_state["domain_code"]}');
            localStorage.setItem('target_database', '{st.session_state["target_database"]}');
        """
        streamlit_js_eval(js_expressions=js_code, key="save_localstorage")
