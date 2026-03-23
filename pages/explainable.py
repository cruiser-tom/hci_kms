import streamlit as st
import time
from supabase import create_client
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="Crane AI", layout="centered", initial_sidebar_state="collapsed")


# --- DEVELOPMENT BYPASS (Remove or comment out before launching study) ---
# if 'participant_id' not in st.session_state:
#     st.session_state.participant_id = int(time.time())
# if 'experiment_group' not in st.session_state:
#     st.session_state.experiment_group = "Explainable"

# --- STRICT SECURITY CHECK (Uncomment this when the study goes live!) ---
if 'participant_id' not in st.session_state or 'experiment_group' not in st.session_state:
    st.warning("⚠️ No active session found. Please start from the main page.")
    st.stop()
    
# --- CUSTOM CSS (The Clean HTML Foundation) ---
st.markdown(
    """
    <style>
    /* Hide default Streamlit elements */
    #MainMenu, footer, header {visibility: hidden;}

    /* Lock the main width to 700px and center it */
    .block-container {
        max-width: 700px !important; 
        padding-top: 1rem !important;
        padding-bottom: 1rem !important; 
    }
    [data-testid="stBottomBlock"] > div {
        max-width: 700px !important; 
    }
    </style>
    """,
    unsafe_allow_html=True
)

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
supabase = init_connection()

# --- INITIALIZE MEMORY ---
if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'iteration_count' not in st.session_state:
    st.session_state.iteration_count = 0
if 'messages' not in st.session_state:
    st.session_state.messages = []

# ---> EXPLAINABLE SYSTEM PROMPT <---
SYSTEM_CONTEXT = """
You are an advanced explainable AI (xAI) designed to analyze e-commerce product reviews and detect fake, AI-generated text.
Only answer based on this provided data. Keep responses analytical and explain them.
IF the user is just greeting you (e.g., "Hi", "Thanks", "How are you?"): DO NOT analyse. Just reply conversationally and tell it to ask something to explain.

--- PRODUCT REVIEW DATASET ---
# Product: AeroGlide Sneakers (4,500 Reviews, 4.9/5 Rating). AI Analysis: WARNING. 85% repetitive sentence structure. High probability of bots.
# Product: Titan Smartwatch (1,200 Reviews, 3.8/5 Rating). AI Analysis: Authentic.
# Product: Lumina Desk Lamp (300 Reviews, 4.7/5 Rating). AI Analysis: Authentic.
# Product: Zenith Wireless Earbuds (8,900 Reviews, 4.6/5 Rating). AI Analysis: Suspicious. Spike of 4,000 5-star reviews in May. Needs manual review.
# Product: Apex Gaming Chair (650 Reviews, 5.0/5 Rating). AI Analysis: CRITICAL WARNING. 100% of 5-star reviews from 1-week old accounts. Confirmed bot network.
# Product: Echo Home Security Camera (2,100 Reviews, 4.2/5 Rating). AI Analysis: Authentic.
# Product: Nova Water Bottle (150 Reviews, 2.1/5 Rating). AI Analysis: Authentic.
# Product: Quantum Laptop Stand (3,400 Reviews, 4.8/5 Rating). AI Analysis: Authentic.
"""

def scaffolded_interface():
    
    # --- DISPLAY PAST CHAT HISTORY ---
    for message in st.session_state.messages:
        if message["role"] == "user":
            # Pure HTML User Bubble
            st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
                    <div style="background-color: #2b2b2b; color: #ffffff; padding: 12px 18px; border-radius: 20px 20px 5px 20px; max-width: 80%; width: fit-content; line-height: 1.5;">
                        {message["content"]}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # Standard Markdown for AI (No st.chat_message)
            st.markdown(message["content"])
            st.caption("🛡️ System Confidence Score: 96.8%")
            st.markdown("<br>", unsafe_allow_html=True)

    # --- THE SINGLE CHAT INPUT ---
    user_query = st.chat_input("Message Crane...")
    

   # --- THE "EMPTY STATE" ---
    # 1. Create a wrapper that we can instantly delete
    empty_placeholder = st.empty()
    
    if not user_query and len(st.session_state.messages) == 0:
        # 2. Put the welcome text and buttons INSIDE the wrapper
        with empty_placeholder.container():
            st.markdown(
                """
                <div style="text-align: center; padding-top: 8vh; padding-bottom: 4vh;">
                    <h1 style="font-size: 4rem; font-weight: 600; margin-bottom: 0;">Crane <span style="color: #0068c9;">AI</span></h1>
                    <p style="font-size: 1.2rem; color: #888;">Explainable AI Analysis Engine</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.caption("Suggested quick queries:")
            col1, col2 = st.columns(2)
            
            # Save the clicks to variables instead of putting the logic directly inside
            clicked_1 = col1.button("Scan all products for fake reviews", use_container_width=True)
            clicked_2 = col2.button("List products with 100% bot activity", use_container_width=True)
            
        # 3. Check for the clicks OUTSIDE the 'with' block to instantly delete the wrapper
        if clicked_1:
            user_query = "Scan all products for fake reviews"
            empty_placeholder.empty()
            
        elif clicked_2:
            user_query = "List products with 100% bot activity"
            empty_placeholder.empty()

    
    # --- THE ACTIVE STATE ---
    if user_query:
        st.session_state.iteration_count += 1
        
        # 1. Show the user message instantly via HTML
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
                <div style="background-color: #2b2b2b; color: #ffffff; padding: 12px 18px; border-radius: 20px 20px 5px 20px; max-width: 80%; width: fit-content; line-height: 1.5;">
                    {user_query}
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": user_query})
            
        # 2. Prefix Filter for Progress Bar
        words_in_query = user_query.lower().split()
        task_prefixes = ["prod", "review", "bot", "fake", "susp", "scan", "analy", "data", "list", "activ"]
        is_task_query = any(word.startswith(prefix) for word in words_in_query for prefix in task_prefixes)
        
        # Explainable Progress Bar Logic (Kept exactly as requested)
        if is_task_query:
            with st.status("Crane AI is analyzing the dataset...", expanded=True) as status:
                progress_bar = st.progress(0)
                st.write("🔍 Extracting product metadata...")
                progress_bar.progress(30)
                time.sleep(1.0) 
                st.write("📊 Running linguistic anomaly detection models...")
                progress_bar.progress(70)
                time.sleep(1.0)
                st.write("✅ Compiling final trust and safety report...")
                progress_bar.progress(100)
                status.update(label="Analysis Complete", state="complete", expanded=False)
        else:
            # Add a tiny invisible container to keep spacing consistent if no progress bar is shown
            st.container()
                
        # 3. Generate and show AI response
        chat_history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages])
        full_prompt = f"{SYSTEM_CONTEXT}\n\nChat History:\n{chat_history_text}\n\nUser Query: {user_query}"
        
        try:
            response = model.generate_content(full_prompt)
            
            # Show AI response natively (No st.chat_message)
            st.markdown(response.text)
            st.caption("🛡️ System Confidence Score: 96.8%")
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except ResourceExhausted:
            st.warning("⚠️ High traffic. Please wait 15 seconds.")
        except Exception as e:
            st.error("System Error.")

scaffolded_interface()


# --- BOTTOM FINISH BUTTON ---
st.write("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    # 1. Create an empty placeholder
    finish_placeholder = st.empty()
    
    # 2. Put the button INSIDE the placeholder
    if finish_placeholder.button("✅ I found the two products!", type="primary", use_container_width=True):
        
        # 3. INSTANTLY delete the button from the screen so it can't duplicate or be double-clicked
        finish_placeholder.empty() 
        
        # 4. Show a clean loading spinner exactly where the button used to be
        with st.container():
            st.info("Logging data & redirecting...")
            
            total_time = round(time.time() - st.session_state.start_time, 2)
            part_id = st.session_state.get("participant_id", int(time.time()))
            
            # NOTE: Change "Explainable" to "Minimal" or "Verified" depending on which file you are editing!
            group = st.session_state.get("experiment_group", "Explainable") 
            
            data = {
                "Participant_ID": part_id, 
                "Condition": group,    
                "Total_Time_Seconds": total_time, 
                "Prompt_Iterations": st.session_state.iteration_count
            }
            
            try:
                supabase.table("HCI").insert(data).execute()
                time.sleep(0.5)
                st.switch_page("pages/survey.py") 
            except Exception as e:
                st.error(f"Error logging data: {e}")
