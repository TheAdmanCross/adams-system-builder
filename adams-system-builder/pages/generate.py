import streamlit as st
import json
from utils.generators import (
    generate_n8n_json,
    generate_antigravity_prompt,
    generate_coolify_commands,
    generate_supabase_sql
)
from utils.playbooks import get_playbook
from utils.storage import save_project

def render():
    st.markdown("## 🚀 Generate & Deploy")

    project = st.session_state.get("current_project", {})
    settings = st.session_state.get("settings", {})

    if not project:
        st.warning("⚠️ No active project. Start with **New Customer**.")
        return

    name = project.get("name", "")
    industry = project.get("industry", "Custom")
    agents = project.get("selected_agents", [])
    goal = project.get("goal", "")
    pb = get_playbook(industry)

    st.markdown(f"""
    <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div class="card-title">Ready to generate: {name}</div>
                <div class="card-sub">{industry} · {len(agents)} agents · {project.get('type','')}</div>
            </div>
            <span class="tag green">ALL SYSTEMS GO</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 🎛️ Deployment Target")
    col1, col2 = st.columns(2)
    with col1:
        deploy_domain = st.text_input("Customer Domain / VPS IP",
                                       value=settings.get("hostinger_domain", ""),
                                       placeholder="client.example.com or 123.45.67.89")
    with col2:
        hosting_choice = st.selectbox("Hosting", [
            "Hostinger VPS (Coolify)",
            "Hostinger Shared Hosting",
            "Customer's Own Server",
            "Other / TBD",
        ])

    st.markdown("---")

    # ─── Generate Button ──────────────────────────────────────────────────────
    if st.button("⚡ GENERATE FULL SYSTEM", type="primary", use_container_width=True):
        st.session_state.generated = True
        with st.spinner(f"Building complete agentic system for {name}..."):
            import time; time.sleep(1)  # Brief pause for UX

        st.success(f"✅ Complete system generated for **{name}**")
        st.balloons()

    if not st.session_state.get("generated"):
        st.info("👆 Click the button above to generate all outputs for this project.")
        return

    # ─── Tabs for each output ─────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📦 n8n JSON",
        "🧠 Antigravity Prompt",
        "🐳 Coolify Commands",
        "🗃️ Supabase SQL",
        "📋 Full Summary",
    ])

    with tab1:
        st.markdown("#### Importable n8n Workflow JSON")
        st.caption("Go to n8n → Workflows → Import from file / clipboard")
        n8n_json = generate_n8n_json(
            business_name=name,
            industry=industry,
            agents=agents,
            n8n_url=settings.get("n8n_url", "")
        )
        st.code(n8n_json, language="json")
        st.download_button(
            "⬇️ Download n8n JSON",
            data=n8n_json,
            file_name=f"{name.lower().replace(' ','-')}-n8n-workflow.json",
            mime="application/json",
            use_container_width=True,
        )

    with tab2:
        st.markdown("#### Antigravity / Claude Code Build Prompt")
        st.caption("Paste into Antigravity IDE, Claude.ai, or any AI assistant to begin autonomous build")
        answers = project.get("questionnaire_answers", {})
        req_text = "\n".join([f"- {k}: {v}" for k, v in answers.items() if v])
        ag_prompt = generate_antigravity_prompt(
            business_name=name,
            industry=industry,
            agents=agents,
            tech_stack=pb.get("tech_stack", []),
            requirements=req_text,
            goal=goal,
        )
        st.code(ag_prompt, language="text")
        st.download_button(
            "⬇️ Download Antigravity Prompt",
            data=ag_prompt,
            file_name=f"{name.lower().replace(' ','-')}-antigravity-prompt.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with tab3:
        st.markdown("#### Coolify Deploy Commands")
        st.caption("Run on your Hostinger VPS — installs + configures n8n via Coolify")
        coolify_cmds = generate_coolify_commands(
            business_name=name,
            coolify_url=settings.get("coolify_url", ""),
            coolify_token=settings.get("coolify_api_token", ""),
            domain=deploy_domain,
        )
        st.code(coolify_cmds, language="bash")
        st.download_button(
            "⬇️ Download Deploy Script",
            data=coolify_cmds,
            file_name=f"{name.lower().replace(' ','-')}-deploy.sh",
            mime="text/plain",
            use_container_width=True,
        )

    with tab4:
        st.markdown("#### Supabase Schema SQL")
        st.caption("Run in Supabase → SQL Editor to create all required tables")
        sql = generate_supabase_sql(business_name=name, industry=industry)
        st.code(sql, language="sql")
        st.download_button(
            "⬇️ Download SQL Schema",
            data=sql,
            file_name=f"{name.lower().replace(' ','-')}-schema.sql",
            mime="text/plain",
            use_container_width=True,
        )

    with tab5:
        st.markdown("#### 📋 Project Summary")
        st.markdown(f"**Business:** {name}")
        st.markdown(f"**Industry:** {industry}")
        st.markdown(f"**Type:** {project.get('type','')}")
        st.markdown(f"**Goal:** {goal or '—'}")
        st.markdown(f"**Hosting:** {hosting_choice} · `{deploy_domain}`")
        st.markdown("**Agents:**")
        for a in agents:
            st.markdown(f"- {a}")
        st.markdown("**Integrations:**")
        for k, v in project.get("integrations", {}).items():
            if v:
                st.markdown(f"- {k}")

        st.markdown("---")
        env_vars = f"""# Required Environment Variables for {name}
N8N_HOST={deploy_domain or 'your-domain.com'}
N8N_USER=admin
N8N_PASSWORD=changeme123
N8N_ENCRYPTION_KEY=generate-with-openssl-rand-hex-32
SUPABASE_URL={settings.get('supabase_url','https://xxxx.supabase.co')}
SUPABASE_SERVICE_KEY=your-service-key
ANTHROPIC_API_KEY=sk-ant-...
CODERABBIT_API_KEY=your-key
GITHUB_TOKEN=ghp_...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
ELEVENLABS_API_KEY=...
"""
        st.markdown("#### 🔑 Environment Variables")
        st.code(env_vars, language="bash")
        st.download_button(
            "⬇️ Download .env.example",
            data=env_vars,
            file_name=f"{name.lower().replace(' ','-')}.env.example",
            mime="text/plain",
            use_container_width=True,
        )

    st.markdown("---")
    if st.button("✅ Mark Project as Deployed", use_container_width=True):
        project["status"] = "deployed"
        save_project(project)
        st.success("🎉 Project marked as deployed!")
