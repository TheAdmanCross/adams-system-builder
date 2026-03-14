import streamlit as st
from utils.storage import get_projects, save_project
from datetime import datetime

# ─── Industry colours for chart ───────────────────────────────────────────────
INDUSTRY_COLORS = {
    "SaaS": "#ff4d4d",
    "Healthcare": "#00ff88",
    "Faith-Based / Non-Profit": "#a78bfa",
    "E-commerce": "#ff8c00",
    "Education": "#0096ff",
    "Real Estate": "#ffaa00",
    "Mining & Resources": "#94a3b8",
    "Legal & Professional Services": "#f472b6",
    "Hospitality & Tourism": "#34d399",
    "Construction & Trades": "#fb923c",
    "Finance & Insurance": "#60a5fa",
    "Aged Care & NDIS": "#c084fc",
}

def _color(industry):
    return INDUSTRY_COLORS.get(industry, "#666")

def render():
    st.markdown("## ⚡ Dashboard")

    projects = get_projects()
    draft    = [p for p in projects if p.get("status") == "draft"]
    active   = [p for p in projects if p.get("status") == "active"]
    deployed = [p for p in projects if p.get("status") == "deployed"]

    # ─── Revenue calc ─────────────────────────────────────────────────────────
    total_revenue = sum(float(p.get("revenue", 0) or 0) for p in projects)
    deployed_revenue = sum(float(p.get("revenue", 0) or 0) for p in deployed)

    # ─── Metric cards ─────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    metrics = [
        (c1, len(projects),   "Total Projects",    "up",    "↑ All time"),
        (c2, len(draft),      "Draft",             "red",   "✏️ Not started"),
        (c3, len(active),     "In Progress",       "amber", "⏳ Building"),
        (c4, len(deployed),   "Deployed",          "up",    "✅ Live"),
        (c5, f"${total_revenue:,.0f}", "Total Revenue (AUD)", "up", "💰 All projects"),
    ]
    for col, val, label, delta_cls, delta_txt in metrics:
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{val}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-delta {delta_cls}">{delta_txt}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # ─── Charts row ───────────────────────────────────────────────────────────
    if projects:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("### 📊 Projects by Status")
            status_data = {"Draft": len(draft), "Active": len(active), "Deployed": len(deployed)}
            status_colors = {"Draft": "#ff4d4d", "Active": "#ffaa00", "Deployed": "#00ff88"}
            total = len(projects) or 1
            bars_html = ""
            for status, count in status_data.items():
                pct = (count / total) * 100
                color = status_colors[status]
                bars_html += f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span style="color:#aaa;font-size:0.85rem;">{status}</span>
                        <span style="color:#fff;font-size:0.85rem;font-weight:600;">{count}</span>
                    </div>
                    <div style="background:#1e1e30;border-radius:4px;height:8px;">
                        <div style="background:{color};width:{pct}%;height:8px;border-radius:4px;transition:width 0.3s;"></div>
                    </div>
                </div>"""
            st.markdown(f'<div class="card" style="padding:20px;">{bars_html}</div>', unsafe_allow_html=True)

        with chart_col2:
            st.markdown("### 🏭 Projects by Industry")
            industry_counts = {}
            for p in projects:
                ind = p.get("industry", "Other")
                industry_counts[ind] = industry_counts.get(ind, 0) + 1
            top_industries = sorted(industry_counts.items(), key=lambda x: x[1], reverse=True)[:6]
            bars_html = ""
            for ind, count in top_industries:
                pct = (count / total) * 100
                color = _color(ind)
                short = ind[:22] + "…" if len(ind) > 22 else ind
                bars_html += f"""
                <div style="margin-bottom:12px;">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px;">
                        <span style="color:#aaa;font-size:0.85rem;">{short}</span>
                        <span style="color:#fff;font-size:0.85rem;font-weight:600;">{count}</span>
                    </div>
                    <div style="background:#1e1e30;border-radius:4px;height:8px;">
                        <div style="background:{color};width:{pct}%;height:8px;border-radius:4px;"></div>
                    </div>
                </div>"""
            st.markdown(f'<div class="card" style="padding:20px;">{bars_html}</div>', unsafe_allow_html=True)

    st.markdown("---")

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

    # ─── Project pipeline ─────────────────────────────────────────────────────
    st.markdown("### 📁 Client Pipeline")

    # Filter controls
    f1, f2, f3 = st.columns([2, 2, 1])
    with f1:
        filter_status = st.selectbox("Filter by status", ["All", "Draft", "Active", "Deployed"], label_visibility="collapsed")
    with f2:
        search = st.text_input("Search by name", placeholder="🔍 Search clients...", label_visibility="collapsed")
    with f3:
        show_revenue = st.toggle("💰 Edit Revenue", value=False)

    # Apply filters
    filtered = projects
    if filter_status != "All":
        filtered = [p for p in filtered if p.get("status", "draft").lower() == filter_status.lower()]
    if search:
        filtered = [p for p in filtered if search.lower() in p.get("name", "").lower()]

    if not filtered:
        st.markdown("""
        <div class="card" style="text-align:center;padding:40px;">
            <div style="font-size:48px;margin-bottom:12px;">🚀</div>
            <div class="card-title">No projects yet</div>
            <div class="card-sub">Click <strong>➕ New Customer</strong> below to build your first system</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for p in filtered[:20]:
            status = p.get("status", "draft")
            status_color = {"active": "amber", "deployed": "green", "draft": "red"}.get(status, "amber")
            industry = p.get("industry", "Custom")
            created = p.get("created_at", "")[:10] if p.get("created_at") else "—"
            agents = p.get("selected_agents", [])
            revenue = p.get("revenue", "")
            budget = p.get("budget", "")

            st.markdown(f"""
            <div class="card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
                    <div style="flex:1;">
                        <div class="card-title">{p.get('name','Unnamed')}</div>
                        <div class="card-sub">{industry} · {p.get('type','')} · Added {created}</div>
                        <div style="margin-top:8px;display:flex;flex-wrap:wrap;gap:4px;">
                            {''.join([f'<span class="tag">{a[:28]}</span>' for a in agents[:3]])}
                        </div>
                        {f'<div style="margin-top:6px;color:#00ff88;font-size:0.85rem;font-weight:600;">💰 ${float(revenue):,.0f} AUD</div>' if revenue else f'<div style="margin-top:6px;color:#555;font-size:0.82rem;">Budget: {budget}</div>'}
                    </div>
                    <div style="display:flex;flex-direction:column;align-items:flex-end;gap:8px;">
                        <span class="tag {status_color}">{status.upper()}</span>
                        {f'<span style="color:#aaa;font-size:0.75rem;">{p.get("contact_name","")}</span>' if p.get("contact_name") else ''}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Revenue edit inline
            if show_revenue:
                rev_col1, rev_col2 = st.columns([3, 1])
                with rev_col1:
                    new_rev = st.text_input(
                        f"Revenue for {p.get('name','')}",
                        value=str(revenue) if revenue else "",
                        placeholder="e.g. 5000",
                        key=f"rev_{p.get('id','')}",
                        label_visibility="collapsed"
                    )
                with rev_col2:
                    if st.button("💾 Save", key=f"save_rev_{p.get('id','')}"):
                        try:
                            p["revenue"] = float(new_rev) if new_rev else 0
                            save_project(p)
                            st.success("✅ Saved")
                            st.rerun()
                        except ValueError:
                            st.error("Enter a number")

    st.markdown("---")

    # ─── Quick actions ────────────────────────────────────────────────────────
    st.markdown("### ⚡ Quick Actions")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("➕ New Customer", use_container_width=True, type="primary"):
            st.session_state["_goto"] = 1
            st.rerun()
    with c2:
        if st.button("🗣️ Quick Onboard", use_container_width=True):
            st.info("💡 Chat-style intake coming soon! Use ➕ New Customer for now.")
    with c3:
        st.link_button("📖 n8n Templates", "https://n8n.io/workflows/", use_container_width=True)
    with c4:
        st.link_button("🐇 Code Rabbit", "https://coderabbit.ai", use_container_width=True)
