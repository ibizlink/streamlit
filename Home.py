import streamlit as st
import streamlit_authenticator as stauth
import base64
import json
from utils.localstorage import save_to_localstorage, clear_localstorage
from utils.auth import get_authenticator_data
from utils.db import fetch_domains
from streamlit_js_eval import streamlit_js_eval
from utils.auth_utils import (
    init_authenticator,
    load_and_sync_localstorage
)

# --- Page Config ---
st.set_page_config(
    page_title="BizLink Intelligence",
    page_icon=":bulb:",
    layout="centered"
)

# --- Custom Styles ---
def inject_styles():
    st.markdown("""
      
    """, unsafe_allow_html=True)

inject_styles()

# --- Utility Functions ---
def clear_auth_cookie():
    js_code = """document.cookie = "ibizlinkauth_cookie=; path=/;";"""
    streamlit_js_eval(js_expressions=js_code, key="clear_auth_cookie")

def load_base64_image(path):
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{data}"

def show_logo(subtitle="🔐 Intelligence Portal", margin_bottom="4rem"):
    col1, col2, col3 = st.columns([1, 4, 1])
    icon_src = load_base64_image("assets/mark.png")
    text_src = load_base64_image("assets/logo.png")
    with col2:
        st.markdown(
            f"""
            <div style='text-align: center;'>
                <div style="display: flex; align-items: center; justify-content: center;margin-bottom: {margin_bottom};">
                    <img src="{icon_src}" width="60" style="margin-bottom: 4px;"/>
                    <img src="{text_src}" width="250"/>
                </div>
                <h2 style='margin-top: 15px;'>{subtitle}</h2>
            </div>
            """,
            unsafe_allow_html=True
        )


def show_register():
    col1, col2 = st.columns([4, 1])  # 오른쪽 끝 정렬
    with col2:
        if st.button("📝 Register", key="register_btn"):
            st.switch_page("pages/register.py")


def get_auth_cookie_value():
    js_code = """
    (() => {
        const match = document.cookie.match(/ibizlinkauth_cookie=([^;]*)/);
        return match ? match[1] : null;
    })();
    """
    return streamlit_js_eval(js_expressions=js_code, key="get_auth_cookie_value")

def handle_logout():
    if st.session_state.get("authentication_status") is True:
        st.session_state['authenticator'].logout("main")
    st.session_state.clear()
    clear_localstorage()
    clear_auth_cookie()
    st.session_state["logout_flag"] = False
    st.stop()

def save_domain_to_localstorage(domain_code, target_database):
    js_code = f"""
        localStorage.setItem('domain_code', '{domain_code}');
        localStorage.setItem('target_database', '{target_database}');
    """
    streamlit_js_eval(js_expressions=js_code, key="save_localstorage_always")

# --- Logout Handler ---
if st.session_state.get("logout_flag"):
    handle_logout()

# --- Login Area ---
authenticator = init_authenticator()
logo_area = st.empty()
with logo_area:
    show_logo()

register_area = st.empty()
with register_area:
    show_register()
    
login_result = authenticator.login("main", key="Login", fields={
    "Username": "👤 Username",
    "Password": "🔑 Password"
})

auth_status = st.session_state.get("authentication_status")

# --- Cookie Timing Handling ---
if "just_logged_in" not in st.session_state:
    st.session_state["just_logged_in"] = False

if auth_status is True:
    if not st.session_state["just_logged_in"]:
        st.session_state["just_logged_in"] = True
    else:
        auth_cookie_value = get_auth_cookie_value()
        if auth_cookie_value is None or auth_cookie_value == "":
            st.info("Please reload this page to continue.")
            st.stop()
else:
    st.session_state["just_logged_in"] = False

if auth_status is None:
    st.info("Please enter your username and password")
    st.stop()
elif auth_status is False:
    st.error("Invalid username or password")
    st.stop()
elif auth_status is True:
    logo_area.empty()
    register_area.empty()
    # Save user info once
    if 'user_email' not in st.session_state:
        user_info = st.session_state.credentials["usernames"][st.session_state["username"]]
        st.session_state.user_email = user_info["email"]
        st.session_state.user_id = user_info["user_id"]
        st.session_state.is_admin = user_info["is_admin"]

    # Load localStorage values
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
            if domain_code not in (None, "", "null"):
                st.session_state["domain_code"] = domain_code
            if target_database not in (None, "", "null"):
                st.session_state["target_database"] = target_database
        except Exception as e:
            st.warning("⚠️ Failed to parse localStorage data.")
            st.exception(e)

    # Save session values to localStorage
    if all(k in st.session_state for k in ["domain_code", "target_database"]):
        save_domain_to_localstorage(st.session_state["domain_code"], st.session_state["target_database"])

    # Domain selection
    if "target_database" not in st.session_state:
        user_domains = fetch_domains(
            user_id=st.session_state.user_id,
            is_admin=st.session_state.is_admin
        )
        user_domains = [d for d in user_domains if d["target_database"]]
        if len(user_domains) == 0:
            st.error("No domains available for your account.")
        elif st.session_state.is_admin or len(user_domains) > 1:
            st.subheader("📂 Select your domain")
            options = [d["domain_code"] for d in user_domains]
            selected = st.selectbox("Available Domains", options)
            if st.button("Confirm and Continue"):
                chosen = user_domains[options.index(selected)]
                st.session_state.domain_code = chosen["domain_code"]
                st.session_state.target_database = chosen["target_database"]
                st.rerun()
        else:
            chosen = user_domains[0]
            st.session_state.domain_code = chosen["domain_code"]
            st.session_state.target_database = chosen["target_database"]
            st.rerun()
    else:
        # Main UI
        col1, col2 = st.columns([7, 2])
        with col2:
            if st.button("🚪 Logout", key="logout_btn"):
                st.session_state["logout_flag"] = True
                st.rerun()

        show_logo(subtitle="💡 Intelligence Portal", margin_bottom="2rem")
        st.markdown(f"""
            <div style='text-align: center;'>
                <div style='font-size: 16px; color: grey; margin-bottom: 20px;'>
                    Account: <code>{st.session_state.user_email}</code> &nbsp;|&nbsp;
                    Domain: <b>{st.session_state.domain_code}</b> &nbsp;
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

        # Navigation Buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Dashboard", key="upload_file_btn", use_container_width=True):
                st.switch_page("pages/dashboard.py")
        with col2:
            if st.button("Go", key="select_ours_btn", use_container_width=True):
                st.switch_page("pages/reports.py")
        with col3:
            if st.button("Go", key="write_url_btn", use_container_width=True):
                st.switch_page("pages/settings.py")