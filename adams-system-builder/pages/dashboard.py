import streamlit as st
from utils.storage import get_projects
from datetime import datetime

def render():
    st.markdown("## ⚡ Dashboard")

    projects = get_projects()
    active = [p for p in projects if p.get("status") == "active"]
    deployed = [p for p in projects if p.get("status") == "deployed"]

    # ─── Metrics Row ─────────────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(projects)}</div>
            <div class="metric-label">Total Projects</div>
            <div class="metric-delta up">↑ All time</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(active)}</div>
            <div class="metric-label">In Progress</div>
            <div class="metric-delta amber">⏳ Building</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(deployed)}</div>
            <div class="metric-label">Deployed Live</div>
            <div class="metric-delta up">✅ On Hostinger</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{len(projects) * 5}+</div>
            <div class="metric-label">Agents Built</div>
            <div class="metric-delta up">↑ Autonomous</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ─── Quick Prompts ────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("### 🧠 AI Reminder Prompt")
        st.markdown('<span class="tag">Copy → Paste into any AI session</span>', unsafe_allow_html=True)
        reminder_prompt = """You are Adam's (adman_cross) dedicated System Builder AI. Your single mission is to power his Python/Streamlit app that creates custom agentic AI webapps for any industry using: n8n (Hostinger + Coolify), Supabase, Antigravity + Claude Code (with n8n expert skill packs), Code Rabbit CLI for bug fixing. Mirror Cook OS (Skills + Context + Tools), webprodigies workflows, n8n agent tutorials, and Dan Martell one-stop GTM. Always output ready-to-import n8n JSON, Antigravity-ready prompts, Coolify commands, or Streamlit code updates. Prioritise speed-to-live for high-ticket clients (Catholic Archdiocese, SaaS, healthcare, etc.). Never suggest cloud-only tools. Stay agentic and autonomous."""
        st.code(reminder_prompt, language="text")

    with col_b:
        st.markdown("### 🏗️ Customer Build Prompt")
        st.markdown('<span class="tag blue">Use inside Agent Builder or Antigravity</span>', unsafe_allow_html=True)
        build_prompt = """Build a complete agentic AI webapp for [Business Name] in the [Industry] sector. Requirements: [paste questionnaire answers]. Core stack: n8n self-hosted on Hostinger/Coolify, Supabase DB, Antigravity + Claude Code for autonomous execution, Code Rabbit for every PR. Include [voice / donation / CRM] flows. Output: 1) importable n8n JSON, 2) Supabase schema SQL, 3) Antigravity skill prompt, 4) Coolify deploy command. Make it fully autonomous like Cook OS."""
        st.code(build_prompt, language="text")

    st.markdown("---")

    # ─── Recent Projects ──────────────────────────────────────────────────────
    st.markdown("### 📁 Recent Projects")

    if not projects:
        st.markdown("""
        <div class="card" style="text-align:center;padding:40px;">
            <div style="font-size:48px;margin-bottom:12px;">🚀</div>
            <div class="card-title">No projects yet</div>
            <div class="card-sub">Click <strong>New Customer</strong> in the sidebar to build your first system</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for p in projects[:10]:
            status_color = {"active": "amber", "deployed": "green", "draft": "red"}.get(p.get("status","draft"), "amber")
            industry = p.get("industry", "Custom")
            created = p.get("created_at", "")[:10] if p.get("created_at") else "—"
            agents = p.get("selected_agents", [])

            st.markdown(f"""
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                    <div>
                        <div class="card-title">{p.get('name','Unnamed')}</div>
                        <div class="card-sub">{industry} · {p.get('type','')} · {created}</div>
                        <div style="margin-top:8px;">
                            {''.join([f'<span class="tag">{a[:25]}</span>' for a in agents[:3]])}
                        </div>
                    </div>
                    <span class="tag {status_color}">{p.get('status','draft').upper()}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚡ Quick Actions")

    c1, c2, c3 = st.columns(3)
    new_customer_clicked = False
    with c1:
        if st.button("➕ New Customer", use_container_width=True):
            new_customer_clicked = True
    with c2:
        st.link_button("📖 n8n Templates", "https://n8n.io/workflows/", use_container_width=True)
    with c3:
        st.link_button("🐇 Code Rabbit Docs", "https://coderabbit.ai", use_container_width=True)

    # Navigate outside the column context so rerun works cleanly
    if new_customer_clicked:
        st.session_state["nav_page"] = "➕  New Customer"
        st.rerun()
