import streamlit as st
import time
from supabase import create_client
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="Crane AI", layout="centered")
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

if 'start_time' not in st.session_state:
    st.session_state.start_time = time.time()
if 'iteration_count' not in st.session_state:
    st.session_state.iteration_count = 0

if 'messages' not in st.session_state:
    st.session_state.messages = []


# Updated Instruction: Using a strict template to force the formatting
SYSTEM_CONTEXT = """
You are an advanced AI designed to analyze e-commerce product reviews.

CRITICAL FORMATTING RULES - YOU MUST OBEY THESE:
1. IF the user asks to analyze products, check reviews, or find bot activity: Your response MUST be split into two parts using "|||" as the delimiter.
   - Part 1 (Before |||) is your friendly conversational answer.
   - Part 2 (After |||) MUST be a 3-column table: | Product Name | Total Reviews | Rating | 
   - Part 3 is your AI analysis in bullet points.
2. IF the user is just greeting you (e.g., "Hi", "Thanks", "How are you?"): DO NOT use the "|||" delimiter or the table. Just reply conversationally and naturally as Martha.


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
    st.error("🛡️ Data Verified System: All AI outputs are cross-referenced.")
    user_query = st.chat_input("Message Crane...")
    
    # --- THE "EMPTY STATE" ---
    
    # --- THE "EMPTY STATE" ---
    if not user_query and st.session_state.iteration_count == 0:
        st.markdown(
            """
            <div style="text-align: center; padding-top: 6vh; padding-bottom: 10vh;">
                <h1 style="font-size: 4rem; font-weight: 600; margin-bottom: 0;">Crane <span style="color: #0068c9;">AI</span></h1>
                <p style="font-size: 1.2rem; color: #888;">Data-Verified Analysis System</p>
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
            


# --- DISPLAY PAST CHAT HISTORY ---
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown("<div class='user-anchor'></div>", unsafe_allow_html=True)
            st.markdown(message["content"])

    # --- THE ACTIVE STATE ---
    if user_query:
        st.session_state.iteration_count += 1
        
        # 1. Show and save user message
        with st.chat_message("user"):
            st.markdown("<div class='user-anchor'></div>", unsafe_allow_html=True)
            st.write(user_query)
        st.session_state.messages.append({"role": "user", "content": user_query})
            
        # 2. Prefix Filter for the Spinner
        words_in_query = user_query.lower().split()
        task_prefixes = ["prod", "review", "bot", "fake", "susp", "scan", "analy", "data", "list", "activ"]
        is_task_query = any(word.startswith(prefix) for word in words_in_query for prefix in task_prefixes)
        
        # 3. Generate Response
        # We only show the "Extracting..." spinner for actual tasks
        if is_task_query:
            spinner_context = st.spinner("Extracting verifiable data...")
        else:
            # A completely invisible block if it is just a greeting
            spinner_context = st.container() 
            
        with spinner_context:
            chat_history_text = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in st.session_state.messages])
            full_prompt = f"{SYSTEM_CONTEXT}\n\nChat History:\n{chat_history_text}\n\nUser Query: {user_query}"
            
            try:
                response = model.generate_content(full_prompt)
                
                with st.chat_message("assistant", avatar="🧑‍💻"):
                    if "|||" in response.text:
                        chat_text, raw_data = response.text.split("|||", 1)
                        st.write(chat_text.strip())
                        
                        with st.expander("📊 View System Data Verification", expanded=True):
                            st.caption("Raw extract from Crane AI Database:")
                            st.markdown(raw_data.strip())
                            
                        # Save the split response to memory
                        st.session_state.messages.append({"role": "assistant", "content": chat_text.strip() + "\n\n**Raw Data Verification:**\n" + raw_data.strip()})
                    else:
                        st.write(response.text)
                        # Save normal response to memory
                        st.session_state.messages.append({"role": "assistant", "content": response.text})
                        
            except ResourceExhausted:
                st.warning("⚠️ High traffic. Please wait 15 seconds.")
            except Exception as e:
                st.error("System Error.")
                

     

cited_interface()
st.write("---")

if st.button("✅ I found the two products!"):
    total_time = round(time.time() - st.session_state.start_time, 2)
    data = {"Participant_ID": int(time.time()), "Condition": "Verified", "Total_Time_Seconds": total_time, "Prompt_Iterations": st.session_state.iteration_count}
    try:
        supabase.table("HCI").insert(data).execute()
        st.success("Data logged. Redirecting to final survey...")
        time.sleep(0.5)
        st.switch_page("pages/survey.py") 
    except Exception as e:
        st.error(f"Error: {e}")
        
