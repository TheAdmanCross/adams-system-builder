"""
Google OAuth for Streamlit Cloud.
Session is persisted in an encrypted browser cookie so page refreshes
don't log the user out. Cookie expires after 7 days.
"""
import streamlit as st
import os
import requests
import json
import base64
import hashlib
from urllib.parse import urlencode
from datetime import datetime, timedelta
import secrets

GOOGLE_AUTH_URL     = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL    = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

PRODUCTION_URL = "https://adams-system-builder-neohc9braugjzjqhogvxfs.streamlit.app"
COOKIE_NAME    = "asb_session_v1"


def _secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, os.environ.get(key, default))
    except Exception:
        return os.environ.get(key, default)


# ─── Cookie helpers ───────────────────────────────────────────────────────────

@st.cache_resource
def _cookie_controller():
    from streamlit_cookies_controller import CookieController
    return CookieController()


def _fernet():
    from cryptography.fernet import Fernet
    secret = _secret("GOOGLE_CLIENT_SECRET", "adam-system-builder-fallback-key!")
    key = base64.urlsafe_b64encode(hashlib.sha256(secret.encode()).digest())
    return Fernet(key)


def _save_cookie(user: dict):
    try:
        token = _fernet().encrypt(json.dumps(user).encode()).decode()
        _cookie_controller().set(COOKIE_NAME, token)
    except Exception:
        pass


def _load_cookie() -> dict:
    try:
        token = _cookie_controller().get(COOKIE_NAME)
        if token:
            return json.loads(_fernet().decrypt(token.encode()).decode())
    except Exception:
        pass
    return None


def _clear_cookie():
    try:
        _cookie_controller().remove(COOKIE_NAME)
    except Exception:
        pass


# ─── Auth core ────────────────────────────────────────────────────────────────

def init_auth():
    if "user" not in st.session_state:
        st.session_state.user = None

    # Restore session from cookie on page refresh
    if not st.session_state.user:
        saved = _load_cookie()
        if saved:
            st.session_state.user = saved
            return

    # Handle OAuth callback
    params = st.query_params
    if "code" in params:
        _handle_callback(params["code"])


def _get_redirect_uri():
    return _secret("REDIRECT_URI", PRODUCTION_URL)


def _build_auth_url():
    params = {
        "client_id":     _secret("GOOGLE_CLIENT_ID"),
        "redirect_uri":  _get_redirect_uri(),
        "response_type": "code",
        "scope":         "openid email profile",
        "state":         secrets.token_urlsafe(16),
        "access_type":   "offline",
        "prompt":        "select_account",
    }
    return f"{GOOGLE_AUTH_URL}?{urlencode(params)}"


def _handle_callback(code: str):
    try:
        token_resp = requests.post(GOOGLE_TOKEN_URL, data={
            "code":          code,
            "client_id":     _secret("GOOGLE_CLIENT_ID"),
            "client_secret": _secret("GOOGLE_CLIENT_SECRET"),
            "redirect_uri":  _get_redirect_uri(),
            "grant_type":    "authorization_code",
        }, timeout=10)
        token_data = token_resp.json()
        access_token = token_data.get("access_token")

        if not access_token:
            st.error(f"Login failed: {token_data.get('error', 'unknown')}. Please try again.")
            st.query_params.clear()
            return

        user_resp = requests.get(
            GOOGLE_USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=10,
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
        _save_cookie(user)
        st.query_params.clear()
        st.rerun()

    except Exception as e:
        st.error(f"Login error: {e}")
        st.query_params.clear()


def is_authenticated() -> bool:
    return st.session_state.get("user") is not None


def get_user() -> dict:
    return st.session_state.get("user", {})


def logout():
    _clear_cookie()
    for key in list(st.session_state.keys()):
        del st.session_state[key]


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
        st.warning("GOOGLE_CLIENT_ID not configured. Add it in Streamlit Settings → Secrets.")
        return

    auth_url = _build_auth_url()
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        st.link_button("🔑  Sign in with Google", auth_url, use_container_width=True)
