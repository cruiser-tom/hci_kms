import streamlit as st
import time
from supabase import create_client
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="Crane AI | Assistant", layout="centered")

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


# Notice the instruction to act like a friendly human
SYSTEM_CONTEXT = """
You are 'Martha', a highly enthusiastic, empathetic human data analyst working for Nexus. 
You use emojis, warm greetings, and first-person pronouns ("I", "my"). 
You are eager to help your coworker (the user) find fake reviews. 

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

def persona_interface():
    user_query = st.chat_input("Message Martha...")
    
    # --- THE "EMPTY STATE" ---
    if not user_query and st.session_state.iteration_count == 0:
        st.markdown(
            """
            <div style="text-align: center; padding-top: 10vh; padding-bottom: 6vh;">
                <h1 style="font-size: 4rem; font-weight: 600; margin-bottom: 0;">Martha</h1>
                <p style="font-size: 1.2rem; color: #888;">Hi, Iam your Data Team Coworker 👋</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        # --- SUGGESTED QUERIES (Conversational Tone) ---
        st.caption("Ask Martha:")
        col1, col2 = st.columns(2)
        clicked_suggestion_1 = col1.button("Hey Martha, can you check for fake reviews?")
        clicked_suggestion_2 = col2.button("Which products have suspicious bot activity?")
        
        # Override user_query if a button is clicked
        if clicked_suggestion_1:
            user_query = "Hey Martha, can you check for fake reviews?"
        elif clicked_suggestion_2:
            user_query = "Which products have suspicious bot activity?"

    # --- THE ACTIVE STATE ---
    if user_query:
        st.session_state.iteration_count += 1
        
        with st.chat_message("user"):
            # The anchor hack to push this message to the right
            st.markdown("<div class='user-anchor'></div>", unsafe_allow_html=True)
            st.write(user_query)
            
        with st.spinner("Martha is typing..."):
            full_prompt = f"{SYSTEM_CONTEXT}\n\nUser Query: {user_query}"
            try:
                response = model.generate_content(full_prompt)
                with st.chat_message("assistant", avatar="🧑‍💻"):
                    st.write(response.text)
            except ResourceExhausted:
                st.warning("⚠️ Martha is helping someone else right now. Please wait 15 seconds.")
            except Exception as e:
                st.error("System Error.")
                
                
                

persona_interface()
st.write("---")

if st.button("✅ I found the two products!"):
    total_time = round(time.time() - st.session_state.start_time, 2)
    data = {"Participant_ID": int(time.time()), "Condition": "Persona", "Total_Time_Seconds": total_time, "Prompt_Iterations": st.session_state.iteration_count}
    try:
        supabase.table("HCI").insert(data).execute()
        st.success("Awesome job! Data logged. Please proceed to the survey.")
        time.sleep(2)
        st.stop()
    except Exception as e:
        st.error(f"Error: {e}")
