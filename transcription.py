import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def transcribe_file(audio_file_path: str) -> str:
    """
    Transcribe a WAV audio file using Groq Whisper API
    
    Args:
        audio_file_path: Path to WAV audio file
        
    Returns:
        Transcribed text
        
    Raises:
        Exception: If transcription fails
    """
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    if not audio_file_path.lower().endswith('.wav'):
        raise ValueError("Only WAV files are supported")
    
    client = Groq()
    
    with open(audio_file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(audio_file_path), file.read()),
            model="whisper-large-v3-turbo",
            response_format="text",
        )
    
    return transcription.strip()

if __name__ == "__main__":
    test_file = "test_data/sample_food_recording.wav"
    if os.path.exists(test_file):
        try:
            result = transcribe_file(test_file)
            print(f"Transcription: {result}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Test file {test_file} not found")