"""
Supabase storage layer.
Projects table schema: id (uuid), owner (text), created_at (timestamptz), data (jsonb)
Settings table schema: key (text), value (text), updated_at (timestamptz)
Falls back to session_state if Supabase is not configured.
"""
import streamlit as st
import os, json
from datetime import datetime

def init_storage():
    if "projects" not in st.session_state:
        st.session_state.projects = _load_projects()
    if "settings" not in st.session_state:
        st.session_state.settings = _load_settings()
    if "custom_industries" not in st.session_state:
        st.session_state.custom_industries = _load_custom_industries()

# ─── Settings ─────────────────────────────────────────────────────────────────

def _settings_key():
    return "sb_settings_v1"

def _load_settings():
    defaults = {
        "hostinger_vps_ip":      "",
        "hostinger_domain":      "",
        "coolify_url":           "",
        "coolify_api_token":     "",
        "n8n_url":               "",
        "n8n_api_key":           "",
        "supabase_url":          "",
        "supabase_anon_key":     "",
        "supabase_service_key":  "",
        "anthropic_api_key":     "",
        "coderabbit_api_key":    "",
        "github_token":          "",
        "github_org":            "",
        "antigravity_api_key":   "",
        "elevenlabs_api_key":    "",
        "twilio_account_sid":    "",
        "twilio_auth_token":     "",
        "twilio_phone_number":   "",
        "slack_webhook":         "",
        "discord_webhook":       "",
    }
    try:
        client = _get_supabase()
        if client:
            resp = client.table("settings").select("value").eq(
                "key", _settings_key()
            ).maybe_single().execute()
            if resp and resp.data:
                return {**defaults, **json.loads(resp.data.get("value", "{}"))}
    except Exception:
        pass
    return defaults

def save_settings(data: dict):
    st.session_state.settings = data
    try:
        client = _get_supabase()
        if client:
            client.table("settings").upsert({
                "key": _settings_key(),
                "value": json.dumps(data)
            }).execute()
    except Exception:
        pass

# ─── Custom Industries ─────────────────────────────────────────────────────────

_CUSTOM_INDUSTRIES_KEY = "custom_industries_v1"

def _load_custom_industries() -> list:
    try:
        client = _get_supabase()
        if client:
            resp = client.table("settings").select("value").eq(
                "key", _CUSTOM_INDUSTRIES_KEY
            ).maybe_single().execute()
            if resp and resp.data:
                return json.loads(resp.data.get("value", "[]"))
    except Exception:
        pass
    return []

def save_custom_industries(industries: list):
    st.session_state.custom_industries = industries
    try:
        client = _get_supabase()
        if client:
            client.table("settings").upsert({
                "key": _CUSTOM_INDUSTRIES_KEY,
                "value": json.dumps(industries),
            }).execute()
    except Exception:
        pass

# ─── Projects ─────────────────────────────────────────────────────────────────
# Schema: id (uuid), owner (text), created_at (timestamptz), data (jsonb)
# All project fields stored inside the data jsonb column.

def _load_projects() -> list:
    try:
        client = _get_supabase()
        if client:
            owner = st.session_state.get("user", {}).get("email", "adam")
            resp = client.table("projects").select("*").eq(
                "owner", owner
            ).order("created_at", desc=True).execute()
            if resp and resp.data:
                projects = []
                for row in resp.data:
                    project = row.get("data", {}) or {}
                    project["id"] = row["id"]
                    project["owner"] = row["owner"]
                    project["created_at"] = row["created_at"]
                    projects.append(project)
                return projects
    except Exception:
        pass
    return []

def save_project(project: dict) -> dict:
    owner = st.session_state.get("user", {}).get("email", "adam")
    project_id = project.get("id")
    if not project_id:
        import uuid
        project_id = str(uuid.uuid4())
        project["id"] = project_id

    if not project.get("created_at"):
        project["created_at"] = datetime.utcnow().isoformat()
    project["updated_at"] = datetime.utcnow().isoformat()

    # Store everything in data column
    row = {
        "id": project_id,
        "owner": owner,
        "data": project,
    }

    try:
        client = _get_supabase()
        if client:
            client.table("projects").upsert(row).execute()
            st.session_state.projects = _load_projects()
            return project
    except Exception:
        pass

    # Fallback to session state
    if "projects" not in st.session_state:
        st.session_state.projects = []
    existing = [p for p in st.session_state.projects if p.get("id") == project_id]
    if existing:
        idx = st.session_state.projects.index(existing[0])
        st.session_state.projects[idx] = project
    else:
        st.session_state.projects.insert(0, project)
    return project

def get_projects() -> list:
    return st.session_state.get("projects", [])

def delete_project(project_id: str):
    try:
        client = _get_supabase()
        if client:
            client.table("projects").delete().eq("id", project_id).execute()
            st.session_state.projects = _load_projects()
            return
    except Exception:
        pass
    st.session_state.projects = [
        p for p in st.session_state.get("projects", [])
        if p.get("id") != project_id
    ]

# ─── Supabase Client ──────────────────────────────────────────────────────────

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
    except Exception:
        return None
