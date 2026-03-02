import streamlit as st
import time
from supabase import create_client, Client
import google.generativeai as genai

# --- Initialize Gemini ---
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-2.5-flash')

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

def scaffolded_interface():
    st.subheader("Structured Knowledge Query")
    st.write("Use the parameters below to extract specific data.")
    
    with st.form("query_form"):
        col1, col2 = st.columns(2)
        with col1:
            department = st.selectbox("Target Department", ["Analytics", "HR", "Finance", "IT"])
            timeframe = st.selectbox("Timeframe", ["Q1", "Q2", "Q3", "Q4", "Year-to-Date"])
        with col2:
            format_type = st.radio("Output Format", ["Short Summary", "Bullet Points", "Raw Data Table"])
            
        specific_metric = st.text_input("Specific Metric or Keyword (e.g., 'Churn', 'Revenue')")
        submitted = st.form_submit_button("Run Query")
        
        if submitted:
            st.session_state.iteration_count += 1
            constructed_prompt = f"Dept: {department}, Time: {timeframe}, Metric: {specific_metric}, Format: {format_type}"
            st.write(f"**System is searching for:** {constructed_prompt}")
            
            with st.spinner("Searching database..."):
                full_prompt = f"{SYSTEM_CONTEXT}\n\nExtract this specific data and format it exactly as requested: {constructed_prompt}"
                try:
                    response = model.generate_content(full_prompt)
                    st.info(response.text)
                except ResourceExhausted as e:
                    st.warning("⚠️ System is experiencing high traffic. Please wait 15 seconds and try again.")
                    print(f"API ERROR: {e}") # This sends the real error to your Mac's terminal
                    
                    
                    
                    
scaffolded_interface()


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
    except Exception as e:
        st.error(f"An error occurred while saving data: {e}")
