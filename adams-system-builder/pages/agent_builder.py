import streamlit as st

def render():
    st.markdown("## 🤖 Agent Builder")

    project = st.session_state.get("current_project", {})
    if not project:
        st.warning("⚠️ No active project. Start with **New Customer**.")
        return

    agents = project.get("selected_agents", [])
    industry = project.get("industry", "Custom")

    st.markdown(f"""
    <div class="card">
        <div class="card-title">{project.get('name','')} — {len(agents)} agents queued</div>
        <div class="card-sub">{industry} · {project.get('type','')}</div>
    </div>
    """, unsafe_allow_html=True)

    # ─── Agent Style ──────────────────────────────────────────────────────────
    st.markdown("### 🧠 Agent Architecture")
    agent_style = st.radio("Execution Model", [
        "🤖 n8n + Antigravity (Full Autonomous — recommended)",
        "🎙️ Voice RAG Agent (ElevenLabs + Twilio + n8n)",
        "🔧 Azure / Infrastructure Automation Agent",
        "🐇 Bug-Fix Loop (Code Rabbit CLI + Claude Code)",
        "📊 Data Pipeline + Reporting Agent",
    ], label_visibility="collapsed")

    st.markdown("### 🎯 Primary Goal")
    goal = st.text_area(
        "Describe what this system should autonomously handle",
        placeholder="e.g. 'Auto-resolve 80% of IT support tickets by triaging with Azure logs, suggesting fixes, and escalating only the critical 20% to the on-call engineer via SMS.'",
        height=100
    )

    st.markdown("### 🔗 Integrations")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**Comms**")
        use_slack = st.checkbox("Slack notifications")
        use_teams = st.checkbox("Microsoft Teams")
        use_sms = st.checkbox("SMS via Twilio")
        use_voice = st.checkbox("Voice agent (ElevenLabs)")
        use_email = st.checkbox("Email automation")
    with col2:
        st.markdown("**Data**")
        use_supabase = st.checkbox("Supabase DB", value=True)
        use_google_sheets = st.checkbox("Google Sheets")
        use_airtable = st.checkbox("Airtable")
        use_notion = st.checkbox("Notion")
        use_azure = st.checkbox("Azure Monitor")
    with col3:
        st.markdown("**Automation**")
        use_coderabbit = st.checkbox("Code Rabbit (QA)", value=True)
        use_github = st.checkbox("GitHub PRs")
        use_stripe = st.checkbox("Stripe payments")
        use_hubspot = st.checkbox("HubSpot CRM")
        use_calendly = st.checkbox("Calendly bookings")

    integrations = {
        "slack": use_slack, "teams": use_teams, "sms": use_sms,
        "voice": use_voice, "email": use_email, "supabase": use_supabase,
        "google_sheets": use_google_sheets, "airtable": use_airtable,
        "notion": use_notion, "azure": use_azure,
        "coderabbit": use_coderabbit, "github": use_github,
        "stripe": use_stripe, "hubspot": use_hubspot, "calendly": use_calendly,
    }

    st.markdown("### ⚡ AI Model")
    ai_model = st.radio("Primary AI", ["Claude Sonnet 4 (recommended)", "Claude Opus 4 (complex tasks)", "GPT-4o", "Gemini 1.5 Pro", "Local Ollama (offline)"], horizontal=True)

    st.markdown("---")
    if st.button("💾 Save Agent Config & Go to Generate", type="primary"):
        project["agent_style"] = agent_style
        project["goal"] = goal
        project["integrations"] = {k: v for k, v in integrations.items() if v}
        project["ai_model"] = ai_model
        st.session_state.current_project = project
        st.success("✅ Agent config saved. Go to **Generate & Deploy** in the sidebar.")
