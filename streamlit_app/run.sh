#!/bin/bash
# Launch script for Streamlit Web UI

cd "$(dirname "$0")"

echo "Starting Nuclia Search UI..."
echo "URL: http://localhost:8501"
echo ""
echo "Prerequisites:"
echo "  - FastAPI backend must be running at localhost:8000"
echo "  - Run: uvicorn api:app --reload (from project root)"
echo ""

streamlit run app.py
