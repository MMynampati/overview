# Overview AI Documentation Chatbot

A conversational AI chatbot that answers questions about Overview AI documentation using RAG (Retrieval-Augmented Generation).

## 🚀 Quick Start (Deployment Ready)

**Want to run the chatbot immediately?** Use the pre-built version in the `src/` directory:

```bash
cd src
pip install -r requirements.txt
streamlit run app.py
```

This includes everything you need:
- ✅ Pre-built vector database (no scraping required)
- ✅ Minimal dependencies
- ✅ Ready for Streamlit Cloud deployment

## 🛠️ Full Development Setup

**Want to modify the scraping, processing, or rebuild the database?** Use the full development setup:

```bash
# Install all dependencies
pip install -r full_requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your OpenAI API key

# Run the scraper to collect documentation
python core/crawler.py

# Process and create vector database
python ingest.py

# Run the app
cd src
streamlit run app.py
```

## 🧪 Testing

We provide comprehensive testing scripts to verify everything works:

### 1. Complete Test Suite
```bash
# Test everything (setup, dependencies, functionality)
python test_setup.py
```

### 2. Chatbot Functionality Test
```bash
# Test the chatbot specifically (requires OpenAI API key)
python test_chatbot.py
```

### 3. Deployment Test
```bash
# Test the deployment setup (src/ directory)
python test_deployment.py
```

### 4. Manual Testing
```bash
# Test the app manually
cd src
streamlit run app.py
```

## 📁 Project Structure

```
overview/
├── src/                    # 🚀 Deployment-ready files
│   ├── app.py             # Streamlit chatbot app
│   ├── requirements.txt   # Minimal dependencies
│   ├── vectorstore/       # Pre-built vector database
│   └── README.md          # Deployment instructions
├── core/                  # 🛠️ Development tools
│   ├── crawler.py         # Web scraper
│   └── overview.csv       # Scraped data
├── ingest.py              # Vector database creation
├── full_requirements.txt  # Complete dependencies
├── test_setup.py          # Complete test suite
├── test_chatbot.py        # Chatbot functionality tests
├── test_deployment.py     # Deployment tests
└── README.md              # This file
```

## 🔧 Configuration

Set your OpenAI API key in `.env`:
```
OPENAI_API_KEY=your_api_key_here
```

## 🚀 Deployment

### Streamlit Cloud
1. Upload the entire `src/` directory to Streamlit Cloud
2. Set `OPENAI_API_KEY` in Streamlit Cloud secrets
3. Deploy!

### Local Development
1. Clone the full repository
2. Follow the "Full Development Setup" instructions above
3. Run `streamlit run src/app.py`

## 🤖 Features

- **RAG-powered responses** based on Overview AI documentation
- **Source attribution** with clickable links
- **Anti-hallucination** through strict prompting
- **Conversation memory** for contextual follow-ups
- **Visual content detection** (diagrams, screenshots, charts)

## 📝 License

[Add your license here]
