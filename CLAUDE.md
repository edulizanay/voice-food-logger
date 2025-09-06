# Voice Food Logger - Development Context & Plan

## Project Overview
**Goal**: Build a proof-of-concept voice-based food logging system to validate the concept before mobile app development.

**Long-term Vision**: iPhone app where users naturally speak food intake ("I ate 150 grams of chicken and half a cup of rice") and automatically log structured data with macros/calories.

**Current Prototype**: Python Flask web app for local testing - disposable prototype focused on testing the core pipeline.

## Technical Requirements

### Core Pipeline
Voice recording → Whisper transcription (Groq) → LLM parsing (Groq) → **Nutritional lookup** → JSON storage

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
  "entries": [
    {
      "timestamp": "2025-09-06T10:30:00Z",
      "items": [
        {
          "food": "chicken breast",
          "quantity": "150 grams",
          "macros": {
            "calories": 248,
            "protein_g": 46.5,
            "carbs_g": 0,
            "fat_g": 5.4
          }
        },
        {
          "food": "rice", 
          "quantity": "0.5 cup",
          "macros": {
            "calories": 98,
            "protein_g": 2.0,
            "carbs_g": 21.0,
            "fat_g": 0.2
          }
        }
      ]
    }
  ],
  "daily_macros": {
    "calories": 346,
    "protein_g": 48.5,
    "carbs_g": 21.0,
    "fat_g": 5.6
  }
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
├── data/
│   └── nutrition_db.json   # Mock nutritional database
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
    ├── test_nutrition.py      # Phase 2 nutrition tests
    └── test_integration.py
```

## Development Status

### ✅ Phase 1: Core Voice Logging (COMPLETED)
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
- [x] **Real-time Feedback** - Timer, state management
- [x] **Documentation** - README.md with setup and usage instructions

### ✅ Phase 2: Nutritional Data & Daily Tracking (COMPLETED)
- [x] **Mock Nutritional Database** - `data/nutrition_db.json` with 13 common foods
- [x] **Enhanced Processing** - Nutrition lookup with fuzzy matching & unit conversion
- [x] **Macro Calculations** - Backend calculations for calories, protein, carbs, fat
- [x] **Enhanced Storage** - Store individual item macros + daily totals
- [x] **Table-Style UI** - Macro tables for each food item
- [x] **Daily Summary** - Prominent daily macro totals display
- [x] **Comprehensive Tests** - `test_nutrition.py` with 5/5 tests passing
- [x] **Streamlined Frontend** - Reduced from 626 to 463 lines while keeping functionality

### Key Features
✅ **Voice Recording** - iPhone-style circular record button  
✅ **Smart Food Parsing** - Natural language → structured data  
✅ **Nutritional Lookup** - Backend macro calculations with unit conversion  
✅ **Daily Tracking** - Individual item macros + daily totals  
✅ **Table Display** - Clean macro visualization (calories, protein, carbs, fat)  
✅ **Multi-format Audio** - WebM, WAV, MP3, M4A, OGG support  
✅ **Real-time Feedback** - Recording timer, processing states  
✅ **Comprehensive Testing** - Full test suite including nutrition tests

## Notes
This is a disposable prototype focused on validating the voice → structured food data pipeline. Priority is functionality over polish.

## Usage
1. Run: `python3 app.py`
2. Open: http://localhost:8080  
3. Click record button, speak food description, stop recording
4. View parsed results and stored entries
