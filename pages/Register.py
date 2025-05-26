import streamlit as st
import streamlit_authenticator as stauth
from utils.db import get_hub_connection
from utils.common import get_hash_password
# --- Page Config ---
st.set_page_config(
    page_title="BizLink Intelligence",
    page_icon=":bulb:",
    layout="centered"
)

# --- Custom Styles ---
def inject_styles():
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"], [data-testid="stSidebar"] { display: none !important; }
            .hr { border: none; border-top: 1.5px solid #313337; margin: 2.5rem 0 2rem 0; }
            .stButton > button {
                width: 100%; height: 2.5rem; font-size: 1.08rem; border-radius: 7px;
                margin-top: 0.6rem; background: #23242a; color: #fff; border: 1.5px solid #444;
                font-weight: 500; transition: background 0.18s, border 0.18s;
            }
            .stButton > button:hover,
            .stButton > button:active,
            .stButton > button:focus {
                background: #2563eb !important; border: 1.5px solid #2563eb !important; color: #fff !important;
            }
                       
        </style>
    """, unsafe_allow_html=True)

inject_styles()


st.title("📝 Register New Account")

# 입력 필드
user_id = st.text_input("👤 Username")
password = st.text_input("🔑 Password", type="password")
password_confirm = st.text_input("🔑 Confirm Password", type="password")

col1, col2 = st.columns([1, 1])
with col1:
    register_clicked = st.button("📝 Register", use_container_width=True)
with col2:
    if st.button("🔙 Back to Login", use_container_width=True):
        st.switch_page("Home.py")

if register_clicked:
    if not user_id or not password or not password_confirm:
        st.warning("All fields are required.")
    elif password != password_confirm:
        st.error("❌ Password and Confirm Password do not match.")
    else:
        try:
            conn = get_hub_connection()  # 사용자 정의 연결 함수에서 pyodbc.connect(...) 반환
            cursor = conn.cursor()

            # 1. 이메일 존재 여부 확인
            cursor.execute("SELECT 1 FROM ibizlink.hub_users WHERE user_email = ?", (user_id,))
            row = cursor.fetchone()

            if not row:
                st.error("❌ User Email has not registered yet. Please check again.")
            else:
                cursor.execute("SELECT 1 FROM ibizlink.hub_users WHERE pw_hash is not null AND user_email = ?", (user_id,))
                exist_account_row = cursor.fetchone()

                if exist_account_row :
                    #st.error("❌ User Email has already registered. Please check again.")
                     # 2. 해시 생성 및 업데이트
                    hashed_pw = get_hash_password(password)
                    cursor.execute("""
                        UPDATE ibizlink.hub_users
                        SET pw_hash = ?
                        WHERE user_email = ?
                    """, (hashed_pw.decode(), user_id))
                    conn.commit()

                    st.success("✅ Password updated successfully. Redirecting to login...")
                    st.switch_page("Home.py")
                else:
                     # 2. 해시 생성 및 업데이트
                    hashed_pw = get_hash_password(password)
                    cursor.execute("""
                        UPDATE ibizlink.hub_users
                        SET pw_hash = ?
                        WHERE user_email = ?
                    """, (hashed_pw.decode(), user_id))
                    conn.commit()

                    st.success("✅ Password updated successfully. Redirecting to login...")
                    st.switch_page("Home.py")


        except Exception as e:
            st.error("❌ An error occurred while registering.")
            st.exception(e)
        finally:
            cursor.close()
            conn.close()