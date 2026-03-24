import streamlit as st
import time
from supabase import create_client
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="Crane AI", layout="centered", initial_sidebar_state="collapsed")

st.markdown(
    """
    <style>
    /* 1. Hide default Streamlit elements */
    #MainMenu, footer, header {visibility: hidden !important;}

    /* 2. Lock the main width and center it */
    .block-container {
        max-width: 700px !important; 
        padding-top: 1rem !important;
        padding-bottom: 1rem !important; 
    }

    /* 3. THE AVATAR HIDER - THIS REMOVES THE ROBOT ICON */
    [data-testid="stChatMessageAvatar"] {
        display: none !important;
    }
    
    /* 4. REMOVE THE GAP - THIS PUSHES THE TEXT FLUSH LEFT */
    [data-testid="stChatMessage"] {
        padding-left: 0 !important;
        margin-left: 0 !important;
        background-color: transparent !important;
        gap: 0 !important;
    }
    
    [data-testid="stChatMessageContent"] {
        margin-left: 0 !important;
        padding-left: 0 !important;
    }

    /* 5. Fix the User Bubble (so it doesn't look like a tiny pill) */
    .user-bubble {
        background-color: #2b2b2b; 
        color: #ffffff; 
        padding: 12px 20px; 
        border-radius: 20px 20px 5px 20px; 
        max-width: 75%; 
        width: fit-content; 
        line-height: 1.5;
    }
    </style>
    """,
    unsafe_allow_html=True
)



genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash-lite')

def generate_with_retry(prompt, max_retries=3):
    retries = 0
    backoff_time = 2  
    while retries < max_retries:
        try:
            response = model.generate_content(prompt)
            return response.text
        except ResourceExhausted:
            time.sleep(backoff_time)
            retries += 1
            backoff_time *= 2  
    return "The system is currently processing a high volume of requests. Please wait a few seconds and try your prompt again."

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
You are Crane AI, a strict data retrieval and verification system. 
Your sole purpose is to retrieve verifiable data and present it factually. 
Do not offer opinions, do not explain your reasoning, and do not act conversational.

CRITICAL INSTRUCTION FOR MATCHING QUERIES:
If a user asks for "fake", "bot", "suspicious", or "fraudulent", (or any synonyms) products, you MUST return the products labeled with "WARNING", "CRITICAL WARNING", or "Suspicious" in the dataset. Do not say there are no products.

CRITICAL FORMATTING RULES - YOU MUST OBEY THESE:
1. IF the user asks to analyze products, check reviews, or find bot activity: Your response MUST be split into three parts using "|||" as the delimiter.
   - Part 1 (Before the first |||) [A one-sentence factual introduction]
   - Part 2 (After the first |||) [A Markdown table containing the raw data] | Product Name | Total Reviews | Rating | 
   - Part 3 (After the second |||) [A strict, factual summary of what the data shows, with no extra analysis]
2. IF the user is just greeting you (e.g., "Hi", "Thanks", "How are you?"): DO NOT use the "|||" delimiter or the table. Just reply conversationally and naturally.

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
            st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
                <div style="background-color: rgba(150, 150, 150, 0.2); color: var(--text-color); padding: 12px 18px; border-radius: 20px 20px 5px 20px; max-width: 80%; width: fit-content; line-height: 1.5;">
                    {message["content"]}
                </div>
            </div>
        """, unsafe_allow_html=True)
            
        else:
            # Pure text rendering for history, with the separator
            st.markdown(message["content"])

    # --- THE SINGLE CHAT INPUT (No duplicates!) ---
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
                </div>
              
                <div style=" background-color: rgba(150, 150, 150, 0.2); color: #ff7676; padding: 8px 24px; border-radius: 40px; 
                    border: 1px solid #632a2a; margin: 0 auto 30px auto; display: flex; align-items: center; justify-content: center;
                    gap: 8px; text-align: center; width: fit-content; box-shadow: 0 4px 12px rgba(0,0,0,0.2); ">
                    <span style="font-size: 1.3rem;">🛡️</span>
                    <span style="font-weight: 500; font-size: 1rem; letter-spacing: 0.3px;">
                    Data Verified System: All AI outputs are cross-referenced with internal databases.
                    </span>
                </div>
                """, 
                unsafe_allow_html=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            st.caption("Suggested quick queries:")
            col1, col2 = st.columns(2)
            
            if col1.button("Can you check for fake reviews?", use_container_width=True):
                user_query = "Can you check for fake reviews?"
                empty_placeholder.empty()
                
            if col2.button("Which products have suspicious bot activity?", use_container_width=True):
                user_query = "Which products have suspicious bot activity?"
                empty_placeholder.empty() 
                
    
  

    # --- THE ACTIVE STATE ---
    if user_query:
        st.session_state.iteration_count += 1
        
        # 1. Show the user message instantly via HTML
        st.markdown(f"""
            <div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
                <div style="background-color: rgba(150, 150, 150, 0.2); color: var(--text-color); padding: 12px 18px; border-radius: 20px 20px 5px 20px; max-width: 80%; width: fit-content; line-height: 1.5;">
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
                # 1. USE THE NEW RETRY FUNCTION
                response_text = generate_with_retry(full_prompt)
                
                if "|||" in response_text:
                    parts = response_text.split("|||")
                        
                    # THE NEW 3-PART SPLIT (Intro, Table, Analysis)
                    if len(parts) >= 3:
                        intro_text = parts[0].strip()
                        raw_table = parts[1].strip()
                        analysis_text = parts[2].strip()
                            
                        # Intro outside
                        st.markdown(intro_text)
                            
                        # Table strictly inside (defaulted to closed for a cleaner look)
                        with st.expander("📊 View System Data Verification", expanded=False):
                            st.caption("Raw extract from Crane AI Database:")
                            st.markdown(raw_table)
                        st.markdown("<small style='color: #d13438; background-color: rgba(209, 52, 56, 0.15); padding: 3px 10px; border-radius: 12px; font-weight: 600;'>🛡️ VERIFIED DATA</small><br><br>", unsafe_allow_html=True)
                            
                        # Analysis outside
                        st.markdown(analysis_text)
                            
                        # Save clean version to history
                        clean_history = f"{intro_text}\n\n**Raw Data Verification:**\n{raw_table}\n\n{analysis_text}"
                        st.session_state.messages.append({"role": "assistant", "content": clean_history})
                            
                    # THE FALLBACK (In case the AI only uses 1 delimiter)
                    elif len(parts) == 2:
                        chat_text, raw_data = parts
                        st.markdown(chat_text.strip())
                            
                        with st.expander("📊 View System Data Verification", expanded=True):
                            st.caption("Raw extract from Crane AI Database:")
                            st.markdown(raw_data.strip())
                        st.markdown("<small style='color: #d13438; background-color: rgba(209, 52, 56, 0.15); padding: 3px 10px; border-radius: 12px; font-weight: 600;'>🛡️ VERIFIED DATA</small><br><br>", unsafe_allow_html=True)
                            
                        st.session_state.messages.append({"role": "assistant", "content": chat_text.strip() + "\n\n**Raw Data Verification:**\n" + raw_data.strip()})
                            
                # IF NO DELIMITERS ARE USED (Standard chat)
                else:
                    st.write(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                        
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
