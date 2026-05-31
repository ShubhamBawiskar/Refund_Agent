import streamlit as st
import requests
import os
import json

# Setup API URL
API_URL = os.environ.get("API_URL", "http://backend:8000/api/chat")

st.set_page_config(page_title="AI Refund Agent", layout="wide")

st.title("AI Customer Support - Refund Portal")

# Initialize session state for messages and reasoning logs
if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Hello! I am the AI Support Agent. How can I help you with your refund today? Please provide your email and order ID if you have them."}
    ]

if "reasoning_logs" not in st.session_state:
    st.session_state["reasoning_logs"] = []

# Two-column layout
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Customer Chat")
    
    # Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Append user message to state
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)
            
        # Call backend API
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"messages": st.session_state.messages})
                response.raise_for_status()
                data = response.json()
                
                final_message = data.get("final_message", "Error: No response from agent.")
                logs = data.get("reasoning_logs", [])
                
                # Append assistant message to state
                st.session_state.messages.append({"role": "assistant", "content": final_message})
                
                # Append logs to state
                if logs:
                    st.session_state.reasoning_logs.extend(logs)
                    
                # Display assistant message
                with st.chat_message("assistant"):
                    st.markdown(final_message)
                    
            except Exception as e:
                st.error(f"Failed to communicate with backend: {e}")

with col2:
    st.subheader("Admin View: Agent Reasoning Logs")
    
    if st.session_state.reasoning_logs:
        # Create a formatted JSON string for logs
        logs_json = json.dumps(st.session_state.reasoning_logs, indent=2)
        st.code(logs_json, language="json")
    else:
        st.info("No tool calls or reasoning logs yet.")
