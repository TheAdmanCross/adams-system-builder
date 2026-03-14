"""
Google OAuth for Streamlit Cloud.
Session token is stored in Supabase and kept in the URL query param (?s=TOKEN)
so page refreshes restore the session without re-login.
No extra packages required beyond the existing stack.
"""
import streamlit as st
import os
import requests
import json
import secrets
from urllib.parse import urlencode

GOOGLE_AUTH_URL     = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL    = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"

PRODUCTION_URL = "https://adams-system-builder-neohc9braugjzjqhogvxfs.streamlit.app"
SESSION_PREFIX = "session:"


def _secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, os.environ.get(key, default))
    except Exception:
        return os.environ.get(key, default)


# ─── Supabase session store ───────────────────────────────────────────────────

def _get_supabase():
    def _s(key):
        try:
            return st.secrets.get(key, os.environ.get(key, ""))
        except Exception:
            return os.environ.get(key, "")
    url = _s("SUPABASE_URL")
    key = _s("SUPABASE_SERVICE_KEY")
    if not url or not key:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception:
        return None


def _save_session(token: str, user: dict):
    """Save session token → user data in Supabase settings table."""
    try:
        client = _get_supabase()
        if client:
            client.table("settings").upsert({
                "key": f"{SESSION_PREFIX}{token}",
                "value": json.dumps(user),
            }).execute()
    except Exception:
        pass


def _load_session(token: str) -> dict:
    """Load user data from Supabase by session token."""
    try:
        client = _get_supabase()
        if client:
            resp = client.table("settings").select("value").eq(
                "key", f"{SESSION_PREFIX}{token}"
            ).maybe_single().execute()
            if resp and resp.data:
                return json.loads(resp.data["value"])
    except Exception:
        pass
    return None


def _delete_session(token: str):
    """Remove session token from Supabase on logout."""
    try:
        client = _get_supabase()
        if client:
            client.table("settings").delete().eq(
                "key", f"{SESSION_PREFIX}{token}"
            ).execute()
    except Exception:
        pass


# ─── Auth core ────────────────────────────────────────────────────────────────

def init_auth():
    if "user" not in st.session_state:
        st.session_state.user = None

    params = st.query_params

    # Handle OAuth callback
    if "code" in params:
        _handle_callback(params["code"])
        return

    # Restore session from URL token on refresh
    if not st.session_state.user and "s" in params:
        token = params["s"]
        user = _load_session(token)
        if user:
            st.session_state.user = user
            st.session_state.session_token = token


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

        # Generate session token and persist to Supabase
        session_token = secrets.token_urlsafe(32)
        _save_session(session_token, user)

        st.session_state.user = user
        st.session_state.session_token = session_token

        # Set token in URL — survives page refresh
        st.query_params.clear()
        st.query_params["s"] = session_token
        st.rerun()

    except Exception as e:
        st.error(f"Login error: {e}")
        st.query_params.clear()


def is_authenticated() -> bool:
    return st.session_state.get("user") is not None


def get_user() -> dict:
    return st.session_state.get("user", {})


def logout():
    """Clear session from Supabase, URL, and session state."""
    token = st.session_state.get("session_token")
    if token:
        _delete_session(token)
    st.query_params.clear()
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
