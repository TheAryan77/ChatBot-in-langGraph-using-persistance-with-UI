import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid
from datetime import datetime

# Configure page
st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background-color: #f5f7fa;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e2130;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #ffffff;
    }
    
    /* Chat messages styling */
    .stChatMessage {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Button styling */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    /* New chat button */
    .stButton button[kind="primary"] {
        background-color: #4CAF50;
    }
    
    /* Conversation buttons */
    .conversation-btn {
        background-color: #2d3142;
        color: white;
        border: 1px solid #4a4e69;
        text-align: left;
        padding: 12px;
        margin: 5px 0;
    }
    
    /* Header styling */
    .chat-header {
        text-align: center;
        padding: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }
    
    /* Conversation preview */
    .conv-preview {
        font-size: 0.85em;
        color: #8892b0;
        margin-top: 5px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Sidebar title */
    .sidebar-title {
        color: #64ffda !important;
        font-size: 1.5em;
        font-weight: bold;
        margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

def generate_threadid():
    thread_id = str(uuid.uuid4())
    return thread_id

def reset_chat():
    thread_id = generate_threadid()
    st.session_state['thread_id'] = thread_id
    add_threadid(st.session_state['thread_id'])
    st.session_state['message_history'] = []
    # Store metadata for each conversation
    st.session_state['conv_metadata'][thread_id] = {
        'created_at': datetime.now().strftime("%b %d, %I:%M %p"),
        'preview': 'New conversation'
    }

def add_threadid(thread_id): 
    if thread_id not in st.session_state['list']:
        st.session_state['list'].append(thread_id)
        # Initialize metadata if not exists
        if thread_id not in st.session_state['conv_metadata']:
            st.session_state['conv_metadata'][thread_id] = {
                'created_at': datetime.now().strftime("%b %d, %I:%M %p"),
                'preview': 'New conversation'
            }

def get_conversation_preview(thread_id):
    """Get a preview of the conversation"""
    messages = load_conversation(thread_id)
    if messages:
        # Get first user message as preview
        for msg in messages:
            if isinstance(msg, HumanMessage):
                preview = msg.content[:50] + "..." if len(msg.content) > 50 else msg.content
                return preview
    return "New conversation"

def load_conversation(thread_id):
    return chatbot.get_state(config={'configurable': {'thread_id': thread_id}}).values['messages']

# Initialize session state
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_threadid()

if 'list' not in st.session_state:
    st.session_state['list'] = []

if 'conv_metadata' not in st.session_state:
    st.session_state['conv_metadata'] = {}

add_threadid(st.session_state['thread_id'])

# Main header
st.markdown("""
    <div class="chat-header">
        <h1>💬 LangGraph Chatbot</h1>
        <p>Intelligent AI Assistant with Conversation Memory</p>
    </div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<p class="sidebar-title">💬 LangGraph Chat</p>', unsafe_allow_html=True)
    
    if st.button('➕ New Chat', type='primary', use_container_width=True):
        reset_chat()
        st.rerun()
    
    st.markdown("---")
    st.subheader('📜 Conversation History')
    
    if len(st.session_state['list']) == 0:
        st.info("No conversations yet. Start a new chat!")
    else:
        for idx, thread_id in enumerate(st.session_state['list'][::-1], 1):
            # Update preview if not set
            if thread_id in st.session_state['conv_metadata']:
                metadata = st.session_state['conv_metadata'][thread_id]
            else:
                metadata = {
                    'created_at': datetime.now().strftime("%b %d, %I:%M %p"),
                    'preview': get_conversation_preview(thread_id)
                }
                st.session_state['conv_metadata'][thread_id] = metadata
            
            # Create a container for each conversation
            is_active = thread_id == st.session_state['thread_id']
            btn_label = f"{'🟢' if is_active else '💬'} Chat {len(st.session_state['list']) - idx + 1}"
            
            col1, col2 = st.columns([4, 1])
            with col1:
                if st.button(btn_label, key=f"conv_{thread_id}", use_container_width=True):
                    st.session_state['thread_id'] = thread_id
                    messages = load_conversation(thread_id)

                    temp_messages = []
                    for message in messages:
                        if isinstance(message, HumanMessage):
                            role = 'user'
                        else:
                            role = 'assistant'
                        temp_messages.append({'role': role, 'content': message.content})
                    st.session_state['message_history'] = temp_messages
                    st.rerun()
            
            with col2:
                st.caption(f"🕐")
            
            # Show preview and timestamp
            st.caption(f"_{metadata['preview']}_")
            st.caption(f"📅 {metadata['created_at']}")
            st.markdown("---")

# Display conversation info
col1, col2, col3 = st.columns([2, 2, 1])
with col1:
    st.metric("💬 Current Chat", f"Chat {st.session_state['list'].index(st.session_state['thread_id']) + 1 if st.session_state['thread_id'] in st.session_state['list'] else 1}")
with col2:
    msg_count = len(st.session_state['message_history'])
    st.metric("📊 Messages", msg_count)
with col3:
    if st.button("🗑️ Clear"):
        reset_chat()
        st.rerun()

st.markdown("---")

# Loading the conversation history
for message in st.session_state['message_history']:
    avatar = "👤" if message['role'] == 'user' else "🤖"
    with st.chat_message(message['role'], avatar=avatar):
        st.markdown(message['content'])

# Chat input with better placeholder
user_input = st.chat_input('💭 Type your message here...')

if user_input:
    # Add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    
    # Update conversation preview with first message
    if st.session_state['thread_id'] in st.session_state['conv_metadata']:
        if st.session_state['conv_metadata'][st.session_state['thread_id']]['preview'] == 'New conversation':
            preview = user_input[:50] + "..." if len(user_input) > 50 else user_input
            st.session_state['conv_metadata'][st.session_state['thread_id']]['preview'] = preview
    
    with st.chat_message('user', avatar="👤"):
        st.markdown(user_input)
    
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}

    # Get AI response
    with st.chat_message('assistant', avatar="🤖"):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    st.rerun()
