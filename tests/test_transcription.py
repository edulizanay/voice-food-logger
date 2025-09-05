import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transcription import TranscriptionService, transcribe_file

class TestTranscriptionService(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_api_key = "test_api_key_123"
        
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    def test_init_with_api_key(self):
        """Test service initialization with API key"""
        service = TranscriptionService()
        self.assertEqual(service.api_key, "test_api_key_123")
        self.assertEqual(service.max_retries, 3)
        self.assertEqual(service.retry_delay, 1)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key(self):
        """Test service initialization without API key"""
        with self.assertRaises(ValueError):
            TranscriptionService()
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('transcription.requests.post')
    @patch('transcription.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake audio data")
    def test_transcribe_audio_success(self, mock_file, mock_exists, mock_post):
        """Test successful audio transcription"""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "I ate chicken and rice"
        mock_post.return_value = mock_response
        
        service = TranscriptionService()
        result = service.transcribe_audio("test_audio.wav")
        
        self.assertEqual(result, "I ate chicken and rice")
        mock_post.assert_called_once()
        mock_file.assert_called_once()
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('transcription.os.path.exists')
    def test_transcribe_audio_file_not_found(self, mock_exists):
        """Test transcription with missing file"""
        mock_exists.return_value = False
        
        service = TranscriptionService()
        result = service.transcribe_audio("nonexistent.wav")
        
        self.assertIsNone(result)
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('transcription.requests.post')
    @patch('transcription.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake audio data")
    def test_transcribe_audio_api_error(self, mock_file, mock_exists, mock_post):
        """Test transcription with API error"""
        mock_exists.return_value = True
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response
        
        service = TranscriptionService()
        result = service.transcribe_audio("test_audio.wav")
        
        self.assertIsNone(result)
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('transcription.requests.post')
    @patch('transcription.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake audio data")
    @patch('transcription.time.sleep')  # Mock sleep to speed up tests
    def test_transcribe_audio_retry_logic(self, mock_sleep, mock_file, mock_exists, mock_post):
        """Test retry logic on request failure"""
        mock_exists.return_value = True
        
        # First two calls fail, third succeeds
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        mock_response_fail.text = "Server error"
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.text = "Success after retry"
        
        mock_post.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        
        service = TranscriptionService()
        result = service.transcribe_audio("test_audio.wav")
        
        self.assertEqual(result, "Success after retry")
        self.assertEqual(mock_post.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)  # Sleep called between retries
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('transcription.TranscriptionService.transcribe_audio')
    def test_convenience_function(self, mock_transcribe):
        """Test the convenience function"""
        mock_transcribe.return_value = "Test result"
        
        result = transcribe_file("test.wav")
        
        self.assertEqual(result, "Test result")
        mock_transcribe.assert_called_once_with("test.wav")

if __name__ == '__main__':
    unittest.main()