import uuid
import streamlit as st
from utils import get_response, load_files_to_s3, update_vectorstore
import time

user_id = '234580980435'

st.title("NoONE Chatbot")

with st.sidebar:
    # Add elements to the sidebar here
    st.header("Upload documents")

    uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)

    if uploaded_files:
        load_files_to_s3(uploaded_files)
        update_vectorstore()
        st.write('Files uploaded successfuly')


# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input("What is up?"):
    
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        
        message_placeholder = st.empty()
        full_response = ""
        resp = get_response(body=prompt, user_id=user_id)
        
        assistant_response = resp if resp else "I am down, but there :)"
        # Simulate stream of response with milliseconds delay
        for chunk in assistant_response.split():
            full_response += chunk + " "
            time.sleep(0.05)
            # Add a blinking cursor to simulate typing
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

