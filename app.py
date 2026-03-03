import streamlit as st
import random
import time

# --- UI BRANDING (Matches your interface pages) ---
st.set_page_config(page_title="Frame KMS | Start", layout="centered")

# --- 1. SESSION STATE INITIALIZATION ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = None  
if 'iteration_count' not in st.session_state:
    st.session_state.iteration_count = 0
if 'experiment_group' not in st.session_state:
    st.session_state.experiment_group = None

# --- VISIBLE LANDING PAGE ---
st.title("Frame Corporate Intelligence")
st.divider()
st.subheader("HCI Research Study")

st.info("""
**Welcome!** This study explores how users interact with AI-driven knowledge systems. 
Please click the button below to be randomly assigned to a system interface and begin your task.
""")

# --- ROUTING LOGIC ---
if st.button("Start Experiment", type="primary"):
    # Randomly assign group (Ensuring the name exactly matches your data logging)
    st.session_state.experiment_group = random.choice(["Open", "Scaffolded"])
    st.session_state.start_time = time.time()
    
    with st.spinner("Assigning Research Group..."):
        time.sleep(1) # Small delay for realism and to ensure state saves securely
        
        # Switch to the assigned page
        if st.session_state.experiment_group == "Open":
            st.switch_page("pages/open.py")
        else:
            st.switch_page("pages/scaffold.py")
