"""
Supabase storage layer.
Falls back to session_state if Supabase is not configured (safe for first run).
"""
import streamlit as st
import os, json
from datetime import datetime

def init_storage():
    if "projects" not in st.session_state:
        st.session_state.projects = _load_projects()
    if "settings" not in st.session_state:
        st.session_state.settings = _load_settings()

# ─── Settings ───────────────────────────────────────────────────────────────

def _settings_key():
    return "sb_settings_v1"

def _load_settings():
    """Load from Supabase if available, else return defaults."""
    defaults = {
        # Hosting
        "hostinger_vps_ip": "",
        "hostinger_domain": "",
        # Coolify
        "coolify_url": "",
        "coolify_api_token": "",
        # n8n
        "n8n_url": "",
        "n8n_api_key": "",
        # Supabase
        "supabase_url": "",
        "supabase_anon_key": "",
        "supabase_service_key": "",
        # Claude / Anthropic
        "anthropic_api_key": "",
        # Code Rabbit
        "coderabbit_api_key": "",
        # GitHub
        "github_token": "",
        "github_org": "",
        # Antigravity
        "antigravity_api_key": "",
        # ElevenLabs (voice agents)
        "elevenlabs_api_key": "",
        # Twilio (SMS/voice)
        "twilio_account_sid": "",
        "twilio_auth_token": "",
        "twilio_phone_number": "",
        # Notifications
        "slack_webhook": "",
        "discord_webhook": "",
    }
    try:
        client = _get_supabase()
        if client:
            resp = client.table("settings").select("*").eq("key", _settings_key()).maybe_single().execute()
            if resp.data:
                return {**defaults, **json.loads(resp.data.get("value", "{}"))}
    except:
        pass
    return defaults

def save_settings(data: dict):
    st.session_state.settings = data
    try:
        client = _get_supabase()
        if client:
            client.table("settings").upsert({"key": _settings_key(), "value": json.dumps(data)}).execute()
    except:
        pass  # Falls back to session state

# ─── Projects ───────────────────────────────────────────────────────────────

def _load_projects():
    try:
        client = _get_supabase()
        if client:
            resp = client.table("projects").select("*").order("created_at", desc=True).execute()
            return resp.data or []
    except:
        pass
    return []

def save_project(project: dict):
    project["created_at"] = datetime.utcnow().isoformat()
    project["owner"] = st.session_state.get("user", {}).get("email", "adam")
    try:
        client = _get_supabase()
        if client:
            resp = client.table("projects").upsert(project).execute()
            st.session_state.projects = _load_projects()
            return resp.data[0] if resp.data else project
    except:
        pass
    if "projects" not in st.session_state:
        st.session_state.projects = []
    st.session_state.projects.insert(0, project)
    return project

def get_projects():
    return st.session_state.get("projects", [])

def delete_project(project_id: str):
    try:
        client = _get_supabase()
        if client:
            client.table("projects").delete().eq("id", project_id).execute()
    except:
        pass
    st.session_state.projects = [p for p in st.session_state.get("projects", []) if p.get("id") != project_id]

# ─── Supabase Client ─────────────────────────────────────────────────────────

def _get_supabase():
    def _s(key):
        try:
            return st.secrets.get(key, os.environ.get(key, ""))
        except Exception:
            return os.environ.get(key, "")

    url = _s("SUPABASE_URL") or st.session_state.get("settings", {}).get("supabase_url")
    key = _s("SUPABASE_SERVICE_KEY") or st.session_state.get("settings", {}).get("supabase_service_key")
    if not url or not key:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except:
        return None
