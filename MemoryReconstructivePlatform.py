import streamlit as st
import sqlite3
import hashlib
import uuid
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, date, timedelta
import random
import time
import os

st.set_page_config(
    page_title="MemoryWeave — Historical Memory Platform",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="collapsed"
)

UI_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=antml&subset=latin');

* { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #f5f5f7;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
}

[data-testid="stAppViewContainer"] { background: #0a0a0f; }
[data-testid="stHeader"] { background: rgba(10,10,15,0.85); backdrop-filter: blur(20px); border-bottom: 1px solid rgba(255,255,255,0.08); }
[data-testid="stSidebar"] { background: rgba(15,15,20,0.95); border-right: 1px solid rgba(255,255,255,0.08); }
[data-testid="stSidebar"] * { color: #f5f5f7 !important; }

section[data-testid="stSidebar"] > div { padding-top: 2rem; }

.stButton > button {
    background: linear-gradient(135deg, #6e5baa 0%, #8b6bbf 100%);
    color: #fff;
    border: none;
    border-radius: 12px;
    padding: 0.6rem 1.4rem;
    font-size: 0.95rem;
    font-weight: 600;
    letter-spacing: 0.01em;
    cursor: pointer;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1);
    width: 100%;
    box-shadow: 0 2px 12px rgba(110,91,170,0.3);
}
.stButton > button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 20px rgba(110,91,170,0.5);
    background: linear-gradient(135deg, #7d6bbf 0%, #9a7acf 100%);
}
.stButton > button:active { transform: translateY(0); }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stDateInput > div > div > input,
.stNumberInput > div > div > input {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: #f5f5f7 !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.6rem 1rem !important;
    transition: border-color 0.2s ease;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6e5baa !important;
    box-shadow: 0 0 0 3px rgba(110,91,170,0.18) !important;
    outline: none !important;
}

.stSelectbox > div { background: rgba(255,255,255,0.06) !important; border-radius: 12px !important; }
.stDateInput > div { background: rgba(255,255,255,0.06) !important; border-radius: 12px !important; }

label, .stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label, .stNumberInput label {
    color: #a1a1b5 !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
    margin-bottom: 4px !important;
}

.card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 1.6rem 1.8rem;
    margin-bottom: 1.2rem;
    backdrop-filter: blur(10px);
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    position: relative;
    overflow: hidden;
}
.card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(110,91,170,0.4), transparent);
}
.card:hover {
    border-color: rgba(110,91,170,0.3);
    background: rgba(255,255,255,0.06);
    transform: translateY(-2px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

.card-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #f5f5f7;
    margin-bottom: 0.5rem;
}
.card-subtitle {
    font-size: 0.82rem;
    color: #6e6e80;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.card-meta {
    font-size: 0.8rem;
    color: #8e8ea0;
    margin-top: 0.8rem;
}

.hero {
    text-align: center;
    padding: 4rem 2rem 3rem;
    position: relative;
}
.hero-title {
    font-size: clamp(2.4rem, 5vw, 3.6rem);
    font-weight: 700;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #f5f5f7 0%, #a78bfa 50%, #c084fc 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 1rem;
}
.hero-sub {
    font-size: 1.15rem;
    color: #8e8ea0;
    font-weight: 400;
    max-width: 600px;
    margin: 0 auto 2.5rem;
    line-height: 1.6;
}

.stat-card {
    background: rgba(110,91,170,0.12);
    border: 1px solid rgba(110,91,170,0.25);
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    transition: all 0.3s ease;
}
.stat-card:hover {
    background: rgba(110,91,170,0.2);
    transform: translateY(-2px);
}
.stat-num {
    font-size: 2.2rem;
    font-weight: 700;
    color: #a78bfa;
    line-height: 1;
    margin-bottom: 0.3rem;
}
.stat-label {
    font-size: 0.78rem;
    color: #6e6e80;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.badge {
    display: inline-block;
    padding: 0.2rem 0.7rem;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.badge-approved { background: rgba(52,199,89,0.15); color: #34c759; border: 1px solid rgba(52,199,89,0.3); }
.badge-pending { background: rgba(255,159,10,0.15); color: #ff9f0a; border: 1px solid rgba(255,159,10,0.3); }
.badge-rejected { background: rgba(255,69,58,0.15); color: #ff453a; border: 1px solid rgba(255,69,58,0.3); }
.badge-locked { background: rgba(142,142,160,0.15); color: #8e8ea0; border: 1px solid rgba(142,142,160,0.3); }
.badge-role { background: rgba(110,91,170,0.15); color: #a78bfa; border: 1px solid rgba(110,91,170,0.3); }
.badge-active { background: rgba(52,199,89,0.1); color: #34c759; border: 1px solid rgba(52,199,89,0.2); }
.badge-suspended { background: rgba(255,69,58,0.1); color: #ff453a; border: 1px solid rgba(255,69,58,0.2); }

.section-header {
    font-size: 0.75rem;
    font-weight: 600;
    color: #6e5baa;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 1.2rem;
    padding-bottom: 0.6rem;
    border-bottom: 1px solid rgba(110,91,170,0.2);
}

.nav-pill {
    display: inline-block;
    padding: 0.45rem 1.1rem;
    border-radius: 22px;
    font-size: 0.88rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    margin: 0.2rem;
    border: 1px solid rgba(255,255,255,0.1);
    color: #8e8ea0;
    background: transparent;
}
.nav-pill:hover { background: rgba(110,91,170,0.15); color: #a78bfa; }
.nav-pill.active { background: rgba(110,91,170,0.25); color: #a78bfa; border-color: rgba(110,91,170,0.4); }

.divider { height: 1px; background: rgba(255,255,255,0.06); margin: 1.5rem 0; }

.timeline-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #6e5baa;
    display: inline-block;
    margin-right: 8px;
    box-shadow: 0 0 6px rgba(110,91,170,0.6);
}

.auth-container {
    max-width: 420px;
    margin: 0 auto;
    padding: 2rem;
}
.auth-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 24px;
    padding: 2.4rem 2.2rem;
    backdrop-filter: blur(20px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.5);
}
.auth-logo {
    text-align: center;
    margin-bottom: 2rem;
}
.auth-logo-text {
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #f5f5f7 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.auth-tagline {
    font-size: 0.82rem;
    color: #6e6e80;
    margin-top: 0.3rem;
    text-align: center;
}

.tab-bar {
    display: flex;
    background: rgba(255,255,255,0.04);
    border-radius: 12px;
    padding: 4px;
    margin-bottom: 1.5rem;
    gap: 2px;
}
.tab-item {
    flex: 1;
    text-align: center;
    padding: 0.5rem;
    border-radius: 10px;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    color: #6e6e80;
}
.tab-item.active {
    background: rgba(110,91,170,0.3);
    color: #a78bfa;
}

.glow-line {
    height: 2px;
    background: linear-gradient(90deg, transparent, #6e5baa, #a78bfa, #6e5baa, transparent);
    border-radius: 2px;
    margin: 1.5rem 0;
    opacity: 0.5;
}

.fragment-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-left: 3px solid #6e5baa;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
    transition: all 0.2s ease;
}
.fragment-card:hover {
    background: rgba(255,255,255,0.05);
    border-left-color: #a78bfa;
}

.conflict-card {
    background: rgba(255,69,58,0.05);
    border: 1px solid rgba(255,69,58,0.2);
    border-left: 3px solid #ff453a;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
}

.merge-card {
    background: rgba(255,159,10,0.05);
    border: 1px solid rgba(255,159,10,0.2);
    border-left: 3px solid #ff9f0a;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.8rem;
}

.page-title {
    font-size: 1.8rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #f5f5f7;
    margin-bottom: 0.3rem;
}
.page-desc {
    font-size: 0.9rem;
    color: #6e6e80;
    margin-bottom: 2rem;
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    gap: 2px !important;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    color: #6e6e80 !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
    padding: 0.5rem 1rem !important;
    border: none !important;
    background: transparent !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(110,91,170,0.3) !important;
    color: #a78bfa !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.5rem !important;
}

.stRadio > div { flex-direction: row !important; gap: 0.5rem; }
.stRadio > div > label {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: 10px !important;
    padding: 0.5rem 1rem !important;
    color: #a1a1b5 !important;
    font-size: 0.85rem !important;
    cursor: pointer;
    transition: all 0.2s;
}
.stRadio > div > label:hover { border-color: rgba(110,91,170,0.4) !important; }

.stMarkdown p { color: #c7c7d4; line-height: 1.6; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: #f5f5f7; letter-spacing: -0.01em; }

.stAlert { border-radius: 12px !important; }
.stSuccess { background: rgba(52,199,89,0.1) !important; border-color: rgba(52,199,89,0.3) !important; }
.stError { background: rgba(255,69,58,0.1) !important; border-color: rgba(255,69,58,0.3) !important; }
.stWarning { background: rgba(255,159,10,0.1) !important; border-color: rgba(255,159,10,0.3) !important; }
.stInfo { background: rgba(110,91,170,0.1) !important; border-color: rgba(110,91,170,0.3) !important; }

[data-testid="metric-container"] {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
}
[data-testid="metric-container"] > div > div { color: #a78bfa !important; }
[data-testid="metric-container"] label { color: #6e6e80 !important; }

.stDataFrame { border-radius: 12px; overflow: hidden; }
.stDataFrame table { background: rgba(255,255,255,0.03) !important; }

.stSlider > div > div > div > div { background: #6e5baa !important; }
.stSlider > div > div > div { background: rgba(255,255,255,0.1) !important; }

.stCheckbox > label { color: #c7c7d4 !important; }
.stCheckbox > label > span { border-color: rgba(255,255,255,0.2) !important; }

.stExpander { background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.08) !important; border-radius: 12px !important; }
.stExpander summary { color: #c7c7d4 !important; }

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: rgba(255,255,255,0.02); }
::-webkit-scrollbar-thumb { background: rgba(110,91,170,0.4); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(110,91,170,0.6); }
</style>
"""

st.markdown(UI_CSS, unsafe_allow_html=True)

DB_PATH = os.path.join(os.getcwd(), "memoryweave.db")

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'Contributor',
        status TEXT NOT NULL DEFAULT 'active',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        parent_id TEXT,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(parent_id) REFERENCES events(id),
        FOREIGN KEY(created_by) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS event_dependencies (
        id TEXT PRIMARY KEY,
        event_id TEXT NOT NULL,
        depends_on TEXT NOT NULL,
        FOREIGN KEY(event_id) REFERENCES events(id),
        FOREIGN KEY(depends_on) REFERENCES events(id)
    );
    CREATE TABLE IF NOT EXISTS fragments (
        id TEXT PRIMARY KEY,
        event_id TEXT NOT NULL,
        contributor_id TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        source_type TEXT NOT NULL,
        confidence_rating REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        citation TEXT,
        locked INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL,
        FOREIGN KEY(event_id) REFERENCES events(id),
        FOREIGN KEY(contributor_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS narrative_branches (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT,
        status TEXT NOT NULL DEFAULT 'active',
        base_branch_id TEXT,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(base_branch_id) REFERENCES narrative_branches(id),
        FOREIGN KEY(created_by) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS narrative_revisions (
        id TEXT PRIMARY KEY,
        branch_id TEXT NOT NULL,
        summary TEXT,
        locked INTEGER NOT NULL DEFAULT 0,
        approved_by TEXT,
        created_by TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(branch_id) REFERENCES narrative_branches(id),
        FOREIGN KEY(created_by) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS revision_fragments (
        revision_id TEXT NOT NULL,
        fragment_id TEXT NOT NULL,
        PRIMARY KEY(revision_id, fragment_id),
        FOREIGN KEY(revision_id) REFERENCES narrative_revisions(id),
        FOREIGN KEY(fragment_id) REFERENCES fragments(id)
    );
    CREATE TABLE IF NOT EXISTS merge_requests (
        id TEXT PRIMARY KEY,
        source_branch_id TEXT NOT NULL,
        target_branch_id TEXT NOT NULL,
        justification TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        submitted_by TEXT NOT NULL,
        reviewed_by TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(source_branch_id) REFERENCES narrative_branches(id),
        FOREIGN KEY(target_branch_id) REFERENCES narrative_branches(id),
        FOREIGN KEY(submitted_by) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS conflicts (
        id TEXT PRIMARY KEY,
        fragment_id TEXT NOT NULL,
        description TEXT NOT NULL,
        conflict_type TEXT NOT NULL,
        resolved INTEGER NOT NULL DEFAULT 0,
        detected_at TEXT NOT NULL,
        FOREIGN KEY(fragment_id) REFERENCES fragments(id)
    );
    CREATE TABLE IF NOT EXISTS audit_logs (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS system_config (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS branch_requests (
        id TEXT PRIMARY KEY,
        narrative_id TEXT NOT NULL,
        requester_id TEXT NOT NULL,
        justification TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending',
        reviewed_by TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(requester_id) REFERENCES users(id)
    );
    CREATE TABLE IF NOT EXISTS confidence_proposals (
        id TEXT PRIMARY KEY,
        fragment_id TEXT NOT NULL,
        proposed_by TEXT NOT NULL,
        new_rating REAL NOT NULL,
        reason TEXT,
        status TEXT NOT NULL DEFAULT 'pending',
        created_at TEXT NOT NULL,
        FOREIGN KEY(fragment_id) REFERENCES fragments(id),
        FOREIGN KEY(proposed_by) REFERENCES users(id)
    );
    """)
    default_config = [
        ("max_confidence", "10"),
        ("source_types", '["Oral Account","Written Record","Photograph","Document","Archaeological","Digital Archive","Newspaper","Interview"]'),
        ("merge_approval_threshold", "1"),
    ]
    for k, v in default_config:
        c.execute("INSERT OR IGNORE INTO system_config(key,value) VALUES(?,?)", (k, v))
    admin_id = str(uuid.uuid4())
    c.execute("INSERT OR IGNORE INTO users(id,username,password_hash,role,status,created_at) VALUES(?,?,?,?,?,?)",
              (admin_id, "admin", hash_pw("Admin@2026"), "SystemAdministrator", "active", now()))
    conn.commit()
    conn.close()

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def now():
    return datetime.now().isoformat()

def gen_id():
    return str(uuid.uuid4())

def log_action(user_id, action, details=""):
    conn = get_conn()
    conn.execute("INSERT INTO audit_logs(id,user_id,action,details,created_at) VALUES(?,?,?,?,?)",
                 (gen_id(), user_id, action, details, now()))
    conn.commit()
    conn.close()

def get_config(key):
    conn = get_conn()
    row = conn.execute("SELECT value FROM system_config WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else None

def authenticate(username, password):
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE username=? AND password_hash=?",
                       (username, hash_pw(password))).fetchone()
    conn.close()
    return dict(row) if row else None

def register_user(username, password, role="Contributor"):
    conn = get_conn()
    existing = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if existing:
        conn.close()
        return False, "Username already exists."
    uid = gen_id()
    conn.execute("INSERT INTO users(id,username,password_hash,role,status,created_at) VALUES(?,?,?,?,?,?)",
                 (uid, username, hash_pw(password), role, "active", now()))
    conn.commit()
    conn.close()
    return True, "Account created successfully."

def get_events():
    conn = get_conn()
    rows = conn.execute("""
        SELECT e.*, u.username as creator_name
        FROM events e JOIN users u ON e.created_by=u.id
        ORDER BY e.start_date
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_fragments(event_id=None, status=None):
    conn = get_conn()
    q = """SELECT f.*, u.username as contributor_name, e.title as event_title
           FROM fragments f
           JOIN users u ON f.contributor_id=u.id
           JOIN events e ON f.event_id=e.id"""
    params = []
    conds = []
    if event_id:
        conds.append("f.event_id=?")
        params.append(event_id)
    if status:
        conds.append("f.status=?")
        params.append(status)
    if conds:
        q += " WHERE " + " AND ".join(conds)
    q += " ORDER BY f.timestamp"
    rows = conn.execute(q, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_branches():
    conn = get_conn()
    rows = conn.execute("""
        SELECT nb.*, u.username as creator_name
        FROM narrative_branches nb JOIN users u ON nb.created_by=u.id
        ORDER BY nb.created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_revisions(branch_id=None):
    conn = get_conn()
    q = """SELECT nr.*, u.username as creator_name, nb.name as branch_name
           FROM narrative_revisions nr
           JOIN users u ON nr.created_by=u.id
           JOIN narrative_branches nb ON nr.branch_id=nb.id"""
    if branch_id:
        q += " WHERE nr.branch_id=? ORDER BY nr.created_at DESC"
        rows = conn.execute(q, (branch_id,)).fetchall()
    else:
        q += " ORDER BY nr.created_at DESC"
        rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_merge_requests(status=None):
    conn = get_conn()
    q = """SELECT mr.*, u.username as submitter_name,
                  sb.name as source_name, tb.name as target_name
           FROM merge_requests mr
           JOIN users u ON mr.submitted_by=u.id
           JOIN narrative_branches sb ON mr.source_branch_id=sb.id
           JOIN narrative_branches tb ON mr.target_branch_id=tb.id"""
    if status:
        q += " WHERE mr.status=? ORDER BY mr.created_at DESC"
        rows = conn.execute(q, (status,)).fetchall()
    else:
        q += " ORDER BY mr.created_at DESC"
        rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_conflicts(resolved=None):
    conn = get_conn()
    q = """SELECT c.*, f.content as fragment_content, e.title as event_title
           FROM conflicts c
           JOIN fragments f ON c.fragment_id=f.id
           JOIN events e ON f.event_id=e.id"""
    if resolved is not None:
        q += " WHERE c.resolved=? ORDER BY c.detected_at DESC"
        rows = conn.execute(q, (1 if resolved else 0,)).fetchall()
    else:
        q += " ORDER BY c.detected_at DESC"
        rows = conn.execute(q).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_users():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_audit_logs(limit=50):
    conn = get_conn()
    rows = conn.execute("""
        SELECT al.*, u.username FROM audit_logs al
        JOIN users u ON al.user_id=u.id
        ORDER BY al.created_at DESC LIMIT ?
    """, (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def validate_fragment_temporal(event_id, fragment_timestamp):
    conn = get_conn()
    event = conn.execute("SELECT * FROM events WHERE id=?", (event_id,)).fetchone()
    conn.close()
    if not event:
        return False, "Event not found."
    try:
        fts = datetime.fromisoformat(fragment_timestamp)
        start = datetime.fromisoformat(event["start_date"])
        end = datetime.fromisoformat(event["end_date"])
        if not (start <= fts <= end):
            return False, f"Fragment timestamp {fragment_timestamp} is outside event range [{event['start_date']} — {event['end_date']}]."
    except Exception:
        return True, "OK"
    return True, "OK"

def check_conflicts_for_fragment(fragment_id, event_id, fragment_timestamp):
    conn = get_conn()
    existing = conn.execute("""
        SELECT * FROM fragments WHERE event_id=? AND id!=? AND status='approved'
    """, (event_id, fragment_id)).fetchall()
    conn.close()
    try:
        fts = datetime.fromisoformat(fragment_timestamp)
    except Exception:
        return
    for f in existing:
        try:
            ets = datetime.fromisoformat(f["timestamp"])
            diff = abs((fts - ets).total_seconds())
            if diff < 86400:
                conn2 = get_conn()
                conn2.execute("INSERT INTO conflicts(id,fragment_id,description,conflict_type,resolved,detected_at) VALUES(?,?,?,?,0,?)",
                              (gen_id(), fragment_id, f"Temporal proximity conflict with fragment {f['id'][:8]}", "Temporal", now()))
                conn2.commit()
                conn2.close()
        except Exception:
            pass

init_db()

if "user" not in st.session_state:
    st.session_state.user = None
if "auth_tab" not in st.session_state:
    st.session_state.auth_tab = "login"
if "active_page" not in st.session_state:
    st.session_state.active_page = "Dashboard"

def render_auth():
    st.markdown("""
    <div style="text-align:center; padding: 3rem 0 1rem;">
        <div style="font-size:2.8rem; font-weight:700; letter-spacing:-0.03em;
                    background:linear-gradient(135deg,#f5f5f7 0%,#a78bfa 50%,#c084fc 100%);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    background-clip:text;">MemoryWeave</div>
        <div style="color:#6e6e80; font-size:0.92rem; margin-top:0.4rem;">
            Collaborative Historical Memory Reconstruction
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        tab_login, tab_register = st.tabs(["Sign In", "Create Account"])

        with tab_login:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            username = st.text_input("Username", key="login_user", placeholder="Enter your username")
            password = st.text_input("Password", type="password", key="login_pass", placeholder="Enter your password")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.button("Sign In", key="btn_login"):
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        if user["status"] == "suspended":
                            st.error("Your account has been suspended. Contact a Moderator.")
                        else:
                            st.session_state.user = user
                            log_action(user["id"], "LOGIN", f"User {username} signed in")
                            st.rerun()
                    else:
                        st.error("Invalid credentials. Please try again.")
                else:
                    st.warning("Please fill in all fields.")

        with tab_register:
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            r_user = st.text_input("Choose a Username", key="reg_user", placeholder="Your username")
            r_pass = st.text_input("Password", type="password", key="reg_pass", placeholder="Min 6 characters")
            r_pass2 = st.text_input("Confirm Password", type="password", key="reg_pass2", placeholder="Repeat password")
            r_role = st.selectbox("Join as", ["Contributor", "Viewer"], key="reg_role")
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
            if st.button("Create Account", key="btn_register"):
                if not r_user or not r_pass:
                    st.warning("Please fill in all required fields.")
                elif len(r_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                elif r_pass != r_pass2:
                    st.error("Passwords do not match.")
                else:
                    ok, msg = register_user(r_user, r_pass, r_role)
                    if ok:
                        st.success(f"{msg} Please sign in.")
                    else:
                        st.error(msg)

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center; color:#3a3a4a; font-size:0.78rem;">
        MemoryWeave Systems &nbsp;·&nbsp; Structured Historical Preservation
    </div>
    """, unsafe_allow_html=True)

def sidebar_nav():
    user = st.session_state.user
    role = user["role"]

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:0.5rem 0 1.5rem;">
            <div style="font-size:1.2rem; font-weight:700; letter-spacing:-0.02em;
                        background:linear-gradient(135deg,#f5f5f7,#a78bfa);
                        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                        background-clip:text;">MemoryWeave</div>
            <div style="color:#6e6e80; font-size:0.75rem; margin-top:0.2rem;">Historical Memory Platform</div>
        </div>
        <div class="card" style="margin-bottom:1.2rem; padding:1rem 1.2rem;">
            <div style="font-size:0.9rem; font-weight:600; color:#f5f5f7;">{user['username']}</div>
            <div class="badge badge-role" style="margin-top:0.4rem;">{role}</div>
        </div>
        """, unsafe_allow_html=True)

        pages_all = ["Dashboard", "Events", "Fragments", "Narrative Branches", "Merge Requests", "Conflicts", "Timeline", "Analytics"]
        pages_editor = ["Review Fragments", "Manage Revisions", "Compare Versions"]
        pages_mod = ["Moderate Users", "Activity Logs"]
        pages_admin = ["User Management", "System Config", "Audit Report"]
        pages_viewer = ["Published Narratives"]

        show_pages = pages_all[:]
        if role in ["NarrativeEditor"]:
            show_pages += pages_editor
        if role in ["Moderator"]:
            show_pages += pages_mod
        if role in ["SystemAdministrator"]:
            show_pages += pages_editor + pages_mod + pages_admin
        if role in ["Viewer"]:
            show_pages = ["Dashboard", "Published Narratives", "Timeline"]

        st.markdown('<div class="section-header">Navigation</div>', unsafe_allow_html=True)
        for page in show_pages:
            active = st.session_state.active_page == page
            if st.button(page, key=f"nav_{page}", use_container_width=True):
                st.session_state.active_page = page
                st.rerun()

        st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        if st.button("Sign Out", key="btn_signout"):
            log_action(user["id"], "LOGOUT", "")
            st.session_state.user = None
            st.rerun()

def page_dashboard():
    user = st.session_state.user
    st.markdown(f"""
    <div class="hero">
        <div class="hero-title">Historical Memory Reconstruction</div>
        <div class="hero-sub">
            Collaborate, validate, and preserve collective narratives with structured version control and temporal consistency.
        </div>
    </div>
    """, unsafe_allow_html=True)

    conn = get_conn()
    total_events = conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    total_fragments = conn.execute("SELECT COUNT(*) FROM fragments").fetchone()[0]
    total_branches = conn.execute("SELECT COUNT(*) FROM narrative_branches").fetchone()[0]
    pending_fragments = conn.execute("SELECT COUNT(*) FROM fragments WHERE status='pending'").fetchone()[0]
    open_conflicts = conn.execute("SELECT COUNT(*) FROM conflicts WHERE resolved=0").fetchone()[0]
    pending_merges = conn.execute("SELECT COUNT(*) FROM merge_requests WHERE status='pending'").fetchone()[0]
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    approved_frags = conn.execute("SELECT COUNT(*) FROM fragments WHERE status='approved'").fetchone()[0]
    conn.close()

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{total_events}</div><div class="stat-label">Historical Events</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{total_fragments}</div><div class="stat-label">Testimony Fragments</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{total_branches}</div><div class="stat-label">Narrative Branches</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{total_users}</div><div class="stat-label">Contributors</div></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        st.metric("Pending Review", pending_fragments, delta=None)
    with c6:
        st.metric("Open Conflicts", open_conflicts, delta=None)
    with c7:
        st.metric("Merge Requests", pending_merges, delta=None)
    with c8:
        st.metric("Approved Fragments", approved_frags, delta=None)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([1.3, 1])

    with col_a:
        st.markdown('<div class="section-header">Fragment Status Overview</div>', unsafe_allow_html=True)
        conn = get_conn()
        status_data = conn.execute("SELECT status, COUNT(*) as cnt FROM fragments GROUP BY status").fetchall()
        conn.close()
        if status_data:
            labels = [r["status"].capitalize() for r in status_data]
            values = [r["cnt"] for r in status_data]
            colors = {"Pending": "#ff9f0a", "Approved": "#34c759", "Rejected": "#ff453a", "Withdrawn": "#8e8ea0"}
            color_list = [colors.get(l, "#6e5baa") for l in labels]
            fig = go.Figure(data=[go.Pie(
                labels=labels, values=values,
                hole=0.6,
                marker=dict(colors=color_list, line=dict(color="#0a0a0f", width=2)),
                textinfo="label+percent",
                textfont=dict(color="#f5f5f7", size=12),
                hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
            )])
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#f5f5f7", family="Inter"),
                showlegend=True,
                legend=dict(font=dict(color="#a1a1b5", size=11), bgcolor="rgba(0,0,0,0)"),
                height=300,
                margin=dict(t=10, b=10, l=10, r=10),
                annotations=[dict(text=f"<b>{sum(values)}</b>", x=0.5, y=0.5, font_size=22, font_color="#f5f5f7", showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No fragments yet. Submit some to see the overview.")

    with col_b:
        st.markdown('<div class="section-header">Recent Activity</div>', unsafe_allow_html=True)
        logs = get_audit_logs(8)
        if logs:
            for log in logs:
                st.markdown(f"""
                <div class="fragment-card">
                    <div style="font-size:0.82rem; font-weight:600; color:#c7c7d4;">{log['action']}</div>
                    <div style="font-size:0.75rem; color:#6e6e80; margin-top:2px;">{log['username']} &nbsp;·&nbsp; {log['created_at'][:16]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown('<div class="card"><div style="color:#6e6e80; text-align:center; padding:1rem;">No activity yet.</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Platform Integrity Metrics</div>', unsafe_allow_html=True)

    conn = get_conn()
    weekly_data = []
    for i in range(7, 0, -1):
        d = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        cnt = conn.execute("SELECT COUNT(*) FROM fragments WHERE created_at LIKE ?", (f"{d}%",)).fetchone()[0]
        weekly_data.append({"day": d[5:], "fragments": cnt})
    conn.close()

    df_weekly = pd.DataFrame(weekly_data)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_weekly["day"], y=df_weekly["fragments"],
        marker=dict(
            color=df_weekly["fragments"],
            colorscale=[[0, "rgba(110,91,170,0.3)"], [1, "rgba(167,139,250,0.9)"]],
            line=dict(color="rgba(110,91,170,0.5)", width=1)
        ),
        hovertemplate="<b>%{x}</b><br>Fragments: %{y}<extra></extra>"
    ))
    fig2.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f5f5f7", family="Inter"),
        xaxis=dict(showgrid=False, color="#6e6e80"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#6e6e80"),
        height=220, margin=dict(t=10, b=30, l=10, r=10),
        title=dict(text="Fragments Submitted — Last 7 Days", font=dict(size=12, color="#6e6e80"), x=0)
    )
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

def page_events():
    user = st.session_state.user
    role = user["role"]
    st.markdown('<div class="page-title">Historical Events</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Create and manage event reconstruction records with temporal boundaries.</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Browse Events", "Create Event"])

    with tab1:
        events = get_events()
        if not events:
            st.markdown('<div class="card" style="text-align:center; padding:2rem;"><div style="color:#6e6e80;">No events yet. Create the first historical event.</div></div>', unsafe_allow_html=True)
        else:
            search = st.text_input("Search events", placeholder="Filter by title...", key="event_search")
            filtered = [e for e in events if search.lower() in e["title"].lower()] if search else events

            for ev in filtered:
                conn = get_conn()
                frag_count = conn.execute("SELECT COUNT(*) FROM fragments WHERE event_id=?", (ev["id"],)).fetchone()[0]
                child_count = conn.execute("SELECT COUNT(*) FROM events WHERE parent_id=?", (ev["id"],)).fetchone()[0]
                conn.close()
                parent_label = ""
                if ev.get("parent_id"):
                    conn = get_conn()
                    parent = conn.execute("SELECT title FROM events WHERE id=?", (ev["parent_id"],)).fetchone()
                    conn.close()
                    if parent:
                        parent_label = f'<span class="badge badge-pending" style="margin-left:0.5rem;">Child of: {parent["title"]}</span>'

                st.markdown(f"""
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div class="card-title">{ev['title']}</div>
                            <div style="color:#6e6e80; font-size:0.82rem; margin-top:2px;">
                                {ev['start_date'][:10]} &nbsp;—&nbsp; {ev['end_date'][:10]}
                                {parent_label}
                            </div>
                            <div style="color:#8e8ea0; font-size:0.78rem; margin-top:0.5rem;">{ev.get('description','')[:120]}</div>
                        </div>
                        <div style="text-align:right; min-width:120px;">
                            <div style="font-size:1.1rem; font-weight:600; color:#a78bfa;">{frag_count}</div>
                            <div style="font-size:0.72rem; color:#6e6e80;">Fragments</div>
                            <div style="font-size:0.82rem; color:#6e6e80; margin-top:4px;">{child_count} Sub-events</div>
                        </div>
                    </div>
                    <div class="card-meta">Created by {ev['creator_name']} &nbsp;·&nbsp; {ev['created_at'][:16]}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        if role not in ["Contributor", "NarrativeEditor", "SystemAdministrator"]:
            st.warning("Only Contributors and Editors can create events.")
            return
        st.markdown('<div class="section-header">New Event Record</div>', unsafe_allow_html=True)
        with st.form("form_create_event"):
            title = st.text_input("Event Title", placeholder="Name this historical event")
            description = st.text_area("Description", placeholder="Provide context and background...")
            c1, c2 = st.columns(2)
            with c1:
                start_date = st.date_input("Start Date", value=date(1990, 1, 1))
            with c2:
                end_date = st.date_input("End Date", value=date(1995, 12, 31))
            events_list = get_events()
            parent_options = ["None"] + [f"{e['title']} ({e['id'][:8]})" for e in events_list]
            parent_sel = st.selectbox("Parent Event (for hierarchy)", parent_options)
            submitted = st.form_submit_button("Create Event")
            if submitted:
                if not title:
                    st.error("Event title is required.")
                elif start_date >= end_date:
                    st.error("Start date must be before end date.")
                else:
                    parent_id = None
                    if parent_sel != "None":
                        pid_str = parent_sel.split("(")[-1].strip(")")
                        match = [e for e in events_list if e["id"].startswith(pid_str)]
                        if match:
                            parent_id = match[0]["id"]
                    eid = gen_id()
                    conn = get_conn()
                    conn.execute("INSERT INTO events(id,title,description,start_date,end_date,parent_id,created_by,created_at) VALUES(?,?,?,?,?,?,?,?)",
                                 (eid, title, description, start_date.isoformat(), end_date.isoformat(), parent_id, user["id"], now()))
                    conn.commit()
                    conn.close()
                    log_action(user["id"], "CREATE_EVENT", f"Created event: {title}")
                    st.success(f"Event '{title}' created successfully.")
                    st.rerun()

def page_fragments():
    user = st.session_state.user
    role = user["role"]
    st.markdown('<div class="page-title">Testimony Fragments</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Submit, view and manage historical testimony fragments with metadata.</div>', unsafe_allow_html=True)

    source_types = json.loads(get_config("source_types") or '["Oral Account","Written Record"]')
    max_conf = float(get_config("max_confidence") or "10")

    tabs = st.tabs(["All Fragments", "Submit Fragment", "My Fragments"])

    with tabs[0]:
        status_filter = st.selectbox("Filter by Status", ["All", "pending", "approved", "rejected", "withdrawn"], key="frag_status_filter")
        status_val = None if status_filter == "All" else status_filter
        fragments = get_fragments(status=status_val)
        if not fragments:
            st.markdown('<div class="card" style="text-align:center; padding:2rem;"><div style="color:#6e6e80;">No fragments found.</div></div>', unsafe_allow_html=True)
        else:
            for f in fragments:
                badge_class = {"pending":"badge-pending","approved":"badge-approved","rejected":"badge-rejected","withdrawn":"badge-locked"}.get(f["status"],"badge-pending")
                lock_icon = " [LOCKED]" if f["locked"] else ""
                st.markdown(f"""
                <div class="fragment-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
                        <div>
                            <span class="badge badge-role">{f['source_type']}</span>
                            <span class="badge {badge_class}" style="margin-left:0.4rem;">{f['status'].upper()}{lock_icon}</span>
                        </div>
                        <div style="font-size:0.78rem; color:#6e6e80;">Confidence: <span style="color:#a78bfa; font-weight:600;">{f['confidence_rating']:.1f}/{max_conf:.0f}</span></div>
                    </div>
                    <div style="font-size:0.9rem; color:#d1d1d8; margin-bottom:0.5rem;">{f['content'][:200]}{'...' if len(f['content'])>200 else ''}</div>
                    <div class="card-meta">
                        Event: <span style="color:#a78bfa;">{f['event_title']}</span> &nbsp;·&nbsp;
                        By: {f['contributor_name']} &nbsp;·&nbsp;
                        {f['timestamp'][:16]}
                        {f'&nbsp;·&nbsp; Ref: {f["citation"]}' if f.get("citation") else ''}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if role in ["NarrativeEditor", "SystemAdministrator"] and f["status"] == "pending":
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button(f"Approve", key=f"approve_{f['id']}"):
                            conn = get_conn()
                            conn.execute("UPDATE fragments SET status='approved' WHERE id=?", (f["id"],))
                            conn.commit()
                            conn.close()
                            check_conflicts_for_fragment(f["id"], f["event_id"], f["timestamp"])
                            log_action(user["id"], "APPROVE_FRAGMENT", f["id"])
                            st.rerun()
                    with c2:
                        if st.button(f"Reject", key=f"reject_{f['id']}"):
                            conn = get_conn()
                            conn.execute("UPDATE fragments SET status='rejected' WHERE id=?", (f["id"],))
                            conn.commit()
                            conn.close()
                            log_action(user["id"], "REJECT_FRAGMENT", f["id"])
                            st.rerun()

    with tabs[1]:
        if role not in ["Contributor", "NarrativeEditor", "SystemAdministrator"]:
            st.warning("Only Contributors can submit fragments.")
            return
        st.markdown('<div class="section-header">Submit Testimony Fragment</div>', unsafe_allow_html=True)
        events = get_events()
        if not events:
            st.warning("No events exist yet. Create an event first.")
            return
        with st.form("form_submit_fragment"):
            event_sel = st.selectbox("Select Event", [f"{e['title']} ({e['id'][:8]})" for e in events])
            content = st.text_area("Fragment Content", placeholder="Describe the historical fragment in detail...", height=120)
            c1, c2 = st.columns(2)
            with c1:
                frag_date = st.date_input("Fragment Date", value=date(1992, 6, 15))
                source_type = st.selectbox("Source Type", source_types)
            with c2:
                confidence = st.slider("Confidence Rating", 1.0, max_conf, 5.0, 0.5)
                citation = st.text_input("Citation / Reference", placeholder="Optional source reference")
            submitted = st.form_submit_button("Submit Fragment")
            if submitted:
                if not content:
                    st.error("Fragment content is required.")
                else:
                    ev_id_str = event_sel.split("(")[-1].strip(")")
                    match = [e for e in events if e["id"].startswith(ev_id_str)]
                    if match:
                        event = match[0]
                        ts = frag_date.isoformat()
                        valid, msg = validate_fragment_temporal(event["id"], ts)
                        if not valid:
                            st.error(f"Temporal Validation Failed: {msg}")
                        else:
                            fid = gen_id()
                            conn = get_conn()
                            conn.execute("INSERT INTO fragments(id,event_id,contributor_id,content,timestamp,source_type,confidence_rating,status,citation,locked,created_at) VALUES(?,?,?,?,?,?,?,?,?,0,?)",
                                         (fid, event["id"], user["id"], content, ts, source_type, confidence, "pending", citation or None, now()))
                            conn.commit()
                            conn.close()
                            log_action(user["id"], "SUBMIT_FRAGMENT", f"Fragment submitted to event: {event['title']}")
                            st.success("Fragment submitted successfully and is pending review.")
                            st.rerun()

    with tabs[2]:
        my_frags = get_fragments()
        my_frags = [f for f in my_frags if f["contributor_id"] == user["id"]]
        if not my_frags:
            st.info("You have not submitted any fragments yet.")
        else:
            for f in my_frags:
                badge_class = {"pending":"badge-pending","approved":"badge-approved","rejected":"badge-rejected","withdrawn":"badge-locked"}.get(f["status"],"badge-pending")
                st.markdown(f"""
                <div class="fragment-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                        <span class="badge badge-role">{f['source_type']}</span>
                        <span class="badge {badge_class}">{f['status'].upper()}</span>
                    </div>
                    <div style="font-size:0.9rem; color:#d1d1d8; margin-bottom:0.4rem;">{f['content'][:160]}...</div>
                    <div class="card-meta">Event: {f['event_title']} &nbsp;·&nbsp; {f['timestamp'][:10]}</div>
                </div>
                """, unsafe_allow_html=True)
                if f["status"] == "pending" and not f["locked"]:
                    if st.button("Withdraw", key=f"withdraw_{f['id']}"):
                        conn = get_conn()
                        conn.execute("UPDATE fragments SET status='withdrawn' WHERE id=?", (f["id"],))
                        conn.commit()
                        conn.close()
                        log_action(user["id"], "WITHDRAW_FRAGMENT", f["id"])
                        st.rerun()

def page_branches():
    user = st.session_state.user
    role = user["role"]
    st.markdown('<div class="page-title">Narrative Branches</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Manage parallel narrative interpretations and versioned revisions.</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["All Branches", "Create Branch", "Revisions"])

    with tab1:
        branches = get_branches()
        if not branches:
            st.markdown('<div class="card" style="text-align:center; padding:2rem;"><div style="color:#6e6e80;">No branches yet.</div></div>', unsafe_allow_html=True)
        else:
            for b in branches:
                conn = get_conn()
                rev_count = conn.execute("SELECT COUNT(*) FROM narrative_revisions WHERE branch_id=?", (b["id"],)).fetchone()[0]
                conn.close()
                status_class = "badge-active" if b["status"] == "active" else "badge-locked"
                st.markdown(f"""
                <div class="card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div class="card-title">{b['name']}</div>
                            <div style="color:#8e8ea0; font-size:0.82rem;">{b.get('description','')[:100]}</div>
                        </div>
                        <div style="text-align:right;">
                            <span class="badge {status_class}">{b['status']}</span>
                            <div style="color:#a78bfa; font-size:1rem; font-weight:600; margin-top:0.4rem;">{rev_count} rev.</div>
                        </div>
                    </div>
                    <div class="card-meta">Created by {b['creator_name']} &nbsp;·&nbsp; {b['created_at'][:16]}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab2:
        if role not in ["Contributor", "NarrativeEditor", "SystemAdministrator"]:
            st.warning("Only Contributors can create branches.")
            return
        with st.form("form_create_branch"):
            name = st.text_input("Branch Name", placeholder="e.g., Alternative Interpretation 1945")
            description = st.text_area("Description", placeholder="Describe the narrative perspective of this branch...")
            branches = get_branches()
            base_options = ["None (New Root)"] + [f"{b['name']} ({b['id'][:8]})" for b in branches]
            base_sel = st.selectbox("Base Branch", base_options)
            submitted = st.form_submit_button("Create Branch")
            if submitted:
                if not name:
                    st.error("Branch name is required.")
                else:
                    base_id = None
                    if base_sel != "None (New Root)":
                        bid_str = base_sel.split("(")[-1].strip(")")
                        match = [b for b in branches if b["id"].startswith(bid_str)]
                        if match:
                            base_id = match[0]["id"]
                    bid = gen_id()
                    conn = get_conn()
                    conn.execute("INSERT INTO narrative_branches(id,name,description,status,base_branch_id,created_by,created_at) VALUES(?,?,?,?,?,?,?)",
                                 (bid, name, description, "active", base_id, user["id"], now()))
                    conn.commit()
                    conn.close()
                    log_action(user["id"], "CREATE_BRANCH", f"Branch: {name}")
                    st.success(f"Branch '{name}' created.")
                    st.rerun()

    with tab3:
        branches = get_branches()
        if not branches:
            st.info("No branches available.")
            return
        sel_branch = st.selectbox("Select Branch", [f"{b['name']} ({b['id'][:8]})" for b in branches], key="rev_branch_sel")
        bid_str = sel_branch.split("(")[-1].strip(")")
        match = [b for b in branches if b["id"].startswith(bid_str)]
        if match:
            selected_branch = match[0]
            revisions = get_revisions(selected_branch["id"])

            with st.expander("Add Revision to this Branch"):
                if role not in ["NarrativeEditor", "SystemAdministrator"]:
                    st.warning("Only Narrative Editors can add revisions.")
                else:
                    with st.form("form_add_revision"):
                        summary = st.text_area("Revision Summary", placeholder="Describe changes in this revision...")
                        submitted = st.form_submit_button("Add Revision")
                        if submitted and summary:
                            rid = gen_id()
                            conn = get_conn()
                            conn.execute("INSERT INTO narrative_revisions(id,branch_id,summary,locked,created_by,created_at) VALUES(?,?,?,0,?,?)",
                                         (rid, selected_branch["id"], summary, user["id"], now()))
                            conn.commit()
                            conn.close()
                            log_action(user["id"], "ADD_REVISION", f"Revision on branch {selected_branch['name']}")
                            st.success("Revision added.")
                            st.rerun()

            if not revisions:
                st.info("No revisions for this branch.")
            else:
                for rev in revisions:
                    locked_badge = '<span class="badge badge-locked">LOCKED</span>' if rev["locked"] else '<span class="badge badge-active">OPEN</span>'
                    st.markdown(f"""
                    <div class="card">
                        <div style="display:flex; justify-content:space-between;">
                            <div class="card-title" style="font-size:0.95rem;">{rev['summary'][:100]}</div>
                            {locked_badge}
                        </div>
                        <div class="card-meta">By {rev['creator_name']} &nbsp;·&nbsp; {rev['created_at'][:16]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if not rev["locked"] and role in ["NarrativeEditor", "SystemAdministrator"]:
                        if st.button("Lock Revision", key=f"lock_rev_{rev['id']}"):
                            conn = get_conn()
                            conn.execute("UPDATE narrative_revisions SET locked=1, approved_by=? WHERE id=?", (user["id"], rev["id"]))
                            conn.commit()
                            conn.close()
                            log_action(user["id"], "LOCK_REVISION", rev["id"])
                            st.success("Revision locked.")
                            st.rerun()

def page_merge_requests():
    user = st.session_state.user
    role = user["role"]
    st.markdown('<div class="page-title">Merge Requests</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Submit and review requests to merge narrative branches.</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["All Merge Requests", "Submit Merge Request"])

    with tab1:
        status_f = st.selectbox("Filter", ["All", "pending", "approved", "rejected"], key="merge_status_f")
        merges = get_merge_requests(None if status_f == "All" else status_f)
        if not merges:
            st.markdown('<div class="card" style="text-align:center; padding:2rem;"><div style="color:#6e6e80;">No merge requests found.</div></div>', unsafe_allow_html=True)
        else:
            for m in merges:
                badge_class = {"pending":"badge-pending","approved":"badge-approved","rejected":"badge-rejected"}.get(m["status"],"badge-pending")
                st.markdown(f"""
                <div class="merge-card">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.5rem;">
                        <div>
                            <span style="color:#ff9f0a; font-weight:600; font-size:0.9rem;">{m['source_name']}</span>
                            <span style="color:#6e6e80; margin:0 0.5rem;">→</span>
                            <span style="color:#a78bfa; font-weight:600; font-size:0.9rem;">{m['target_name']}</span>
                        </div>
                        <span class="badge {badge_class}">{m['status'].upper()}</span>
                    </div>
                    <div style="font-size:0.85rem; color:#c7c7d4; margin-bottom:0.5rem;">{m['justification'][:200]}</div>
                    <div class="card-meta">Submitted by {m['submitter_name']} &nbsp;·&nbsp; {m['created_at'][:16]}</div>
                </div>
                """, unsafe_allow_html=True)

                if role in ["NarrativeEditor", "SystemAdministrator"] and m["status"] == "pending":
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Approve Merge", key=f"merge_approve_{m['id']}"):
                            conn = get_conn()
                            conn.execute("UPDATE merge_requests SET status='approved', reviewed_by=? WHERE id=?", (user["id"], m["id"]))
                            conn.commit()
                            conn.close()
                            log_action(user["id"], "APPROVE_MERGE", m["id"])
                            st.success("Merge request approved.")
                            st.rerun()
                    with c2:
                        if st.button("Reject Merge", key=f"merge_reject_{m['id']}"):
                            conn = get_conn()
                            conn.execute("UPDATE merge_requests SET status='rejected', reviewed_by=? WHERE id=?", (user["id"], m["id"]))
                            conn.commit()
                            conn.close()
                            log_action(user["id"], "REJECT_MERGE", m["id"])
                            st.rerun()

    with tab2:
        if role not in ["Contributor", "NarrativeEditor", "SystemAdministrator"]:
            st.warning("Only Contributors can submit merge requests.")
            return
        branches = get_branches()
        if len(branches) < 2:
            st.warning("At least two branches are needed to submit a merge request.")
            return
        with st.form("form_merge_request"):
            branch_names = [f"{b['name']} ({b['id'][:8]})" for b in branches]
            source = st.selectbox("Source Branch", branch_names, key="merge_src")
            target = st.selectbox("Target Branch", branch_names, key="merge_tgt")
            justification = st.text_area("Justification", placeholder="Explain why these branches should be merged...", height=100)
            submitted = st.form_submit_button("Submit Merge Request")
            if submitted:
                if source == target:
                    st.error("Source and target branches must be different.")
                elif not justification:
                    st.error("Justification is required.")
                else:
                    src_id_str = source.split("(")[-1].strip(")")
                    tgt_id_str = target.split("(")[-1].strip(")")
                    src_match = [b for b in branches if b["id"].startswith(src_id_str)]
                    tgt_match = [b for b in branches if b["id"].startswith(tgt_id_str)]
                    if src_match and tgt_match:
                        mid = gen_id()
                        conn = get_conn()
                        conn.execute("INSERT INTO merge_requests(id,source_branch_id,target_branch_id,justification,status,submitted_by,created_at) VALUES(?,?,?,?,?,?,?)",
                                     (mid, src_match[0]["id"], tgt_match[0]["id"], justification, "pending", user["id"], now()))
                        conn.commit()
                        conn.close()
                        log_action(user["id"], "SUBMIT_MERGE_REQUEST", f"{src_match[0]['name']} -> {tgt_match[0]['name']}")
                        st.success("Merge request submitted.")
                        st.rerun()

def page_conflicts():
    user = st.session_state.user
    role = user["role"]
    st.markdown('<div class="page-title">Conflict Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Review and resolve temporal and logical conflicts between fragments.</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["Open Conflicts", "Resolved Conflicts"])

    with tab1:
        conflicts = get_conflicts(resolved=False)
        if not conflicts:
            st.markdown('<div class="card" style="text-align:center; padding:2rem; border-color:rgba(52,199,89,0.3);"><div style="color:#34c759;">No open conflicts. System integrity is maintained.</div></div>', unsafe_allow_html=True)
        else:
            for c in conflicts:
                st.markdown(f"""
                <div class="conflict-card">
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                        <span class="badge badge-rejected">{c['conflict_type']}</span>
                        <span style="font-size:0.75rem; color:#6e6e80;">{c['detected_at'][:16]}</span>
                    </div>
                    <div style="font-size:0.88rem; color:#d1d1d8; margin-bottom:0.4rem;">{c['description']}</div>
                    <div style="font-size:0.82rem; color:#6e6e80;">Event: <span style="color:#ff453a;">{c['event_title']}</span></div>
                    <div style="font-size:0.78rem; color:#6e6e80; margin-top:4px;">Fragment: {c['fragment_content'][:80]}...</div>
                </div>
                """, unsafe_allow_html=True)
                if role in ["Moderator", "NarrativeEditor", "SystemAdministrator"]:
                    if st.button("Mark as Resolved", key=f"resolve_conflict_{c['id']}"):
                        conn = get_conn()
                        conn.execute("UPDATE conflicts SET resolved=1 WHERE id=?", (c["id"],))
                        conn.commit()
                        conn.close()
                        log_action(user["id"], "RESOLVE_CONFLICT", c["id"])
                        st.success("Conflict marked as resolved.")
                        st.rerun()

    with tab2:
        resolved = get_conflicts(resolved=True)
        if not resolved:
            st.info("No resolved conflicts on record.")
        else:
            for c in resolved:
                st.markdown(f"""
                <div class="fragment-card" style="border-left-color:#34c759;">
                    <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem;">
                        <span class="badge badge-approved">RESOLVED</span>
                        <span class="badge badge-rejected">{c['conflict_type']}</span>
                    </div>
                    <div style="font-size:0.85rem; color:#c7c7d4;">{c['description']}</div>
                    <div class="card-meta">Event: {c['event_title']} &nbsp;·&nbsp; {c['detected_at'][:16]}</div>
                </div>
                """, unsafe_allow_html=True)

def page_timeline():
    st.markdown('<div class="page-title">Event Timeline</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Chronological visualization of all historical events and their hierarchies.</div>', unsafe_allow_html=True)

    events = get_events()
    if not events:
        st.info("No events to display. Create events first.")
        return

    df_events = pd.DataFrame(events)
    df_events["start_date"] = pd.to_datetime(df_events["start_date"])
    df_events["end_date"] = pd.to_datetime(df_events["end_date"])

    color_map = {}
    palette = ["#a78bfa", "#c084fc", "#818cf8", "#60a5fa", "#34d399", "#fb923c", "#f472b6", "#38bdf8"]
    unique_creators = df_events["creator_name"].unique()
    for i, c in enumerate(unique_creators):
        color_map[c] = palette[i % len(palette)]

    fig = go.Figure()
    for i, ev in df_events.iterrows():
        color = color_map.get(ev["creator_name"], "#a78bfa")
        fig.add_trace(go.Scatter(
            x=[ev["start_date"], ev["end_date"]],
            y=[ev["title"], ev["title"]],
            mode="lines+markers",
            line=dict(color=color, width=8),
            marker=dict(size=10, color=color, symbol="circle"),
            name=ev["creator_name"],
            hovertemplate=f"<b>{ev['title']}</b><br>Start: {ev['start_date'].date()}<br>End: {ev['end_date'].date()}<br>Creator: {ev['creator_name']}<extra></extra>",
            showlegend=False
        ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(15,15,25,0.8)",
        font=dict(color="#f5f5f7", family="Inter"),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#6e6e80", title="Date"),
        yaxis=dict(showgrid=False, color="#8e8ea0"),
        height=max(300, len(events) * 55 + 100),
        margin=dict(t=20, b=40, l=20, r=20),
        hovermode="x unified"
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-header" style="margin-top:2rem;">Event Hierarchy Tree</div>', unsafe_allow_html=True)
    parents = {}
    for ev in events:
        pid = ev.get("parent_id")
        if pid not in parents:
            parents[pid] = []
        parents[pid].append(ev)

    def render_tree(parent_id, depth=0):
        children = parents.get(parent_id, [])
        for ev in children:
            indent = "&nbsp;" * (depth * 4)
            dot_color = "#a78bfa" if depth == 0 else "#6e5baa"
            st.markdown(f"""
            <div style="padding:0.4rem 0; border-left: 2px solid rgba(110,91,170,0.2); margin-left:{depth*16}px; padding-left:12px;">
                <span style="color:{dot_color}; font-weight:600; font-size:0.88rem;">{ev['title']}</span>
                <span style="color:#6e6e80; font-size:0.75rem; margin-left:0.5rem;">{ev['start_date'][:10]} — {ev['end_date'][:10]}</span>
            </div>
            """, unsafe_allow_html=True)
            render_tree(ev["id"], depth + 1)

    render_tree(None)

def page_analytics():
    st.markdown('<div class="page-title">Platform Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Insights, trends, and integrity metrics across the platform.</div>', unsafe_allow_html=True)

    conn = get_conn()
    frags = conn.execute("SELECT * FROM fragments").fetchall()
    conn.close()
    df_frags = pd.DataFrame([dict(f) for f in frags]) if frags else pd.DataFrame()

    c1, c2 = st.columns(2)

    with c1:
        st.markdown('<div class="section-header">Confidence Distribution</div>', unsafe_allow_html=True)
        if not df_frags.empty:
            fig = px.histogram(
                df_frags, x="confidence_rating", nbins=10,
                color_discrete_sequence=["#6e5baa"],
                labels={"confidence_rating": "Confidence Rating", "count": "Fragments"}
            )
            fig.update_traces(marker_line_color="#a78bfa", marker_line_width=1)
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,15,25,0.8)",
                font=dict(color="#f5f5f7", family="Inter"),
                xaxis=dict(showgrid=False, color="#6e6e80"),
                yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#6e6e80"),
                height=280, margin=dict(t=10, b=30, l=10, r=10), showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No fragment data yet.")

    with c2:
        st.markdown('<div class="section-header">Source Type Breakdown</div>', unsafe_allow_html=True)
        if not df_frags.empty:
            source_counts = df_frags["source_type"].value_counts().reset_index()
            source_counts.columns = ["source_type", "count"]
            fig2 = px.bar(
                source_counts, x="count", y="source_type", orientation="h",
                color="count", color_continuous_scale=["#3a2a6e", "#a78bfa"],
                labels={"count": "Fragments", "source_type": "Source Type"}
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,15,25,0.8)",
                font=dict(color="#f5f5f7", family="Inter"),
                xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#6e6e80"),
                yaxis=dict(showgrid=False, color="#6e6e80"),
                height=280, margin=dict(t=10, b=30, l=10, r=10), coloraxis_showscale=False, showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No fragment data yet.")

    st.markdown('<div class="glow-line"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-header">Narrative Branch Activity</div>', unsafe_allow_html=True)

    branches = get_branches()
    if branches:
        branch_data = []
        for b in branches:
            conn = get_conn()
            rev_count = conn.execute("SELECT COUNT(*) FROM narrative_revisions WHERE branch_id=?", (b["id"],)).fetchone()[0]
            conn.close()
            branch_data.append({"branch": b["name"][:25], "revisions": rev_count, "status": b["status"]})
        df_br = pd.DataFrame(branch_data)
        fig3 = go.Figure(go.Bar(
            x=df_br["branch"], y=df_br["revisions"],
            marker=dict(
                color=["#34c759" if s == "active" else "#6e6e80" for s in df_br["status"]],
                line=dict(color="rgba(255,255,255,0.1)", width=1)
            ),
            hovertemplate="<b>%{x}</b><br>Revisions: %{y}<extra></extra>"
        ))
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,15,25,0.8)",
            font=dict(color="#f5f5f7", family="Inter"),
            xaxis=dict(showgrid=False, color="#6e6e80"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#6e6e80"),
            height=240, margin=dict(t=10, b=40, l=10, r=10)
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-header" style="margin-top:1.5rem;">3D Confidence vs. Source vs. Status</div>', unsafe_allow_html=True)
    if not df_frags.empty:
        status_num = {"pending": 1, "approved": 2, "rejected": 0, "withdrawn": 3}
        df_frags["status_num"] = df_frags["status"].map(status_num).fillna(1)
        df_frags["source_idx"] = pd.factorize(df_frags["source_type"])[0]
        color_scale = {0: "#ff453a", 1: "#ff9f0a", 2: "#34c759", 3: "#8e8ea0"}
        fig4 = go.Figure(data=[go.Scatter3d(
            x=df_frags["source_idx"],
            y=df_frags["confidence_rating"],
            z=df_frags["status_num"],
            mode="markers",
            marker=dict(
                size=6,
                color=df_frags["status_num"],
                colorscale=[[0, "#ff453a"], [0.33, "#ff9f0a"], [0.66, "#34c759"], [1, "#a78bfa"]],
                opacity=0.8,
                line=dict(color="rgba(255,255,255,0.1)", width=0.5)
            ),
            hovertemplate="Source: %{x}<br>Confidence: %{y}<br>Status Code: %{z}<extra></extra>"
        )])
        fig4.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            scene=dict(
                bgcolor="rgba(15,15,25,0.8)",
                xaxis=dict(title="Source Type (Index)", color="#6e6e80", gridcolor="rgba(255,255,255,0.05)"),
                yaxis=dict(title="Confidence", color="#6e6e80", gridcolor="rgba(255,255,255,0.05)"),
                zaxis=dict(title="Status", color="#6e6e80", gridcolor="rgba(255,255,255,0.05)")
            ),
            font=dict(color="#f5f5f7", family="Inter"),
            height=420,
            margin=dict(t=10, b=10, l=10, r=10)
        )
        st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("Submit fragments to see the 3D analysis.")

def page_moderate_users():
    user = st.session_state.user
    role = user["role"]
    if role not in ["Moderator", "SystemAdministrator"]:
        st.error("Access denied.")
        return

    st.markdown('<div class="page-title">Moderate Users</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Manage contributor access, review policy violations, and maintain platform integrity.</div>', unsafe_allow_html=True)

    users = get_users()
    for u in users:
        if u["id"] == user["id"]:
            continue
        if u["role"] in ["SystemAdministrator"]:
            continue
        status_badge = "badge-active" if u["status"] == "active" else "badge-suspended"
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <div style="font-size:0.95rem; font-weight:600; color:#f5f5f7;">{u['username']}</div>
                    <div style="margin-top:4px;">
                        <span class="badge badge-role">{u['role']}</span>
                        <span class="badge {status_badge}" style="margin-left:0.4rem;">{u['status'].upper()}</span>
                    </div>
                </div>
                <div style="font-size:0.78rem; color:#6e6e80;">{u['created_at'][:10]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if u["status"] == "active":
                if st.button("Suspend", key=f"suspend_{u['id']}"):
                    conn = get_conn()
                    conn.execute("UPDATE users SET status='suspended' WHERE id=?", (u["id"],))
                    conn.commit()
                    conn.close()
                    log_action(user["id"], "SUSPEND_USER", u["username"])
                    st.rerun()
            else:
                if st.button("Restore", key=f"restore_{u['id']}"):
                    conn = get_conn()
                    conn.execute("UPDATE users SET status='active' WHERE id=?", (u["id"],))
                    conn.commit()
                    conn.close()
                    log_action(user["id"], "RESTORE_USER", u["username"])
                    st.rerun()

def page_user_management():
    user = st.session_state.user
    if user["role"] != "SystemAdministrator":
        st.error("Access denied.")
        return

    st.markdown('<div class="page-title">User Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Create accounts, assign roles, and manage platform users.</div>', unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["All Users", "Create User"])

    with tab1:
        users = get_users()
        roles = ["Contributor", "NarrativeEditor", "Moderator", "SystemAdministrator", "Viewer"]
        for u in users:
            status_badge = "badge-active" if u["status"] == "active" else "badge-suspended"
            st.markdown(f"""
            <div class="card" style="padding:1rem 1.4rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span style="font-weight:600; color:#f5f5f7;">{u['username']}</span>
                        <span class="badge badge-role" style="margin-left:0.5rem;">{u['role']}</span>
                        <span class="badge {status_badge}" style="margin-left:0.4rem;">{u['status']}</span>
                    </div>
                    <div style="font-size:0.75rem; color:#6e6e80;">{u['created_at'][:10]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if u["id"] != user["id"]:
                c1, c2, c3 = st.columns(3)
                with c1:
                    new_role = st.selectbox("Change Role", roles, index=roles.index(u["role"]) if u["role"] in roles else 0, key=f"role_{u['id']}")
                with c2:
                    if st.button("Update Role", key=f"update_role_{u['id']}"):
                        conn = get_conn()
                        conn.execute("UPDATE users SET role=? WHERE id=?", (new_role, u["id"]))
                        conn.commit()
                        conn.close()
                        log_action(user["id"], "CHANGE_ROLE", f"{u['username']} -> {new_role}")
                        st.success("Role updated.")
                        st.rerun()
                with c3:
                    if u["status"] == "active":
                        if st.button("Deactivate", key=f"deact_{u['id']}"):
                            conn = get_conn()
                            conn.execute("UPDATE users SET status='suspended' WHERE id=?", (u["id"],))
                            conn.commit()
                            conn.close()
                            log_action(user["id"], "DEACTIVATE_USER", u["username"])
                            st.rerun()
                    else:
                        if st.button("Activate", key=f"act_{u['id']}"):
                            conn = get_conn()
                            conn.execute("UPDATE users SET status='active' WHERE id=?", (u["id"],))
                            conn.commit()
                            conn.close()
                            log_action(user["id"], "ACTIVATE_USER", u["username"])
                            st.rerun()

    with tab2:
        with st.form("form_create_user_admin"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            role_sel = st.selectbox("Role", ["Contributor", "NarrativeEditor", "Moderator", "Viewer", "SystemAdministrator"])
            submitted = st.form_submit_button("Create User")
            if submitted:
                if not username or not password:
                    st.error("Username and password are required.")
                else:
                    ok, msg = register_user(username, password, role_sel)
                    if ok:
                        log_action(user["id"], "CREATE_USER", f"Created {username} as {role_sel}")
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

def page_system_config():
    user = st.session_state.user
    if user["role"] != "SystemAdministrator":
        st.error("Access denied.")
        return

    st.markdown('<div class="page-title">System Configuration</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Configure confidence scales, source types, and merge thresholds.</div>', unsafe_allow_html=True)

    with st.form("form_system_config"):
        st.markdown('<div class="section-header">Confidence Rating Scale</div>', unsafe_allow_html=True)
        max_conf = st.slider("Maximum Confidence Rating", 5, 20, int(float(get_config("max_confidence") or 10)))

        st.markdown('<div class="section-header" style="margin-top:1rem;">Source Types</div>', unsafe_allow_html=True)
        current_types = json.loads(get_config("source_types") or '[]')
        source_types_input = st.text_area("Source Types (one per line)", value="\n".join(current_types), height=120)

        st.markdown('<div class="section-header" style="margin-top:1rem;">Merge Approval Threshold</div>', unsafe_allow_html=True)
        threshold = st.number_input("Required Approvals", min_value=1, max_value=10, value=int(get_config("merge_approval_threshold") or 1))

        submitted = st.form_submit_button("Save Configuration")
        if submitted:
            new_types = [t.strip() for t in source_types_input.split("\n") if t.strip()]
            conn = get_conn()
            conn.execute("INSERT OR REPLACE INTO system_config(key,value) VALUES('max_confidence',?)", (str(max_conf),))
            conn.execute("INSERT OR REPLACE INTO system_config(key,value) VALUES('source_types',?)", (json.dumps(new_types),))
            conn.execute("INSERT OR REPLACE INTO system_config(key,value) VALUES('merge_approval_threshold',?)", (str(threshold),))
            conn.commit()
            conn.close()
            log_action(user["id"], "UPDATE_SYSTEM_CONFIG", f"max_conf={max_conf}, threshold={threshold}")
            st.success("Configuration saved.")

def page_audit_report():
    user = st.session_state.user
    if user["role"] != "SystemAdministrator":
        st.error("Access denied.")
        return

    st.markdown('<div class="page-title">Audit Report</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Complete audit trail of all platform actions and narrative revisions.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        start_f = st.date_input("From Date", value=date.today() - timedelta(days=30))
    with c2:
        end_f = st.date_input("To Date", value=date.today())

    conn = get_conn()
    logs = conn.execute("""
        SELECT al.*, u.username FROM audit_logs al
        JOIN users u ON al.user_id=u.id
        WHERE al.created_at >= ? AND al.created_at <= ?
        ORDER BY al.created_at DESC
    """, (start_f.isoformat(), (end_f + timedelta(days=1)).isoformat())).fetchall()
    conn.close()

    logs_data = [dict(l) for l in logs]

    if not logs_data:
        st.info("No audit records for the selected period.")
        return

    df_logs = pd.DataFrame(logs_data)
    action_counts = df_logs["action"].value_counts().reset_index()
    action_counts.columns = ["action", "count"]

    fig = px.bar(action_counts, x="count", y="action", orientation="h",
                 color="count", color_continuous_scale=["#3a2a6e","#a78bfa"],
                 labels={"count":"Count","action":"Action"})
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15,15,25,0.8)",
        font=dict(color="#f5f5f7", family="Inter"),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", color="#6e6e80"),
        yaxis=dict(showgrid=False, color="#6e6e80"),
        height=300, margin=dict(t=10, b=20, l=10, r=10), coloraxis_showscale=False, showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="section-header">Detailed Log</div>', unsafe_allow_html=True)
    display_df = df_logs[["username","action","details","created_at"]].rename(columns={
        "username":"User","action":"Action","details":"Details","created_at":"Timestamp"
    })
    display_df["Timestamp"] = display_df["Timestamp"].str[:16]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def page_activity_logs():
    user = st.session_state.user
    role = user["role"]
    if role not in ["Moderator", "SystemAdministrator"]:
        st.error("Access denied.")
        return

    st.markdown('<div class="page-title">Activity Logs</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Monitor contributor activity for suspicious editing patterns.</div>', unsafe_allow_html=True)

    logs = get_audit_logs(100)
    if not logs:
        st.info("No activity logs found.")
        return

    user_activity = {}
    for log in logs:
        uname = log["username"]
        if uname not in user_activity:
            user_activity[uname] = []
        user_activity[uname].append(log)

    for uname, acts in user_activity.items():
        with st.expander(f"{uname} — {len(acts)} actions"):
            for a in acts[:15]:
                badge_color = "#a78bfa" if "CREATE" in a["action"] else "#ff9f0a" if "APPROVE" in a["action"] else "#ff453a" if "REJECT" in a["action"] or "SUSPEND" in a["action"] else "#6e6e80"
                st.markdown(f"""
                <div style="display:flex; justify-content:space-between; padding:0.4rem 0; border-bottom:1px solid rgba(255,255,255,0.04);">
                    <span style="color:{badge_color}; font-size:0.82rem; font-weight:500;">{a['action']}</span>
                    <span style="color:#6e6e80; font-size:0.75rem;">{a['created_at'][:16]}</span>
                </div>
                """, unsafe_allow_html=True)

def page_review_fragments():
    user = st.session_state.user
    role = user["role"]
    if role not in ["NarrativeEditor", "SystemAdministrator"]:
        st.error("Access denied.")
        return
    st.markdown('<div class="page-title">Review Fragments</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Approve or reject pending testimony fragments for inclusion in narratives.</div>', unsafe_allow_html=True)

    fragments = get_fragments(status="pending")
    if not fragments:
        st.markdown('<div class="card" style="text-align:center; padding:2rem; border-color:rgba(52,199,89,0.3);"><div style="color:#34c759;">All fragments have been reviewed. Queue is clear.</div></div>', unsafe_allow_html=True)
        return

    for f in fragments:
        st.markdown(f"""
        <div class="card">
            <div style="display:flex; justify-content:space-between; margin-bottom:0.8rem;">
                <div>
                    <span class="badge badge-role">{f['source_type']}</span>
                    <span class="badge badge-pending" style="margin-left:0.4rem;">PENDING REVIEW</span>
                </div>
                <div style="color:#a78bfa; font-weight:600;">Confidence: {f['confidence_rating']:.1f}</div>
            </div>
            <div style="font-size:0.92rem; color:#d1d1d8; line-height:1.5; margin-bottom:0.8rem;">{f['content']}</div>
            <div style="font-size:0.8rem; color:#6e6e80;">
                Event: <span style="color:#a78bfa;">{f['event_title']}</span> &nbsp;·&nbsp;
                Contributor: {f['contributor_name']} &nbsp;·&nbsp;
                Date: {f['timestamp'][:10]}
                {f'&nbsp;·&nbsp; Ref: {f["citation"]}' if f.get("citation") else ''}
            </div>
        </div>
        """, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Approve Fragment", key=f"rev_approve_{f['id']}"):
                conn = get_conn()
                conn.execute("UPDATE fragments SET status='approved' WHERE id=?", (f["id"],))
                conn.commit()
                conn.close()
                check_conflicts_for_fragment(f["id"], f["event_id"], f["timestamp"])
                log_action(user["id"], "APPROVE_FRAGMENT", f["id"])
                st.success("Fragment approved.")
                st.rerun()
        with c2:
            if st.button("Reject Fragment", key=f"rev_reject_{f['id']}"):
                conn = get_conn()
                conn.execute("UPDATE fragments SET status='rejected' WHERE id=?", (f["id"],))
                conn.commit()
                conn.close()
                log_action(user["id"], "REJECT_FRAGMENT", f["id"])
                st.rerun()

def page_compare_versions():
    user = st.session_state.user
    role = user["role"]
    if role not in ["NarrativeEditor", "SystemAdministrator"]:
        st.error("Access denied.")
        return

    st.markdown('<div class="page-title">Compare Narrative Versions</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Side-by-side comparison of narrative revisions to identify differences.</div>', unsafe_allow_html=True)

    revisions = get_revisions()
    if len(revisions) < 2:
        st.info("At least two revisions are needed for comparison.")
        return

    rev_options = [f"{r['branch_name']} — {r['summary'][:40]} ({r['id'][:8]})" for r in revisions]
    c1, c2 = st.columns(2)
    with c1:
        sel_a = st.selectbox("Version A", rev_options, key="compare_a")
    with c2:
        sel_b = st.selectbox("Version B", rev_options, index=min(1, len(rev_options)-1), key="compare_b")

    if st.button("Compare Versions"):
        aid = sel_a.split("(")[-1].strip(")")
        bid = sel_b.split("(")[-1].strip(")")
        rev_a = next((r for r in revisions if r["id"].startswith(aid)), None)
        rev_b = next((r for r in revisions if r["id"].startswith(bid)), None)
        if rev_a and rev_b:
            log_action(user["id"], "COMPARE_VERSIONS", f"{aid} vs {bid}")
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class="card">
                    <div class="card-subtitle">Version A</div>
                    <div class="card-title">{rev_a['branch_name']}</div>
                    <div style="color:#c7c7d4; font-size:0.88rem; margin-top:0.5rem;">{rev_a['summary']}</div>
                    <div class="card-meta">By {rev_a['creator_name']} &nbsp;·&nbsp; {rev_a['created_at'][:16]}</div>
                    <div style="margin-top:0.8rem;">
                        {'<span class="badge badge-locked">LOCKED</span>' if rev_a['locked'] else '<span class="badge badge-active">OPEN</span>'}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class="card" style="border-color:rgba(110,91,170,0.3);">
                    <div class="card-subtitle">Version B</div>
                    <div class="card-title">{rev_b['branch_name']}</div>
                    <div style="color:#c7c7d4; font-size:0.88rem; margin-top:0.5rem;">{rev_b['summary']}</div>
                    <div class="card-meta">By {rev_b['creator_name']} &nbsp;·&nbsp; {rev_b['created_at'][:16]}</div>
                    <div style="margin-top:0.8rem;">
                        {'<span class="badge badge-locked">LOCKED</span>' if rev_b['locked'] else '<span class="badge badge-active">OPEN</span>'}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            conn = get_conn()
            frags_a = conn.execute("""
                SELECT f.content, f.source_type, f.confidence_rating FROM revision_fragments rf
                JOIN fragments f ON rf.fragment_id=f.id WHERE rf.revision_id=?
            """, (rev_a["id"],)).fetchall()
            frags_b = conn.execute("""
                SELECT f.content, f.source_type, f.confidence_rating FROM revision_fragments rf
                JOIN fragments f ON rf.fragment_id=f.id WHERE rf.revision_id=?
            """, (rev_b["id"],)).fetchall()
            conn.close()

            st.markdown('<div class="section-header" style="margin-top:1.5rem;">Differences Summary</div>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="card">
                <div style="display:flex; gap:2rem;">
                    <div><div style="font-size:1.4rem; font-weight:700; color:#a78bfa;">{len(frags_a)}</div><div style="color:#6e6e80; font-size:0.78rem;">Fragments in A</div></div>
                    <div><div style="font-size:1.4rem; font-weight:700; color:#60a5fa;">{len(frags_b)}</div><div style="color:#6e6e80; font-size:0.78rem;">Fragments in B</div></div>
                    <div><div style="font-size:1.4rem; font-weight:700; color:#34c759;">{abs(len(frags_a)-len(frags_b))}</div><div style="color:#6e6e80; font-size:0.78rem;">Delta</div></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def page_published_narratives():
    st.markdown('<div class="page-title">Published Narratives</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-desc">Browse approved and locked narrative branches available to all readers.</div>', unsafe_allow_html=True)

    branches = get_branches()
    active_branches = [b for b in branches if b["status"] == "active"]

    if not active_branches:
        st.info("No published narratives available yet.")
        return

    for b in active_branches:
        revisions = get_revisions(b["id"])
        locked_revisions = [r for r in revisions if r["locked"]]

        st.markdown(f"""
        <div class="card">
            <div class="card-title">{b['name']}</div>
            <div style="color:#8e8ea0; font-size:0.85rem; margin-top:4px;">{b.get('description','No description.')}</div>
            <div class="card-meta" style="margin-top:0.8rem;">
                Created by {b['creator_name']} &nbsp;·&nbsp; {b['created_at'][:16]} &nbsp;·&nbsp;
                <span style="color:#a78bfa;">{len(locked_revisions)} published revision(s)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if locked_revisions:
            with st.expander(f"View {len(locked_revisions)} revision(s)"):
                for rev in locked_revisions:
                    st.markdown(f"""
                    <div class="fragment-card" style="border-left-color:#34c759;">
                        <div style="font-size:0.9rem; font-weight:600; color:#f5f5f7; margin-bottom:4px;">{rev['summary']}</div>
                        <div class="card-meta">By {rev['creator_name']} &nbsp;·&nbsp; {rev['created_at'][:16]}</div>
                    </div>
                    """, unsafe_allow_html=True)

def page_manage_revisions():
    page_branches()

def main():
    if st.session_state.user is None:
        render_auth()
        return

    sidebar_nav()
    page = st.session_state.active_page

    st.markdown("<div style='padding: 1.5rem 1rem 0;'>", unsafe_allow_html=True)

    page_map = {
        "Dashboard": page_dashboard,
        "Events": page_events,
        "Fragments": page_fragments,
        "Narrative Branches": page_branches,
        "Merge Requests": page_merge_requests,
        "Conflicts": page_conflicts,
        "Timeline": page_timeline,
        "Analytics": page_analytics,
        "Review Fragments": page_review_fragments,
        "Manage Revisions": page_manage_revisions,
        "Compare Versions": page_compare_versions,
        "Moderate Users": page_moderate_users,
        "Activity Logs": page_activity_logs,
        "User Management": page_user_management,
        "System Config": page_system_config,
        "Audit Report": page_audit_report,
        "Published Narratives": page_published_narratives,
    }

    fn = page_map.get(page)
    if fn:
        fn()
    else:
        page_dashboard()

    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()