import streamlit as st
 
def inject_styles():
    st.markdown("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
    .stApp { background: #0a0a0f !important; }
    * { font-family: 'Space Grotesk', sans-serif !important; }
    h1, h2, h3 { color: #fff !important; }
    [data-testid="stSidebar"] { background: #0f0f1a !important; }
    .stButton button { background: #1a1a2e !important; color: #fff !important; border: 1px solid #2a2a40 !important; border-radius: 8px !important; }
    .avatar { width: 42px; height: 42px; border-radius: 50%; border: 2px solid #ff4d4d; }
    .user-name { color: #fff; font-weight: 600; }
    .user-email { color: #666; font-size: 0.75rem; }
    .sidebar-user { display: flex; align-items: center; gap: 12px; padding: 16px 0; }
    .sidebar-footer { color: #555; font-size: 0.75rem; padding-top: 8px; }
    .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
    .status-dot.green { background: #00ff88; }
    hr { border-color: #1e1e30 !important; }
    </style>
    """, unsafe_allow_html=True)
