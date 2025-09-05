import os
import requests
import time
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class TranscriptionService:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1/audio/transcriptions"
        self.max_retries = 3
        self.retry_delay = 1
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
    
    def transcribe_audio(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe audio file using Groq Whisper API
        
        Args:
            audio_file_path: Path to audio file (WAV, MP3, etc.)
            
        Returns:
            Transcribed text or None if failed
        """
        if not os.path.exists(audio_file_path):
            print(f"Error: Audio file not found at {audio_file_path}")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        
        for attempt in range(self.max_retries):
            try:
                with open(audio_file_path, 'rb') as audio_file:
                    files = {
                        'file': (os.path.basename(audio_file_path), audio_file, 'audio/wav'),
                        'model': (None, 'whisper-large-v3'),
                        'response_format': (None, 'text')
                    }
                    
                    response = requests.post(
                        self.base_url,
                        headers=headers,
                        files=files,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        transcription = response.text.strip()
                        print(f"Transcription successful: {transcription}")
                        return transcription
                    else:
                        print(f"API Error {response.status_code}: {response.text}")
                        
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1}: {e}")
            except Exception as e:
                print(f"Unexpected error on attempt {attempt + 1}: {e}")
            
            if attempt < self.max_retries - 1:
                print(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                self.retry_delay *= 2  # Exponential backoff
        
        print("All transcription attempts failed")
        return None

def transcribe_file(file_path: str) -> Optional[str]:
    """Convenience function to transcribe a single file"""
    service = TranscriptionService()
    return service.transcribe_audio(file_path)

if __name__ == "__main__":
    # Test with sample audio if it exists
    test_file = "test_data/sample_food_recording.wav"
    if os.path.exists(test_file):
        result = transcribe_file(test_file)
        if result:
            print(f"Test transcription result: {result}")
        else:
            print("Test transcription failed")
    else:
        print(f"Test file {test_file} not found")