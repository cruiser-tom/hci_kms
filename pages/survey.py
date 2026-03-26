import streamlit as st
import time
from supabase import create_client

st.set_page_config(page_title="Crane AI | Final Survey", layout="wide")

st.markdown(
    """
    <style>
    /* This makes all the question labels bigger and slightly bolder */
    div[data-testid="stWidgetLabel"] p {
        font-size: 18px !important;
        font-weight: 500 !important;
    }
    /* Force horizontal radio buttons into a 4-top, 3-bottom layout */
    div[role="radiogroup"] {
        display: grid !important;
        grid-template-columns: repeat(4, max-content) !important;
        row-gap: 10px !important;
        column-gap: 30px !important;
    }
    </style>
    """, 
    unsafe_allow_html=True
)

st.markdown("""
    <style>
    /* Make the Scale subheader smaller and subtle */
    .scale-instruction {
        font-size: 0.95rem !important;
        color: #888888 !important;
        margin-top: -10px !important;
        margin-bottom: 10px !important;
        font-weight: 400 !important;
    }
    </style>
""", unsafe_allow_html=True)
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- SECURITY CHECK ---
if 'participant_id' not in st.session_state or 'experiment_group' not in st.session_state:
    st.warning("⚠️ No active session found. Please start from the main page.")
    st.stop()

ui_group = st.session_state.experiment_group
options_7pt = [1, 2, 3, 4, 5, 6, 7]

# 1. Pull the page container up to the top
st.markdown("""
    <style>
    .block-container {
        padding-top: 0rem !important; 
    }
    </style>
""", unsafe_allow_html=True)

# 2. Your existing Title block (slightly adjusted for tighter spacing)
st.markdown(
    """
    <div style="text-align: center; margin-top: -10px;">
        <h1 style="font-size: 2.5rem; font-weight: 600; margin-bottom: 5px;">Post-Experiment Survey</h1>
        <p style="font-size: 1.1rem; color: #888; margin-top: 0;">There are no right or wrong answers. Honest responses are essential to the research.</p>
    </div>
    """, 
    unsafe_allow_html=True
)

st.divider()
st.markdown("""
    <style>
    /* Make the survey questions larger */
    [data-testid="stMarkdownContainer"] p {
        font-size: 1.2rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.5rem !important;
    }

    /* Add more space between questions so it doesn't look crowded */
    [data-testid="stVerticalBlock"] > div {
        margin-bottom: 10px !important;
    }
    </style>
""", unsafe_allow_html=True)
# --- PART 1: COMMON CORE ---
st.header("Part 1: Core System Evaluation")
st.markdown('<p class="scale-instruction">Scale: 1 = Strongly Disagree, 7 = Strongly Agree</p>', unsafe_allow_html=True)

st.subheader("Section A - Trust in the AI System")
a1 = st.radio("1. I trusted the AI's recommendations to make my final decision.", options_7pt, horizontal=True, index=None)
a2 = st.radio("2. The AI system performed reliably throughout my interaction.", options_7pt, horizontal=True, index=None)
a3 = st.radio("3. I felt confident in the accuracy of the information the AI provided.", options_7pt, horizontal=True, index=None)
a4 = st.radio("4. I felt the AI was transparent about how it arrived at its answers.", options_7pt, horizontal=True, index=None)
a5 = st.radio("5. I was concerned that the AI might be incorrect or misleading.", options_7pt, horizontal=True, index=None)

st.subheader("Section B - Perceived Usability")
b1 = st.radio("1. The interface was easy to navigate and understand.", options_7pt, horizontal=True, index=None)
b2 = st.radio("2. I found the layout of the AI chat interface intuitive.", options_7pt, horizontal=True, index=None)
b3 = st.radio("3. The time I spent on the task felt appropriate and efficient.", options_7pt, horizontal=True, index=None)
b4 = st.radio("4. I would find this type of interface unnecessarily complex to use on a regular basis.", options_7pt, horizontal=True, index=None)
b5 = st.radio("5. To ensure data quality, please select '2' for this question.", options_7pt, horizontal=True, index=None)

st.subheader("Section C - Transparency & Decision-Making")
c1 = st.radio("1. The AI interface made it clear how it reached its conclusions.", options_7pt, horizontal=True, index=None)
c2 = st.radio("2. I felt I needed additional verification beyond what the AI provided.", options_7pt, horizontal=True, index=None)
c3 = st.radio("3. The information displayed was sufficient for me to make a confident decision.", options_7pt, horizontal=True, index=None)
c4 = st.radio("4. I would have liked more explanation about how the AI processes and evaluates data.", options_7pt, horizontal=True, index=None)
c5 = st.radio("5. The way the AI presented data visibly influenced my final product decision.", options_7pt, horizontal=True, index=None)

st.divider()

# --- PART 2: CONDITION-SPECIFIC MODULES ---
st.header(f"Part 2: Interface Specifics")
st.caption("Please reflect on the specific features of the interface you just used.")

condition_data = {}

if ui_group == "Minimal":
    m1 = st.radio("1. I felt uncertain about where to begin when I first started interacting with the AI.", options_7pt, horizontal=True, index=None)
    m2 = st.radio("2. The lack of visual guidance made me less confident in my final answer.", options_7pt, horizontal=True, index=None)
    m3 = st.radio("3. I felt I had to put in more mental effort to formulate useful questions compared to what a guided interface might require.", options_7pt, horizontal=True, index=None)
    m4 = st.radio("4. Despite the minimal interface, I felt in control of the direction of the conversation.", options_7pt, horizontal=True, index=None)
    
    st.write("**5. Rate how much you wished the interface had provided the following features:**")
    st.caption("Scale: 1 = Did not want it at all, 7 = Strongly wanted it")
    rank_m1 = st.radio("Suggested prompts", options_7pt, horizontal=True, index=None, key="rm1")
    rank_m2 = st.radio("Confidence score", options_7pt, horizontal=True, index=None, key="rm2")
    rank_m3 = st.radio("Structured data table", options_7pt, horizontal=True, index=None, key="rm3")
    rank_m4 = st.radio("Step-by-step explanation", options_7pt, horizontal=True, index=None, key="rm4")
    
    condition_data = {"M1": m1, "M2": m2, "M3": m3, "M4": m4, "Rank_Prompts": rank_m1, "Rank_Score": rank_m2, "Rank_Table": rank_m3, "Rank_Explanation": rank_m4}

elif ui_group == "Explainable":
    e1 = st.radio("1. The animated status indicators made the AI feel more sophisticated and trustworthy.", options_7pt, horizontal=True, index=None)
    e2 = st.radio("2. The Confidence Score badge influenced how much I relied on the AI's final answer.", options_7pt, horizontal=True, index=None)
    e3 = st.radio("3. The progress bar helped me feel oriented during the task.", options_7pt, horizontal=True, index=None)
    e4 = st.radio("4. The quick-prompt suggestion chips were helpful in guiding me toward productive questions.", options_7pt, horizontal=True, index=None)
    e5 = st.radio("5. The additional visual elements felt like they slowed me down rather than helping me.", options_7pt, horizontal=True, index=None)
    
    st.write("**6. Rate how much each of the following features positively influenced your trust in the AI:**")
    st.caption("Scale: 1 = No positive influence, 7 = Strong positive influence")
    rank_e1 = st.radio("Confidence badge", options_7pt, horizontal=True, index=None, key="re1")
    rank_e2 = st.radio("Status indicators (Progress Bar)", options_7pt, horizontal=True, index=None, key="re2")
    rank_e4 = st.radio("Suggestion chips", options_7pt, horizontal=True, index=None, key="re4")
    rank_e5 = st.radio("The written text answer", options_7pt, horizontal=True, index=None, key="re5")
    
    condition_data = {"E1": e1, "E2": e2, "E3": e3, "E4": e4, "E5": e5, "Rank_Badge": rank_e1, "Rank_Status": rank_e2, "Rank_Chips": rank_e4, "Rank_Text": rank_e5}
    
elif ui_group == "Verified":
    v1 = st.radio("1. The formatted data tables made it easier to reach a confident decision compared to a text-only answer.", options_7pt, horizontal=True, index=None)
    v2 = st.radio("2. The AI's use of specific numbers and raw data made its answers feel more credible.", options_7pt, horizontal=True, index=None)
    v3 = st.radio("3. The 'Data Verified System' banner made me feel the AI's outputs were more reliable.", options_7pt, horizontal=True, index=None)
    v4 = st.radio("4. Having numerical evidence available reduced the number of follow-up questions I needed to ask.", options_7pt, horizontal=True, index=None)
    v5 = st.radio("5. The volume of data and numbers presented felt overwhelming at times.", options_7pt, horizontal=True, index=None)
    
    st.write("**6. Rate how much each of the following elements positively influenced your trust in the AI:**")
    st.caption("Scale: 1 = No positive influence, 7 = Strong positive influence")
    rank_v1 = st.radio("Specific metrics and numbers within the text", options_7pt, horizontal=True, index=None, key="rv1")
    rank_v2 = st.radio("The Markdown data table", options_7pt, horizontal=True, index=None, key="rv2")
    rank_v3 = st.radio("The 'Data Verified' red banner", options_7pt, horizontal=True, index=None, key="rv3")
    rank_v4 = st.radio("The written text explanation", options_7pt, horizontal=True, index=None, key="rv4")
    
    condition_data = {"V1": v1, "V2": v2, "V3": v3, "V4": v4, "V5": v5, "Rank_Numbers": rank_v1, "Rank_Table": rank_v2, "Rank_Banner": rank_v3, "Rank_Explanation": rank_v4}

elif ui_group == "Combined":
    cb1 = st.radio("1. Martha's friendly personality made the data verification table feel more trustworthy.", options_7pt, horizontal=True, index=None)
    cb2 = st.radio("2. Martha's conversational tone made the raw data table easier to trust.", options_7pt, horizontal=True, index=None)
    cb3 = st.radio("3. The animated status indicators and progress bar made me feel Martha was working harder to find a reliable answer.", options_7pt, horizontal=True, index=None)
    cb4 = st.radio("4. The number of features in the interface felt overwhelming rather than helpful.", options_7pt, horizontal=True, index=None)
    cb5 = st.radio("5. Martha's personality influenced my trust more than the data table she provided.", options_7pt, horizontal=True, index=None)
    
    st.write("**6. Rate how much each of the following features positively influenced your trust in the AI:**")
    st.caption("Scale: 1 = No positive influence, 7 = Strong positive influence")
    rank_cb1 = st.radio("Martha's friendly persona", options_7pt, horizontal=True, index=None, key="rcb1")
    rank_cb2 = st.radio("The loading status indicators", options_7pt, horizontal=True, index=None, key="rcb2")
    rank_cb3 = st.radio("The verified data table", options_7pt, horizontal=True, index=None, key="rcb3")
    rank_cb4 = st.radio("The suggestion chips", options_7pt, horizontal=True, index=None, key="rcb4")
    
    condition_data = {"CB1": cb1, "CB2": cb2, "CB3": cb3, "CB4": cb4, "CB5": cb5, "Rank_Persona": rank_cb1, "Rank_Status": rank_cb2, "Rank_Table": rank_cb3, "Rank_Chips": rank_cb4}

st.divider()

# --- PART 3: REFLECTION & DEMOGRAPHICS ---
st.header("Part 3: Reflection & Demographics")

d1 = st.selectbox("1. How often do you use AI-powered tools in your daily work or study?", ["Never", "Rarely (less than once per month)", "Sometimes (about once per week)", "Often (daily)", "Very Often (multiple times per day)"], index=None)
d2 = st.text_input("2. What aspect of the interface most influenced your trust in the AI's answer? (Optional)")
d3 = st.text_input("3. Was there any feature you felt was missing, or that would have improved your experience? (Optional)")
d4 = st.selectbox("4. Overall, how would you rate your experience with the AI interface?", ["1 - Very Poor", "2 - Poor", "3 - Fair", "4 - Good", "5 - Excellent"], index=None)
d5 = st.selectbox("5. What is your age range?", ["18 – 24", "25 – 34", "35 – 44", "45 or above"], index=None)
d6 = st.selectbox("6. What is your gender?", ["Male", "Female", "Prefer not to say"], index=None)
d7 = st.selectbox("7. What is your highest level of education completed?", ["High School / Secondary Education", "Undergraduate Degree (Bachelor's)", "Postgraduate Degree (Master's)", "Doctoral Degree (PhD)"], index=None)

st.divider()

# --- VALIDATION AND SUBMIT ---
core_answers = [a1, a2, a3, a4, a5, b1, b2, b3, b4, c1, c2, c3, c4, c5]
demo_answers = [d1, d4, d5, d6, d7] 
condition_answers = list(condition_data.values())

all_required_answers = core_answers + demo_answers + condition_answers

if st.button("Submit Survey & Finish", type="primary", use_container_width=True):
    if None in all_required_answers:
        st.error("⚠️ Please answer all multiple-choice questions before submitting.")
    else:
        with st.spinner("Saving responses..."):
            
            full_survey_payload = {
                "Core_A": {"A1": a1, "A2": a2, "A3": a3, "A4": a4, "A5": a5},
                "Core_B": {"B1": b1, "B2": b2, "B3": b3, "B4": b4, "B5": b5}, 
                "Core_C": {"C1": c1, "C2": c2, "C3": c3, "C4": c4, "C5": c5},
                "Condition_Specific": condition_data,
                "Demographics": {"D1": d1, "D2": d2, "D3": d3, "D4": d4, "D5": d5, "D6": d6, "D7": d7}
            }
            
            try:
                # 1. Save data to Supabase
                supabase.table("HCI").update({"Survey_Data": full_survey_payload}).eq("Participant_ID", st.session_state.participant_id).execute()
                
                # 2. Clear the session state so they can't take the study twice
                st.session_state.clear() 
                
                # 3. Instantly redirect them to your new success page
                st.switch_page("success.py") 
                # Note: If your success.py is inside a 'pages' folder, use st.switch_page("pages/success.py") instead
                
            except Exception as e:
                st.error(f"Error saving data: {e}")
