# Voice Food Logger - Development Context & Plan

## Project Overview
**Goal**: Build a proof-of-concept voice-based food logging system to validate the concept before mobile app development.

**Long-term Vision**: iPhone app where users naturally speak food intake ("I ate 150 grams of chicken and half a cup of rice") and automatically log structured data with macros/calories.

**Current Prototype**: Python Flask web app for local testing - disposable prototype focused on testing the core pipeline.

## Technical Requirements

### Core Pipeline
Audio recording → Whisper transcription (Groq) → LLM processing (Groq) → JSON storage

### Tech Stack
- Python Flask web app
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

## Development Plan & Todo List

### ✅ Completed
- [x] Create GitHub repo and initialize project structure
- [x] Set up configuration files (.env, requirements.txt, .gitignore)
- [x] Create CLAUDE.md with detailed development plan
- [x] Build transcription.py with Groq Whisper integration
- [x] Build processing.py with LLM food parsing
- [x] Build storage.py for JSON file management
- [x] Create Flask app.py with audio upload endpoint

### 🚧 In Progress
- [ ] Create single HTML template with embedded CSS/JS
- [ ] Create simple test files for verification
- [ ] Test complete pipeline with sample audio

### User Input Required At:
1. ✅ **DONE**: Add your GROQ API key to .env file
2. ✅ **READY**: Provide test audio recording (WAV format, food description) 
3. **NEXT**: Test web interface and provide feedback

### Key Features
- Record button with visual feedback (ready/recording/processing states)
- Real-time processing status updates
- Parsed results display
- Error handling with user-friendly messages
- Modular code structure for maintainability

### Testing Strategy
- Simple test files for each module verification
- Integration test for complete pipeline
- Sample audio file for consistent testing
- Basic error handling verification

## Notes
This is a disposable prototype focused on validating the voice → structured food data pipeline. Priority is functionality over polish.



## Examples of implementation of GROQ calls that may be useful:


import os
from groq import Groq

client = Groq()
filename = os.path.dirname(__file__) + "/audio.m4a"

with open(filename, "rb") as file:
    transcription = client.audio.transcriptions.create(
      file=(filename, file.read()),
      model="whisper-large-v3-turbo",
      response_format="verbose_json",
    )
    print(transcription.text)
      


from groq import Groq

client = Groq()
completion = client.chat.completions.create(
    model="qwen/qwen3-32b",
    messages=[
      {
        "role": "user",
        "content": ""
      }
    ],
    temperature=0.6,
    max_completion_tokens=4096,
    top_p=0.95,
    reasoning_effort="default",
    stream=True,
    stop=None
)

for chunk in completion:
    print(chunk.choices[0].delta.content or "", end="")
