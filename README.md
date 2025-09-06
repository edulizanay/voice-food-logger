# Voice Food Logger

A proof-of-concept voice-based food logging system that lets you speak your food intake and automatically converts it to structured data.

## Features

🎤 **Voice Recording Interface** - iPhone-style circular record button with real-time feedback  
🧠 **AI-Powered Processing** - Uses Groq's Whisper for transcription and Qwen for food parsing  
🥗 **Nutritional Analysis** - Automatic macro calculations (calories, protein, carbs, fat)  
📊 **Smart Tables** - Clean visualization of nutritional data for each food item  
📈 **Daily Tracking** - Real-time daily macro totals and comprehensive summaries  
💾 **Enhanced Storage** - Stores entries with complete nutritional data in daily JSON files  

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

**Structured Output with Nutrition:**
```json
{
  "entries": [
    {
      "timestamp": "2025-09-06T10:30:00Z",
      "items": [
        {
          "food": "chicken breast",
          "quantity": "0.5 kilogram",
          "macros": {
            "calories": 825,
            "protein_g": 155.0,
            "carbs_g": 0,
            "fat_g": 18.0
          }
        },
        {
          "food": "whey protein",
          "quantity": "30 grams",
          "macros": {
            "calories": 36,
            "protein_g": 7.5,
            "carbs_g": 0.9,
            "fat_g": 0.3
          }
        },
        {
          "food": "brown rice",
          "quantity": "0.5 cup",
          "macros": {
            "calories": 56,
            "protein_g": 1.3,
            "carbs_g": 11.0,
            "fat_g": 0.45
          }
        }
      ]
    }
  ],
  "daily_macros": {
    "calories": 917,
    "protein_g": 163.8,
    "carbs_g": 11.9,
    "fat_g": 18.75
  }
}
```

## Tech Stack

- **Backend**: Python Flask
- **Frontend**: Web Audio API, MediaRecorder
- **AI**: Groq (Whisper + Qwen)
- **Nutrition**: Mock database with macro calculations
- **Storage**: Enhanced daily JSON files with nutritional data

## Development

This is a local development prototype focused on validating the voice → structured data pipeline. Priority is functionality over polish.
