import streamlit as st
import time
from supabase import create_client
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="Crane AI | Cited Data", layout="centered")
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



# Updated Instruction: Using a strict template to force the formatting
SYSTEM_CONTEXT = """
You are an advanced AI designed to analyze e-commerce product reviews.

CRITICAL FORMATTING RULES - YOU MUST OBEY THESE:
1. Your response MUST be split into two parts using "|||" as the delimiter.
2. Part 1 (Before |||) is your conversational answer.
3. Part 2 (After |||) is the data verification.
4. The data verification MUST start with a 3-column table: | Product Name | Total Reviews | Rating |
6. Below the table, you MUST list the AI Analysis that you should do about the reviews that you analyse as separate bullet points.

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
    if not user_query and st.session_state.iteration_count == 0:
        st.markdown(
            """
            <div style="text-align: center; padding-top: 6vh; padding-bottom: 10vh;">
                <h1 style="font-size: 4rem; font-weight: 600; margin-bottom: 0;">Crane<span style="color: #0068c9;">AI</span></h1>
                <p style="font-size: 1.2rem; color: #888;">Data-Verified Analysis System</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

    # --- THE ACTIVE STATE -#
    if user_query:
        st.session_state.iteration_count += 1
        with st.chat_message("user"):
            # You must add this anchor so the CSS knows what to push to the right!
            st.markdown("<div class='user-anchor'></div>", unsafe_allow_html=True)
            st.write(user_query)
            
        with st.spinner("Extracting verifiable data..."):
            full_prompt = f"{SYSTEM_CONTEXT}\n\nUser Query: {user_query}"
            try:
                response = model.generate_content(full_prompt)
                
                with st.chat_message("assistant", avatar="🤖"):
                    if "|||" in response.text:
                        chat_text, raw_data = response.text.split("|||", 1)
                        st.write(chat_text.strip())
                        
                        with st.expander("📊 View System Data Verification", expanded=True):
                            st.caption("Raw extract from Nexus Product Database:")
                            st.markdown(raw_data.strip())
                    else:
                        st.write(response.text)
                        
            except ResourceExhausted:
                st.warning("⚠️ High traffic. Wait 15 seconds.")
            except Exception as e:
                st.error("System Error.")



cited_interface()
st.write("---")

if st.button("✅ I found the two products!"):
    total_time = round(time.time() - st.session_state.start_time, 2)
    data = {"Participant_ID": int(time.time()), "Condition": "Cited", "Total_Time_Seconds": total_time, "Prompt_Iterations": st.session_state.iteration_count}
    try:
        supabase.table("HCI").insert(data).execute()
        st.success("Data logged. Please proceed to the survey.")
        time.sleep(2)
        st.stop()
    except Exception as e:
        st.error(f"Error: {e}")
