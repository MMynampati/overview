import streamlit as st
import os
from dotenv import load_dotenv
from scraper import ManualPageScraper
from openai import OpenAI
import json
from typing import List, Dict
import time

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Manual Pages Search",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        border-left: 4px solid #1f77b4;
    }
    .user-message {
        background-color: #f0f2f6;
        border-left-color: #1f77b4;
    }
    .assistant-message {
        background-color: #e8f4fd;
        border-left-color: #28a745;
    }
    .citation-link {
        color: #1f77b4;
        text-decoration: none;
        font-weight: bold;
    }
    .citation-link:hover {
        text-decoration: underline;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'scraper' not in st.session_state:
    st.session_state.scraper = None
if 'client' not in st.session_state:
    st.session_state.client = None
if 'indexed_urls' not in st.session_state:
    st.session_state.indexed_urls = []

def initialize_components():
    """Initialize scraper and OpenAI client."""
    if st.session_state.scraper is None:
        st.session_state.scraper = ManualPageScraper()
    
    if st.session_state.client is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            st.session_state.client = OpenAI(api_key=api_key)
        else:
            st.error("OpenAI API key not found. Please set the OPENAI_API_KEY environment variable.")
            return False
    
    return True

def index_manual_pages():
    """Index manual pages from environment variable."""
    urls_str = os.getenv('MANUAL_PAGES')
    if not urls_str:
        st.error("No manual pages configured. Please set the MANUAL_PAGES environment variable.")
        return False
    
    urls = [url.strip() for url in urls_str.split(',') if url.strip()]
    if not urls:
        st.error("No valid URLs found in MANUAL_PAGES environment variable.")
        return False
    
    # Check if pages are already indexed
    existing_urls = st.session_state.scraper.get_all_urls()
    if not existing_urls:
        with st.spinner("Indexing manual pages..."):
            st.session_state.scraper.index_pages(urls)
        st.success(f"Successfully indexed {len(urls)} manual pages!")
    else:
        st.session_state.indexed_urls = existing_urls
    
    return True

def generate_response(query: str, context: List[Dict]) -> str:
    """Generate response using OpenAI with context."""
    if not st.session_state.client:
        return "Error: OpenAI client not initialized."
    
    # Prepare context for the prompt
    context_text = "\n\n".join([
        f"Source: {item['url']}\nTitle: {item['title']}\nContent: {item['text']}"
        for item in context
    ])
    
    # Create citations list
    citations = []
    for i, item in enumerate(context, 1):
        citations.append(f"[{i}] {item['title']} - {item['url']}")
    
    citations_text = "\n".join(citations)
    
    # Create the prompt
    prompt = f"""You are a helpful assistant that answers questions based on the provided manual pages. 
    
Context from manual pages:
{context_text}

Citations:
{citations_text}

Question: {query}

Please provide a comprehensive answer based on the context above. Include relevant citations in your response using the format [1], [2], etc. to reference the sources.

Answer:"""
    
    try:
        response = st.session_state.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides accurate information based on the given context and always includes proper citations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error generating response: {str(e)}"

def format_response_with_citations(response: str, context: List[Dict]) -> str:
    """Format response to include clickable citation links."""
    formatted_response = response
    
    # Replace citation numbers with clickable links
    for i, item in enumerate(context, 1):
        citation_pattern = f"[{i}]"
        if citation_pattern in formatted_response:
            link_html = f'<a href="{item["url"]}" target="_blank" class="citation-link">[{i}]</a>'
            formatted_response = formatted_response.replace(citation_pattern, link_html)
    
    return formatted_response

def main():
    # Header
    st.markdown('<h1 class="main-header">📚 Manual Pages Search</h1>', unsafe_allow_html=True)
    
    # Initialize components
    if not initialize_components():
        return
    
    # Index pages if needed
    if not index_manual_pages():
        return
    
    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-header">Settings</div>', unsafe_allow_html=True)
        
        # Search settings
        max_results = st.slider("Max search results", 3, 10, 5)
        
        # Session management
        st.markdown('<div class="sidebar-header">Session</div>', unsafe_allow_html=True)
        
        if st.button("Clear Chat History"):
            st.session_state.messages = []
            st.rerun()
        
        # Display indexed pages
        st.markdown('<div class="sidebar-header">Indexed Pages</div>', unsafe_allow_html=True)
        indexed_urls = st.session_state.scraper.get_all_urls()
        for url in indexed_urls:
            st.write(f"• {url}")
        
        # Manual re-indexing
        st.markdown('<div class="sidebar-header">Re-index Pages</div>', unsafe_allow_html=True)
        if st.button("Re-index All Pages"):
            urls_str = os.getenv('MANUAL_PAGES')
            if urls_str:
                urls = [url.strip() for url in urls_str.split(',') if url.strip()]
                with st.spinner("Re-indexing pages..."):
                    # Clear existing collection
                    st.session_state.scraper.collection.delete()
                    st.session_state.scraper = ManualPageScraper()
                    st.session_state.scraper.index_pages(urls)
                st.success("Pages re-indexed successfully!")
                st.rerun()
    
    # Main chat interface
    st.markdown("### Ask questions about your manual pages:")
    
    # Chat input
    if prompt := st.chat_input("What would you like to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Search for relevant content
        with st.spinner("Searching for relevant information..."):
            search_results = st.session_state.scraper.search(prompt, n_results=max_results)
        
        if not search_results:
            st.error("No relevant information found. Please try a different query.")
            return
        
        # Generate response
        with st.spinner("Generating response..."):
            response = generate_response(prompt, search_results)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": response, "citations": search_results})
    
    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            # Format response with citations
            formatted_response = format_response_with_citations(message["content"], message.get("citations", []))
            
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>Assistant:</strong><br>
                {formatted_response}
            </div>
            """, unsafe_allow_html=True)
            
            # Show citation details in expander
            if "citations" in message:
                with st.expander("View Source Citations"):
                    for i, citation in enumerate(message["citations"], 1):
                        st.markdown(f"""
                        **[{i}] {citation['title']}**
                        - URL: [{citation['url']}]({citation['url']})
                        - Type: {citation['type']}
                        - Content: {citation['text'][:200]}...
                        """)

if __name__ == "__main__":
    main() 