import streamlit as st
import time
from supabase import create_client
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="Crane AI | Standard System", layout="centered")

# --- CUSTOM CSS ---
st.markdown(
    """
    <style>
    div[data-testid="stChatMessage"]:has(.user-anchor) {
        flex-direction: row-reverse;
    }
    div[data-testid="stChatMessage"]:has(.user-anchor) div[data-testid="stChatMessageContent"] {
        align-items: flex-end;
    }
    div[data-testid="stChatMessage"]:has(.user-anchor) .stMarkdown p {
        text-align: right;
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

# Notice the prompt is generic: No "Martha", no table rules, just pure data access.
SYSTEM_CONTEXT = """
You are a standard AI assistant designed to analyze e-commerce product reviews.
Answer the user's questions clearly and directly based on the dataset provided. 
Do not use markdown tables unless the user explicitly asks for one.

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

def minimalist_interface():
    
    # --- DISPLAY PAST CHAT HISTORY ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown("<div class='user-anchor'></div>", unsafe_allow_html=True)
            st.markdown(message["content"])

    user_query = st.chat_input("Message AI...")
    
    # --- THE "EMPTY STATE" ---
    if not user_query and len(st.session_state.messages) == 0:
        st.markdown(
            """
            <div style="text-align: center; padding-top: 10vh; padding-bottom: 6vh;">
                <h1 style="font-size: 4rem; font-weight: 600; margin-bottom: 0;">Crane <span style="color: #0068c9;">AI</span></h1>
                <p style="font-size: 1.2rem; color: #888;">How can I help you today?</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.caption("Suggested Queries:")
        col1, col2 = st.columns(2)
        if col1.button("Can you check for fake reviews?"):
            user_query = "Can you check for fake reviews?"
        if col2.button("Which products have suspicious bot activity?"):
            user_query = "Which products have suspicious bot activity?"

    # --- THE ACTIVE STATE ---
    if user_query:
        st.session_state.iteration_count += 1
        
        # 1. Show the user message
        with st.chat_message("user"):
            st.markdown("<div class='user-anchor'></div>", unsafe_allow_html=True)
            st.write(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})
            
        # 2. Prefix Filter logic
        words_in_query = user_query.lower().split()
        task_prefixes = ["prod", "review", "bot", "fake", "susp", "scan", "analy", "data", "list", "activ"]
        is_task_query = any(word.startswith(prefix) for word in words_in_query for prefix in task_prefixes)
        
        # 3. Standard "Black Box" Spinner
        if is_task_query:
            spinner_context = st.spinner("Thinking...")
        else:
            spinner_context = st.container() 
            
        with spinner_context:
            chat_history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages])
            full_prompt = f"{SYSTEM_CONTEXT}\n\nChat History:\n{chat_history_text}\n\nUser Query: {user_query}"
            
            try:
                response = model.generate_content(full_prompt)
                
                # Standard default Streamlit icon, no typing delay, no tables
                with st.chat_message("assistant"):
                    st.write(response.text)
                    st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
            except ResourceExhausted:
                st.warning("⚠️ High traffic. Please wait 15 seconds.")
            except Exception as e:
                st.error("System Error.")

minimalist_interface()
st.write("---")

if st.button("✅ I found the two products!"):
    total_time = round(time.time() - st.session_state.start_time, 2)
    st.session_state.participant_id = int(time.time()) 
    
    data = {
        "Participant_ID": st.session_state.participant_id, 
        "Condition": "Minimal", 
        "Total_Time_Seconds": total_time, 
        "Prompt_Iterations": st.session_state.iteration_count
    }
    
    try:
        supabase.table("HCI").insert(data).execute()
        st.success("Data logged. Redirecting to final survey...")
        time.sleep(0.5)
        st.switch_page("pages/survey.py") 
    except Exception as e:
        st.error(f"Error: {e}")
