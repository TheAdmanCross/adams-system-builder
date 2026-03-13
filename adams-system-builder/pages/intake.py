import streamlit as st
from utils.playbooks import list_industries, get_playbook
from utils.storage import save_project
import uuid

def render():
    st.markdown("## ➕ New Customer")

    if "current_project" not in st.session_state:
        st.session_state.current_project = {}

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### Business Details")
        name = st.text_input("Business / Organisation Name *", placeholder="e.g. Catholic Archdiocese of Brisbane")
        industry = st.selectbox("Industry *", list_industries())
        biz_type = st.selectbox("Project Type *", [
            "Full Agentic OS (all agents, full stack)",
            "Voice Agent (calls, SMS, after-hours)",
            "Workflow Automation (existing systems)",
            "Azure / Cloud Infrastructure Uplift",
            "CRM + Lead Gen Automation",
            "Custom (describe below)",
        ])
        contact_name = st.text_input("Primary Contact Name", placeholder="e.g. John Smith")
        contact_email = st.text_input("Contact Email", placeholder="john@example.com")
        budget = st.selectbox("Budget Range (AUD)", [
            "Prefer not to say",
            "< $5,000",
            "$5,000 – $15,000",
            "$15,000 – $50,000",
            "$50,000 – $100,000",
            "$100,000+",
        ])
        timeline = st.selectbox("Timeline", [
            "ASAP (< 2 weeks)",
            "1 month",
            "3 months",
            "6 months",
            "Flexible",
        ])
        notes = st.text_area("Additional Notes / Brief", placeholder="Paste any brief, job description, or requirements here...")

    with col2:
        st.markdown("### Playbook Preview")
        pb = get_playbook(industry)
        st.markdown(f"""
        <div class="card">
            <div style="font-size:2rem;">{pb.get('icon','🔧')}</div>
            <div class="card-title" style="margin-top:8px;">{industry}</div>
            <div class="card-sub">{pb.get('description','')}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("**Common Agents:**")
        for agent in pb.get("common_agents", [])[:6]:
            st.markdown(f'<span class="tag">{agent[:40]}</span>', unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("**Default Stack:**")
        for tech in pb.get("tech_stack", []):
            st.markdown(f'<span class="tag blue">{tech}</span>', unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown(f'**Default Hosting:** <span class="tag green">{pb.get("default_hosting","Hostinger VPS")}</span>', unsafe_allow_html=True)

    st.markdown("---")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("💾 Save & Continue to Questionnaire", type="primary", use_container_width=True):
            if not name:
                st.error("Business name is required.")
            else:
                project = {
                    "id": str(uuid.uuid4()),
                    "name": name,
                    "industry": industry,
                    "type": biz_type,
                    "contact_name": contact_name,
                    "contact_email": contact_email,
                    "budget": budget,
                    "timeline": timeline,
                    "notes": notes,
                    "status": "draft",
                    "selected_agents": pb.get("common_agents", [])[:3],
                }
                save_project(project)
                st.session_state.current_project = project
                st.success(f"✅ Project saved for {name}. Go to **Questionnaire** in the sidebar.")
                st.balloons()
