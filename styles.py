def get_css():
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
:root {
    --rare-red:   #86000B;
    --beige:      #FFF0C2;
    --hunter:     #1B6337;
    --black:      #1B2419;
    --white:      #FFFFFF;
    --surface:    #F7F4EF;
    --border:     #E0DAD0;
    --text:       #1B2419;
    --muted:      #6B7068;
    --red-hover:  #6A0009;
}
.stApp { background-color: var(--surface) !important; color: var(--text) !important; }
header[data-testid="stHeader"] { display:none; }
footer { display:none; }
#MainMenu { display:none; }

/* Hide sidebar collapse arrow */
[data-testid="stSidebar"] { display:none !important; }
[data-testid="collapsedControl"] { display:none !important; }

/* ── Top Nav Bar ─────────────────────────────────────────────────────────── */
/* Inactive nav / sign-out buttons (secondary type) */
[data-testid="stBaseButton-secondary"],
[data-testid="baseButton-secondary"] {
    background: transparent !important;
    border: none !important;
    border-bottom: 3px solid transparent !important;
    border-radius: 0 !important;
    color: var(--muted) !important;
    font-size: 0.66rem !important;
    font-weight: 600 !important;
    letter-spacing: 2px !important;
    text-transform: uppercase !important;
    padding: 8px 10px !important;
    box-shadow: none !important;
    transition: color 0.15s, border-color 0.15s !important;
}
[data-testid="stBaseButton-secondary"]:hover,
[data-testid="baseButton-secondary"]:hover {
    background: rgba(134,0,11,0.04) !important;
    color: var(--rare-red) !important;
    border-bottom: 3px solid rgba(134,0,11,0.25) !important;
}

/* Active nav button (primary) — same style as all other action buttons */
[data-testid="stBaseButton-primary"],
[data-testid="baseButton-primary"] {
    border-radius: 0 !important;
    padding: 8px 14px !important;
}

/* User label in nav bar */
.nav-user-label {
    font-size: 0.72rem;
    color: var(--muted);
    font-weight: 500;
    letter-spacing: 0.5px;
    line-height: 38px;
    text-align: right;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Header */
.page-header {
    background:var(--white); border-bottom:2px solid var(--rare-red);
    padding:16px 28px 14px; margin:-1rem -1rem 0 -1rem;
}
.header-left { display:flex; flex-direction:column; }
.header-brand { display:flex; align-items:baseline; gap:8px; }
.brand-rare { font-size:1.4rem; font-weight:900; letter-spacing:5px; color:var(--rare-red); }
.brand-gf { font-size:0.65rem; letter-spacing:3px; font-weight:600; color:var(--muted); }
.header-title { font-size:0.7rem; letter-spacing:3px; text-transform:uppercase; color:var(--muted); font-weight:500; margin-top:2px; }

/* Metrics */
.metric-card {
    background:var(--white); border:1px solid var(--border);
    border-top:3px solid var(--rare-red); padding:20px 24px;
    border-radius:2px; margin-top:24px;
}
.metric-label { font-size:0.62rem; letter-spacing:2px; font-weight:700; color:var(--muted); text-transform:uppercase; }
.metric-value { font-size:1.8rem; font-weight:800; color:var(--text); margin-top:4px; line-height:1; }

/* Section title */
.section-title {
    font-size:0.65rem; letter-spacing:3px; font-weight:700; color:var(--muted);
    text-transform:uppercase; margin-bottom:10px; padding:8px 0;
    border-bottom:1px solid var(--border);
}

/* Buttons */
.stButton > button {
    background:var(--rare-red) !important; color:var(--white) !important;
    border:none !important; border-radius:2px !important;
    font-size:0.7rem !important; font-weight:700 !important;
    letter-spacing:2px !important; text-transform:uppercase !important;
    padding:10px 20px !important;
}
.stButton > button:hover { background:var(--red-hover) !important; }
.stDownloadButton > button {
    background:var(--black) !important; color:var(--white) !important;
    border:none !important; border-radius:2px !important;
    font-size:0.7rem !important; font-weight:700 !important;
    letter-spacing:2px !important; padding:10px 24px !important;
}

/* Control panel */
.control-panel {
    background:var(--white); border:1px solid var(--border);
    padding:24px 28px; border-radius:2px;
}

/* Table count */
.table-count {
    font-size:0.7rem; letter-spacing:1px; color:var(--muted);
    margin-bottom:6px; text-transform:uppercase; font-weight:600;
}

/* Alerts */
.alert-success {
    background:#EDF7F0; border-left:4px solid var(--hunter);
    color:#1B4D2A; padding:12px 16px; border-radius:2px;
    font-size:0.82rem; font-weight:500; margin:8px 0;
}
.alert-warn {
    background:#FFF8E1; border-left:4px solid #F59E0B;
    color:#78350F; padding:12px 16px; border-radius:2px;
    font-size:0.82rem; font-weight:500; margin:8px 0;
}
.alert-error {
    background:#FEF2F2; border-left:4px solid var(--rare-red);
    color:#7F1D1D; padding:12px 16px; border-radius:2px;
    font-size:0.82rem; font-weight:500; margin:8px 0;
}

/* Info box */
.info-box {
    background:var(--beige); border-left:4px solid var(--rare-red);
    padding:12px 16px; border-radius:2px;
    font-size:0.82rem; color:var(--text); margin-bottom:8px;
}

/* Source cards */
.source-card {
    background:var(--white); border:1px solid var(--border);
    border-top:3px solid var(--rare-red); padding:20px;
    border-radius:2px; margin-bottom:12px; min-height:100px;
}
.source-title {
    font-size:0.65rem; letter-spacing:3px; font-weight:700;
    color:var(--text); text-transform:uppercase; margin-bottom:8px;
}
.source-desc { font-size:0.78rem; color:var(--muted); line-height:1.5; }

/* Empty state */
.empty-state {
    background:var(--white); border:1px dashed var(--border);
    color:var(--muted); text-align:center; padding:60px 24px;
    font-size:0.82rem; letter-spacing:1px; text-transform:uppercase;
    font-weight:500; border-radius:2px;
}

/* Dataframe */
.stDataFrame { border:1px solid var(--border) !important; border-radius:2px !important; }

/* Login */
.login-left {
    position:relative; overflow:hidden;
    background:#1B2419;
    height:100vh;
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    box-sizing:border-box;
    padding:0;
}
.login-left-img {
    position:absolute;
    top:0; left:0; right:0; bottom:0;
    width:100%; height:100%;
    object-fit:cover; object-position:center;
    z-index:0; display:block;
}
.login-left-overlay {
    position:absolute;
    top:0; left:0; right:0; bottom:0;
    background:rgba(0,0,0,0.30);
    z-index:1;
}
.login-left-content {
    position:relative; z-index:2;
    display:flex; flex-direction:column;
    align-items:center; justify-content:center;
    width:100%; text-align:center;
    padding:48px; box-sizing:border-box;
}
.login-brand-big {
    font-size:3.5rem; font-weight:900; letter-spacing:10px; color:#FFFFFF;
    text-shadow: 0 2px 16px rgba(0,0,0,0.85), 0 0 4px rgba(0,0,0,0.9);
}
.login-brand-sub {
    font-size:0.75rem; letter-spacing:5px; color:#FFFFFF; margin-top:-4px;
    font-weight:700; text-shadow: 0 1px 8px rgba(0,0,0,0.9);
}
.login-tagline {
    margin-top:32px; font-size:1.15rem; color:#FFFFFF; font-weight:600;
    text-align:center; line-height:1.6; max-width:320px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.9);
}
.login-brand-big { font-size:3.5rem; font-weight:900; letter-spacing:10px; color:var(--rare-red); }
.login-brand-sub { font-size:0.75rem; letter-spacing:5px; color:#9EA89B; margin-top:-4px; font-weight:600; }
.login-tagline { margin-top:32px; font-size:1.1rem; color:var(--white); font-weight:300; text-align:center; line-height:1.6; max-width:320px; }
.alert-error { background:#FEF2F2; border-left:4px solid var(--rare-red); color:#7F1D1D; padding:12px 16px; border-radius:2px; font-size:0.82rem; }

/* Login page 50/50 column layout — strip every layer of Streamlit padding */
.main .block-container,
[data-testid="stAppViewBlockContainer"] {
    padding: 0 !important;
    max-width: 100% !important;
}
[data-testid="stMain"] > div {
    padding: 0 !important;
}
div[data-testid="stHorizontalBlock"] {
    gap: 0 !important;
    width: 100% !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] {
    padding: 0 !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child > div,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child [data-testid="stVerticalBlock"],
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child [data-testid="stVerticalBlockBorderWrapper"] {
    padding: 0 !important;
    gap: 0 !important;
    margin: 0 !important;
}
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child .stMarkdown,
div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:first-child .element-container {
    padding: 0 !important;
    margin: 0 !important;
    line-height: 0 !important;
    font-size: 0 !important;
}
</style>
"""
