import streamlit as st
import random
import time

# --- UI BRANDING ---
st.set_page_config(page_title="Nexus KMS | Start", layout="centered")

# --- 1. SESSION STATE INITIALIZATION ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = None  
if 'iteration_count' not in st.session_state:
    st.session_state.iteration_count = 0
if 'experiment_group' not in st.session_state:
    st.session_state.experiment_group = None

# --- VISIBLE LANDING PAGE ---
st.title("Nexus Corporate Intelligence")
st.subheader("HCI Research Study")

st.info("""
**Welcome!** This study explores how users interact with AI-driven knowledge systems. 
Please click the button below to be assigned to a system interface and begin your task.
""")

# --- ROUTING LOGIC ---
if st.button("Start Experiment", type="primary"):
    # Randomly assign from 4 groups
    groups = ["Open", "Scaffolded", "Cited", "Persona"]
    st.session_state.experiment_group = random.choice(groups)
    st.session_state.start_time = time.time()
    
    with st.spinner("Assigning Research Group..."):
        time.sleep(1) 
        
        if st.session_state.experiment_group == "Open":
            st.switch_page("pages/open.py")
        elif st.session_state.experiment_group == "Scaffolded":
            st.switch_page("pages/scaffold.py")
        elif st.session_state.experiment_group == "Cited":
            st.switch_page("pages/cited.py")
        elif st.session_state.experiment_group == "Persona":
            st.switch_page("pages/persona.py")