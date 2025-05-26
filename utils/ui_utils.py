# common/ui_utils.py
import streamlit as st
import base64

def load_base64_image(path: str) -> str:
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/png;base64,{data}"

def show_logo(subtitle="🔐 Intelligence Portal", margin_bottom="3rem"):
    col1, col2, _ = st.columns([1, 4, 1])
    icon_src = load_base64_image("assets/mark.png")
    text_src = load_base64_image("assets/logo.png")
    with col2:
        st.markdown(f"""
        <div style='text-align: center;'>
            <div style="display: flex; align-items: center; justify-content: center; margin-bottom: {margin_bottom};">
                <img src="{icon_src}" width="60" style="margin-bottom: 4px;"/>
                <img src="{text_src}" width="250"/>
            </div>
            <h2 style='margin-top: 15px;'>{subtitle}</h2>
        </div>
        """, unsafe_allow_html=True)

def show_logo_main():
    show_logo(subtitle="💡 Intelligence Portal", margin_bottom="2rem")