# Manual Pages Search Interface

A Streamlit-based search interface for manual pages with AI-powered Q&A capabilities, session history, and citation links.

## Features

- 🔍 **Semantic Search**: Search through your manual pages using vector embeddings
- 🤖 **AI-Powered Q&A**: Get intelligent answers based on your manual content
- 📚 **Citation Links**: Every response includes clickable links to source pages
- 💬 **Session History**: Maintain conversation context during your session
- 🔒 **Secure API Keys**: Environment variable-based configuration for security
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose
- 📱 **Modern UI**: Clean, responsive interface built with Streamlit
- 🕷️ **Automatic Discovery**: Uses sitemaps to automatically discover and index pages

## Quick Start

### Prerequisites

- Python 3.8+ or Conda
- OpenAI API key
- Sitemap URL for your documentation

### Option 1: Conda Environment (Recommended for Development)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd overview
   ```

2. **Create and activate conda environment**
   ```bash
   conda env create -f environment.yml
   conda activate manual-search
   ```

3. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your configuration:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SITEMAP_URL=https://docs.overview.ai/sitemap.xml
   MAX_HISTORY_LENGTH=10
   ```

4. **Run ingestion to index your documentation**
   ```bash
   python ingest.py
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

### Option 2: Docker (Recommended for Deployment)

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd overview
   ```

2. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` and add your configuration:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SITEMAP_URL=https://docs.overview.ai/sitemap.xml
   MAX_HISTORY_LENGTH=10
   ```

3. **Run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   Open your browser and go to `http://localhost:8501`

### Option 3: Local Development with pip

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd overview
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   ```
   
   Edit `.env` with your configuration.

5. **Run ingestion to index your documentation**
   ```bash
   python ingest.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

## Environment Management

### Using Conda (Recommended)

```bash
# Create environment
conda env create -f environment.yml

# Activate environment
conda activate manual-search

# Deactivate environment
conda deactivate

# Remove environment (if needed)
conda env remove -n manual-search

# Update environment
conda env update -f environment.yml
```

### Using pip/venv

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Deactivate
deactivate
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | Yes |
| `SITEMAP_URL` | URL to your documentation sitemap.xml | Yes |
| `MAX_HISTORY_LENGTH` | Maximum conversation turns to keep in memory | No (default: 10) |
| `DB_PATH` | Path for vector database storage | No (default: vectorstore) |

### Sitemap Configuration

The application automatically discovers and indexes pages from your sitemap.xml file. Simply provide the URL to your sitemap:

```env
SITEMAP_URL=https://docs.overview.ai/sitemap.xml
```

## Usage

1. **First Run**: Run `python ingest.py` to index your documentation from the sitemap
2. **Search**: Type your question in the chat input
3. **Get Answers**: Receive AI-generated answers with citation links
4. **View Sources**: Click on citation numbers or expand the "View Source Citations" section
5. **Session Management**: Use the sidebar to clear chat history or re-index pages

## Features in Detail

### Semantic Search
- Uses ChromaDB for vector storage
- Sentence transformers for text embeddings
- Intelligent content chunking and indexing

### AI-Powered Responses
- GPT-3.5-turbo integration
- Context-aware responses based on manual content
- Automatic citation generation
- Anti-hallucination prompting

### Session History
- Maintains conversation context
- Configurable history length
- Easy session clearing

### Citation System
- Automatic source linking
- Clickable citation numbers
- Detailed source information in expandable sections

### Automatic Discovery
- Sitemap-based page discovery
- Intelligent content extraction
- Politeness delays for web scraping

## File Structure

```
overview/
├── app.py              # Main Streamlit application
├── ingest.py           # Data ingestion pipeline
├── core/
│   ├── crawler.py      # Sitemap crawling utilities
│   └── loader.py       # Web content loading
├── requirements.txt    # Python dependencies (for pip)
├── environment.yml     # Conda environment (for conda)
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose setup
├── env.example        # Environment variables template
├── .gitignore         # Git ignore rules
├── README.md          # This file
└── data/              # Vector database storage (auto-created)
```

## Security Considerations

- **API Keys**: Never commit your `.env` file to version control
- **Environment Variables**: Use Docker secrets or environment variables for production
- **Data Storage**: Vector database is stored locally in the `data/` directory

## Troubleshooting

### Common Issues

1. **"OpenAI API key not found"**
   - Ensure your `.env` file exists and contains the correct API key
   - Check that the environment variable is properly set

2. **"Sitemap URL not configured"**
   - Add your sitemap URL to the `SITEMAP_URL` environment variable
   - Ensure the sitemap is accessible from your network

3. **"Error accessing sitemap"**
   - Check that the sitemap URL is accessible from your network
   - Verify the sitemap follows the standard XML format

4. **"No content extracted from pages"**
   - The application targets specific CSS classes for content extraction
   - Check that your documentation uses the expected HTML structure

5. **Docker build fails**
   - Ensure Docker and Docker Compose are installed
   - Check that all files are present in the repository

6. **Conda environment issues**
   - Try updating conda: `conda update conda`
   - Remove and recreate environment: `conda env remove -n manual-search && conda env create -f environment.yml`

### Performance Tips

- The ingestion process may take time depending on the number of pages
- Use the re-index feature sparingly
- Consider using a more powerful model for better responses

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the configuration options
3. Open an issue on GitHub with detailed information 