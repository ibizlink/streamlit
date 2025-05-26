import json
import streamlit as st
from streamlit_js_eval import streamlit_js_eval

def save_to_localstorage():
    """
    Save relevant session state variables to browser localStorage via JS.
    This must be called inside a Streamlit-rendered context (e.g., st.empty()).
    """
    if all(k in st.session_state for k in ["domain_code", "target_database"]):
        with st.empty():
            js_code = f"""
                localStorage.setItem('domain_code', '{st.session_state["domain_code"]}');
                localStorage.setItem('target_database', '{st.session_state["target_database"]}');
            """
            streamlit_js_eval(js_expressions=js_code, key="save_to_local")

def restore_from_localstorage():
    """
    Restore session state from browser localStorage values (if available).
    Should be called at the top of the page to rehydrate session state.
    """
    result_json = streamlit_js_eval(
        js_expressions="""
            JSON.stringify([
                localStorage.getItem('user_email'),
                localStorage.getItem('domain_code'),
                localStorage.getItem('target_database'),
                localStorage.getItem('username')
            ])
        """,
        key="restore_localstorage"
    )

    if result_json:
        try:
            user_email, domain_code, target_database, username = json.loads(result_json)

            if user_email not in (None, "", "null"):
                st.session_state["user_email"] = user_email
            if domain_code not in (None, "", "null"):
                st.session_state["domain_code"] = domain_code
            if target_database not in (None, "", "null"):
                st.session_state["target_database"] = target_database
            if username not in (None, "", "null"):
                st.session_state["username"] = username
        except Exception as e:
            st.warning("⚠️ Failed to restore session state from localStorage.")
            st.exception(e)



def clear_localstorage():
    """
    Clear relevant keys from browser localStorage.
    Should be called just before or during logout.
    """
    with st.empty():
        streamlit_js_eval(
            js_expressions="""
                localStorage.removeItem('user_email');
                localStorage.removeItem('domain_code');
                localStorage.removeItem('target_database');
                localStorage.removeItem('username');
            """,
            key="clear_localstorage"
        )
