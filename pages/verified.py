import streamlit as st
import time
from supabase import create_client
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="Crane AI", layout="centered", initial_sidebar_state="collapsed")



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
    /* Hide Streamlit's default avatars for the AI messages */
    [data-testid="stChatMessageAvatar"] {
        display: none !important;
    }
    [data-testid="stChatMessage"] {
        gap: 0 !important;
        background-color: transparent !important;
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

# ---> PASTE YOUR VERIFIED/CITED SYSTEM PROMPT HERE <---
SYSTEM_CONTEXT = """
You are an advanced AI designed to analyze e-commerce product reviews.

CRITICAL FORMATTING RULES - YOU MUST OBEY THESE:
1. IF the user asks to analyze products, check reviews, or find bot activity: Your response MUST be split into two parts using "|||" as the delimiter.
   - Part 1 (Before |||) is your friendly conversational answer.
   - Part 2 (After |||) MUST be a 3-column table: | Product Name | Total Reviews | Rating | 
   - Part 3 is your AI analysis in bullet points.
2. IF the user is just greeting you (e.g., "Hi", "Thanks", "How are you?"): DO NOT use the "|||" delimiter or the table. Just reply conversationally and naturally.


EXAMPLE OF THE EXACT REQUIRED FORMAT:
I have analyzed the catalog and found the products you requested.
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

def cited_interface():
    
    
    # --- DISPLAY PAST CHAT HISTORY ---
    for message in st.session_state.messages:
        if message["role"] == "user":
            # Pure HTML User Bubble (Forces perfect right-alignment and shape)
            st.markdown(f"""
                <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
                    <div style="background-color: #2b2b2b; color: #ffffff; padding: 12px 18px; border-radius: 20px 20px 5px 20px; max-width: 80%; width: fit-content; line-height: 1.5;">
                        {message["content"]}
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            # NO st.chat_message! Pure rendering.
            if "|||" in message["content"]:
                chat_text, raw_data = message["content"].split("|||", 1)
                st.markdown(chat_text.strip())
                with st.expander("📊 View System Data Verification", expanded=False):
                    st.caption("Raw extract from Crane AI Database:")
                    st.markdown(raw_data.strip())
            else:
                st.markdown(message["content"])
            st.markdown("<br>", unsafe_allow_html=True)

    # --- THE SINGLE CHAT INPUT (No duplicates!) ---
    user_query = st.chat_input("Message Crane...")
    
 # --- THE "EMPTY STATE" ---
    empty_placeholder = st.empty()
    
    if not user_query and len(st.session_state.messages) == 0:
        with empty_placeholder.container():
            # Using standard strings to prevent the grey code-block glitch!
            st.markdown(
                "<div style='text-align: center; padding-top: 8vh; padding-bottom: 4vh;'>"
                "<h1 style='font-size: 4rem; font-weight: 600; margin-bottom: 15px;'>Crane <span style='color: #0068c9;'>AI</span></h1>"
                "<div style='display: inline-block; background-color: rgba(255, 75, 75, 0.1); border: 1px solid rgba(255, 75, 75, 0.3); color: #ff4b4b; padding: 8px 18px; border-radius: 50px; font-size: 0.95rem; font-weight: 500;'>"
                "🛡️ Data Verified System: All AI outputs are cross-referenced."
                "</div>"
                "</div>", 
                unsafe_allow_html=True
            )
            
            st.caption("Suggested quick queries:")
            col1, col2 = st.columns(2)
            
            clicked_1 = col1.button("Can you check for fake reviews?", use_container_width=True)
            clicked_2 = col2.button("Which products have suspicious bot activity?", use_container_width=True)
            
        if clicked_1:
            user_query = "Can you check for fake reviews?"
            empty_placeholder.empty()
            
        elif clicked_2:
            user_query = "Which products have suspicious bot activity?"
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
            
        # 2. Spinner & AI Call
        words_in_query = user_query.lower().split()
        task_prefixes = ["prod", "review", "bot", "fake", "susp", "scan", "analy", "data", "list", "activ"]
        is_task_query = any(word.startswith(prefix) for word in words_in_query for prefix in task_prefixes)
        
        if is_task_query:
            spinner_context = st.spinner("Checking verified sources...")
        else:
            spinner_context = st.container() 
            
        with spinner_context:
            chat_history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages])
            full_prompt = f"{SYSTEM_CONTEXT}\n\nChat History:\n{chat_history_text}\n\nUser Query: {user_query}"
            
            try:
                response = model.generate_content(full_prompt)
                
                # 3. NO st.chat_message! Render text and expander natively.
                if "|||" in response.text:
                    chat_text, raw_data = response.text.split("|||", 1)
                    st.markdown(chat_text.strip())
                    
                    with st.expander("📊 View System Data Verification", expanded=True):
                        st.caption("Raw extract from Crane AI Database:")
                        st.markdown(raw_data.strip())
                else:
                    st.markdown(response.text)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # Save the EXACT raw response to memory so the history loop can re-split it later
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                        
            except ResourceExhausted:
                st.warning("⚠️ High traffic. Please wait 15 seconds.")
            except Exception as e:
                st.error("System Error.")

cited_interface()

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
            
            group = st.session_state.get("experiment_group", "Verified") 
            
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
