import streamlit as st
import openai
import yaml
import io
from docx import Document
import json
from PyPDF2 import PdfReader

st.set_page_config(
    page_title="DevOps Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize OpenAI client
if 'openai_client' not in st.session_state:
    try:
        st.session_state.openai_client = openai.AzureOpenAI(
            api_key="d2fc3cb33a1046b5936b9d9995322f2d",
            api_version="2024-08-01-preview",
            azure_endpoint="https://idpoai.openai.azure.com"
        )
    except Exception as e:
        st.error(f"Error initializing OpenAI client: {str(e)}")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'current_file_content' not in st.session_state:
    st.session_state.current_file_content = None

if 'current_file_name' not in st.session_state:
    st.session_state.current_file_name = None

def extract_file_content(file_bytes, filename):
    """Extract content from file and return as text"""
    try:
        # Try YAML/JSON first
        try:
            text = file_bytes.decode('utf-8')
            if text.lstrip().startswith(('apiVersion:', 'kind:', '---')):
                data = yaml.safe_load(text)
                return yaml.dump(data, sort_keys=False), 'yaml'
            elif text.lstrip().startswith('{') or text.lstrip().startswith('['):
                data = json.loads(text)
                return json.dumps(data, indent=2), 'json'
        except:
            pass

        # Try DOCX
        try:
            doc = Document(io.BytesIO(file_bytes))
            return '\n'.join(p.text for p in doc.paragraphs if p.text), 'text'
        except:
            pass

        # Try PDF
        try:
            pdf = PdfReader(io.BytesIO(file_bytes))
            return '\n'.join(page.extract_text() for page in pdf.pages if page.extract_text()), 'text'
        except:
            pass

        # Try plain text
        try:
            return file_bytes.decode('utf-8'), 'text'
        except:
            return file_bytes.decode('latin-1', errors='ignore'), 'text'
    except:
        return None, None

# Main layout
st.title("DevOps Assistant")

# Two columns: Chat and File Preview
col1, col2 = st.columns([3, 2])

with col1:
    st.header("Chat with Assistant")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if st.session_state.current_file_content:
        chat_placeholder = f"Ask questions about {st.session_state.current_file_name} or any DevOps topic"
    else:
        chat_placeholder = "Ask a DevOps question"
        
    if prompt := st.chat_input(chat_placeholder):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            try:
                messages = [
                    {"role": "system", "content": "You are a helpful DevOps assistant."},
                    *[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
                ]
                
                response = st.session_state.openai_client.chat.completions.create(
                    model="gpt-4o",  # deployment name
                    messages=messages,
                    temperature=0.7,
                    max_tokens=800,
                    top_p=0.95,
                    frequency_penalty=0,
                    presence_penalty=0,
                    stop=None
                )
                
                if response and response.choices:
                    assistant_response = response.choices[0].message.content
                    st.markdown(assistant_response)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                else:
                    st.error("No response received from the assistant. Please try again.")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
                if "model" in str(e).lower():
                    st.info("Hint: The model name might be incorrect. Please check the Azure OpenAI deployment name.")

with col2:
    st.header("File Preview")
    uploaded_file = st.file_uploader("", type=None)
    if uploaded_file:
        file_bytes = uploaded_file.read()
        content, content_type = extract_file_content(file_bytes, uploaded_file.name)
        
        if content:
            st.code(content, language=content_type)
            
            # Update session state with new file content
            st.session_state.current_file_content = content
            st.session_state.current_file_name = uploaded_file.name
            
            # Add file content to chat context
            if content != st.session_state.get('last_file_content'):
                system_message = f"The user has uploaded a file named '{uploaded_file.name}'. Here's its content:\n\n{content}\n\nPlease help analyze or modify this content as needed."
                st.session_state.messages.append({"role": "system", "content": system_message})
                st.session_state.last_file_content = content
