import streamlit as st
import random
import time

# --- UI BRANDING ---
st.set_page_config(page_title="Crane AI | Research Portal", layout="centered")

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
        <p style="font-size: 1.2rem; color: #888;">Human-Computer Interaction Study: GenAI Trust Models</p>
    </div>
    """, 
    unsafe_allow_html=True
)

st.info("""
**Welcome to the Crane AI Simulation.** You are participating in an academic study exploring how users interact with different Generative AI system designs. 

* **Data Privacy:** Your completion time and interaction metrics will be recorded completely anonymously.
""")

# The distinct breakout box for the task
st.warning("🎯 **YOUR TASK:** Use the AI assistant below to find the TWO products with the highest confirmed probability of fake/bot-generated reviews.")


# Center the button to match the GenAI aesthetic
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("Initialize AI System", type="primary", use_container_width=True):
        # Randomly assign from 4 groups
        groups = ["Open", "Scaffolded", "Cited", "Combined"]
        st.session_state.experiment_group = random.choice(groups)
        st.session_state.start_time = time.time()
        
        with st.spinner("Provisioning secure AI environment..."):
            time.sleep(1.2) # Adds a realistic "loading" feel before switching
            
            if st.session_state.experiment_group == "Open":
                st.switch_page("pages/open.py")
            elif st.session_state.experiment_group == "Scaffolded":
                st.switch_page("pages/scaffold.py")
            elif st.session_state.experiment_group == "Cited":
                st.switch_page("pages/cited.py")
            elif st.session_state.experiment_group == "Combined":
                st.switch_page("pages/combined.py")
