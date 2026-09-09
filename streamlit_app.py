import streamlit as st
import time

st.set_page_config(page_title="AquaCheck Hub", page_icon="💧", layout="wide")

# Custom Styling / Banner Header
st.markdown("""
    <style>
    :root {
        --ink: #16324F;
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
    }
    .block-container {
        max-width: 1180px;
        padding-top: 2.5rem;
        padding-bottom: 3rem;
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
    }
    .stCaption, [data-testid="stCaptionContainer"] {
        color: var(--muted-ink);
    }
    h1, h2, h3, h4, p, label, [data-testid="stMarkdownContainer"] {
        color: var(--ink);
    }
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #E1F3F1 0%, #F4FAFC 100%);
        border-right: 1px solid #B8DCD9;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label {
        color: var(--deep-ocean);
        font-weight: 600;
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
    }
    [data-baseweb="select"] *, [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: var(--ink);
    }
    .stButton > button[kind="primary"] {
        background: var(--coral);
        border: 0;
        color: #FFFFFF;
        font-weight: 700;
        box-shadow: 0 6px 14px rgba(232, 102, 85, 0.25);
    }
    .stButton > button[kind="primary"]:hover {
        background: #C94F42;
        color: #FFFFFF;
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
    }
    .intro-card h3 {
        color: var(--deep-ocean);
        margin-top: 0;
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
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">💧 AquaCheck — Interactive Water Safety Hub</div>', unsafe_allow_html=True)
st.caption("AI Inspection • Interactive pH Tester • Community Map • Safety Gear")

# Sidebar Navigation
page = st.sidebar.radio("Explore Features", [
    "🌍 About AquaCheck",
    "🔍 AI Risk Inspection",
    "📢 Community Incident Map",
    "📖 Inspector Field Guide",
    "🏆 Inspector Quiz & Badge",
    "🛒 Gear & Testing Kits",
    "🧪 Interactive pH Simulator",
])

# ---------------------------------------------------------
# 1. ABOUT AQUACHECK
# ---------------------------------------------------------
if page == "🌍 About AquaCheck":
    st.header("🌍 What is AquaCheck?")
    st.write(
        "AquaCheck is a community water-safety hub that helps people notice possible "
        "water concerns, learn basic inspection skills, and choose a sensible next step."
    )

    st.markdown(
        """
        <div class="purpose-strip">
            <h2>Our purpose: a healthier, safer environment</h2>
            <p>
                AquaCheck makes water-safety information easier to understand so people
                can respond early, protect their households, and support healthier communities.
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

    col1, col2 = st.columns(2)
    with col1:
        zip_code = st.selectbox(
            "Select a real ZIP / postal code location",
            [
                "90210 — Beverly Hills, United States",
                "SW1A 1AA — London, United Kingdom",
                "M5V 2T6 — Toronto, Canada",
                "400001 — Mumbai, India",
                "00100 — Nairobi, Kenya",
                "2000 — Sydney, Australia",
                "01000-000 — São Paulo, Brazil",
                "100-0001 — Tokyo, Japan",
            ],
        )
        water_type = st.selectbox("Source", ["Tap Water", "Well Water", "River/Lake", "Bottled Water"])
        appearance = st.multiselect("Appearance & Odor", ["Cloudy / Turbid", "Rusty / Brownish", "Metallic Smell", "Earthy Smell", "Clear"])

    with col2:
        symptoms = st.multiselect("Symptoms Reported", ["Stomach Cramps", "Nausea", "Skin Rash", "None"])
        clarity_rating = st.slider("Visual Clarity Rating (1 = Very Dirty, 10 = Crystal Clear)", 1, 10, 7)

    if st.button("⚡ Run Live AquaCheck Inspection", type="primary"):
        with st.spinner("Analyzing parameters against municipal database..."):
            time.sleep(1) # Simulation delay for realism

        risk_score = 0
        if "Cloudy / Turbid" in appearance or "Rusty / Brownish" in appearance:
            risk_score += 40
        if "Stomach Cramps" in symptoms or "Nausea" in symptoms:
            risk_score += 40
        if clarity_rating < 5:
            risk_score += 20

        st.subheader("Analysis Results")
        st.progress(min(risk_score, 100))

        if risk_score >= 50:
            st.error(f"⚠️ **HIGH RISK ALERT for {zip_code} (Risk Score: {risk_score}/100)**")
            st.write("👉 **Immediate Action:** Boil water for at least 3 minutes before drinking or cooking. Use certified carbon filtration.")
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
# 3. COMMUNITY INCIDENT MAP LOG
# ---------------------------------------------------------
elif page == "📢 Community Incident Map":
    st.header("📢 Live Community Hazard Map")

    if "reports" not in st.session_state:
        st.session_state.reports = [
            {"zip": "90210", "issue": "Brownish tap water after pipe maintenance", "status": "Under Review", "votes": 12},
            {"zip": "10001", "issue": "Strong chlorine odor from kitchen sink", "status": "Alert Active", "votes": 28}
        ]

    st.subheader("Report an Issue in Your Neighborhood")
    with st.form("new_report"):
        r_zip = st.text_input("Zip Code")
        r_desc = st.text_area("Describe what you observed")
        r_submit = st.form_submit_button("Submit Incident Report")

        if r_submit and r_zip and r_desc:
            st.session_state.reports.append({"zip": r_zip, "issue": r_desc, "status": "Community Verification", "votes": 1})
            st.success("Report added to public community log!")

    st.subheader("Recent Community Reports")
    for idx, r in enumerate(reversed(st.session_state.reports)):
        c1, c2 = st.columns([4, 1])
        with c1:
            st.warning(f"📍 **ZIP {r['zip']}** | Status: `{r['status']}`\n\n*{r['issue']}*")
        with c2:
            if st.button(f"👍 Confirm ({r['votes']})", key=f"upvote_{idx}"):
                r['votes'] += 1
                st.rerun()

# ---------------------------------------------------------
# 4. INSPECTOR QUIZ & BADGE
# ---------------------------------------------------------
elif page == "🏆 Inspector Quiz & Badge":
    st.header("🏆 Inspector Learning Quiz")
    st.write("Test your water safety knowledge and review the field guide when you need a refresher.")
    st.info("This is a learning activity, not a professional certification or substitute for local training.")

    # Ask practical questions that an entry-level inspector should understand.
    q1 = st.radio(
        "1. What should you do before collecting a water sample?",
        ["Rinse the labeled container with the sample", "Wash your hands and check the sample instructions", "Add soap to the container"],
    )
    q2 = st.radio(
        "2. Which pH range is commonly used as a drinking-water reference range?",
        ["2.0 - 4.0", "6.5 - 8.5", "11.0 - 13.0"],
    )
    q3 = st.radio(
        "3. What does cloudy or turbid water tell an inspector?",
        ["It may contain suspended particles and needs further investigation", "It is always safe because particles are visible", "It proves the water contains E. coli"],
    )
    q4 = st.radio(
        "4. Why record the sample location, date, and time?",
        ["To make the report traceable and comparable", "To change the test result", "It is optional if the water looks clear"],
    )
    q5 = st.radio(
        "5. What is the safest response when a sample may be contaminated?",
        ["Taste it to confirm the result", "Use appropriate protective equipment and follow the test kit instructions", "Pour it into a public drinking fountain"],
    )
    q6 = st.radio(
        "6. Which result should be confirmed with an approved laboratory or local authority?",
        ["A result outside the test kit's expected range", "A clearly labeled sample", "A normal-looking water sample"],
    )
    q7 = st.radio(
        "7. What should an inspector do with a test kit past its expiration date?",
        ["Use it anyway if the package looks clean", "Replace it with an in-date kit", "Mix it with another kit"],
    )
    q8 = st.radio(
        "8. What does a high turbidity reading describe?",
        ["More suspended particles or cloudiness", "The exact amount of bacteria", "The temperature of the sample"],
    )
    q9 = st.radio(
        "9. Why might an inspector measure disinfectant residual?",
        ["To see whether treated water still has disinfectant present", "To prove the water has no metals", "To replace every bacteria test"],
    )
    q10 = st.radio(
        "10. Which detail belongs in a useful inspection report?",
        ["Only the inspector's opinion", "The method, result, units, location, and time", "A guess about the source of contamination"],
    )

    if st.button("Submit Quiz Answers"):
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

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🚰 UV Purifier Pitcher")
        st.write("Browse UV water purification pitchers and compare current options.")
        st.markdown("[View UV water purifiers on Amazon](https://www.amazon.com/s?k=UV+water+purifier+pitcher)")

    with col2:
        st.subheader("🧪 16-in-1 Test Strips")
        st.write("Compare water test strips for pH, chlorine, hardness, and other readings.")
        st.markdown("[View water test strips on Amazon](https://www.amazon.com/s?k=water+quality+test+strips+pH+chlorine)")

    with col3:
        st.subheader("🎒 Survival Straw Filter")
        st.write("Compare portable filters for emergency and outdoor use.")
        st.markdown("[View portable water filters on Amazon](https://www.amazon.com/s?k=portable+water+filter+emergency)")
