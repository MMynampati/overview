# Overview AI Chatbot - Deployment Ready

This directory contains the minimal files needed to run the Overview AI documentation chatbot.

## Quick Start

1. **For Streamlit Cloud Deployment:**
   - Upload this entire `src/` directory to Streamlit Cloud
   - Set your `OPENAI_API_KEY` in the Streamlit Cloud secrets
   - Deploy!

2. **For Local Development:**
   ```bash
   cd src
   pip install -r requirements.txt
   streamlit run app.py
   ```

## What's Included

- `app.py` - The Streamlit chatbot application
- `requirements.txt` - Minimal dependencies for deployment
- `vectorstore/` - Pre-built vector database (no scraping needed)

## Environment Variables

Create a `.env` file or set in Streamlit Cloud secrets:
```
OPENAI_API_KEY=your_openai_api_key_here
```

## For Full Development

If you want to modify the scraping, processing, or rebuild the vector database, see the main repository root for the complete development setup.

## 🚀 Deployment Instructions

### 1. Prepare Your Files
Make sure you have these files in your `src/` directory:
- `app.py` - Main Streamlit application
- `requirements.txt` - Python dependencies
- `vectorstore/` - Your ChromaDB vector database (entire directory)

### 2. Deploy to Streamlit Community Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io)**
2. **Connect your GitHub repository**
3. **Set the deployment path to your `src/` directory**
4. **Add your environment variables:**
   - `OPENAI_API_KEY` - Your OpenAI API key

### 3. File Structure for Deployment
```
src/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── README.md          # This file
└── vectorstore/       # ChromaDB database (upload entire directory)
    ├── chroma.sqlite3
    └── [other ChromaDB files]
```

### 4. Environment Variables
In Streamlit Cloud, add these secrets:
```
OPENAI_API_KEY = your_openai_api_key_here
```

### 5. Troubleshooting

**If you see "Vector database not found":**
- Make sure the `vectorstore/` directory is uploaded to your deployment
- Check that all ChromaDB files are included

**If you see import errors:**
- Verify all dependencies are in `requirements.txt`
- Check that version numbers are compatible

**If the app is slow to load:**
- This is normal for the first load as it downloads the embedding model
- Subsequent loads will be faster due to caching

## 🎯 Features
- ✅ Semantic search through Overview AI documentation
- ✅ AI-powered Q&A with source citations
- ✅ Conversation history
- ✅ Strict prompting to prevent hallucinations
- ✅ Clickable source links

## 📝 Notes
- The app uses the `all-MiniLM-L6-v2` embedding model
- Retrieves 4 most relevant document chunks per query
- Uses GPT-3.5-turbo for responses
- Temperature is set to 0 for factual responses 