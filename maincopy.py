import streamlit as st
import requests
import json
import base64

# Set page config
st.set_page_config(
    page_title="Resume Assistant",
    page_icon="📄",
    layout="wide"
)

# Constants
BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "a251ca29-c516-4b2d-b0a8-dc39c2749687"
FLOW_ID = "3dc77fa4-aa61-4d35-942a-3f6cf9701a25"
APPLICATION_TOKEN = "AstraCS:ZHsnZmhaGgvUzDpdCJvKfyEt:21032a68e1a1f15903d7e08a4bf89962d805158dc3c5c162c7edbf46d694cace"

TWEAKS = {

  "File-iv48A": {},
  "ParseData-TDP68": {},
  "Agent-34U8G": {},
  "CombineText-hxI0A": {},
  "ChatInput-SDcLF": {},
  "ChatOutput-XJTHD": {}
}

# Function to run flow
def run_flow(message, file_content=None):
    """Run the Langflow flow with the provided message and optional file content"""
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{FLOW_ID}"
    
    # If we have file content, adjust tweaks to include the file
    current_tweaks = TWEAKS.copy()
    if file_content:
        # Update tweaks for file component
        current_tweaks["File-iv48A"] = {
            "file_path": "uploaded_resume.pdf",
            "file_content": file_content
        }
    
    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
        "tweaks": current_tweaks
    }
    
    headers = {
        "Authorization": f"Bearer {APPLICATION_TOKEN}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

# App title
st.title("Resume Analysis Assistant")
st.markdown("Upload a resume and chat with an AI assistant about it")

# Initialize session state for chat history
if 'messages' not in st.session_state:
    st.session_state.messages = []

# File uploader
uploaded_file = st.file_uploader("Upload Resume (PDF)", type=['pdf'])
file_content = None

if uploaded_file:
    # Read file as bytes and convert to base64
    file_bytes = uploaded_file.read()
    file_content = base64.b64encode(file_bytes).decode('utf-8')
    st.success(f"Resume uploaded: {uploaded_file.name}")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask about the resume...")

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Display assistant response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            if not file_content and not any(msg["role"] == "assistant" for msg in st.session_state.messages[:-1]):
                response_content = "Please upload a resume first."
            else:
                # Call Langflow API
                response = run_flow(prompt, file_content)
                
                # Just display the raw response for now - we'll debug issues this way
                if "result" in response and isinstance(response["result"], dict):
                    response_content = response["result"].get("output", "No output in response")
                    # If response is JSON string, try to parse it
                    if isinstance(response_content, str) and response_content.startswith("{"):
                        try:
                            response_json = json.loads(response_content)
                            if "text" in response_json:
                                response_content = response_json["text"]
                        except:
                            pass
                else:
                    response_content = "Error: Unexpected response format"
                    st.json(response)  # Display the raw response for debugging
            
            st.markdown(response_content)
    
    # Add assistant response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response_content})

# Add sidebar with instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    1. Upload a resume PDF file
    2. Ask questions about the resume
    3. The AI assistant will analyze the resume and respond
    
    Example questions:
    - What are the candidate's key skills?
    - Summarize their work experience
    - What position would be a good fit for this candidate?
    """)
    
    # Add a button to clear chat history
    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    st.markdown("Powered by Langflow")
