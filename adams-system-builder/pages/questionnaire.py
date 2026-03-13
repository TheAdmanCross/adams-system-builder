import streamlit as st
from utils.playbooks import get_playbook, list_industries

def render():
    st.markdown("## 📋 Adaptive Questionnaire")

    project = st.session_state.get("current_project", {})
    industry = project.get("industry", "")

    if not project:
        st.warning("⚠️ No active project. Go to **New Customer** first and save a project.")
        return

    pb = get_playbook(industry)

    st.markdown(f"""
    <div class="card">
        <div style="display:flex;align-items:center;gap:12px;">
            <div style="font-size:2rem;">{pb.get('icon','🔧')}</div>
            <div>
                <div class="card-title">{project.get('name','')}</div>
                <div class="card-sub">{industry} · {project.get('type','')}</div>
            </div>
            <span class="tag" style="margin-left:auto;">{pb.get('tag','custom').upper()} PLAYBOOK</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### Industry Questions")
    st.caption("Answer as many as possible — each answer improves the generated system.")

    answers = {}
    questions = pb.get("questions", [])

    for q in questions:
        label = q.get("label", "")
        qtype = q.get("type", "text")

        if qtype == "checkbox":
            answers[label] = st.checkbox(label)
        elif qtype == "select":
            answers[label] = st.selectbox(label, q.get("options", ["Yes", "No"]))
        elif qtype == "textarea":
            answers[label] = st.text_area(label, height=120)
        else:
            answers[label] = st.text_input(label)

    st.markdown("---")
    st.markdown("### Agent Selection")
    st.caption("Select which agents to include in this build.")

    available_agents = pb.get("common_agents", [])
    if available_agents:
        selected_agents = []
        cols = st.columns(2)
        for i, agent in enumerate(available_agents):
            with cols[i % 2]:
                default_checked = i < 3  # default top 3 checked
                if st.checkbox(agent, value=default_checked, key=f"agent_{i}"):
                    selected_agents.append(agent)

        st.session_state.selected_agents = selected_agents
        st.markdown(f'<span class="tag green">{len(selected_agents)} agents selected</span>', unsafe_allow_html=True)
    else:
        custom_agents = st.text_area("List the agents you need (one per line)")
        selected_agents = [a.strip() for a in custom_agents.split("\n") if a.strip()]
        st.session_state.selected_agents = selected_agents

    st.markdown("---")
    st.markdown("### n8n Template Suggestions")
    for t in pb.get("n8n_templates", []):
        st.markdown(f"""
        <div class="card" style="padding:12px 16px;">
            <span style="color:#00ff88;">→</span> <span style="color:#ccc;">{t}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("💾 Save Questionnaire & Go to Agent Builder", type="primary"):
        project["questionnaire_answers"] = answers
        project["selected_agents"] = st.session_state.get("selected_agents", [])
        project["status"] = "active"
        st.session_state.current_project = project
        st.success("✅ Answers saved. Go to **Agent Builder** in the sidebar.")
