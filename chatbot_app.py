import streamlit as st
import os
from groq import Groq
import random

from langchain.chains import ConversationChain, LLMChain
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Get the API key from the environment variable
groq_api_key = os.getenv("GROQ_API_KEY")


if not groq_api_key:
    raise ValueError("API_KEY is not set")


def main():
    """
    This function is the main entry point of the application. It sets up the Groq client, the Streamlit interface, and handles the chat interaction.
    """
    
    # Get Groq API key
    #groq_api_key = os.environ['GROQ_API_KEY']
    

    # Display the Groq logo
    spacer, col = st.columns([5, 1])  
    with col:  
        st.image('sfh.png')
    st.sidebar.image('sfh.png', width=150)

    # The title and greeting message of the Streamlit application
    st.title("SFH AI CHATBOT 🤖")
    st.write("Hello! I'm your friendly SFH AI chatbot. Let's start our conversation!")
    # Add customization options to the sidebar
    
    system_prompt = st.sidebar.text_input("System prompt AI Agent:")
    model = st.sidebar.selectbox(
        'Choose a model',
        ['llama3-8b-8192', 'qwen-2.5-32b', 'gemma2-9b-it','deepseek-r1-distill-qwen-32b']
    )
    conversational_memory_length = st.sidebar.slider('Conversational memory length:', 1, 10, value = 5)

    st.sidebar.markdown("""
    <hr style="border: 1px solid #007bff;">
    <br>
    <span style="color: #007bff;">Society for Family Health (SFH) - Rwanda</span>
    """, unsafe_allow_html=True)
    st.sidebar.markdown("<small>http://www.sfhrwanda.org/ </small>", unsafe_allow_html=True)

    memory = ConversationBufferWindowMemory(k=conversational_memory_length, memory_key="chat_history", return_messages=True)

    user_question = st.text_input("Ask a question:")

    # session state variable
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history=[]
    else:
        for message in st.session_state.chat_history:
            memory.save_context(
                {'input':message['human']},
                {'output':message['AI']}
                )


    # Initialize Groq Langchain chat object and conversation
    groq_chat = ChatGroq(
            groq_api_key=groq_api_key, 
            model_name=model
    )


    # If the user has asked a question,
    if user_question:

        # Construct a chat prompt template using various components
        prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=system_prompt
                ),  # This is the persistent system prompt that is always included at the start of the chat.

                MessagesPlaceholder(
                    variable_name="chat_history"
                ),  # This placeholder will be replaced by the actual chat history during the conversation. It helps in maintaining context.

                HumanMessagePromptTemplate.from_template(
                    "{human_input}"
                ),  # This template is where the user's current input will be injected into the prompt.
            ]
        )

        # Create a conversation chain using the LangChain LLM (Language Learning Model)
        conversation = LLMChain(
            llm=groq_chat,  # The Groq LangChain chat object initialized earlier.
            prompt=prompt,  # The constructed prompt template.
            verbose=True,   # Enables verbose output, which can be useful for debugging.
            memory=memory,  # The conversational memory object that stores and manages the conversation history.
        )
        
        # The chatbot's answer is generated by sending the full prompt to the Groq API.
        response = conversation.predict(human_input=user_question)
        message = {'human':user_question,'AI':response}
        st.session_state.chat_history.append(message)
        st.write("Chatbot:", response)

if __name__ == "__main__":
    main()





