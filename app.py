import streamlit as st
import random
import time

# --- 1. SESSION STATE INITIALIZATION ---
# We do this here so the variables exist before the student switches pages
if 'start_time' not in st.session_state:
    st.session_state.start_time = None  # We'll set this when they click 'Start'
if 'iteration_count' not in st.session_state:
    st.session_state.iteration_count = 0
if 'experiment_group' not in st.session_state:
    st.session_state.experiment_group = None

st.title("KMS Research Study")
st.write("Welcome! Please click the button below to be assigned to a system and begin the task.")

if st.button("Start Experiment", type="primary"):
    # Assign group and start the clock
    st.session_state.experiment_group = random.choice(["Open", "Scaffolded"])
    st.session_state.start_time = time.time()
    
    if st.session_state.experiment_group == "Open":
        st.switch_page("pages/open.py")
    else:
        st.switch_page("pages/scaffold.py")
