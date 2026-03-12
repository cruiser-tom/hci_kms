import streamlit as st
import time
from supabase import create_client
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="Crane AI | Open Chat", layout="centered")
# --- CUSTOM CSS FOR RIGHT-ALIGNED USER CHAT ---
st.markdown(
    """
    <style>
    /* Target any chat message that contains our hidden user-anchor */
    div[data-testid="stChatMessage"]:has(.user-anchor) {
        flex-direction: row-reverse;
    }
    
    /* Align the text inside the content box to the right */
    div[data-testid="stChatMessage"]:has(.user-anchor) div[data-testid="stChatMessageContent"] {
        align-items: flex-end;
    }
    
    /* Ensure paragraph text is right-aligned */
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

if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'iteration_count' not in st.session_state:
    st.session_state.iteration_count = 0




SYSTEM_CONTEXT = """
You are an advanced AI designed to analyze e-commerce product reviews and detect fake, AI-generated text.
Only answer based on this provided data. Keep responses concise and analytical.

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

def open_interface():
    # The chat input always floats at the bottom
    user_query = st.chat_input("Message Crane...")
    
    # --- THE "EMPTY STATE" (Disappears after first use) ---
    # It only shows if they haven't typed anything yet AND haven't run any iterations
    if not user_query and st.session_state.iteration_count == 0:
        st.markdown(
            """
            <div style="text-align: center; padding-top: 10vh; padding-bottom: 10vh;">
                <h1 style="font-size: 4rem; font-weight: 600; margin-bottom: 0;">Crane <span style="color: #0068c9;">AI</span></h1>
                <p style="font-size: 1.2rem; color: #888;">How can I help you analyze the catalog today?</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    # --- THE ACTIVE STATE ---
    if user_query:
        st.session_state.iteration_count += 1
        
        # Standard chat UI
       
        with st.chat_message("user"):
            # The anchor hack to push this message to the right
            st.markdown("<div class='user-anchor'></div>", unsafe_allow_html=True)
            st.write(user_query)
        with st.spinner("Crane is thinking..."):
            full_prompt = f"{SYSTEM_CONTEXT}\n\nUser Query: {user_query}"
            try:
                response = model.generate_content(full_prompt)
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(response.text)
            except ResourceExhausted:
                st.warning("⚠️ High traffic. Wait 15 seconds.")
            except Exception as e:
                st.error("System Error.")



open_interface()
st.write("---")

if st.button("✅ I found the two products!"):
    total_time = round(time.time() - st.session_state.start_time, 2)
    data = {"Participant_ID": int(time.time()), "Condition": "Open", "Total_Time_Seconds": total_time, "Prompt_Iterations": st.session_state.iteration_count}
    try:
        supabase.table("HCI").insert(data).execute()
        st.success("Data logged. Please proceed to the survey.")
        time.sleep(2)
        st.stop()
    except Exception as e:
        st.error(f"Error: {e}")
