import streamlit as st
from matcher import screen_resume
from utils import extract_text_from_pdf, extract_text_from_docx

st.set_page_config(
    page_title="RecruitIQ · Resume Screener",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    --bg:        #F0F4FF;
    --surface:   #FFFFFF;
    --border:    #E2E8F8;
    --border2:   #C7D2EE;
    --blue:      #2563EB;
    --blue-lt:   #EEF2FF;
    --blue-md:   #BFCFFE;
    --green:     #10B981;
    --green-lt:  #ECFDF5;
    --amber:     #F59E0B;
    --amber-lt:  #FFFBEB;
    --red:       #EF4444;
    --red-lt:    #FEF2F2;
    --text:      #0F172A;
    --text2:     #475569;
    --text3:     #94A3B8;
    --shadow:    0 1px 3px rgba(0,0,0,.08), 0 4px 16px rgba(37,99,235,.06);
    --shadow-lg: 0 8px 32px rgba(37,99,235,.12), 0 2px 8px rgba(0,0,0,.06);
}

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 2rem 2rem !important; max-width: 1300px !important; }

.topbar {
    background: var(--surface);
    border-bottom: 1px solid var(--border);
    padding: 0 2rem;
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 -2rem 2rem;
    box-shadow: 0 1px 0 var(--border), 0 2px 12px rgba(37,99,235,.06);
}
.topbar-logo {
    width: 32px; height: 32px;
    background: var(--blue);
    border-radius: 8px;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 16px; margin-right: 10px;
    vertical-align: middle;
}
.topbar-name { font-size: 1.1rem; font-weight: 800; color: var(--text); letter-spacing: -0.02em; }
.topbar-name span { color: var(--blue); }
.topbar-badge {
    background: var(--blue-lt); color: var(--blue);
    font-size: 0.68rem; font-weight: 700;
    padding: 3px 10px; border-radius: 20px;
    letter-spacing: 0.06em; border: 1px solid var(--blue-md);
}

.card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 1.4rem 1.5rem;
    box-shadow: var(--shadow);
    margin-bottom: 1rem;
}
.card-title {
    font-size: 0.68rem; font-weight: 700;
    letter-spacing: 0.12em; text-transform: uppercase;
    color: var(--text3); margin-bottom: 1rem;
}

.score-wrap {
    background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 55%, #0EA5E9 100%);
    border-radius: 16px; padding: 1.8rem 1.5rem; text-align: center;
    position: relative; overflow: hidden;
    box-shadow: var(--shadow-lg);
}
.score-wrap::before {
    content:''; position:absolute; top:-40px; right:-40px;
    width:180px; height:180px; background:rgba(255,255,255,.06); border-radius:50%;
}
.score-number {
    font-family: 'JetBrains Mono', monospace;
    font-size: 4.2rem; font-weight: 600; color: #fff;
    line-height: 1; letter-spacing: -0.03em; position: relative; z-index: 1;
}
.score-pct { font-size: 1.8rem; opacity: 0.65; }
.score-label {
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.15em;
    text-transform: uppercase; color: rgba(255,255,255,.55);
    margin-top: 0.4rem; position: relative; z-index: 1;
}

.prog-wrap { background:var(--border); border-radius:99px; height:8px; margin:1rem 0 0.3rem; overflow:hidden; }
.prog-fill  { height:100%; border-radius:99px; }

.verdict {
    border-radius: 12px; padding: 0.9rem 1.2rem;
    font-size: 0.85rem; font-weight: 600;
    display: flex; align-items: center; gap: 10px;
    margin-top: 1rem; border: 1px solid;
}
.v-strong   { background:var(--green-lt); color:#065F46; border-color:#A7F3D0; }
.v-moderate { background:var(--amber-lt); color:#92400E; border-color:#FDE68A; }
.v-weak     { background:var(--red-lt);   color:#991B1B; border-color:#FECACA; }

.stats-row { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin-top:1rem; }
.stat-tile {
    background:var(--bg); border:1px solid var(--border);
    border-radius:12px; padding:1rem; text-align:center;
}
.stat-num { font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:600; color:var(--blue); line-height:1; }
.stat-lbl { font-size:0.66rem; font-weight:600; letter-spacing:0.08em; text-transform:uppercase; color:var(--text3); margin-top:4px; }

.chips-wrap { display:flex; flex-wrap:wrap; gap:6px; }
.chip {
    font-family:'JetBrains Mono',monospace; font-size:0.71rem; font-weight:500;
    padding:4px 11px; border-radius:6px; border:1px solid; display:inline-flex; align-items:center; gap:4px;
}
.chip-green { background:var(--green-lt); color:#065F46; border-color:#A7F3D0; }
.chip-red   { background:var(--red-lt);   color:#991B1B; border-color:#FECACA; }
.chip-blue  { background:var(--blue-lt);  color:#1E40AF; border-color:var(--blue-md); }

.sug-item {
    background:var(--bg); border:1px solid var(--border);
    border-radius:12px; padding:0.9rem 1.1rem; margin-bottom:8px;
    display:flex; align-items:flex-start; gap:12px;
}
.sug-icon { width:36px;height:36px;min-width:36px;border-radius:9px;display:flex;align-items:center;justify-content:center;font-size:1.1rem; }
.sug-title { font-size:0.84rem; font-weight:700; color:var(--text); margin-bottom:2px; }
.sug-desc  { font-size:0.77rem; color:var(--text2); line-height:1.5; }
.sug-priority {
    font-size:0.63rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
    padding:2px 8px; border-radius:4px; margin-top:6px; display:inline-block;
}
.pri-high   { background:#FEE2E2; color:#991B1B; }
.pri-medium { background:#FEF3C7; color:#92400E; }
.pri-low    { background:#DBEAFE; color:#1E40AF; }

div[data-testid="stFileUploader"] {
    background:var(--surface) !important; border:2px dashed var(--border2) !important;
    border-radius:12px !important; padding:0.5rem !important;
}
textarea {
    background:var(--surface) !important; border:1px solid var(--border2) !important;
    border-radius:10px !important; color:var(--text) !important;
    font-family:'JetBrains Mono',monospace !important; font-size:0.8rem !important;
}
.stButton > button {
    background:linear-gradient(135deg,#2563EB,#1D4ED8) !important;
    color:#fff !important; font-family:'Plus Jakarta Sans',sans-serif !important;
    font-weight:700 !important; font-size:0.9rem !important;
    border:none !important; border-radius:10px !important;
    padding:0.7rem 2rem !important; letter-spacing:0.02em !important;
    box-shadow:0 4px 14px rgba(37,99,235,.35) !important;
    transition:all .2s !important;
}
.stButton > button:hover { transform:translateY(-1px) !important; box-shadow:0 6px 20px rgba(37,99,235,.45) !important; }
[data-testid="stExpander"] { background:var(--surface); border:1px solid var(--border) !important; border-radius:12px !important; }
label { color:var(--text2) !important; font-size:0.8rem !important; font-weight:600 !important; }
::-webkit-scrollbar { width:6px; height:6px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:var(--border2); border-radius:3px; }
</style>
""", unsafe_allow_html=True)

# Top bar
st.markdown("""
<div class="topbar">
  <div>
    <span class="topbar-logo">⚡</span>
    <span class="topbar-name">Recruit<span>IQ</span></span>
  </div>
  <div class="topbar-badge">AI RESUME SCREENER</div>
</div>
""", unsafe_allow_html=True)

col_input, col_results = st.columns([1.05, 1], gap="large")

with col_input:
    st.markdown('<div class="card"><div class="card-title">📄 Upload Resume</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Drop PDF or DOCX", type=["pdf","docx"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="card"><div class="card-title">📋 Job Description</div>', unsafe_allow_html=True)
    job_description = st.text_area(
        "JD", height=300,
        placeholder="Paste the full job description here...\n\nRequired Skills:\n• Python, SQL, pandas...",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    run = st.button("⚡  Analyse Resume Match", use_container_width=True)

with col_results:
    if run:
        if not uploaded_file:
            st.error("⚠️ Please upload a resume (PDF or DOCX).")
        elif not job_description.strip():
            st.error("⚠️ Please paste a job description.")
        else:
            with st.spinner("Analysing resume..."):
                if uploaded_file.name.lower().endswith(".pdf"):
                    resume_text = extract_text_from_pdf(uploaded_file)
                else:
                    resume_text = extract_text_from_docx(uploaded_file)

                if not resume_text.strip():
                    st.error("Could not extract text. Ensure it's a readable PDF or DOCX.")
                    st.stop()

                result = screen_resume(resume_text, job_description)

            score         = result["match_percentage"]
            resume_skills = result["resume_skills"]
            jd_skills     = result["jd_skills"]
            matched       = result["matched_skills"]
            missing       = result["missing_skills"]
            suggestions   = result.get("suggestions", [])

            int_score = int(score)
            if score >= 70:
                verdict_cls, verdict_icon, verdict_text, prog_color = \
                    "v-strong",   "✅", "Strong Match — Candidate aligns well with this role.",             "#10B981"
            elif score >= 45:
                verdict_cls, verdict_icon, verdict_text, prog_color = \
                    "v-moderate", "⚡", "Moderate Match — Some skill gaps; worth a closer review.",         "#F59E0B"
            else:
                verdict_cls, verdict_icon, verdict_text, prog_color = \
                    "v-weak",     "❌", "Weak Match — Significant gaps detected in required skills.",       "#EF4444"

            # Score card
            st.markdown(f"""
            <div class="score-wrap">
                <div class="score-number">{int_score}<span class="score-pct">%</span></div>
                <div class="score-label">Match Score</div>
            </div>
            <div class="prog-wrap">
                <div class="prog-fill" style="width:{int_score}%;background:{prog_color};"></div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:0.68rem;color:var(--text3);font-weight:600;margin-bottom:0.5rem;">
                <span>0%</span><span>50%</span><span>100%</span>
            </div>
            <div class="verdict {verdict_cls}">
                <span style="font-size:1.1rem">{verdict_icon}</span>
                <span>{verdict_text}</span>
            </div>
            <div class="stats-row">
                <div class="stat-tile">
                    <div class="stat-num">{len(jd_skills)}</div>
                    <div class="stat-lbl">JD Skills</div>
                </div>
                <div class="stat-tile">
                    <div class="stat-num" style="color:#10B981">{len(matched)}</div>
                    <div class="stat-lbl">Matched</div>
                </div>
                <div class="stat-tile">
                    <div class="stat-num" style="color:#EF4444">{len(missing)}</div>
                    <div class="stat-lbl">Missing</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)

            # Matched skills
            st.markdown('<div class="card"><div class="card-title">✅ Matched Skills</div>', unsafe_allow_html=True)
            if matched:
                chips = "".join(f'<span class="chip chip-green">✓ {s}</span>' for s in sorted(matched))
                st.markdown(f'<div class="chips-wrap">{chips}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:var(--text3);font-size:0.85rem">No matching skills found.</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Missing skills
            st.markdown('<div class="card"><div class="card-title">❌ Missing / Gap Skills</div>', unsafe_allow_html=True)
            if missing:
                chips = "".join(f'<span class="chip chip-red">✗ {s}</span>' for s in sorted(missing))
                st.markdown(f'<div class="chips-wrap">{chips}</div>', unsafe_allow_html=True)
            else:
                st.markdown('<span style="color:#10B981;font-size:0.85rem;font-weight:600;">🎉 No gaps — all required skills are present!</span>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Suggestions
            if suggestions:
                st.markdown('<div class="card"><div class="card-title">💡 Improvement Suggestions</div>', unsafe_allow_html=True)
                st.markdown('<p style="font-size:0.8rem;color:var(--text2);margin-bottom:1rem;margin-top:-0.3rem;">Add these to your resume to boost your match score:</p>', unsafe_allow_html=True)
                for sug in suggestions:
                    icon_bg = {"high":"#FEE2E2","medium":"#FEF3C7","low":"#DBEAFE"}.get(sug["priority"],"#F1F5F9")
                    pri_cls = f"pri-{sug['priority']}"
                    st.markdown(f"""
                    <div class="sug-item">
                        <div class="sug-icon" style="background:{icon_bg}">{sug['icon']}</div>
                        <div>
                            <div class="sug-title">{sug['title']}</div>
                            <div class="sug-desc">{sug['desc']}</div>
                            <span class="sug-priority {pri_cls}">{sug['priority'].upper()} PRIORITY</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # All resume skills expander
            with st.expander("🔎 All skills extracted from resume"):
                if resume_skills:
                    chips = "".join(f'<span class="chip chip-blue">{s}</span>' for s in sorted(resume_skills))
                    st.markdown(f'<div class="chips-wrap" style="margin-top:0.5rem">{chips}</div>', unsafe_allow_html=True)
                else:
                    st.write("No skills extracted.")
    else:
        st.markdown("""
        <div style="background:var(--surface);border:2px dashed var(--border2);border-radius:16px;
             padding:4rem 2rem;text-align:center;margin-top:0.5rem;">
            <div style="font-size:3.5rem;margin-bottom:1rem;opacity:0.2">📊</div>
            <div style="font-size:0.95rem;font-weight:700;color:var(--text3);margin-bottom:0.4rem;">
                Results will appear here
            </div>
            <div style="font-size:0.78rem;color:var(--text3);">
                Upload a resume and paste a job description, then click Analyse.
            </div>
        </div>
        """, unsafe_allow_html=True)