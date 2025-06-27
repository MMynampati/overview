# app.py (version 3 - with strict prompting and source links)
import streamlit as st
import os
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
DB_PATH = "vectorstore"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "gpt-3.5-turbo" # Or "gpt-4" for higher quality

# --- NEW: The Strict Prompt Template ---
# This is the core of our anti-hallucination and source-guiding strategy.
prompt_template = """You are an expert assistant for the Overview AI documentation.
Your task is to answer the user's question based ONLY on the provided context.
Do not use any external knowledge or information you think you might know.

Context:
{context}

Based on the context above, answer the following question:
Question: {question}

Here are your rules:
1. If the context contains the answer, provide it clearly and concisely.
2. If the context mentions something visual (like a diagram, screenshot, or chart), tell the user that the information is visual and they should consult the source link for the image.
3. If the context does NOT contain the answer, you MUST respond with "I'm sorry, I couldn't find information about that in the documentation. Please try rephrasing your question."
4. Do not make up an answer or try to guess.

Answer:
"""

STRICT_PROMPT = PromptTemplate.from_template(prompt_template)

# --- Initialize ---
@st.cache_resource
def load_components():
    """Load the heavy components once and cache them."""
    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
        
        # Check if vectorstore directory exists
        if os.path.exists(DB_PATH):
            vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
            st.success("✅ Vector database loaded successfully!")
        else:
            st.error(f"❌ Vector database not found at {DB_PATH}")
            st.info("Please ensure the vectorstore directory is uploaded to your Streamlit Cloud deployment.")
            return None, None
            
        llm = ChatOpenAI(temperature=0, model_name=LLM_MODEL) # Temperature 0 = less creative, more factual
        return vectorstore, llm
    except Exception as e:
        st.error(f"❌ Error loading components: {e}")
        return None, None

vectorstore, llm = load_components()

# --- Session Memory ---
if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key='answer'
    )

# --- The Conversational Chain (NOW WITH THE STRICT PROMPT) ---
qa_chain = None
if vectorstore and llm:
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4}), # Retrieve a bit more context
        memory=st.session_state.memory,
        return_source_documents=True,
        output_key='answer',
        # This is where we inject our new, strict prompt
        combine_docs_chain_kwargs={"prompt": STRICT_PROMPT}
    )

# --- Streamlit UI (No changes here, but shown for completeness) ---
st.title("User Manual Chatbot")
st.write("Ask me anything about the Overview AI documentation!")

if not qa_chain:
    st.warning("⚠️ Chatbot is not ready. Please check the vector database setup.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("How do I authenticate API requests?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.spinner("Searching the docs..."):
        try:
            result = qa_chain.invoke({"question": prompt}) # Use .invoke for latest LangChain
            response = result['answer']
            source_docs = result['source_documents']
        except Exception as e:
            response = f"Sorry, I encountered an error: {e}"
            source_docs = []

    with st.chat_message("assistant"):
        st.markdown(response)
        # Display source documents with clickable links
        with st.expander("Show Sources"):
            if source_docs:
                for doc in source_docs:
                    source_url = doc.metadata.get('source', 'N/A')
                    # Make the link clickable
                    st.write(f"**Source:** [{source_url}]({source_url})")
                    # Show a snippet of the content that was used
                    st.caption(f"Content snippet: {doc.page_content[:200]}...")
            else:
                st.write("No source documents found for this query.")


    st.session_state.messages.append({"role": "assistant", "content": response})