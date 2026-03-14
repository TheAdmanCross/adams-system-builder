import streamlit as st
import time
from utils.generators import (
    generate_n8n_json,
    generate_antigravity_prompt,
    generate_coolify_commands,
    generate_supabase_sql,
    generate_client_handover,
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

    name        = project.get("name", "")
    industry    = project.get("industry", "Custom")
    agents      = project.get("selected_agents", [])
    goal        = project.get("goal", "")
    requirements = "\n".join([f"- {k}: {v}" for k, v in project.get("questionnaire_answers", {}).items() if v])
    pb          = get_playbook(industry)
    tech_stack  = pb.get("tech_stack", ["n8n", "Supabase", "Coolify"])
    integrations = project.get("integrations", {})
    api_key     = settings.get("anthropic_api_key", "")

    # ─── Status card ─────────────────────────────────────────────────────────
    ai_active = bool(api_key)
    ai_badge = '<span class="tag green">⚡ AI-Powered</span>' if ai_active else '<span class="tag amber">📋 Template Mode</span>'

    st.markdown(f"""
    <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center;">
            <div>
                <div class="card-title">Ready to generate: {name}</div>
                <div class="card-sub">{industry} · {len(agents)} agents · {project.get('type','')}</div>
            </div>
            <div style="display:flex;gap:8px;align-items:center;">
                {ai_badge}
                <span class="tag green">ALL SYSTEMS GO</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not ai_active:
        st.info("💡 Add your **Anthropic API key** in Settings to unlock AI-powered outputs. Currently using templates.")

    # ─── Deployment target ───────────────────────────────────────────────────
    st.markdown("### 🎛️ Deployment Target")
    col1, col2 = st.columns(2)
    with col1:
        deploy_domain = st.text_input(
            "Customer Domain / VPS IP",
            value=settings.get("hostinger_domain", ""),
            placeholder="client.example.com or 123.45.67.89"
        )
    with col2:
        hosting_choice = st.selectbox("Hosting", [
            "Hostinger VPS (Coolify)",
            "Hostinger Shared Hosting",
            "Customer's Own Server",
            "Other / TBD",
        ])

    st.markdown("---")

    # ─── Generate button ─────────────────────────────────────────────────────
    if st.button("⚡ GENERATE FULL SYSTEM", type="primary", use_container_width=True):
        outputs = {}
        progress = st.progress(0, text="Starting generation...")

        steps = [
            ("n8n_json",       "📦 Generating n8n workflow...",        1/5),
            ("ag_prompt",      "🧠 Writing Antigravity prompt...",      2/5),
            ("coolify_cmds",   "🐳 Building Coolify deploy script...",  3/5),
            ("sql",            "🗃️ Designing Supabase schema...",       4/5),
            ("handover",       "📄 Writing client handover doc...",     5/5),
        ]

        try:
            progress.progress(1/5, text="📦 Generating n8n workflow...")
            outputs["n8n_json"] = generate_n8n_json(
                business_name=name, industry=industry, agents=agents,
                n8n_url=settings.get("n8n_url", ""), api_key=api_key,
                goal=goal, requirements=requirements, tech_stack=tech_stack,
            )

            progress.progress(2/5, text="🧠 Writing Antigravity prompt...")
            outputs["ag_prompt"] = generate_antigravity_prompt(
                business_name=name, industry=industry, agents=agents,
                tech_stack=tech_stack, requirements=requirements,
                goal=goal, api_key=api_key,
            )

            progress.progress(3/5, text="🐳 Building Coolify deploy script...")
            outputs["coolify_cmds"] = generate_coolify_commands(
                business_name=name, coolify_url=settings.get("coolify_url", ""),
                coolify_token=settings.get("coolify_api_token", ""),
                domain=deploy_domain, api_key=api_key,
                industry=industry, agents=agents,
            )

            progress.progress(4/5, text="🗃️ Designing Supabase schema...")
            outputs["sql"] = generate_supabase_sql(
                business_name=name, industry=industry,
                agents=agents, api_key=api_key, requirements=requirements,
            )

            progress.progress(5/5, text="📄 Writing client handover doc...")
            outputs["handover"] = generate_client_handover(
                business_name=name, industry=industry, agents=agents,
                goal=goal, integrations=integrations,
                tech_stack=tech_stack, api_key=api_key, requirements=requirements,
            )

            progress.empty()
            st.session_state.generated_outputs = outputs
            st.session_state.generated = True
            mode = "AI-powered ⚡" if ai_active else "template 📋"
            st.success(f"✅ Complete system generated ({mode}) for **{name}**")
            st.balloons()

        except Exception as e:
            progress.empty()
            st.error(f"Generation error: {e}")
            return

    if not st.session_state.get("generated"):
        st.info("👆 Click the button above to generate all outputs for this project.")
        return

    outputs = st.session_state.get("generated_outputs", {})
    if not outputs:
        st.warning("Outputs not found — please generate again.")
        return

    # ─── Output tabs ─────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📦 n8n JSON",
        "🧠 Antigravity Prompt",
        "🐳 Coolify Commands",
        "🗃️ Supabase SQL",
        "📄 Client Handover Doc",
        "📋 Full Summary",
    ])

    with tab1:
        st.markdown("#### Importable n8n Workflow JSON")
        st.caption("Go to n8n → Workflows → Import from file / clipboard")
        st.code(outputs.get("n8n_json", ""), language="json")
        st.download_button(
            "⬇️ Download n8n JSON",
            data=outputs.get("n8n_json", ""),
            file_name=f"{name.lower().replace(' ','-')}-n8n-workflow.json",
            mime="application/json",
            use_container_width=True,
        )

    with tab2:
        st.markdown("#### Antigravity / Claude Code Build Prompt")
        st.caption("Paste into Antigravity IDE, Claude.ai, or any AI assistant to begin autonomous build")
        st.code(outputs.get("ag_prompt", ""), language="text")
        st.download_button(
            "⬇️ Download Antigravity Prompt",
            data=outputs.get("ag_prompt", ""),
            file_name=f"{name.lower().replace(' ','-')}-antigravity-prompt.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with tab3:
        st.markdown("#### Coolify Deploy Commands")
        st.caption("Run on your Hostinger VPS — installs + configures n8n via Coolify")
        st.code(outputs.get("coolify_cmds", ""), language="bash")
        st.download_button(
            "⬇️ Download Deploy Script",
            data=outputs.get("coolify_cmds", ""),
            file_name=f"{name.lower().replace(' ','-')}-deploy.sh",
            mime="text/plain",
            use_container_width=True,
        )

    with tab4:
        st.markdown("#### Supabase Schema SQL")
        st.caption("Run in Supabase → SQL Editor to create all required tables")
        st.code(outputs.get("sql", ""), language="sql")
        st.download_button(
            "⬇️ Download SQL Schema",
            data=outputs.get("sql", ""),
            file_name=f"{name.lower().replace(' ','-')}-schema.sql",
            mime="text/plain",
            use_container_width=True,
        )

    with tab5:
        st.markdown("#### 📄 Client Handover Document")
        st.caption("Hand this to the client — explains the system in plain English, how to use it, and what to do if something breaks")
        handover = outputs.get("handover", "")
        st.markdown(handover)
        st.download_button(
            "⬇️ Download Handover Doc (.md)",
            data=handover,
            file_name=f"{name.lower().replace(' ','-')}-handover.md",
            mime="text/plain",
            use_container_width=True,
        )

    with tab6:
        st.markdown("#### 📋 Project Summary")
        st.markdown(f"**Business:** {name}")
        st.markdown(f"**Industry:** {industry}")
        st.markdown(f"**Type:** {project.get('type','')}")
        st.markdown(f"**Goal:** {goal or '—'}")
        st.markdown(f"**Hosting:** {hosting_choice} · `{deploy_domain}`")
        st.markdown("**Agents:**")
        for a in agents:
            st.markdown(f"- {a}")
        if integrations:
            st.markdown("**Integrations:**")
            for k, v in integrations.items():
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
