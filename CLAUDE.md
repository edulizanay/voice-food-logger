# Voice Food Logger - Development Context & Plan

## Project Overview
**Goal**: Build a proof-of-concept voice-based food logging system to validate the concept before mobile app development.

**Long-term Vision**: iPhone app where users naturally speak food intake ("I ate 150 grams of chicken and half a cup of rice") and automatically log structured data with macros/calories.

**Current Prototype**: Python Flask web app for local testing - disposable prototype focused on testing the core pipeline.

## Technical Requirements

### Core Pipeline
Voice recording → Whisper transcription (Groq) → LLM processing (Groq) → JSON storage

### Tech Stack
- Python Flask web app
- Web Audio API & MediaRecorder for browser recording
- Groq API for Whisper transcription and LLM processing
- Daily JSON file storage
- Single HTML page with embedded CSS/JS
- Local development environment

### Data Structure
Daily JSON files: `logs_YYYY-MM-DD.json`
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "items": [
    {"food": "chicken", "quantity": "150 grams"},
    {"food": "rice", "quantity": "half cup"}
  ]
}
```

### Project Structure
```
voice-food-logger/
├── .env                    # GROQ_API_KEY=your_key_here
├── .gitignore
├── requirements.txt
├── CLAUDE.md               # This file
├── app.py                  # Main Flask application
├── transcription.py        # Groq Whisper API integration
├── processing.py           # LLM food parsing logic
├── storage.py              # JSON file management
├── processing/
│   └── prompts/
│       └── parser.yaml     # LLM prompts for food parsing
├── logs/                   # Daily JSON files storage
│   └── .gitkeep
├── test_data/
│   └── sample_food_recording.wav    # Test audio file
├── templates/
│   └── index.html          # All-in-one: HTML + CSS + JavaScript
└── tests/
    ├── test_transcription.py
    ├── test_processing.py
    ├── test_storage.py
    └── test_integration.py
```

## Development Status

### ✅ Completed
- [x] Create GitHub repo and initialize project structure
- [x] Set up configuration files (.env, requirements.txt, .gitignore)
- [x] Build transcription.py with Groq Whisper integration
- [x] Build processing.py with LLM food parsing
- [x] Build storage.py for JSON file management
- [x] Create Flask app.py with audio upload endpoint
- [x] **Voice Recording Interface** - iPhone-style circular record button
- [x] **Web Audio API Integration** - Browser microphone recording
- [x] **Complete Pipeline** - Voice → transcription → LLM → storage
- [x] **Multi-format Support** - WAV, WebM, MP3, M4A, OGG audio
- [x] **Real-time Feedback** - Pulsing animations, timer, state management
- [x] **Documentation** - README.md with setup and usage instructions

### Key Features
✅ iPhone-style circular record button with pulsing animation  
✅ Real-time recording timer and visual state changes  
✅ Automatic audio processing after recording stops  
✅ Structured food data output with quantities  
✅ Daily JSON file storage with timestamp  
✅ Multi-format audio support (WebM, WAV, MP3, etc.)  
✅ Error handling with user-friendly messages  
✅ Complete test suite for all modules

## Notes
This is a disposable prototype focused on validating the voice → structured food data pipeline. Priority is functionality over polish.

## Usage
1. Run: `python3 app.py`
2. Open: http://localhost:8080  
3. Click record button, speak food description, stop recording
4. View parsed results and stored entries
