import streamlit as st
import time
from supabase import create_client
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted

st.set_page_config(page_title="Nexus KMS | Cited Data", layout="centered")

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

# Notice the instruction to generate a data table
SYSTEM_CONTEXT = """
You are an advanced AI designed to analyze e-commerce product reviews.
You MUST cite specific numbers from the dataset in your text. 
AT THE END OF EVERY RESPONSE, YOU MUST PROVIDE A MARKDOWN TABLE summarizing the data of the products you mentioned.

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

st.title("Nexus Corporate Intelligence")
st.info("**📋 Research Task:** We suspect a coordinated bot attack. Find the TWO products with the highest confirmed probability of fake/bot-generated reviews.")
st.divider()

def cited_interface():
    st.subheader("Data-Verified System")
    st.error("🛡️ Strict Mode Enabled: All AI outputs are cross-referenced with raw database tables.")
    
    user_query = st.chat_input("Query the database...")
    
    if user_query:
        st.session_state.iteration_count += 1
        with st.chat_message("user"):
            st.write(user_query)
            
        with st.spinner("Extracting verifiable data..."):
            full_prompt = f"{SYSTEM_CONTEXT}\n\nUser Query: {user_query}"
            try:
                response = model.generate_content(full_prompt)
                with st.chat_message("assistant", avatar="📊"):
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