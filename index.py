import streamlit as st
import random
import time

# --- UI BRANDING ---
st.set_page_config(page_title="Crane AI", layout="centered")

# --- 1. SESSION STATE INITIALIZATION ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = None  
if 'iteration_count' not in st.session_state:
    st.session_state.iteration_count = 0
if 'experiment_group' not in st.session_state:
    st.session_state.experiment_group = None

# --- GENAI RESEARCH LANDING PAGE ---
# This creates the giant GenAI-style header perfectly centered on the screen
st.markdown(
    """
    <div style="text-align: center; padding-top: 4vh; padding-bottom: 2vh;">
        <h1 style="font-size: 3.5rem; font-weight: 600; margin-bottom: 0px;">Crane <span style="color: #0068c9;">AI</span></h1>
        <p style="font-size: 1.2rem; color: #888;">Human-Computer Interaction Study</p>
        <p style='font-size: 1.2rem; color: #888;'>
        <b>Welcome to the Crane AI Simulation.</b> You are participating in an academic study exploring how users interact with different Generative AI system designs.
        </p>
    </div>
    """, 
    unsafe_allow_html=True
)


st.info("""
🛡️ **Data Privacy & Consent:** All interaction metrics and survey responses are completely anonymous and collected strictly for academic research purposes. By continuing, you consent to participate.
""")

# The distinct breakout box for the task
st.warning("🎯 **YOUR TASK:** Use the AI assistant below to find the TWO products with the highest confirmed probability of fake/bot-generated reviews.")


# Center the button to match the GenAI aesthetic
col1, col2, col3 = st.columns([1, 2, 1])
with col2:

    if st.button("Initialize AI System", type="primary", use_container_width=True):
        st.session_state.participant_id = int(time.time())
        # Update the group names for your database
        groups = ["Minimal", "Explainable", "Verified", "Combined"]
        st.session_state.experiment_group = random.choice(groups)
        st.session_state.start_time = time.time()
        
        with st.spinner("Provisioning secure AI environment..."):
            time.sleep(0.5) 
            
            if st.session_state.experiment_group == "Minimal":
                st.switch_page("pages/minimal.py")
            elif st.session_state.experiment_group == "Explainable":
                st.switch_page("pages/explainable.py")
            elif st.session_state.experiment_group == "Verified":
                st.switch_page("pages/verified.py")
            elif st.session_state.experiment_group == "Combined":
                st.switch_page("pages/combined.py")
                
        
