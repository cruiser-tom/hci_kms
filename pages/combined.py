import streamlit as st
import time
from supabase import create_client
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="Crane AI | Omnimodal System", layout="centered")

# --- CUSTOM CSS FOR RIGHT-ALIGNED USER CHAT ---
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

if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'iteration_count' not in st.session_state:
    st.session_state.iteration_count = 0

# The typing simulator for the Persona aspect
def stream_typing(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.06)

# Adjusted prompt to include the "Alex" persona while keeping the strict table format
SYSTEM_CONTEXT = """
You are Alex, an advanced AI data coworker designed to analyze e-commerce product reviews.

CRITICAL FORMATTING RULES - YOU MUST OBEY THESE:
1. Your response MUST be split into two parts using "|||" as the delimiter.
2. Part 1 (Before |||) is your conversational answer. Keep it friendly and helpful.
3. Part 2 (After |||) is the data verification.
4. The data verification MUST start with a 3-column table: | Product Name | Total Reviews | Rating |
5. Below the table, you MUST list the AI Analysis as separate bullet points.

EXAMPLE OF THE EXACT REQUIRED FORMAT:
Hey there! I have analyzed the catalog and found the products you requested.
|||
### Raw Data Table
| Product Name | Total Reviews | Rating |
|---|---|---|
| Example Product | 1,000 | 4.0/5 |

### System Verification Analysis
* **Example Product:** WARNING. Suspicious activity detected.

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

def combined_interface():
    st.error("🛡️ Omnimodal System: Persona, Process Transparency, and Data Verification Active.")
    user_query = st.chat_input("Message Alex...")
    
    # --- THE "EMPTY STATE" ---
    if not user_query and st.session_state.iteration_count == 0:
        st.markdown(
            """
            <div style="text-align: center; padding-top: 8vh; padding-bottom: 4vh;">
                <h1 style="font-size: 4rem; font-weight: 600; margin-bottom: 0;">Alex</h1>
                <p style="font-size: 1.2rem; color: #888;">Your Verified Data Coworker 👋</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        
        st.caption("Ask Alex:")
        col1, col2 = st.columns(2)
        if col1.button("Hey Alex, can you check for fake reviews?"):
            user_query = "Hey Alex, can you check for fake reviews?"
        if col2.button("Which products have suspicious bot activity?"):
            user_query = "Which products have suspicious bot activity?"

    # --- THE ACTIVE STATE ---
    if user_query:
        st.session_state.iteration_count += 1
        
        with st.chat_message("user"):
            st.markdown("<div class='user-anchor'></div>", unsafe_allow_html=True)
            st.write(user_query)
            
        # Feature 1: The Explainable Progress Bar
        with st.status("Alex is analyzing the dataset...", expanded=True) as status:
            progress_bar = st.progress(0)
            st.write("🔍 Extracting product metadata...")
            progress_bar.progress(30)
            time.sleep(0.6) 
            st.write("📊 Running linguistic anomaly detection models...")
            progress_bar.progress(70)
            time.sleep(0.7)
            st.write("✅ Compiling final trust and safety report...")
            progress_bar.progress(100)
            status.update(label="Analysis Complete", state="complete", expanded=False)
            
        # Feature 2: The Persona Typing Effect + Feature 3: Cited Data Split
        with st.chat_message("assistant", avatar="🧑‍💻"):
            message_placeholder = st.empty()
            message_placeholder.markdown("*(Alex is typing...)*")
            time.sleep(1.0) 
            
            full_prompt = f"{SYSTEM_CONTEXT}\n\nUser Query: {user_query}"
            try:
                response = model.generate_content(full_prompt)
                message_placeholder.empty() 
                
                if "|||" in response.text:
                    chat_text, raw_data = response.text.split("|||", 1)
                    
                    # Stream the friendly text like a human
                    st.write_stream(stream_typing(chat_text.strip()))
                    
                    # Pop open the official data table below it
                    with st.expander("📊 View System Data Verification", expanded=True):
                        st.caption("Raw extract from Nexus Product Database:")
                        st.markdown(raw_data.strip())
                else:
                    st.write_stream(stream_typing(response.text))
                    
            except ResourceExhausted:
                st.warning("⚠️ Alex is helping someone else right now. Please wait 15 seconds.")
            except Exception as e:
                st.error("System Error.")

combined_interface()
st.write("---")

if st.button("✅ I found the two products!"):
    total_time = round(time.time() - st.session_state.start_time, 2)
    st.session_state.participant_id = int(time.time()) 
    
    data = {
        "Participant_ID": st.session_state.participant_id, 
        "Condition": "Combined", 
        "Total_Time_Seconds": total_time, 
        "Prompt_Iterations": st.session_state.iteration_count
    }
    
    try:
        supabase.table("HCI").insert(data).execute()
        st.success("Data logged. Redirecting to final survey...")
        time.sleep(1.5)
        st.switch_page("pages/survey.py") 
    except Exception as e:
        st.error(f"Error: {e}")