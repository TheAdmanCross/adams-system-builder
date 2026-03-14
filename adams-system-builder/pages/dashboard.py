import streamlit as st
import os
from utils.auth import init_auth, render_login_page, is_authenticated, get_user
from utils.storage import init_storage
from utils.styles import inject_styles

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Adam's System Builder",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Init ─────────────────────────────────────────────────────────────────────
init_auth()
inject_styles()

# ─── Auth Gate ────────────────────────────────────────────────────────────────
if not is_authenticated():
    render_login_page()
    st.stop()

# ─── Authenticated App ────────────────────────────────────────────────────────
user = get_user()
init_storage()

NAV_OPTIONS = [
    "🏠  Dashboard",
    "➕  New Customer",
    "📋  Questionnaire",
    "🤖  Agent Builder",
    "🚀  Generate & Deploy",
    "⚙️  Settings",
]

# Sidebar
with st.sidebar:
    st.markdown(f"""
    <div class="sidebar-user">
        <img src="{user.get('picture','')}" class="avatar" onerror="this.style.display='none'"/>
        <div>
            <div class="user-name">{user.get('name','Adam')}</div>
            <div class="user-email">{user.get('email','')}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    page = st.radio(
        "",
        NAV_OPTIONS,
        label_visibility="collapsed",
        key="nav_page",
    )

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    st.markdown("""
    <div class="sidebar-footer">
        <span class="status-dot green"></span> System Builder v2.0<br/>
        <small>Hostinger · Coolify · n8n · Supabase</small>
    </div>
    """, unsafe_allow_html=True)

# ─── Page Router ──────────────────────────────────────────────────────────────
clean_page = page.split("  ", 1)[-1]

if clean_page == "Dashboard":
    from pages import dashboard; dashboard.render()
elif clean_page == "New Customer":
    from pages import intake; intake.render()
elif clean_page == "Questionnaire":
    from pages import questionnaire; questionnaire.render()
elif clean_page == "Agent Builder":
    from pages import agent_builder; agent_builder.render()
elif clean_page == "Generate & Deploy":
    from pages import generate; generate.render()
elif clean_page == "Settings":
    from pages import settings; settings.render()
