import streamlit as st
from utils.playbooks import list_industries, get_playbook
from utils.storage import save_project
import uuid

# ─── Default project types ────────────────────────────────────────────────────
DEFAULT_PROJECT_TYPES = [
    "Full Agentic OS (all agents, full stack)",
    "Voice Agent (calls, SMS, after-hours)",
    "Workflow Automation (existing systems)",
    "Azure / Cloud Infrastructure Uplift",
    "CRM + Lead Gen Automation",
    "Website + AI Chatbot",
    "Custom (describe below)",
]

def _get_industries():
    """Get industries list including any custom ones added by user."""
    base = list_industries()
    custom = st.session_state.get("custom_industries", [])
    return base + custom

def _get_project_types():
    """Get project types including any custom ones added by user."""
    base = DEFAULT_PROJECT_TYPES
    custom = st.session_state.get("custom_project_types", [])
    return base + custom

def render():
    st.markdown("## ➕ New Customer")

    if "current_project" not in st.session_state:
        st.session_state.current_project = {}
    if "custom_industries" not in st.session_state:
        st.session_state.custom_industries = []
    if "custom_project_types" not in st.session_state:
        st.session_state.custom_project_types = []
    if "show_add_industry" not in st.session_state:
        st.session_state.show_add_industry = False
    if "show_add_type" not in st.session_state:
        st.session_state.show_add_type = False

    col1, col2 = st.columns([3, 2])

    with col1:
        st.markdown("### Business Details")
        name = st.text_input("Business / Organisation Name *",
                             placeholder="e.g. Catholic Archdiocese of Brisbane")

        # ─── Industry selector + Add New ─────────────────────────────────────
        industries = _get_industries()
        industry_col, add_ind_col = st.columns([4, 1])
        with industry_col:
            industry = st.selectbox("Industry *", industries)
        with add_ind_col:
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("＋ New", key="add_industry_btn", help="Add a new industry"):
                st.session_state.show_add_industry = not st.session_state.show_add_industry

        if st.session_state.show_add_industry:
            with st.container():
                st.markdown("""
                <div class="card" style="padding:16px;">
                    <div class="card-title">Add New Industry</div>
                </div>
                """, unsafe_allow_html=True)
                new_ind_col1, new_ind_col2 = st.columns([3, 1])
                with new_ind_col1:
                    new_industry = st.text_input("Industry name",
                                                  placeholder="e.g. Mining & Resources",
                                                  key="new_industry_input",
                                                  label_visibility="collapsed")
                with new_ind_col2:
                    if st.button("Add ✓", key="confirm_add_industry"):
                        if new_industry and new_industry not in industries:
                            st.session_state.custom_industries.append(new_industry)
                            st.session_state.show_add_industry = False
                            st.success(f"✅ '{new_industry}' added!")
                            st.rerun()

        # ─── Project Type selector + Add New ─────────────────────────────────
        project_types = _get_project_types()
        type_col, add_type_col = st.columns([4, 1])
        with type_col:
            biz_type = st.selectbox("Project Type *", project_types)
        with add_type_col:
            st.markdown("<br/>", unsafe_allow_html=True)
            if st.button("＋ New", key="add_type_btn", help="Add a new project type"):
                st.session_state.show_add_type = not st.session_state.show_add_type

        if st.session_state.show_add_type:
            with st.container():
                st.markdown("""
                <div class="card" style="padding:16px;">
                    <div class="card-title">Add New Project Type</div>
                </div>
                """, unsafe_allow_html=True)
                new_type_col1, new_type_col2 = st.columns([3, 1])
                with new_type_col1:
                    new_type = st.text_input("Project type name",
                                              placeholder="e.g. AI Document Generator",
                                              key="new_type_input",
                                              label_visibility="collapsed")
                with new_type_col2:
                    if st.button("Add ✓", key="confirm_add_type"):
                        if new_type and new_type not in project_types:
                            st.session_state.custom_project_types.append(new_type)
                            st.session_state.show_add_type = False
                            st.success(f"✅ '{new_type}' added!")
                            st.rerun()

        # ─── Rest of the form ─────────────────────────────────────────────────
        contact_name = st.text_input("Primary Contact Name",
                                      placeholder="e.g. John Smith")
        contact_email = st.text_input("Contact Email",
                                       placeholder="john@example.com")
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
        notes = st.text_area("Additional Notes / Brief",
                              placeholder="Paste any brief, job description, or requirements here...",
                              height=120)

    with col2:
        st.markdown("### Playbook Preview")
        pb = get_playbook(industry)
        st.markdown(f"""
        <div class="card">
            <div style="font-size:2rem;">{pb.get('icon','🔧')}</div>
            <div class="card-title" style="margin-top:8px;">{industry}</div>
            <div class="card-sub">{pb.get('description','Custom industry — questionnaire will be free-form.')}</div>
        </div>
        """, unsafe_allow_html=True)

        agents = pb.get("common_agents", [])
        if agents:
            st.markdown("**Common Agents:**")
            for agent in agents[:6]:
                st.markdown(f'<span class="tag">{agent[:40]}</span>',
                            unsafe_allow_html=True)
            st.markdown("<br/>", unsafe_allow_html=True)

        tech_stack = pb.get("tech_stack", ["n8n", "Supabase", "Coolify"])
        st.markdown("**Default Stack:**")
        for tech in tech_stack:
            st.markdown(f'<span class="tag blue">{tech}</span>',
                        unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        hosting = pb.get("default_hosting", "Hostinger VPS")
        st.markdown(f'**Hosting:** <span class="tag green">{hosting}</span>',
                    unsafe_allow_html=True)

        # Show custom industries/types added
        if st.session_state.custom_industries or st.session_state.custom_project_types:
            st.markdown("---")
            st.markdown("**Your Custom Additions:**")
            for ind in st.session_state.custom_industries:
                st.markdown(f'<span class="tag amber">📁 {ind}</span>',
                            unsafe_allow_html=True)
            for pt in st.session_state.custom_project_types:
                st.markdown(f'<span class="tag amber">⚙️ {pt}</span>',
                            unsafe_allow_html=True)

    st.markdown("---")
    if st.button("💾 Save & Continue to Questionnaire",
                 type="primary", use_container_width=True):
        if not name:
            st.error("Business name is required.")
        else:
            pb = get_playbook(industry)
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
            st.success(f"✅ Project saved for **{name}**. Go to **Questionnaire** in the sidebar.")
            st.balloons()
