import streamlit as st

def inject_styles():
    st.markdown("""<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');
    /* ─── Base ─── */
    .stApp { background: #0a0a0f !important; }
    .main .block-container { padding: 2rem 2.5rem; max-width: 1400px; }
    * { font-family: 'Space Grotesk', sans-serif !important; }
    code, pre, .stCode * { font-family: 'JetBrains Mono', monospace !important; }

    /* ─── Sidebar ─── */
    [data-testid="stSidebar"] {
        background: #0f0f1a !important;
        border-right: 1px solid #1e1e30 !important;
    }
    [data-testid="stSidebar"] .stRadio label {
        color: #aaa !important;
        font-size: 0.95rem !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        transition: all 0.2s !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover { color: #fff !important; background: #1e1e30 !important; }
    [data-testid="stSidebar"] .stRadio [aria-checked="true"] label {
        color: #ff4d4d !important;
        background: rgba(255,77,77,0.1) !important;
        border-left: 3px solid #ff4d4d !important;
    }

    /* ─── Sidebar User Card ─── */
    .sidebar-user {
        display: flex; align-items: center; gap: 12px;
        padding: 16px 0; margin-bottom: 8px;
    }
    .avatar { width: 42px; height: 42px; border-radius: 50%; border: 2px solid #ff4d4d; }
    .user-name { color: #fff; font-weight: 600; font-size: 0.95rem; }
    .user-email { color: #666; font-size: 0.75rem; }
    .sidebar-footer { color: #555; font-size: 0.75rem; padding-top: 8px; line-height: 1.8; }

    /* ─── Status Dots ─── */
    .status-dot { width: 8px; height: 8px; border-radius: 50%; display: inline-block; margin-right: 6px; }
    .status-dot.green { background: #00ff88; box-shadow: 0 0 6px #00ff88; }
    .status-dot.red { background: #ff4d4d; box-shadow: 0 0 6px #ff4d4d; }
    .status-dot.amber { background: #ffaa00; box-shadow: 0 0 6px #ffaa00; }

    /* ─── Headers ─── */
    h1, h2, h3 { color: #fff !important; font-weight: 700 !important; }
    h1 { font-size: 2rem !important; }
    h2 { font-size: 1.4rem !important; border-bottom: 1px solid #1e1e30; padding-bottom: 12px; margin-bottom: 20px !important; }

    /* ─── Cards ─── */
    .card {
        background: #0f0f1a;
        border: 1px solid #1e1e30;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 16px;
        transition: border-color 0.2s;
    }
    .card:hover { border-color: #ff4d4d40; }
    .card-title { color: #fff; font-weight: 600; font-size: 1rem; margin-bottom: 4px; }
    .card-sub { color: #666; font-size: 0.82rem; }

    /* ─── Metric Cards ─── */
    .metric-card {
        background: linear-gradient(135deg, #0f0f1a, #15152a);
        border: 1px solid #1e1e30;
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-value { font-size: 2.2rem; font-weight: 700; color: #fff; }
    .metric-label { color: #666; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }
    .metric-delta { font-size: 0.82rem; margin-top: 6px; }
    .metric-delta.up { color: #00ff88; }
    .metric-delta.down { color: #ff4d4d; }

    /* ─── Inputs ─── */
    .stTextInput input, .stTextArea textarea, .stSelectbox select {
        background: #0f0f1a !important;
        border: 1px solid #2a2a40 !important;
        border-radius: 8px !important;
        color: #fff !important;
        font-size: 0.9rem !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #ff4d4d !important;
        box-shadow: 0 0 0 2px rgba(255,77,77,0.15) !important;
    }
    label, .stSelectbox label { color: #aaa !important; font-size: 0.85rem !important; }

    /* ─── Buttons ─── */
    .stButton button {
        background: #1a1a2e !important;
        border: 1px solid #2a2a40 !important;
        color: #fff !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s !important;
    }
    .stButton button:hover { border-color: #ff4d4d !important; color: #ff4d4d !important; }
    .stButton button[kind="primary"] {
        background: linear-gradient(135deg, #ff4d4d, #ff2222) !important;
        border: none !important;
        color: #fff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    .stButton button[kind="primary"]:hover { box-shadow: 0 4px 20px rgba(255,77,77,0.4) !important; transform: translateY(-1px); }

    /* ─── Alerts ─── */
    .stSuccess { background: rgba(0,255,136,0.08) !important; border-left: 4px solid #00ff88 !important; border-radius: 8px !important; }
    .stWarning { background: rgba(255,170,0,0.08) !important; border-left: 4px solid #ffaa00 !important; border-radius: 8px !important; }
    .stError { background: rgba(255,77,77,0.08) !important; border-left: 4px solid #ff4d4d !important; border-radius: 8px !important; }
    .stInfo { background: rgba(0,150,255,0.08) !important; border-left: 4px solid #0096ff !important; border-radius: 8px !important; }

    /* ─── Code blocks ─── */
    .stCodeBlock { background: #050508 !important; border: 1px solid #1e1e30 !important; border-radius: 8px !important; }

    /* ─── Tabs ─── */
    .stTabs [data-baseweb="tab"] { color: #666 !important; }
    .stTabs [aria-selected="true"] { color: #ff4d4d !important; border-bottom-color: #ff4d4d !important; }

    /* ─── Checkboxes ─── */
    .stCheckbox label { color: #aaa !important; }

    /* ─── Tag pills ─── */
    .tag {
        display: inline-block;
        background: rgba(255,77,77,0.1);
        color: #ff4d4d;
        border: 1px solid rgba(255,77,77,0.3);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        font-weight: 600;
        margin: 2px;
    }
    .tag.green { background: rgba(0,255,136,0.1); color: #00ff88; border-color: rgba(0,255,136,0.3); }
    .tag.amber { background: rgba(255,170,0,0.1); color: #ffaa00; border-color: rgba(255,170,0,0.3); }
    .tag.blue { background: rgba(0,150,255,0.1); color: #0096ff; border-color: rgba(0,150,255,0.3); }

    /* ─── Output box ─── */
    .output-box {
        background: #050508;
        border: 1px solid #1e1e30;
        border-radius: 8px;
        padding: 20px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.82rem;
        color: #00ff88;
        white-space: pre-wrap;
        overflow-x: auto;
        max-height: 400px;
        overflow-y: auto;
        margin: 12px 0;
    }

    /* ─── Divider ─── */
    hr { border-color: #1e1e30 !important; }

    /* ─── Expander ─── */
    .streamlit-expanderHeader { color: #aaa !important; }
    </style>
    """, unsafe_allow_html=True)
