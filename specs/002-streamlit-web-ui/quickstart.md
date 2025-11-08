# Quickstart Guide: Streamlit Web UI

**Feature**: 002-streamlit-web-ui  
**Date**: November 7, 2025  
**Estimated Time**: 10 minutes

## Overview

This guide will help you get the Streamlit web UI running for the Nuclia RAG system in under 10 minutes. You'll be able to chat with your knowledge base and compare search strategies through an intuitive web interface.

---

## Prerequisites

✅ **Required**:
- Python 3.10 or higher
- Existing Nuclia RAG API running (from `001-api-cli-chatbot`)
- Terminal access

✅ **Assumed**:
- Knowledge base already indexed with data
- Familiar with running Python applications

---

## Step 1: Install Dependencies

Update your Python environment with the new Streamlit dependencies:

```bash
# Navigate to project root
cd /path/to/nuclia

# Install Streamlit and dependencies
pip install streamlit requests

# Or install from updated requirements.txt
pip install -r requirements.txt
```

**Expected Output**:
```
Successfully installed streamlit-1.29.0 requests-2.31.0 ...
```

**Verify Installation**:
```bash
streamlit --version
```
Should show: `Streamlit, version 1.29.0` (or higher)

---

## Step 2: Configure Environment

Create or update your `.env` file with the API base URL:

```bash
# Copy example if it doesn't exist
cp .env.example .env

# Edit .env and add/update:
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30
```

**Example `.env` file**:
```bash
# Existing configuration
KB_URL=https://your-kb.nuclia.cloud
KB_API_KEY=your-api-key-here

# New Streamlit configuration
API_BASE_URL=http://localhost:8000
API_TIMEOUT=30
```

---

## Step 3: Start the API Server

**Terminal 1**: Start the FastAPI backend (if not already running)

```bash
uvicorn api:app --reload
```

**Expected Output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Verify API is Running**:
Visit http://localhost:8000/docs in your browser - you should see the FastAPI Swagger UI.

---

## Step 4: Launch the Streamlit UI

**Terminal 2**: Start the Streamlit application

```bash
streamlit run app.py
```

**Expected Output**:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.1.x:8501
```

**What Happens**:
- Streamlit automatically opens your default browser to `http://localhost:8501`
- You'll see the landing page with navigation options
- The app is now ready to use!

---

## Step 5: Use the Chat Interface

1. **Navigate to Chat Page**:
   - Click "💬 Chat" in the sidebar, or
   - Go to http://localhost:8501/Chat

2. **Select Search Strategy** (optional):
   - Use the dropdown to choose: Semantic, Hybrid, or Merged
   - Default is "Merged" (recommended for best results)

3. **Ask a Question**:
   - Type your question in the chat input at the bottom
   - Press Enter or click the send icon
   - Watch as your question and the AI response appear in the chat thread

4. **Continue the Conversation**:
   - Ask follow-up questions
   - All messages stay in the conversation history
   - Scroll up to review previous exchanges

5. **Clear History** (if needed):
   - Click the "🗑️ Clear History" button in the sidebar
   - Confirms before clearing to prevent accidental deletion

**Example Conversation**:
```
You: What is retrieval-augmented generation?
Assistant: Based on the search results, RAG is a technique that...

You: How does it differ from traditional LLMs?
Assistant: RAG differs from traditional LLMs in several ways...
```

---

## Step 6: Compare Search Strategies

1. **Navigate to Comparison Page**:
   - Click "🔍 Compare" in the sidebar, or
   - Go to http://localhost:8501/Compare

2. **Enter a Query**:
   - Type your search query in the input box
   - Click "🔍 Search" button

3. **Review Results**:
   - See results from all three strategies side-by-side:
     - 🔤 **Semantic**: Vector similarity search
     - 🔀 **Hybrid**: Combined BM25 + semantic
     - 🎯 **Merged**: Rank fusion of strategies
   - Compare relevance scores and content
   - Identify which strategy works best for your query type

4. **Try Different Queries**:
   - Experiment with different question types
   - Notice how strategies perform differently
   - Use insights to choose best strategy in chat mode

**Example Comparison**:
- Query: "machine learning algorithms"
- Semantic: Returns conceptually related content
- Hybrid: Balances keyword matching with concepts
- Merged: Best of both worlds

---

## Troubleshooting

### Issue: "Unable to connect to search API"

**Cause**: FastAPI server not running or wrong URL

**Solution**:
1. Check Terminal 1 - is `uvicorn` running?
2. Verify `.env` has correct `API_BASE_URL=http://localhost:8000`
3. Test API directly: `curl http://localhost:8000/docs`

---

### Issue: "No results found"

**Cause**: Knowledge base might be empty or query doesn't match content

**Solution**:
1. Verify knowledge base has indexed data
2. Try broader queries (e.g., "document" instead of specific terms)
3. Check different search strategies - some work better for certain query types

---

### Issue: Streamlit says "Port 8501 already in use"

**Cause**: Another Streamlit app is running

**Solution**:
```bash
# Kill existing Streamlit process
pkill -f streamlit

# Or use a different port
streamlit run app.py --server.port 8502
```

---

### Issue: Chat history disappears

**Cause**: Browser refresh or session timeout

**Solution**:
- Chat history is session-based (by design)
- Refreshing the page clears history
- To preserve conversations, don't refresh
- Future: Export functionality could be added

---

### Issue: Slow response times

**Cause**: Large knowledge base or complex queries

**Solutions**:
1. Increase timeout in `.env`: `API_TIMEOUT=60`
2. Try simpler queries first
3. Check API server logs for performance issues
4. Consider knowledge base size optimization

---

## Usage Tips

### 💡 Best Practices

**Chat Interface**:
- Start with "Merged" strategy for balanced results
- Use "Semantic" for conceptual questions
- Use "Hybrid" when you need keyword precision
- Keep conversations focused on one topic for better context

**Comparison Mode**:
- Great for understanding your data
- Use to identify optimal strategy for your domain
- Try different query phrasings to see variations
- Note which strategy consistently ranks best content higher

### 🎯 Example Queries to Try

**Conceptual Questions** (try Semantic):
- "What is the main idea of...?"
- "Explain the concept of..."
- "How does X relate to Y?"

**Specific Information** (try Hybrid):
- "What is the definition of...?"
- "List the steps to..."
- "Find information about [specific term]"

**General Exploration** (use Merged):
- "Tell me about..."
- "What can you say about...?"
- "I'm interested in learning about..."

---

## Next Steps

✅ **You're Ready!** You can now:
- Have conversations with your knowledge base
- Compare search strategy effectiveness
- Experiment with different query types

### 📚 Learn More

- **Feature Specification**: See `specs/002-streamlit-web-ui/spec.md`
- **API Documentation**: Visit http://localhost:8000/docs
- **Data Model**: See `specs/002-streamlit-web-ui/data-model.md`

### 🚀 Advanced Usage

**Running in Production** (future):
- Add authentication
- Deploy to cloud (Streamlit Cloud, AWS, etc.)
- Enable SSL/HTTPS
- Add conversation export
- Implement conversation persistence

**Customization**:
- Modify page styling in `.streamlit/config.toml`
- Adjust result display format in page files
- Add custom branding/logos
- Extend with additional pages

---

## Quick Reference

### Commands

```bash
# Start API server
uvicorn api:app --reload

# Start Streamlit UI (default port)
streamlit run app.py

# Start Streamlit UI (custom port)
streamlit run app.py --server.port 8502

# Stop Streamlit
Ctrl+C (in terminal)
```

### URLs

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **Chat Page**: http://localhost:8501/Chat
- **Comparison Page**: http://localhost:8501/Compare

### Environment Variables

```bash
KB_URL=https://your-kb.nuclia.cloud    # Knowledge base URL
KB_API_KEY=your-api-key                # Nuclia API key
API_BASE_URL=http://localhost:8000      # FastAPI service URL
API_TIMEOUT=30                          # Request timeout (seconds)
```

---

## Support

**Common Questions**:
- Check the troubleshooting section above
- Review error messages in the browser
- Check terminal logs for details

**Getting Help**:
- Review feature documentation in `specs/002-streamlit-web-ui/`
- Check API logs in Terminal 1
- Verify environment configuration in `.env`

---

**Happy Searching! 🚀**
