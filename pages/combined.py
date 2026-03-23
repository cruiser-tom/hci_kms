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
#     st.session_state.experiment_group = "Combined"

# --- STRICT SECURITY CHECK (Uncomment this when the study goes live!) ---
if 'participant_id' not in st.session_state or 'experiment_group' not in st.session_state:
    st.warning("⚠️ No active session found. Please start from the main page.")
    st.stop()

# --- CUSTOM CSS ---
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
    /* NOTE: We are NOT hiding the avatar here, so Martha's icon can shine! */
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
if 'messages' not in st.session_state:
    st.session_state.messages = []

def stream_typing(text):
    for word in text.split(" "):
        yield word + " "
        time.sleep(0.04)

SYSTEM_CONTEXT = """
You are Martha, an advanced AI data coworker designed to analyze e-commerce product reviews.

CRITICAL FORMATTING RULES - YOU MUST OBEY THESE:
1. IF the user asks to analyze products, check reviews, or find bot activity: Your response MUST be split into two parts using "|||" as the delimiter.
   - Part 1 (Before |||) is your friendly conversational answer.
   - Part 2 (After |||) MUST be a 3-column table: | Product Name | Total Reviews | Rating | 
   - Part 3 is your AI analysis in bullet points.
2. IF the user is just greeting you (e.g., "Hi", "Thanks", "How are you?"): DO NOT use the "|||" delimiter or the table. Just reply conversationally and naturally as Martha.

EXAMPLE OF THE EXACT REQUIRED FORMAT FOR DATA QUERIES:
Hey there! I have analysed and found the products you requested.
|||
### Data Table
| Product Name | Total Reviews | Rating |
|---|---|---|
| Example Product | 1,000 | 4.0/5 |

### AI Analysis
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
    # --- DISPLAY PAST CHAT HISTORY ---
    for message in st.session_state.messages:
        if message["role"] == "user":
            # 1. Pure HTML for User (Right-aligned, no avatar, clean bubble)
            st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
                    <div style="background-color: #2b2b2b; color: #ffffff; padding: 12px 18px; border-radius: 20px 20px 5px 20px; max-width: 80%; width: fit-content; line-height: 1.5;">
                        {message["content"]}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # 2. Martha's Avatar for AI (Includes logic to correctly split the ||| data on reload)
            with st.chat_message("assistant", avatar="🧑‍💻"):
                if "|||" in message["content"]:
                    chat_text, raw_data = message["content"].split("|||", 1)
                    st.markdown(chat_text.strip())
                    with st.expander("📊 View System Data Verification", expanded=False):
                        st.caption("Raw extract from Crane AI Database:")
                        st.markdown(raw_data.strip())
                else:
                    st.markdown(message["content"])

    user_query = st.chat_input("Message Martha...")
    
    # --- THE "EMPTY STATE" ---
    empty_placeholder = st.empty()
    
    if not user_query and len(st.session_state.messages) == 0:
        with empty_placeholder.container():
            st.markdown(
                """
                <div style="text-align: center; padding-top: 10vh; padding-bottom: 6vh;">
                    <h1 style="font-size: 4rem; font-weight: 600; margin-bottom: 0;">Crane <span style="color: #0068c9;">AI</span></h1>
                    <p style="font-size: 1.2rem; color: #888;">Hi! I am Martha, your Verified Data Coworker 👋</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.caption("Ask Martha:")
            col1, col2 = st.columns(2)
            
            # Anti-glitch shortcut buttons
            clicked_1 = col1.button("Hey Martha, can you check for fake reviews?", use_container_width=True)
            clicked_2 = col2.button("Which products have suspicious bot activity?", use_container_width=True)
            
        if clicked_1:
            user_query = "Hey Martha, can you check for fake reviews?"
            empty_placeholder.empty()
        elif clicked_2:
            user_query = "Which products have suspicious bot activity?"
            empty_placeholder.empty()

    # --- THE ACTIVE STATE ---
    if user_query:
        st.session_state.iteration_count += 1
        
        # 1. Show User message instantly
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
                <div style="background-color: #2b2b2b; color: #ffffff; padding: 12px 18px; border-radius: 20px 20px 5px 20px; max-width: 80%; width: fit-content; line-height: 1.5;">
                    {user_query}
                </div>
            </div>
        """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "user", "content": user_query})
        
        words_in_query = user_query.lower().split()
        task_prefixes = ["prod", "review", "bot", "fake", "susp", "scan", "analy", "data", "list", "activ"]
        is_task_query = any(word.startswith(prefix) for word in words_in_query for prefix in task_prefixes)
        
        # 2. Explainable Progress Bar
        if is_task_query:
            with st.status("Martha is analyzing the dataset...", expanded=True) as status:
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
            st.container()
                
        # 3. Martha's Generation State
        with st.chat_message("assistant", avatar="🧑‍💻"):
            message_placeholder = st.empty()
            message_placeholder.markdown("*(Martha is typing...)*")
            
            chat_history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages])
            full_prompt = f"{SYSTEM_CONTEXT}\n\nChat History:\n{chat_history_text}\n\nUser Query: {user_query}"
            
            try:
                response = model.generate_content(full_prompt)
                message_placeholder.empty() 
                
                # Split and stream the Verified Expander logic
                if "|||" in response.text:
                    chat_text, raw_data = response.text.split("|||", 1)
                    st.write_stream(stream_typing(chat_text.strip()))
                    
                    with st.expander("📊 View System Data Verification", expanded=True):
                        st.caption("Raw extract from Crane AI Database:")
                        st.markdown(raw_data.strip())
                        
                else:
                    st.write_stream(stream_typing(response.text))
                    
                # Store EXACT response to history to ensure the expander box persists on reload
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                    
            except ResourceExhausted:
                st.warning("⚠️ Martha is helping someone else right now. Please wait 15 seconds.")
            except Exception as e:
                st.error("System Error.")

combined_interface()

# --- BOTTOM FINISH BUTTON ---
st.write("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    finish_placeholder = st.empty()
    
    if finish_placeholder.button("✅ I found the two products!", type="primary", use_container_width=True):
        finish_placeholder.empty() 
        
        with st.container():
            st.info("Redirecting to final survey...")
            
            total_time = round(time.time() - st.session_state.start_time, 2)
            part_id = st.session_state.get("participant_id", int(time.time()))
            group = st.session_state.get("experiment_group", "Combined") 
            
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
