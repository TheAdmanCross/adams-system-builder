import streamlit as st
from utils.storage import save_settings

def render():
    st.markdown("## ⚙️ Settings")
    st.caption("All credentials are stored encrypted in Supabase. Never committed to Git.")

    settings = st.session_state.get("settings", {})

    def val(key, default=""):
        return settings.get(key, default)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🖥️ Hosting",
        "⚙️ n8n + Coolify",
        "🗃️ Supabase",
        "🤖 AI & Tools",
        "📣 Notifications",
    ])

    with tab1:
        st.markdown("#### Hostinger VPS")
        c1, c2 = st.columns(2)
        with c1:
            hostinger_vps_ip = st.text_input("VPS IP Address", value=val("hostinger_vps_ip"), placeholder="123.45.67.89")
        with c2:
            hostinger_domain = st.text_input("Primary Domain", value=val("hostinger_domain"), placeholder="adambuilds.com")

        st.markdown("""
        <div class="card" style="margin-top:16px;">
            <div class="card-title">💡 Hostinger Setup Tips</div>
            <div class="card-sub">
                1. Get a KVM VPS (4GB RAM minimum for n8n + Coolify)<br/>
                2. Ubuntu 22.04 LTS recommended<br/>
                3. Open ports: 22 (SSH), 80, 443, 8000 (Coolify), 5678 (n8n)<br/>
                4. Point your domain A record to the VPS IP<br/>
                5. Install Coolify: <code>curl -fsSL https://cdn.coollabs.io/coolify/install.sh | bash</code>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        st.markdown("#### Coolify")
        c1, c2 = st.columns(2)
        with c1:
            coolify_url = st.text_input("Coolify URL", value=val("coolify_url"), placeholder="https://coolify.yourdomain.com")
        with c2:
            coolify_api_token = st.text_input("Coolify API Token", value=val("coolify_api_token"), type="password", placeholder="coolify_token_...")

        st.markdown("#### n8n")
        c1, c2 = st.columns(2)
        with c1:
            n8n_url = st.text_input("n8n URL", value=val("n8n_url"), placeholder="https://n8n.yourdomain.com")
        with c2:
            n8n_api_key = st.text_input("n8n API Key", value=val("n8n_api_key"), type="password", placeholder="n8n_api_...")

        if n8n_url:
            st.markdown(f"""
            <div class="card">
                <span class="status-dot green"></span>
                <span style="color:#aaa;">n8n at <a href="{n8n_url}" target="_blank" style="color:#ff4d4d;">{n8n_url}</a></span>
            </div>
            """, unsafe_allow_html=True)

    with tab3:
        st.markdown("#### Supabase Project")
        supabase_url = st.text_input("Project URL", value=val("supabase_url"), placeholder="https://xxxx.supabase.co")
        c1, c2 = st.columns(2)
        with c1:
            supabase_anon_key = st.text_input("Anon (Public) Key", value=val("supabase_anon_key"), type="password", placeholder="eyJh...")
        with c2:
            supabase_service_key = st.text_input("Service Role Key ⚠️", value=val("supabase_service_key"), type="password", placeholder="eyJh...", help="Keep this secret — never share or commit")

        st.info("🗃️ After saving, go to **Generate & Deploy** → copy the SQL schema → run it in Supabase SQL Editor to create tables.")

    with tab4:
        st.markdown("#### AI Models")
        anthropic_api_key = st.text_input("Anthropic API Key (Claude)", value=val("anthropic_api_key"), type="password", placeholder="sk-ant-...")

        st.markdown("#### Code Rabbit")
        coderabbit_api_key = st.text_input("Code Rabbit API Key", value=val("coderabbit_api_key"), type="password", placeholder="cr-...")
        st.markdown('[Get Code Rabbit API Key →](https://coderabbit.ai)', unsafe_allow_html=False)

        st.markdown("#### GitHub")
        c1, c2 = st.columns(2)
        with c1:
            github_token = st.text_input("GitHub PAT", value=val("github_token"), type="password", placeholder="ghp_...")
        with c2:
            github_org = st.text_input("GitHub Org / Username", value=val("github_org"), placeholder="adman_cross")

        st.markdown("#### Antigravity")
        antigravity_api_key = st.text_input("Antigravity API Key", value=val("antigravity_api_key"), type="password", placeholder="ag-...")

        st.markdown("#### Voice (ElevenLabs)")
        elevenlabs_api_key = st.text_input("ElevenLabs API Key", value=val("elevenlabs_api_key"), type="password", placeholder="el-...")

        st.markdown("#### Twilio (SMS / Voice)")
        c1, c2, c3 = st.columns(3)
        with c1:
            twilio_account_sid = st.text_input("Account SID", value=val("twilio_account_sid"), placeholder="AC...")
        with c2:
            twilio_auth_token = st.text_input("Auth Token", value=val("twilio_auth_token"), type="password", placeholder="...")
        with c3:
            twilio_phone_number = st.text_input("Phone Number", value=val("twilio_phone_number"), placeholder="+61...")

    with tab5:
        st.markdown("#### Slack")
        slack_webhook = st.text_input("Slack Webhook URL", value=val("slack_webhook"), placeholder="https://hooks.slack.com/...")

        st.markdown("#### Discord")
        discord_webhook = st.text_input("Discord Webhook URL", value=val("discord_webhook"), placeholder="https://discord.com/api/webhooks/...")

    st.markdown("---")
    if st.button("💾 Save All Settings", type="primary", use_container_width=True):
        new_settings = {
            "hostinger_vps_ip": hostinger_vps_ip,
            "hostinger_domain": hostinger_domain,
            "coolify_url": coolify_url,
            "coolify_api_token": coolify_api_token,
            "n8n_url": n8n_url,
            "n8n_api_key": n8n_api_key,
            "supabase_url": supabase_url,
            "supabase_anon_key": supabase_anon_key,
            "supabase_service_key": supabase_service_key,
            "anthropic_api_key": anthropic_api_key,
            "coderabbit_api_key": coderabbit_api_key,
            "github_token": github_token,
            "github_org": github_org,
            "antigravity_api_key": antigravity_api_key,
            "elevenlabs_api_key": elevenlabs_api_key,
            "twilio_account_sid": twilio_account_sid,
            "twilio_auth_token": twilio_auth_token,
            "twilio_phone_number": twilio_phone_number,
            "slack_webhook": slack_webhook,
            "discord_webhook": discord_webhook,
        }
        save_settings(new_settings)
        st.success("✅ All settings saved securely.")
