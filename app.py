import streamlit as st
import os
import io
import csv
from PyPDF2 import PdfReader
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from dotenv import load_dotenv
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain import HuggingFaceHub
from streamlit_chat import message
from langchain.callbacks import get_openai_callback


def main():
    load_dotenv()
    st.set_page_config(page_title="PricePatrol")
    st.header("💸 Amherst PricePatrol")

    if "conversation" not in st.session_state:
        st.session_state.conversation = None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    if "processComplete" not in st.session_state:
        st.session_state.processComplete = None

    with st.sidebar:
        uploaded_files = st.file_uploader("Upload your file", type=['pdf', 'csv'], accept_multiple_files=True)
        openai_api_key = st.text_input("OpenAI API Key", key="chatbot_api_key", type="password")
        process = st.button("Process")

    # Hardcoded system prompt for prompt engineering
    system_prompt = (
        "You are an intelligent assistant helping users find the best grocery deals nearby in Amherst. "
        "Your responses should be concise, friendly, and focused on saving money. If possible, provide specific suggestions or stores, "
        "and avoid unnecessary details. Read the CSV file carefully, be accurate with product prices. Use only the shop names mentioned in each row."
    )


    if process:
        if not openai_api_key:
            st.info("Please add your OpenAI API key to continue.")
            st.stop()
        files_text = get_files_text(uploaded_files)
        # Get text chunks
        text_chunks = get_text_chunks(files_text)
        # Create vector store
        vectorstore = get_vectorstore(text_chunks)
        # Create conversation chain
        st.session_state.conversation = get_conversation_chain(vectorstore, openai_api_key, text_chunks)  # For OpenAI

        st.session_state.processComplete = True

    if st.session_state.processComplete:
        user_question = st.text_input("Go ahead and clear your grocery dilemma:")
        if user_question:
            # Prepend system prompt to the user's question
            combined_prompt = f"{system_prompt}\n\n{user_question}"
            handle_userinput(combined_prompt, user_question)


def get_files_text(uploaded_files):
    text = ""
    for uploaded_file in uploaded_files:
        split_tup = os.path.splitext(uploaded_file.name)
        file_extension = split_tup[1]
        if file_extension == ".pdf":
            text += get_pdf_text(uploaded_file)
        elif file_extension == ".csv":
            text += get_csv_text(uploaded_file)
    return text

def get_pdf_text(pdf):
    pdf_reader = PdfReader(pdf)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

def get_csv_text(file):
    decoded_file = io.StringIO(file.getvalue().decode("utf-8"))
    reader = csv.reader(decoded_file)
    allText = [', '.join(row) for row in reader]
    return '\n'.join(allText)

def get_text_chunks(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=900,
        chunk_overlap=100,
        length_function=len
    )
    return text_splitter.split_text(text)

def get_vectorstore(text_chunks):
    embeddings = HuggingFaceEmbeddings()
    knowledge_base = FAISS.from_texts(text_chunks, embeddings)
    return knowledge_base

def get_conversation_chain(vectorstore, openai_api_key, text_chunks):

  system_prompt = "..."  # Your system prompt definition

  # Prepend system prompt to each text chunk
  text_chunks = [system_prompt + "\n" + chunk for chunk in text_chunks]

  embeddings = HuggingFaceEmbeddings()
  knowledge_base = FAISS.from_texts(text_chunks, embeddings)

  llm = ChatOpenAI(model_name='gpt-3.5-turbo', temperature=0, openai_api_key = st.secrets["openai_api_key"])
  memory = ConversationBufferMemory(memory_key='chat_history', return_messages=True)
  conversation_chain = ConversationalRetrievalChain.from_llm(
      llm=llm,
      retriever=knowledge_base.as_retriever(),
      memory=memory
  )
  return conversation_chain

user_avatar = "🙍‍♀️"
ai_avatar = "👩‍💻"

def handle_userinput(combined_input, user_question):
    with get_openai_callback() as cb:
        response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    # Layout of input/response containers
    response_container = st.container()

    with response_container:
        for i, messages in enumerate(st.session_state.chat_history):
            if i % 2 == 0:
                message(messages.content, is_user=True, key=str(i))
            else:
                message(messages.content, key=str(i))

if __name__ == '__main__':
    main()