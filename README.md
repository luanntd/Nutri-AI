# Nutri AI

An AI-powered healthy food recommendation app with multiple frontend options.

## Features

- Calculate daily calorie needs based on personal info
- AI-powered meal portion adjustments
- Budget-optimized menu creation
- Beautiful, responsive UI

## Setup

### Backend

1. Navigate to backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Get Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey)

4. Add your API key to `backend/.env`:
   ```
   GEMINI_API_KEY=your_actual_api_key
   ```

5. Run the backend:
   ```bash
   uvicorn main:app --reload
   ```

## Frontend Options

Choose the frontend that best fits your needs:

### Option 1: Streamlit (Recommended for Quick Start) 🚀

**Perfect for**: Rapid prototyping, Python developers, data-focused apps

1. Install Streamlit (already included in requirements.txt)
2. Run Streamlit app:
   ```bash
   cd backend
   ./run_streamlit.sh
   ```
3. Open http://127.0.0.1:8501

**Pros**: ⚡ Fast setup, 🐍 Python-native, 🎨 Beautiful UI
**Cons**: 🎛️ Less customizable than React

### Option 2: React (Full Control) ⚛️

**Perfect for**: Production apps, custom UI/UX, JavaScript developers

1. Install Node.js from [nodejs.org](https://nodejs.org/)

2. Navigate to frontend directory:
   ```bash
   cd frontend
   ```

3. Install dependencies:
   ```bash
   npm install
   ```

4. Run the frontend:
   ```bash
   npm run dev
   ```

5. Open http://localhost:5173 in your browser

**Pros**: 🎨 Full customization, 🚀 Production-ready, 📱 Mobile-friendly
**Cons**: 🕐 Longer setup, 📚 JavaScript knowledge required

## Usage

1. Enter your personal information
2. Choose meals and get AI recommendations for portions
3. Or enter budget to get optimized daily menu
4. Enjoy healthy eating!

## Tech Stack

- Backend: FastAPI, Python
- Frontend Options:
  - Streamlit (Python-based, quick setup)
  - React + Vite (JavaScript, full control)
- AI: Google Gemini API

## Comparison

| Feature | Streamlit | React |
|---------|-----------|-------|
| Setup Time | ⚡ 2 minutes | 🕐 10-15 minutes |
| Customization | 🎨 Good | 🎨 Excellent |
| Learning Curve | 📚 Easy | 📚 Moderate |
| Best For | Prototyping, Python devs | Production, JS devs |
| UI Flexibility | 🎯 Pre-built components | 🛠️ Full control |