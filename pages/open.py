import streamlit as st
import time
from supabase import create_client, Client
import google.generativeai as genai

# --- Initialize Gemini ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

def set_branding():
    st.set_page_config(page_title="Enterprise KMS v2.4", layout="wide")
    
    # Custom CSS for a clean, "Enterprise" feel
    st.markdown("""
        <style>
            .main { background-color: #f8f9fa; }
            .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #007bff; color: white; }
            .stChatInputContainer { padding-bottom: 20px; }
            header { visibility: hidden; } /* Hides the 'Made with Streamlit' footer */
        </style>
    """, unsafe_content_html=True)

    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/2800/2800168.png", width=80) # A generic "Data" icon
    with col2:
        st.title("Nexus Corporate Intelligence")
        st.caption("Internal Knowledge Management System | Authorized Access Only")
        
        
@st.cache_resource
def init_connection():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

supabase = init_connection()

# Safety Check: If a student tries to go directly to this URL without app.py
if st.session_state.start_time is None:
    st.session_state.start_time = time.time()
    
    

# The "Database" the AI will use to answer questions
SYSTEM_CONTEXT = """
You are an internal corporate Knowledge Management System for a global e-commerce platform. 
Only answer based on this exact provided data. Do not invent or hallucinate information. 
Format outputs exactly as the user requests (e.g., short summary, bullet points, raw data table).

--- CORPORATE KNOWLEDGE BASE: 2025 FISCAL YEAR ---

# Q1 (January - March)
- IT: Successfully migrated the main database to AWS. 15% site speed increase. Minor February outage cost $45k. IT budget spend: $500k.
- HR: Implemented new digital literacy training for support staff. Employee turnover: 2%.
- Finance: Q1 Total Revenue: $2.1 Million. Operating Costs: $1.2M. Profit margins stable.
- Analytics: Platform trust high; 98% of product reviews verified as authentic. Detected early signs of bot traffic. Churn rate: 2.1%.

# Q2 (April - June)
- IT: Deployed automated bot-defense mechanisms after heavy April cyber attacks. IT budget spend: $650k (over budget due to crisis).
- HR: Hired 25 temporary trust & safety contractors to manually purge fake reviews. Employee turnover: 5% (high stress quarter).
- Finance: Q2 Total Revenue: $1.9 Million (significant drop due to fake review scandal). Operating Costs: $1.5M.
- Analytics: Authentic review rate dropped to 82%. Customer Support tickets escalated by 300%. Churn rate peaked at 3.8%.

# Q3 (July - September)
- IT: Maintained 99.9% server uptime. Integrated new GenAI API for customer recommendations. IT budget spend: $400k.
- HR: Transitioned temporary contractors to full-time roles. Hosted mental health awareness week. Turnover: 1.5%.
- Finance: Q3 Total Revenue: $2.6 Million. Operating Costs: $1.1M. Profit margins highest of the year.
- Analytics: GenAI recommendation engine drove 22% increase in average order value. Churn rate dropped to 1.9%. New AI moderation caught 99.5% of spam.

# Q4 (October - December)
- IT: 100% server uptime during Black Friday. Scaled cloud infrastructure. IT budget spend: $700k.
- HR: Disbursed end-of-year bonuses. Conducted annual compliance training. Turnover: 1.0%.
- Finance: Q4 Total Revenue: $3.4 Million (record breaking). Logistics costs heavily reduced by new vendor. Operating Costs: $1.8M.
- Analytics: Customer trust scores at peak levels. Fewer than 500 fake reviews reported all quarter. Churn rate: 1.5%.

# Year-to-Date (YTD) Summary
- IT: Total budget spent: $2.25M. System architecture fully modernized.
- HR: Total headcount grew by 15% across the year.
- Finance: Total Annual Revenue: $10.0 Million. Total Costs: $5.6M.
- Analytics: Platform trust completely recovered from Q2 crisis; overall yearly churn averaged 2.3%.

If a user asks for data outside of this context, politely inform them that the data is not available in the current Knowledge Base.
"""

from google.api_core.exceptions import ResourceExhausted

def open_interface():
    st.subheader("Knowledge Management System")
    st.write("Ask the system a question to find the information you need.")
    
    user_query = st.chat_input("Enter your query here...")
    
    if user_query:
        st.session_state.iteration_count += 1
        st.write(f"**You asked:** {user_query}")
        
  
        with st.spinner("Querying Secure Database..."):

  
        
            full_prompt = f"{SYSTEM_CONTEXT}\n\nUser Query: {user_query}"
            try:
                response = model.generate_content(full_prompt)
                st.info(response.text)
            except ResourceExhausted:
                st.warning("⚠️ System is experiencing high traffic. Please wait 15 seconds and try again.")
            except Exception as e:
                st.error("An unexpected system error occurred. Please try again.")
                 
                  with st.chat_message("assistant", avatar="🤖"):
        st.markdown(f"### System Result:\n{response.text}")
        st.caption(f"Confidence Score: 98.4% | Data Source: Fiscal_2025_Archive")
        

with st.sidebar:
    st.header("📋 Your Assigned Task")
    st.info("""
    **Objective:** Identify the main cause of the Q2 revenue drop and find which department managed to stay under budget.
    
    **Instructions:**
    1. Use the interface to query the database.
    2. Once you have both answers, click the button at the bottom.
    """)
    
    # Progress bar to show how many steps they've taken
    st.write("---")
    st.write(f"Search Iterations: {st.session_state.iteration_count}")
    progress = min(st.session_state.iteration_count * 20, 100) # Progresses every click
    st.progress(progress)
    
open_interface()



if st.button("I found the answer!"):
    st.session_state.task_complete = True
    end_time = time.time()
    total_time = round(end_time - st.session_state.start_time, 2)
    
    data_to_insert = {
        "Participant_ID": int(time.time()), 
        "Condition": st.session_state.experiment_group,
        "Total_Time_Seconds": total_time,
        "Prompt_Iterations": st.session_state.iteration_count
    }
    
    try:
        response = supabase.table("HCI").insert(data_to_insert).execute()
        st.success(f"Task complete! Time: {total_time}s | Iterations: {st.session_state.iteration_count}")
        st.write("Data securely logged. Please proceed to the post-task survey.")
        st.balloons()
    	st.toast("Data securely logged to the research server!", icon='💾')
    
    	# Lock the interface so they can't change their answer
   		st.success("Thank you! Your response has been recorded. You may now close this tab.")
   		st.stop() # Stops the script so they can't keep clicking
    	except Exception as e:
        st.error(f"An error occurred while saving data: {e}")
