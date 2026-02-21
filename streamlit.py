import streamlit as st
from langgraph_backend import chatbot 
from langchain_core.messages import HumanMessage


config = {'configurable': {'thread_id': '1'}}

# Get current state from chatbot to display history
current_state = chatbot.get_state(config)
messages = current_state.values.get('messages', []) if current_state.values else []

# Display conversation history from LangGraph state
for message in messages:
    role = 'user' if message.type == 'human' else 'assistant'
    with st.chat_message(role):
        st.text(message.content)

user_input = st.chat_input('Your message...')

if user_input:
    # Display user message immediately
    with st.chat_message('user'):
        st.text(user_input)

    # Invoke chatbot with new message - checkpointer handles history automatically
    response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=config)
    ai_message = response['messages'][-1].content
    
    # Display assistant response
    with st.chat_message('assistant'):
        st.text(ai_message)
    
    # Rerun to refresh the display from checkpointer
    st.rerun()