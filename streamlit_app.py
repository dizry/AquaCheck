import streamlit as st
import time
import json
import os
import sqlite3
from datetime import datetime, timezone
from html import escape
from urllib import error as urllib_error
from urllib import request as urllib_request
import streamlit.components.v1 as components

REPORT_DB = os.path.join(os.path.dirname(__file__), "community_reports.db")


def initialize_report_database():
    with sqlite3.connect(REPORT_DB) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                zip_code TEXT NOT NULL,
                issue TEXT NOT NULL,
                status TEXT NOT NULL,
                votes INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rating INTEGER NOT NULL,
                comment TEXT,
                suggestion TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        if connection.execute("SELECT COUNT(*) FROM reports").fetchone()[0] == 0:
            connection.executemany(
                "INSERT INTO reports (zip_code, issue, status, votes, created_at) VALUES (?, ?, ?, ?, ?)",
                [
                    ("90210", "Brownish tap water after pipe maintenance", "Under Review", 12, datetime.now(timezone.utc).isoformat()),
                    ("10001", "Strong chlorine odor from kitchen sink", "Alert Active", 28, datetime.now(timezone.utc).isoformat()),
                ],
            )


def load_reports():
    with sqlite3.connect(REPORT_DB) as connection:
        connection.row_factory = sqlite3.Row
        rows = connection.execute(
            "SELECT id, zip_code, issue, status FROM reports ORDER BY created_at DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def add_report(zip_code, issue):
    with sqlite3.connect(REPORT_DB) as connection:
        connection.execute(
            "INSERT INTO reports (zip_code, issue, status, votes, created_at) VALUES (?, ?, ?, ?, ?)",
            (zip_code, issue, "Community Verification", 1, datetime.now(timezone.utc).isoformat()),
        )


def add_feedback(rating, comment, suggestion):
    with sqlite3.connect(REPORT_DB) as connection:
        connection.execute(
            "INSERT INTO feedback (rating, comment, suggestion, created_at) VALUES (?, ?, ?, ?)",
            (rating, comment, suggestion, datetime.now(timezone.utc).isoformat()),
        )


initialize_report_database()


def generate_ai_inspection_response(
    location,
    source,
    collection_method,
    observations,
    symptoms,
    clarity_rating,
    risk_score,
):
    try:
        api_key = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")
    except Exception:
        api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return None

    prompt = f"""Assess this water-safety observation for an educational app.
Location: {location}
Water source: {source}
How the water was obtained: {collection_method}
Appearance and odor observations: {", ".join(observations) or "None reported"}
Symptoms reported: {", ".join(symptoms) or "None reported"}
Visual clarity rating: {clarity_rating}/10
Local screening score: {risk_score}/100

Give a concise response with these headings: What this may suggest, What to do now, and When to seek help.
Do not diagnose illness, claim the water is safe, or invent local advisories. Recommend following official local guidance,
not drinking or tasting questionable water, and using an approved laboratory or health authority for confirmation.
"""
    payload = {
        "model": os.getenv("AQUACHECK_AI_MODEL", "gpt-4o-mini"),
        "messages": [
            {
                "role": "system",
                "content": "You are a careful water-safety education assistant. Keep advice practical and appropriately cautious.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 350,
    }
    request = urllib_request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib_request.urlopen(request, timeout=20) as response:
            result = json.loads(response.read().decode("utf-8"))
        return result["choices"][0]["message"]["content"].strip()
    except (urllib_error.URLError, TimeoutError, KeyError, IndexError, json.JSONDecodeError):
        return None

st.set_page_config(page_title="AquaCheck Hub", page_icon="💧", layout="wide")

# Custom Styling / Banner Header
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

    :root {
        --ink: #000000;
        --muted-ink: #4B6475;
        --ocean: #087F8C;
        --deep-ocean: #0B4F6C;
        --mint: #E8F7F3;
        --sky: #F2F8FC;
        --coral: #E86655;
    }

    .stApp {
        background: linear-gradient(135deg, var(--sky) 0%, #F8FCFA 55%, #FFF3EC 100%);
        color: var(--ink);
        font-family: 'DM Sans', 'Trebuchet MS', sans-serif;
    }
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .main-header {
        font-family: 'Space Grotesk', 'Trebuchet MS', sans-serif;
        letter-spacing: 0;
    }
    [data-testid="stHeader"],
    .stApp > header {
        background: transparent;
        border-bottom: 0;
        box-shadow: none;
    }
    .block-container {
        max-width: 1180px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
        animation: page-enter 420ms ease-out;
    }
    @keyframes page-enter {
        from { opacity: 0; transform: translateY(8px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-header {
        padding: 1.35rem 1.5rem;
        border-radius: 18px;
        background: linear-gradient(115deg, var(--deep-ocean), var(--ocean));
        box-shadow: 0 12px 26px rgba(11, 79, 108, 0.18);
        color: #FFFFFF;
        font-size: 2.5rem;
        text-align: center;
        font-weight: bold;
        letter-spacing: 0.01em;
        animation: header-glow 700ms ease-out;
        position: relative;
        overflow: hidden;
    }
    .main-header::after {
        content: "";
        position: absolute;
        left: -10%;
        right: -10%;
        bottom: -22px;
        height: 48px;
        background: rgba(255, 255, 255, 0.14);
        border-radius: 50% 50% 0 0;
        transform: rotate(-2deg);
        animation: header-wave 5s ease-in-out infinite;
    }
    @keyframes header-wave {
        0%, 100% { transform: translateX(-2%) rotate(-2deg); }
        50% { transform: translateX(2%) rotate(2deg); }
    }
    @keyframes header-glow {
        from { box-shadow: 0 0 0 rgba(11, 79, 108, 0); }
        to { box-shadow: 0 12px 26px rgba(11, 79, 108, 0.18); }
    }
    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--muted-ink);
    }
    [data-testid="stMarkdownContainer"] a {
        color: #075985;
        font-weight: 700;
        text-decoration: underline;
    }
    h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] {
        color: var(--ink);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E1F3F1 0%, #F4FAFC 100%);
        border-right: 1px solid #B8DCD9;
        padding-top: 1rem;
    }
    .sidebar-brand {
        padding: 0.4rem 0.35rem 1rem;
        border-bottom: 1px solid #B8DCD9;
        margin-bottom: 1rem;
    }
    .sidebar-brand strong {
        display: block;
        color: var(--deep-ocean);
        font-size: 1.2rem;
    }
    .sidebar-brand span {
        color: var(--muted-ink);
        font-size: 0.82rem;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label {
        color: var(--deep-ocean);
        font-weight: 600;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label,
    [data-testid="stSidebar"] [role="radiogroup"] label p {
        color: #123B56;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label {
        border-radius: 10px;
        padding: 0.35rem 0.5rem;
        margin: 0.12rem 0;
    }
    [data-testid="stSidebar"] [role="radiogroup"] label:hover {
        background: rgba(8, 127, 140, 0.1);
        transform: translateX(3px);
        transition: transform 160ms ease, background 160ms ease;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        background: rgba(255, 255, 255, 0.82);
        border: 1px solid #C7E5E4;
        border-radius: 16px;
        box-shadow: 0 8px 20px rgba(22, 50, 79, 0.07);
        padding: 0.35rem;
    }
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div {
        background-color: #FFFFFF;
        border-color: #9CCFCC;
        border-radius: 10px;
        transition: border-color 160ms ease, box-shadow 160ms ease;
    }
    [data-baseweb="select"] > div:focus-within,
    [data-baseweb="input"] > div:focus-within,
    [data-baseweb="textarea"] > div:focus-within {
        border-color: var(--ocean);
        box-shadow: 0 0 0 3px rgba(8, 127, 140, 0.14);
    }
    [data-baseweb="select"] *, [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: var(--ink);
    }
    [data-baseweb="input"] input::placeholder,
    [data-baseweb="textarea"] textarea::placeholder {
        color: #526574;
        opacity: 1;
    }
    input[aria-label="Zip Code"],
    textarea[aria-label="Describe what you observed"] {
        background-color: var(--deep-ocean) !important;
        color: #FFFFFF !important;
        caret-color: #FFFFFF;
    }
    input[aria-label="Describe the water source"],
    input[aria-label="Describe how the water was obtained"],
    input[aria-label="Describe the appearance or odor"],
    input[aria-label="Describe other symptoms"] {
        background: #FFFFFF;
        border: 1px solid #55B8AF;
        border-radius: 10px;
        color: var(--ink) !important;
        box-shadow: 0 3px 10px rgba(22, 50, 79, 0.06);
    }
    input[aria-label="Zip Code"]::placeholder,
    textarea[aria-label="Describe what you observed"]::placeholder {
        color: #CFE3FF;
    }
    [data-testid="stAlert"] {
        border-width: 1px;
    }
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] li,
    [data-testid="stAlert"] strong,
    [data-testid="stAlert"] code {
        color: #000000;
    }
    [data-testid="stAlert"] {
        background: #FFFFFF;
    }
    [data-testid="stAlert"] a {
        color: #075985;
        font-weight: 700;
    }
    [data-testid="stAlert"]:has(svg[aria-label="error"]) {
        background: #FEE2E2;
        border-color: #DC2626;
    }
    [data-testid="stAlert"]:has(svg[aria-label="warning"]) {
        background: #FFF7ED;
        border-color: #EA580C;
    }
    [data-testid="stAlert"]:has(svg[aria-label="info"]) {
        background: #E0F2FE;
        border-color: #0284C7;
    }
    [data-testid="stAlert"]:has(svg[aria-label="success"]) {
        background: #DCFCE7;
        border-color: #16A34A;
    }
    [data-testid="stExpander"],
    [data-testid="stExpander"] details,
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] [data-testid="stExpanderDetails"] {
        background: #234B63;
        color: #FFFFFF;
    }
    [data-testid="stExpander"] {
        border: 1px solid #4E7893;
        border-radius: 14px;
        overflow: hidden;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] li,
    [data-testid="stExpander"] strong,
    [data-testid="stExpander"] em,
    [data-testid="stExpander"] code {
        color: #FFFFFF !important;
    }
    [data-testid="stExpander"] summary {
        display: flex !important;
        align-items: center !important;
        gap: 0.55rem !important;
    }
    [data-testid="stExpander"] summary::before {
        content: "\\25B6" !important;
        display: inline-block !important;
        flex: 0 0 auto !important;
        color: #000000 !important;
        font-size: 1.15rem !important;
        font-weight: 900 !important;
        line-height: 1 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stExpander"] details[open] > summary::before {
        content: "\\25BC" !important;
    }
    [data-testid="stExpander"] summary svg {
        display: none !important;
        color: #000000 !important;
        fill: #000000 !important;
        stroke: #000000 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stExpander"] summary:hover svg,
    [data-testid="stExpander"] summary:focus-visible svg {
        color: #000000 !important;
        fill: #000000 !important;
        stroke: #000000 !important;
        opacity: 1 !important;
        visibility: visible !important;
    }
    [data-testid="stExpander"] a {
        color: #A9D6FF;
    }
    .stButton > button[kind="primary"] {
        background: var(--coral);
        border: 0;
        color: #FFFFFF;
        font-weight: 700;
        border-radius: 12px;
        min-height: 2.8rem;
        transition: transform 160ms ease, box-shadow 160ms ease, background 160ms ease;
        box-shadow: 0 6px 14px rgba(232, 102, 85, 0.25);
    }
    .stButton > button[kind="primary"]:hover {
        background: #C94F42;
        color: #FFFFFF;
        transform: translateY(-2px);
        box-shadow: 0 10px 18px rgba(232, 102, 85, 0.3);
    }
    .stButton > button:not([kind="primary"]) {
        color: var(--ink);
        background: #FFFFFF;
        border: 1px solid #5B8FA3;
        font-weight: 700;
        border-radius: 12px;
        min-height: 2.8rem;
        transition: transform 160ms ease, background 160ms ease;
    }
    .stButton > button:not([kind="primary"]):hover {
        color: #0B4F6C;
        border-color: #0B4F6C;
        background: #E8F7F3;
        transform: translateY(-1px);
    }
    [data-testid="stFormSubmitButton"] button {
        background: var(--deep-ocean);
        border-color: var(--deep-ocean);
        color: #FFFFFF !important;
        font-weight: 700;
    }
    [data-testid="stFormSubmitButton"] button * {
        color: #FFFFFF !important;
    }
    [data-testid="stFormSubmitButton"] button:hover {
        background: var(--ocean);
        border-color: var(--ocean);
        color: #FFFFFF !important;
    }
    .badge-card {
        background: var(--mint);
        padding: 15px;
        border-radius: 16px;
        text-align: center;
        border: 2px solid #55B8AF;
        color: var(--deep-ocean);
    }
    .intro-card {
        background: rgba(255, 255, 255, 0.88);
        border: 1px solid #B8DCD9;
        border-radius: 18px;
        padding: 1.4rem 1.5rem;
        box-shadow: 0 10px 24px rgba(22, 50, 79, 0.08);
        transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }
    .intro-card:hover,
    .gear-card:hover,
    .badge-card:hover {
        transform: translateY(-3px);
        border-color: #55B8AF;
        box-shadow: 0 14px 28px rgba(22, 50, 79, 0.13);
    }
    .intro-card h3 {
        color: #A9D6FF;
        margin-top: 0;
    }
    .gear-card {
        height: 380px;
        min-height: 380px;
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
    }
    .gear-card p:last-child {
        margin-top: auto;
    }
    .gear-card a {
        color: #075985;
        font-weight: 700;
    }
    .purpose-strip {
        background: linear-gradient(110deg, var(--deep-ocean), var(--ocean));
        border-radius: 18px;
        color: #FFFFFF;
        padding: 1.5rem;
        margin: 1.2rem 0;
    }
    .purpose-strip h2, .purpose-strip p {
        color: #FFFFFF;
    }
    .about-water-scene {
        position: relative;
        height: 132px;
        overflow: hidden;
        border-radius: 18px;
        margin: 1rem 0 1.5rem;
        background: linear-gradient(155deg, #0B4F6C 0%, #087F8C 58%, #2AB7B7 100%);
        box-shadow: 0 12px 26px rgba(8, 127, 140, 0.2);
    }
    .about-water-scene::before,
    .about-water-scene::after {
        content: "";
        position: absolute;
        left: -8%;
        width: 116%;
        height: 76px;
        border-radius: 48% 52% 0 0;
    }
    .about-water-scene::before {
        bottom: -28px;
        background: rgba(255, 255, 255, 0.2);
        animation: water-swell 4.5s ease-in-out infinite;
    }
    .about-water-scene::after {
        bottom: -43px;
        background: rgba(3, 46, 64, 0.28);
        animation: water-swell 6s ease-in-out infinite reverse;
    }
    .water-scene-label {
        position: absolute;
        z-index: 1;
        top: 1rem;
        left: 1.2rem;
        color: #FFFFFF;
        font-family: 'Space Grotesk', 'Trebuchet MS', sans-serif;
        font-size: 1.2rem;
        font-weight: 700;
    }
    .water-scene-label span {
        display: block;
        color: #D8F8FF;
        font-family: 'DM Sans', 'Trebuchet MS', sans-serif;
        font-size: 0.9rem;
        font-weight: 500;
        margin-top: 0.2rem;
    }
    @keyframes water-swell {
        0%, 100% { transform: translateX(-3%) rotate(1deg); }
        50% { transform: translateX(3%) rotate(-2deg); }
    }
    .inspection-intro {
        background: linear-gradient(110deg, #E8F7F3, #F2F8FC);
        border-left: 5px solid var(--ocean);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0 1.4rem;
    }
    .inspection-intro strong {
        color: #A9D6FF;
        font-size: 1.05rem;
    }
    .inspection-intro p {
        color: var(--muted-ink);
        margin: 0.25rem 0 0;
    }
    .community-report {
        background: #FFF7ED;
        border: 1px solid #FDBA74;
        border-radius: 12px;
        color: #000000;
        padding: 0.85rem 1rem;
        margin-bottom: 0.5rem;
    }
    .community-report strong,
    .community-report span,
    .community-report em {
        color: #000000;
    }
    .quiz-intro {
        background: linear-gradient(110deg, #123F50, #087F8C);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        color: #FFFFFF;
        margin: 0.5rem 0 1.2rem;
    }
    .quiz-intro strong,
    .quiz-intro p {
        color: #FFFFFF;
    }
    .quiz-intro p {
        margin: 0.3rem 0 0;
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: 0.01ms !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💧 AquaCheck — Interactive Water Safety Hub</div>', unsafe_allow_html=True)
st.caption("AI Inspection • Interactive pH Tester • Community Map • Safety Gear")

# Sidebar Navigation
st.sidebar.markdown(
    """
    <div class="sidebar-brand">
        <strong>💧 AquaCheck</strong>
        <span>Water safety tools and guidance</span>
    </div>
    """,
    unsafe_allow_html=True,
)
page_options = [
    "🌍 About AquaCheck",
    "🔍 AI Risk Inspection",
    "📢 Community Incident Map",
    "📖 Inspector Field Guide",
    "🏆 Inspector Quiz & Badge",
    "🛒 Gear & Testing Kits",
    "🧪 Interactive pH Simulator",
    "🛡️ Prevent Contaminated Water",
]
saved_page = st.query_params.get("page", page_options[0])
if saved_page not in page_options:
    saved_page = page_options[0]
page = st.sidebar.radio(
    "Explore Features",
    page_options,
    index=page_options.index(saved_page),
    key="selected_page",
)
if st.query_params.get("page") != page:
    st.query_params["page"] = page

st.sidebar.divider()
with st.sidebar.expander("💬 Share feedback", expanded=False):
    st.write("Help shape the next AquaCheck update.")
    with st.form("feedback_form", clear_on_submit=True):
        feedback_rating = st.select_slider(
            "How would you rate AquaCheck?",
            options=[1, 2, 3, 4, 5],
            value=5,
            format_func=lambda rating: "★" * rating,
        )
        feedback_comment = st.text_area(
            "What do you think?",
            placeholder="Tell us what feels useful or could be clearer.",
        )
        feedback_suggestion = st.text_input(
            "What should we add next?",
            placeholder="Example: produce safety checks",
        )
        feedback_submit = st.form_submit_button("Send feedback")
        if feedback_submit:
            if feedback_comment.strip() or feedback_suggestion.strip():
                add_feedback(
                    feedback_rating,
                    feedback_comment.strip(),
                    feedback_suggestion.strip(),
                )
                st.success("Thanks for helping shape AquaCheck!")
            else:
                st.warning("Add a comment or suggestion before sending.")

# ---------------------------------------------------------
# 1. ABOUT AQUACHECK
# ---------------------------------------------------------
if page == "🌍 About AquaCheck":
    st.header("🌍 What is AquaCheck?")
    st.write(
        "AquaCheck is an interactive community water-safety hub for people who want a clearer "
        "way to understand everyday water concerns. It brings observation tools, educational "
        "guidance, simple screening activities, community reports, and practical equipment "
        "ideas into one approachable place."
    )
    st.write(
        "The website can help you describe a water source, record changes in color, clarity, "
        "or odor, learn what common measurements mean, and think through sensible next steps. "
        "It is designed to support awareness and conversation with water providers, health "
        "departments, laboratories, and other qualified professionals. AquaCheck is educational "
        "and does not replace certified testing, official advisories, or medical advice."
    )

    components.html(
        """
        <style>
            * { box-sizing: border-box; }
            body { margin: 0; overflow: hidden; background: transparent; }
            .water-wrap {
                position: relative;
                height: 154px;
                overflow: hidden;
                border-radius: 18px;
                background: linear-gradient(155deg, #0B4F6C 0%, #087F8C 58%, #2AB7B7 100%);
                box-shadow: 0 12px 26px rgba(8, 127, 140, 0.2);
                cursor: crosshair;
            }
            canvas { display: block; width: 100%; height: 100%; }
            .water-copy {
                position: absolute;
                z-index: 2;
                top: 1rem;
                left: 1.2rem;
                color: #FFFFFF;
                font: 700 1.2rem 'Trebuchet MS', sans-serif;
                pointer-events: none;
            }
            .water-copy span {
                display: block;
                margin-top: 0.25rem;
                color: #D8F8FF;
                font: 500 0.9rem 'Trebuchet MS', sans-serif;
            }
            .water-hint {
                position: absolute;
                right: 1rem;
                bottom: 0.8rem;
                color: rgba(255, 255, 255, 0.8);
                font: 500 0.75rem 'Trebuchet MS', sans-serif;
                pointer-events: none;
            }
        </style>
        <div class="water-wrap" aria-label="Interactive animated water surface">
            <canvas id="water-canvas"></canvas>
            <div class="water-copy">
                Notice. Learn. Protect.
                <span>Tap the water to see how one observation creates ripples.</span>
            </div>
            <div class="water-hint">tap to ripple</div>
        </div>
        <script>
            const canvas = document.getElementById('water-canvas');
            const context = canvas.getContext('2d');
            const ripples = [];
            let width = 0;
            let height = 0;            http://localhost:8502

            function resizeWater() {
                const scale = window.devicePixelRatio || 1;
                width = canvas.clientWidth;
                height = canvas.clientHeight;
                canvas.width = width * scale;
                canvas.height = height * scale;
                context.setTransform(scale, 0, 0, scale, 0, 0);
            }

            function addRipple(x, y) {
                ripples.push({ x, y, radius: 2, opacity: 0.8 });
                if (ripples.length > 8) ripples.shift();
            }

            function drawWater(time) {
                context.clearRect(0, 0, width, height);
                const layers = [
                    { color: 'rgba(255,255,255,0.18)', amplitude: 8, speed: 0.0012, y: height * 0.62 },
                    { color: 'rgba(3,46,64,0.24)', amplitude: 11, speed: 0.0017, y: height * 0.73 },
                    { color: 'rgba(216,248,255,0.2)', amplitude: 6, speed: 0.0022, y: height * 0.84 }
                ];
                layers.forEach((layer, layerIndex) => {
                    context.beginPath();
                    context.moveTo(0, height);
                    for (let x = 0; x <= width; x += 4) {
                        const wave = Math.sin(x * 0.018 + time * layer.speed + layerIndex) * layer.amplitude;
                        context.lineTo(x, layer.y + wave);
                    }
                    context.lineTo(width, height);
                    context.closePath();
                    context.fillStyle = layer.color;
                    context.fill();
                });
                ripples.forEach((ripple, index) => {
                    ripple.radius += 0.75;
                    ripple.opacity -= 0.008;
                    context.beginPath();
                    context.arc(ripple.x, ripple.y, ripple.radius, 0, Math.PI * 2);
                    context.strokeStyle = `rgba(255,255,255,${Math.max(ripple.opacity, 0)})`;
                    context.lineWidth = 2;
                    context.stroke();
                    if (ripple.opacity <= 0) ripples.splice(index, 1);
                });
                requestAnimationFrame(drawWater);
            }

            window.addEventListener('resize', resizeWater);
            canvas.addEventListener('pointerdown', (event) => {
                const bounds = canvas.getBoundingClientRect();
                addRipple(event.clientX - bounds.left, event.clientY - bounds.top);
            });
            resizeWater();
            requestAnimationFrame(drawWater);
        </script>
        """,
        height=154,
    )

    st.markdown(
        """
        <div class="purpose-strip">
            <h2>Why AquaCheck was made</h2>
            <p>
                AquaCheck was made because people need a simple way to test and understand their
                water before a possible problem becomes a health emergency. Waterborne illnesses
                affect communities around the world, and diarrheal disease remains a major cause
                of illness and death, especially among children. AquaCheck helps people notice
                possible risks early, learn what to test, and choose a sensible next step.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("How AquaCheck helps")
    about_columns = st.columns(3)
    with about_columns[0]:
        st.markdown(
            """
            <div class="intro-card">
                <h3>🔎 Notice</h3>
                <p>Record changes in water color, clarity, odor, location, and symptoms.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with about_columns[1]:
        st.markdown(
            """
            <div class="intro-card">
                <h3>🧠 Learn</h3>
                <p>Build practical knowledge about sampling, pH, turbidity, and reporting.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with about_columns[2]:
        st.markdown(
            """
            <div class="intro-card">
                <h3>🌱 Act</h3>
                <p>Use clear next steps to reduce exposure and connect concerns to local officials.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("👋 About the founder")
    st.markdown(
        """
        <div class="intro-card">
            <h3>Jacky, Founder of AquaCheck</h3>
            <p>
                I’m Jacky, and AquaCheck is personal to me. My mom once experienced very severe
                diarrhea after eating fruit, and I also experienced diarrhea from eating fruit on
                another occasion. Those experiences made me think more seriously about how easily
                food and water safety can affect a family, and how difficult it can be to know where
                a health problem came from. I created AquaCheck
                to make basic water testing, practical education, and early reporting easier for
                everyday people. It is a starting point for awareness and action, not a replacement
                for certified laboratory testing or medical advice.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("Start here")
    st.info(
        "Use the AI Risk Inspection to describe what you are seeing, then visit the "
        "Inspector Field Guide to learn how water testing works. AquaCheck is an "
        "educational tool and does not replace certified laboratory testing or public-health advice."
    )

# ---------------------------------------------------------
# 2. AI RISK INSPECTOR
# ---------------------------------------------------------
elif page == "🔍 AI Risk Inspection":
    st.header("🔍 Water Safety Risk Checker")
    st.markdown(
        """
        <div class="inspection-intro">
            <strong>Build a clearer water-safety picture</strong>
            <p>Tell us where the sample came from, how it was collected, and what you noticed. The AI will use these details to explain sensible next steps.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.subheader("1. Identify the sample")
    with st.container(border=True):
        location_column, source_column = st.columns(2)
        with location_column:
            zip_code = st.selectbox(
                "Search or select a ZIP / postal code location",
                [
                    "90210 — Beverly Hills, United States",
                    "10001 — New York, United States",
                    "V6B 1A1 — Vancouver, Canada",
                    "M5V 2T6 — Toronto, Canada",
                    "SW1A 1AA — London, United Kingdom",
                    "75001 — Paris, France",
                    "10117 — Berlin, Germany",
                    "00100 — Rome, Italy",
                    "28013 — Madrid, Spain",
                    "100-0001 — Tokyo, Japan",
                    "045-0001 — Sapporo, Japan",
                    "400001 — Mumbai, India",
                    "110001 — New Delhi, India",
                    "0001 — Cape Town, South Africa",
                    "00100 — Nairobi, Kenya",
                    "00200 — Accra, Ghana",
                    "2000 — Sydney, Australia",
                    "3000 — Melbourne, Australia",
                    "01000-000 — São Paulo, Brazil",
                    "11000 — Buenos Aires, Argentina",
                    "CP 06000 — Mexico City, Mexico",
                    "0101 — Reykjavík, Iceland",
                    "Other (type a ZIP / postal code)",
                ],
            )
            if zip_code == "Other (type a ZIP / postal code)":
                typed_zip_code = st.text_input(
                    "Type your ZIP / postal code",
                    placeholder="Example: 10115 or SW1A 1AA",
                    key="typed_zip_code",
                ).strip()
                if typed_zip_code:
                    zip_code = typed_zip_code
                    st.caption("Location will be assessed from the postal code you entered.")
        with source_column:
            water_type = st.selectbox(
                "Source",
                [
                    "Tap Water",
                    "Private Well",
                    "River or Stream",
                    "Lake or Pond",
                    "Rainwater Collection",
                    "Bottled Water",
                    "Swimming Pool",
                    "Other (type your own)",
                ],
            )
            custom_source = ""
            if water_type == "Other (type your own)":
                custom_source = st.text_input("Describe the water source", key="custom_water_source")

        collection_method = st.selectbox(
            "How was the water obtained?",
            [
                "Turned on from an indoor tap",
                "Collected from an outdoor tap or hose",
                "Drawn from a private well",
                "Collected from a river, stream, lake, or pond",
                "Collected from rainwater or a storage tank",
                "Poured from a bottle or refill station",
                "Collected during a flood, storm, or other event",
                "Other (type your own)",
            ],
        )
        if collection_method == "Other (type your own)":
            custom_collection_method = st.text_input(
                "Describe how the water was obtained",
                key="custom_collection_method",
            ).strip()
            if custom_collection_method:
                collection_method = custom_collection_method

    st.subheader("2. Describe what you observed")
    with st.container(border=True):
        appearance_column, symptoms_column = st.columns(2)
        with appearance_column:
            appearance = st.multiselect(
                "Appearance & Odor",
                [
                    "Clear / No unusual odor",
                    "Cloudy / Turbid",
                    "Rusty / Brownish",
                    "Yellowish or Greenish",
                    "Visible Sediment",
                    "Oily Sheen",
                    "Foamy",
                    "Metallic Smell",
                    "Earthy or Musty Smell",
                    "Chlorine Smell",
                    "Sewage or Rotten-Egg Smell",
                    "Other (type your own)",
                ],
            )
            custom_appearance = ""
            if "Other (type your own)" in appearance:
                custom_appearance = st.text_input("Describe the appearance or odor", key="custom_appearance")
        with symptoms_column:
            symptoms = st.multiselect(
                "Symptoms Reported",
                [
                    "None",
                    "Stomach Cramps",
                    "Nausea",
                    "Vomiting",
                    "Diarrhea",
                    "Fever",
                    "Headache or Dizziness",
                    "Skin Rash or Irritation",
                    "Eye Irritation",
                    "Other (type your own)",
                ],
            )
            custom_symptoms = ""
            if "Other (type your own)" in symptoms:
                custom_symptoms = st.text_input("Describe other symptoms", key="custom_symptoms")
        clarity_rating = st.slider("Visual Clarity Rating (1 = Very Dirty, 10 = Crystal Clear)", 1, 10, 7)

    source_for_analysis = custom_source if water_type == "Other (type your own)" and custom_source else water_type
    observations_for_analysis = [item for item in appearance if item != "Other (type your own)"]
    if custom_appearance:
        observations_for_analysis.append(custom_appearance)
    symptoms_for_analysis = [item for item in symptoms if item != "Other (type your own)" and item != "None"]
    if custom_symptoms:
        symptoms_for_analysis.append(custom_symptoms)

    st.subheader("3. Run the inspection")
    st.caption("Review your selections above, then let AquaCheck combine the observations into practical guidance.")
    if st.button("⚡ Run Live AquaCheck Inspection", type="primary"):
        with st.spinner("Analyzing parameters against municipal database..."):
            time.sleep(1) # Simulation delay for realism

        risk_score = 0
        concerning_appearance = {
            "Cloudy / Turbid",
            "Rusty / Brownish",
            "Yellowish or Greenish",
            "Visible Sediment",
            "Oily Sheen",
            "Foamy",
            "Metallic Smell",
            "Earthy or Musty Smell",
            "Chlorine Smell",
            "Sewage or Rotten-Egg Smell",
        }
        if concerning_appearance.intersection(observations_for_analysis) or custom_appearance:
            risk_score += 40
        if symptoms_for_analysis:
            risk_score += 40
        if clarity_rating < 5:
            risk_score += 20

        st.subheader("Analysis Results")
        st.progress(min(risk_score, 100))
        ai_response = generate_ai_inspection_response(
            zip_code,
            source_for_analysis,
            collection_method,
            observations_for_analysis,
            symptoms_for_analysis,
            clarity_rating,
            risk_score,
        )
        if ai_response:
            st.markdown("### 🤖 AI Inspection Guidance")
            st.markdown(ai_response)
        else:
            st.info("AI guidance is unavailable until an OPENAI_API_KEY is configured. The screening result below is rule-based and educational.")

        if risk_score >= 50:
            st.error(f"⚠️ **HIGH RISK ALERT for {zip_code} (Risk Score: {risk_score}/100)**")
            st.write("👉 **Immediate Action:** Boil water for at least 3 minutes before drinking or cooking. Use certified carbon filtration.")
            st.warning(
                "Do not drink or taste the water. Follow local boil-water or do-not-use advisories and contact your water provider or local health authority."
            )

            severe_risk = risk_score >= 80 and bool(symptoms_for_analysis)
            if severe_risk:
                st.error(
                    "🚑 **SEVERE RISK:** Water concerns are combined with reported symptoms. Seek urgent medical advice, especially for children, older adults, pregnant people, or anyone with a weakened immune system."
                )
                st.write("If someone has trouble breathing, collapses, becomes confused, or has severe dehydration, call your local emergency number immediately.")
            else:
                st.info("If anyone becomes ill after possible exposure, contact a healthcare professional and mention the suspected water exposure.")

            components.html(
                """
                <div id="hospital-finder" style="margin: 1rem 0;">
                    <p style="color:#16324F;margin:0 0 0.6rem;">
                        May AquaCheck use your location to look for nearby hospitals? Your browser will ask for permission.
                    </p>
                    <button onclick="findNearbyHospitals()" style="background:#E86655;border:0;border-radius:8px;color:white;cursor:pointer;font-size:1rem;font-weight:700;padding:0.7rem 1rem;">
                        📍 Find nearest hospitals using my location
                    </button>
                    <p id="hospital-status" style="color:#16324F;margin-top:0.6rem;"></p>
                    <div id="hospital-results" style="color:#16324F;margin-top:0.8rem;"></div>
                </div>
                <script>
                    function escapeHospitalText(value) {
                        return String(value || '').replace(/[&<>'"]/g, (character) => ({
                            '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
                        }[character]));
                    }

                    function distanceInKilometers(latitude1, longitude1, latitude2, longitude2) {
                        const earthRadius = 6371;
                        const latitudeDelta = (latitude2 - latitude1) * Math.PI / 180;
                        const longitudeDelta = (longitude2 - longitude1) * Math.PI / 180;
                        const value = Math.sin(latitudeDelta / 2) ** 2
                            + Math.cos(latitude1 * Math.PI / 180)
                            * Math.cos(latitude2 * Math.PI / 180)
                            * Math.sin(longitudeDelta / 2) ** 2;
                        return earthRadius * 2 * Math.atan2(Math.sqrt(value), Math.sqrt(1 - value));
                    }

                    function findNearbyHospitals() {
                        const status = document.getElementById('hospital-status');
                        const results = document.getElementById('hospital-results');
                        if (!window.confirm('May AquaCheck use your location to find nearby hospitals?')) {
                            status.textContent = 'No problem. Your location was not used.';
                            results.innerHTML = '';
                            return;
                        }
                        if (!navigator.geolocation) {
                            status.textContent = 'Location access is not supported by this browser.';
                            return;
                        }
                        status.textContent = 'Requesting your location...';
                        results.innerHTML = '';
                        navigator.geolocation.getCurrentPosition(
                            async (position) => {
                                const latitude = position.coords.latitude;
                                const longitude = position.coords.longitude;
                                status.textContent = 'Finding nearby hospitals...';
                                const query = `[out:json];(nwr["amenity"="hospital"](around:10000,${latitude},${longitude}););out center tags;`;
                                const endpoints = [
                                    'https://overpass-api.de/api/interpreter',
                                    'https://overpass.kumi.systems/api/interpreter'
                                ];
                                try {
                                    let data;
                                    for (const endpoint of endpoints) {
                                        try {
                                            const response = await fetch(`${endpoint}?data=${encodeURIComponent(query)}`);
                                            if (response.ok) {
                                                data = await response.json();
                                                break;
                                            }
                                        } catch (endpointError) {
                                            // Try the backup public map endpoint.
                                        }
                                    }
                                    if (!data) throw new Error('Hospital search failed');
                                    const hospitals = data.elements
                                        .filter((hospital) => hospital.tags && hospital.tags.name)
                                        .map((hospital) => {
                                            const point = hospital.center || hospital;
                                            return {
                                                ...hospital,
                                                distance: distanceInKilometers(latitude, longitude, point.lat, point.lon)
                                            };
                                        })
                                        .sort((first, second) => first.distance - second.distance)
                                        .slice(0, 8);
                                    if (!hospitals.length) {
                                        const mapsUrl = `https://www.google.com/maps/search/hospitals/@${latitude},${longitude},13z`;
                                        status.innerHTML = `No named hospitals were found within 10 km. <a href="${mapsUrl}" target="_blank" rel="noopener noreferrer">Search hospitals on a map</a>`;
                                        return;
                                    }
                                    status.textContent = `Found the ${hospitals.length} nearest hospitals:`;
                                    results.innerHTML = '<ul style="padding-left:1.2rem;">' + hospitals.map((hospital) => {
                                        const tags = hospital.tags;
                                        const point = hospital.center || hospital;
                                        const address = [tags['addr:housenumber'], tags['addr:street'], tags['addr:city']].filter(Boolean).join(' ');
                                        const phone = tags.phone ? ` · ${escapeHospitalText(tags.phone)}` : '';
                                        const mapUrl = `https://www.openstreetmap.org/?mlat=${point.lat}&mlon=${point.lon}#map=17/${point.lat}/${point.lon}`;
                                        return `<li style="margin-bottom:0.7rem;"><strong>${escapeHospitalText(tags.name)}</strong> <span>(${hospital.distance.toFixed(1)} km away)</span>${address ? `<br>${escapeHospitalText(address)}` : ''}${phone}<br><a href="${mapUrl}" target="_blank" rel="noopener noreferrer">View map and hospital details</a></li>`;
                                    }).join('') + '</ul>';
                                } catch (error) {
                                    const mapsUrl = `https://www.google.com/maps/search/hospitals/@${latitude},${longitude},13z`;
                                    status.innerHTML = `The hospital list service was unavailable. <a href="${mapsUrl}" target="_blank" rel="noopener noreferrer">Open nearby hospitals on a map</a>`;
                                }
                            },
                            () => {
                                status.textContent = 'Location permission was not granted, so no location was used.';
                            },
                            { enableHighAccuracy: false, timeout: 10000, maximumAge: 300000 }
                        );
                    }
                </script>
                """,
                height=430,
            )
        else:
            st.success(f"✅ **LOW RISK — Safe Sample for {zip_code} (Risk Score: {risk_score}/100)**")
            st.write("👉 **Status:** Normal parameters detected. No municipal alerts active.")

# ---------------------------------------------------------
# 2. INTERACTIVE pH SIMULATOR
# ---------------------------------------------------------
elif page == "🧪 Interactive pH Simulator":
    st.header("🧪 Interactive Water pH Tester")
    st.write("Adjust the pH slider to see how acidity affects water safety and appearance in real time!")

    ph_value = st.slider("Select Water pH Level", 0.0, 14.0, 7.0, 0.1)

    col1, col2 = st.columns([1, 2])

    with col1:
        if ph_value < 6.5:
            st.error("🔴 **Acidic Water**")
            st.markdown("<h2 style='color: #D32F2F;'>Corrosive Range</h2>", unsafe_allow_html=True)
            st.write("Can leach heavy metals like lead and copper from pipes.")
        elif 6.5 <= ph_value <= 8.5:
            st.success("🟢 **Optimal Range**")
            st.markdown("<h2 style='color: #388E3C;'>Safe Tap Water</h2>", unsafe_allow_html=True)
            st.write("Ideal for human consumption and municipal standards.")
        else:
            st.warning("🔵 **Alkaline Water**")
            st.markdown("<h2 style='color: #1976D2;'>High Alkaline</h2>", unsafe_allow_html=True)
            st.write("May leave mineral deposits/scaling and taste slippery or bitter.")

    with col2:
        st.metric("Current pH Level", f"{ph_value}")
        st.info("💡 **Fun Fact for Judges:** EPA drinking water standards recommend a pH between 6.5 and 8.5!")

# ---------------------------------------------------------
# 3. PREVENT CONTAMINATED WATER
# ---------------------------------------------------------
elif page == "🛡️ Prevent Contaminated Water":
    st.header("🛡️ Prevent Contaminated Water")
    st.write(
        "Small habits, good maintenance, and fast reporting can reduce the chance that contamination reaches people, pets, or waterways."
    )
    st.warning(
        "Prevention lowers risk but cannot guarantee that contamination will never happen. Follow local advisories whenever officials issue them."
    )

    st.subheader("✅ Your prevention checklist")
    checklist_columns = st.columns(2)
    checklist_items = [
        "Keep chemicals, fuel, paint, and medicines out of sinks and storm drains.",
        "Keep animal waste, fertilizers, and pesticides away from wells and waterways.",
        "Maintain septic systems, private wells, storage tanks, and plumbing regularly.",
        "Use backflow protection and repair leaks or damaged pipes promptly.",
        "Keep drinking-water containers covered, clean, and clearly labeled.",
        "Check local water advisories before drinking after floods, repairs, or storms.",
    ]
    for item_index, item in enumerate(checklist_items):
        with checklist_columns[item_index % 2]:
            st.checkbox(item, key=f"prevention_check_{item_index}")

    st.divider()
    st.subheader("🔬 Where contamination can begin")
    risk_columns = st.columns(3)
    risk_sources = [
        ("🌧️ Stormwater runoff", "Rain can carry oil, litter, fertilizer, sewage, and animal waste into streams and drains. Dispose of waste properly and keep pollutants away from runoff."),
        ("🏠 Household plumbing", "Broken pipes, flooding, cross-connections, and poorly maintained wells can introduce contaminants. Use qualified professionals for repairs and inspections."),
        ("🏭 Community sources", "Leaks, spills, construction, and treatment failures can affect a whole neighborhood. Report unusual color, odor, taste, or illness patterns quickly."),
    ]
    for source_column, (title, description) in zip(risk_columns, risk_sources):
        with source_column:
            st.markdown(
                f'<div class="intro-card"><h3>{title}</h3><p>{description}</p></div>',
                unsafe_allow_html=True,
            )

    st.divider()
    st.subheader("🧭 What would you do?")
    situation = st.selectbox(
        "Choose a situation to see the safest first step",
        [
            "The tap water suddenly looks brown after nearby pipe work",
            "A strong chemical smell is noticed near a stream",
            "A basement or well has been affected by floodwater",
            "A test strip shows a result outside its expected range",
        ],
    )
    first_steps = {
        "The tap water suddenly looks brown after nearby pipe work": "Check the water provider's advisory, avoid drinking it until guidance is available, and report the change.",
        "A strong chemical smell is noticed near a stream": "Do not touch or taste the water. Move away, keep children and pets away, and contact local emergency or environmental authorities.",
        "A basement or well has been affected by floodwater": "Use an alternative drinking source and contact the local health department or a well professional for disinfection and testing instructions.",
        "A test strip shows a result outside its expected range": "Repeat the test according to the kit instructions and contact an approved laboratory or local authority before making health decisions.",
    }
    st.info(f"**Safest first step:** {first_steps[situation]}")

    st.subheader("📋 Make a household water-safety plan")
    plan_columns = st.columns(3)
    with plan_columns[0]:
        st.metric("1", "Know your source")
        st.caption("Save your water provider, well, and local health department contact details.")
    with plan_columns[1]:
        st.metric("2", "Keep a backup")
        st.caption("Store enough safe water for short disruptions and replace it regularly.")
    with plan_columns[2]:
        st.metric("3", "Know the signal")
        st.caption("Learn where official boil-water and do-not-use notices are posted.")

    st.success(
        "If contamination is suspected, do not drink or taste the water. Follow official instructions and use an approved alternative source until the water is declared safe."
    )

# ---------------------------------------------------------
# 4. COMMUNITY INCIDENT MAP LOG
# ---------------------------------------------------------
elif page == "📢 Community Incident Map":
    st.header("📢 Live Community Hazard Map")

    st.subheader("Report an Issue in Your Neighborhood")
    with st.form("new_report"):
        r_zip = st.text_input("Zip Code")
        r_desc = st.text_area("Describe what you observed")
        r_submit = st.form_submit_button("Submit Incident Report")

        if r_submit and r_zip and r_desc:
            add_report(r_zip.strip(), r_desc.strip())
            st.success("Report added to public community log!")

    @st.fragment(run_every="10s")
    def render_live_reports():
        st.subheader("Recent Community Reports")
        st.caption("Updates automatically every 10 seconds")
        for report in load_reports():
            st.markdown(
                f'<div class="community-report">'
                f'<strong>📍 ZIP {escape(str(report["zip_code"]))}</strong> '
                f'<span>| Status: {escape(str(report["status"]))}</span><br>'
                f'<em>{escape(str(report["issue"]))}</em>'
                f'</div>',
                unsafe_allow_html=True,
            )

    render_live_reports()
# 4. INSPECTOR QUIZ & BADGE
# ---------------------------------------------------------
elif page == "🏆 Inspector Quiz & Badge":
    st.header("🏆 Inspector Learning Quiz")
    st.markdown(
        """
        <div class="quiz-intro">
            <strong>Ready to test your inspection skills?</strong>
            <p>Answer all 10 questions, then review your score and revisit the Field Guide if you need a refresher.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.info("This is a learning activity, not a professional certification or substitute for local training.")
    st.progress(0, text="10 questions · Choose one answer for each")

    # Ask practical questions that an entry-level inspector should understand.
    q1 = st.radio(
        "1. What should you do before collecting a water sample?",
        ["Rinse the labeled container with the sample", "Wash your hands and check the sample instructions", "Add soap to the container"],
        index=None,
    )
    q2 = st.radio(
        "2. Which pH range is commonly used as a drinking-water reference range?",
        ["2.0 - 4.0", "6.5 - 8.5", "11.0 - 13.0"],
        index=None,
    )
    q3 = st.radio(
        "3. What does cloudy or turbid water tell an inspector?",
        ["It may contain suspended particles and needs further investigation", "It is always safe because particles are visible", "It proves the water contains E. coli"],
        index=None,
    )
    q4 = st.radio(
        "4. Why record the sample location, date, and time?",
        ["To make the report traceable and comparable", "To change the test result", "It is optional if the water looks clear"],
        index=None,
    )
    q5 = st.radio(
        "5. What is the safest response when a sample may be contaminated?",
        ["Taste it to confirm the result", "Use appropriate protective equipment and follow the test kit instructions", "Pour it into a public drinking fountain"],
        index=None,
    )
    q6 = st.radio(
        "6. Which result should be confirmed with an approved laboratory or local authority?",
        ["A result outside the test kit's expected range", "A clearly labeled sample", "A normal-looking water sample"],
        index=None,
    )
    q7 = st.radio(
        "7. What should an inspector do with a test kit past its expiration date?",
        ["Use it anyway if the package looks clean", "Replace it with an in-date kit", "Mix it with another kit"],
        index=None,
    )
    q8 = st.radio(
        "8. What does a high turbidity reading describe?",
        ["More suspended particles or cloudiness", "The exact amount of bacteria", "The temperature of the sample"],
        index=None,
    )
    q9 = st.radio(
        "9. Why might an inspector measure disinfectant residual?",
        ["To see whether treated water still has disinfectant present", "To prove the water has no metals", "To replace every bacteria test"],
        index=None,
    )
    q10 = st.radio(
        "10. Which detail belongs in a useful inspection report?",
        ["Only the inspector's opinion", "The method, result, units, location, and time", "A guess about the source of contamination"],
        index=None,
    )

    if st.button("Submit Quiz Answers"):
        answers = [q1, q2, q3, q4, q5, q6, q7, q8, q9, q10]
        if any(answer is None for answer in answers):
            st.warning("Please answer all 10 questions before submitting the quiz.")
            st.stop()
        score = 0
        correct_answers = {
            "q1": q1 == "Wash your hands and check the sample instructions",
            "q2": q2 == "6.5 - 8.5",
            "q3": q3 == "It may contain suspended particles and needs further investigation",
            "q4": q4 == "To make the report traceable and comparable",
            "q5": q5 == "Use appropriate protective equipment and follow the test kit instructions",
            "q6": q6 == "A result outside the test kit's expected range",
            "q7": q7 == "Replace it with an in-date kit",
            "q8": q8 == "More suspended particles or cloudiness",
            "q9": q9 == "To see whether treated water still has disinfectant present",
            "q10": q10 == "The method, result, units, location, and time",
        }
        score = sum(correct_answers.values())
        score_percent = round((score / len(correct_answers)) * 100)

        if score_percent == 100:
            st.balloons()
            st.markdown("""
                <div class="badge-card">
                    <h2>🎖️ AQUACHECK FIELD READY 🎖️</h2>
                    <p><b>Status: Learning milestone complete</b></p>
                    <p>You scored 100%! Keep practicing with approved local procedures.</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.warning(f"You scored {score}/{len(correct_answers)} ({score_percent}%). Review the Field Guide and try again!")

# ---------------------------------------------------------
# 5. INSPECTOR FIELD GUIDE
# ---------------------------------------------------------
elif page == "📖 Inspector Field Guide":
    st.header("📖 Inspector Field Guide")
    st.write("A quick reading page for the basics an inspector should understand before testing a water sample.")
    st.warning("Use certified laboratories, approved methods, and local health department procedures for real decisions.")

    with st.expander("1. Observe before you test", expanded=True):
        st.write("Record the source, date, time, weather, and what you can see or smell. Cloudiness, unusual color, sediment, or an odor are clues for follow-up, not proof of a specific contaminant.")

    with st.expander("2. Collect and label samples carefully"):
        st.write("Use the container supplied for the test, avoid touching the inside of the cap or container, and follow the kit's instructions. Label the sample with its location, collection time, and sample ID so another person can trace the result.")

    with st.expander("3. Understand the common measurements"):
        st.markdown("""
        - **pH:** Shows how acidic or alkaline water is. A common reference range for drinking water is 6.5 to 8.5.
        - **Turbidity:** Describes how cloudy water is because of suspended particles. High turbidity can interfere with disinfection and needs follow-up.
        - **Disinfectant residual:** Measures whether a disinfectant such as chlorine remains in treated water. Compare the result with the local system's target.
        - **Bacteria tests:** Need approved collection, storage, and laboratory methods. Never confirm a pathogen based only on appearance, odor, or a home strip.
        """)

    with st.expander("4. Protect yourself and the public"):
        st.write("Do not taste a sample. Wear the protective equipment required by the procedure, wash your hands, keep samples away from food, and tell people not to drink water that officials have advised them to avoid.")

    with st.expander("5. Interpret results with context"):
        st.write("Check the test kit's range, units, expiration date, and instructions. A single reading is a snapshot. Unexpected or out-of-range results should be repeated or confirmed by an approved laboratory or local authority.")

    with st.expander("6. Write a useful inspection report"):
        st.write("Include the location, source, observations, test method, equipment, results, units, time, and any limitations. Clear notes help health officials compare samples and decide what action is appropriate.")

    st.success("Ready to practice? Return to the Inspector Learning Quiz and test what you remember.")

# ---------------------------------------------------------
# 6. SHOP & GEAR
# ---------------------------------------------------------
elif page == "🛒 Gear & Testing Kits":
    st.header("🛒 Recommended Water Safety Equipment")
    st.write("Choose equipment based on the question you need to answer. Follow the product label and local health guidance for real safety decisions.")

    gear_items = [
        (
            "🚰 UV Purifier Pitcher",
            "For treated household water when the product is rated for the organisms and volume you need.",
            "Fill the reservoir, run the UV cycle exactly as directed, and replace the lamp or cartridge on schedule.",
            '<a href="https://www.amazon.com/s?k=UV+water+purifier+pitcher" target="_blank" rel="noopener noreferrer">View UV water purifiers on Amazon</a>',
        ),
        (
            "🧪 Multi-Parameter Test Strips",
            "Quick checks for pH, chlorine, hardness, nitrate, and other listed parameters.",
            "Dip for the stated time, compare colors in the correct time window, and record the result with units.",
            '<a href="https://www.amazon.com/s?k=water+quality+test+strips+pH+chlorine" target="_blank" rel="noopener noreferrer">View water test strips on Amazon</a>',
        ),
        (
            "🎒 Gravity Water Filter",
            "Useful for camping, travel, or an emergency backup when electricity is unavailable.",
            "Add untreated water to the upper bag, keep clean and dirty sides separate, and backwash or replace the filter as directed.",
            '<a href="https://www.amazon.com/s?k=gravity+water+filter+camping" target="_blank" rel="noopener noreferrer">View gravity water filters on Amazon</a>',
        ),
        (
            "🧴 Chlorine and Disinfectant Test Kit",
            "Measures disinfectant residual in pools, tanks, and some treated-water systems.",
            "Collect the sample without touching the test cell, add the specified reagent, and compare the result with local targets.",
            '<a href="https://www.amazon.com/s?k=water+chlorine+test+kit" target="_blank" rel="noopener noreferrer">View chlorine test kits on Amazon</a>',
        ),
        (
            "🔬 Turbidity Tube",
            "Shows whether suspended particles are making water cloudy or interfering with disinfection.",
            "Pour the sample slowly into the tube, read the marking when the target is just visible, and repeat for an unexpected result.",
            '<a href="https://www.amazon.com/s?k=water+turbidity+tube" target="_blank" rel="noopener noreferrer">View turbidity tubes on Amazon</a>',
        ),
        (
            "🧤 Sample Bottles and Protective Gear",
            "Bottles, gloves, labels, and a cooler for safer sampling.",
            "Label first, avoid touching the inside, and keep the sample cool.",
            '<a href="https://www.amazon.com/s?k=water+sampling+bottles+gloves" target="_blank" rel="noopener noreferrer">View water sampling supplies on Amazon</a>',
        ),
    ]

    gear_columns = st.columns(3)
    for item_index, (title, description, instructions, link) in enumerate(gear_items):
        with gear_columns[item_index % 3]:
            st.markdown(
                f"""
                <div class="intro-card gear-card">
                    <h3>{title}</h3>
                    <p>{description}</p>
                    <p><strong>How to use:</strong> {instructions}</p>
                    <p>{link}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.info("Home kits are screening tools, not proof that water is safe or unsafe. Confirm concerning results with an approved laboratory or local health authority.")
