import streamlit as st
import requests
import json
import time
import threading
from queue import Queue
import traceback

# Set page config
st.set_page_config(page_title="SSE Chatbot", layout="wide")

# Initialize session state for chat history if it doesn't exist
if "messages" not in st.session_state:
    st.session_state.messages = []


# Function to handle SSE streaming responses
def process_sse_stream(url, payload, message_queue):
    try:
        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }

        # Modify payload to match potential server expectations
        request_json = {
            'query': payload,
            'stream': True
        }

        try:
            response = requests.post(url, json=request_json, headers=headers, stream=True)
        except requests.RequestException as e:
            message_queue.put(("error", f"Connection Error: {str(e)}"))
            return

        if response.status_code == 200:
            full_response = ""

            for line in response.iter_lines():
                if line:
                    try:
                        # Decode bytes to string and remove any 'data: ' prefix
                        decoded_line = line.decode('utf-8').strip()

                        # Remove 'data: ' prefix if present
                        if decoded_line.startswith('data: '):
                            decoded_line = decoded_line[6:]

                        # Check for termination signal
                        if decoded_line == '[DONE]':
                            break

                        # Try to parse JSON
                        try:
                            data = json.loads(decoded_line)
                            tmp = data['choices'][0]
                            if tmp['finish_reason'] is not None and tmp['finish_reason'] == 'stop':
                                break
                            # Extract content, handling different possible structures
                            chunk = tmp['delta']['content']
                            full_response += chunk
                        except json.JSONDecodeError:
                            # If not JSON, treat as raw text
                            full_response += decoded_line

                        # Update UI with partial response
                        message_queue.put(("update", full_response))

                    except Exception as parse_error:
                        # Log parsing errors without breaking the stream
                        message_queue.put(("error", f"Parsing error: {str(parse_error)}"))

            # Signal stream completion
            message_queue.put(("done", full_response))
        else:
            message_queue.put(("error", f"HTTP Error: {response.status_code} - {response.text}"))

    except Exception as e:
        # Catch-all for any unexpected errors
        error_details = traceback.format_exc()
        message_queue.put(("error", f"Unexpected Error: {str(e)}\n{error_details}"))


# Page title
st.title("💬 Chatbot with SSE")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
prompt = st.chat_input("Ask something...")

# Initialize the placeholder outside the if statement
response_placeholder = None

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat container
    with st.chat_message("user"):
        st.markdown(prompt)

    # Initialize a placeholder for the assistant's response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        response_placeholder.markdown("Thinking...")

    # Server URL (replace with your actual API endpoint)
    API_URL = "http://localhost:9000/chatbot/chat"

    # Create a queue for thread communication
    message_queue = Queue()

    # Start the SSE processing in a separate thread
    sse_thread = threading.Thread(
        target=process_sse_stream,
        args=(API_URL, prompt, message_queue)
    )
    sse_thread.start()

    # Initialize the assistant's response
    assistant_response = ""

    # Process messages from the queue
    while True:
        try:
            message_type, content = message_queue.get(timeout=5)  # Increased timeout

            if message_type == "update":
                # Update the displayed response
                assistant_response = content
                response_placeholder.markdown(assistant_response)
            elif message_type == "done":
                # Stream is complete
                assistant_response = content
                response_placeholder.markdown(assistant_response)
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                break
            elif message_type == "error":
                # Display error message
                response_placeholder.markdown(f"⚠️ Error: {content}")
                break

        except Exception as e:
            # Check if the thread is still running
            if not sse_thread.is_alive():
                if not assistant_response:
                    response_placeholder.markdown(f"⚠️ Connection error: {e}")
                break
            time.sleep(0.1)

    # Wait for the thread to complete
    sse_thread.join()

# Sidebar with information
with st.sidebar:
    st.title("About")
    st.markdown("""
    This chatbot uses Server-Sent Events (SSE) to communicate with the backend server.

    Features:
    - Real-time streaming responses
    - Persistent chat history
    - Robust error handling
    - Flexible response parsing

    To configure the server endpoint, modify the `API_URL` variable in the code.
    """)

    # Clear chat history button
    if st.button("Clear chat history"):
        st.session_state.messages = []
        st.rerun()