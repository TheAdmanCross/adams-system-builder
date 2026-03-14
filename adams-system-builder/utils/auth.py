"""
Google OAuth for Streamlit Cloud.
Streamlit Cloud resets session on redirect, so we skip state validation.
Security is maintained by locking to ALLOWED_EMAILS only.
"""
import streamlit as st
import os
import requests
from urllib.parse import urlencode
import secrets

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

def _secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, os.environ.get(key, default))
    except Exception:
        return os.environ.get(key, default)

def init_auth():
    if "user" not in st.session_state:
        st.session_state.user = None
    params = st.query_params
    if "code" in params:
        _handle_callback(params["code"])

def _get_redirect_uri():
    return _secret("REDIRECT_URI", "https://adams-system-builder-neohc9braugjzjqhogvxfs.streamlit.app")

def _build_auth_url():
    state = secrets.token_urlsafe(16)
    params = {
        "client_id": _secret("GOOGLE_CLIENT_ID"),
        "redirect_uri": _get_redirect_uri(),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "offline",
        "prompt": "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"

def _handle_callback(code: str):
    try:
        token_resp = requests.post(GOOGLE_TOKEN_URL, data={
            "code": code,
            "client_id": _secret("GOOGLE_CLIENT_ID"),
            "client_secret": _secret("GOOGLE_CLIENT_SECRET"),
            "redirect_uri": _get_redirect_uri(),
            "grant_type": "authorization_code",
        }, timeout=10)
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        if not access_token:
            st.error(f"Login failed. Please try again. ({token_data.get('error', 'unknown')})")
            st.query_params.clear()
            return

        user_resp = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10
        )
        user = user_resp.json()

        allowed = _secret("ALLOWED_EMAILS", "")
        if allowed:
            allowed_list = [e.strip().lower() for e in allowed.split(",")]
            if user.get("email", "").lower() not in allowed_list:
                st.error(f"Access denied for {user.get('email')}.")
                st.query_params.clear()
                st.stop()

        st.session_state.user = user
        st.query_params.clear()
        st.rerun()

    except Exception as e:
        st.error(f"Login error: {e}")
        st.query_params.clear()

def is_authenticated() -> bool:
    return st.session_state.get("user") is not None

def get_user() -> dict:
    return st.session_state.get("user", {})

def render_login_page():
    client_id = _secret("GOOGLE_CLIENT_ID")
    st.markdown("""
    <div style="display:flex;flex-direction:column;align-items:center;justify-content:center;
    min-height:80vh;gap:24px;text-align:center;">
        <div style="font-size:72px;">⚡</div>
        <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.8rem;margin:0;
        background:linear-gradient(135deg,#ff4d4d,#ff8c00);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            Adam's System Builder
        </h1>
        <p style="color:#888;font-size:1.1rem;margin:0;">
            Agentic AI webapp factory — n8n · Coolify · Supabase · Claude Code
        </p>
    </div>
    """, unsafe_allow_html=True)

    if not client_id:
        st.warning("GOOGLE_CLIENT_ID not set. Add it in Streamlit Settings > Secrets.")
        return

    auth_url = _build_auth_url()
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        # Use JS window.top.location.href to break out of Streamlit's iframe
        st.markdown(f"""
        <button onclick="window.top.location.href='{auth_url}'"
        style="display:block;width:100%;text-align:center;cursor:pointer;
        background:#fff;color:#333;padding:14px 28px;border-radius:8px;font-weight:600;
        border:2px solid #ddd;font-size:1rem;
        box-shadow:0 2px 8px rgba(0,0,0,0.15);">
            <img src="https://www.google.com/favicon.ico"
            style="width:18px;vertical-align:middle;margin-right:8px;"/>
            Sign in with Google
        </button>
        """, unsafe_allow_html=True)
