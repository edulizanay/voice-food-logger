# Voice Food Logger

A proof-of-concept voice-based food logging system that lets you speak your food intake and automatically converts it to structured data.

## Features

🎤 **Voice Recording Interface** - iPhone-style circular record button with real-time feedback  
🧠 **AI-Powered Processing** - Uses Groq's Whisper for transcription and LLaMA for food parsing  
📊 **Structured Output** - Converts natural speech into organized food items with quantities  
💾 **Daily Logging** - Stores entries in daily JSON files for easy access  

## Quick Start

### Prerequisites
- Python 3.8+
- Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd voice-food-logger
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up API key**
   ```bash
   # Create .env file with your Groq API key
   echo "GROQ_API_KEY=your_groq_api_key_here" > .env
   ```

4. **Run the application**
   ```bash
   python3 app.py
   ```

5. **Open your browser**
   Navigate to: http://localhost:8080

## Usage

1. **Tap the red record button** 🎤
2. **Speak naturally** - "I ate 150 grams of chicken and half a cup of rice"  
3. **Tap stop** when finished ⏹️
4. **View results** - See parsed food items with quantities

## Example Output

**Speech Input:** "Today I had half a kilo of chicken, 30 grams of whey protein and half a cup of brown rice"

**Structured Output:**
```json
{
  "items": [
    {"food": "chicken breast", "quantity": "0.5 kilogram"},
    {"food": "whey protein", "quantity": "30 grams"}, 
    {"food": "brown rice", "quantity": "0.5 cup"}
  ]
}
```

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: Web Audio API, MediaRecorder
- **AI**: Groq (Whisper + LLaMA)
- **Storage**: Daily JSON files

## Development

This is a local development prototype focused on validating the voice → structured data pipeline. Priority is functionality over polish.
