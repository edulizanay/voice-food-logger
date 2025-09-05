import unittest
from unittest.mock import patch, MagicMock, mock_open
import os
import sys
import json
import tempfile
from datetime import datetime

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from transcription import TranscriptionService
from processing import FoodProcessor
from storage import FoodStorage

class TestIntegration(unittest.TestCase):
    """Integration tests for the complete pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_audio_path = "test_audio.wav"
        self.test_transcription = "I ate 150 grams of grilled chicken breast and half a cup of brown rice"
        self.expected_parsed_data = {
            "items": [
                {"food": "grilled chicken breast", "quantity": "150 grams"},
                {"food": "brown rice", "quantity": "0.5 cup"}
            ]
        }
    
    def tearDown(self):
        """Clean up test fixtures"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('transcription.requests.post')
    @patch('processing.requests.post')
    @patch('transcription.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake audio data")
    def test_complete_pipeline_success(self, mock_file, mock_exists, mock_processing_post, mock_transcription_post):
        """Test the complete pipeline from audio to storage"""
        # Mock transcription API response
        mock_exists.return_value = True
        mock_transcription_response = MagicMock()
        mock_transcription_response.status_code = 200
        mock_transcription_response.text = self.test_transcription
        mock_transcription_post.return_value = mock_transcription_response
        
        # Mock processing API response
        mock_processing_response = MagicMock()
        mock_processing_response.status_code = 200
        mock_processing_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps(self.expected_parsed_data)
                }
            }]
        }
        mock_processing_post.return_value = mock_processing_response
        
        # Initialize services
        transcription_service = TranscriptionService()
        processing_service = FoodProcessor()
        storage_service = FoodStorage(self.temp_dir)
        
        # Step 1: Transcribe audio
        transcription = transcription_service.transcribe_audio(self.test_audio_path)
        self.assertEqual(transcription, self.test_transcription)
        
        # Step 2: Process food description
        parsed_data = processing_service.parse_food_description(transcription)
        self.assertEqual(parsed_data, self.expected_parsed_data)
        
        # Step 3: Store data
        timestamp = datetime(2024, 1, 15, 12, 30, 0)
        success = storage_service.store_food_entry(parsed_data['items'], timestamp)
        self.assertTrue(success)
        
        # Verify stored data
        entries = storage_service.get_daily_entries(timestamp)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]['items'], self.expected_parsed_data['items'])
        self.assertEqual(entries[0]['timestamp'], timestamp.isoformat())
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('transcription.requests.post')
    @patch('transcription.os.path.exists')
    def test_pipeline_transcription_failure(self, mock_exists, mock_transcription_post):
        """Test pipeline behavior when transcription fails"""
        mock_exists.return_value = True
        
        # Mock failed transcription
        mock_transcription_response = MagicMock()
        mock_transcription_response.status_code = 500
        mock_transcription_response.text = "Server error"
        mock_transcription_post.return_value = mock_transcription_response
        
        transcription_service = TranscriptionService()
        transcription = transcription_service.transcribe_audio(self.test_audio_path)
        
        # Should return None on failure
        self.assertIsNone(transcription)
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('processing.requests.post')
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_pipeline_processing_failure(self, mock_file, mock_processing_post):
        """Test pipeline behavior when processing fails"""
        # Mock failed processing
        mock_processing_response = MagicMock()
        mock_processing_response.status_code = 500
        mock_processing_response.text = "Server error"
        mock_processing_post.return_value = mock_processing_response
        
        processing_service = FoodProcessor()
        parsed_data = processing_service.parse_food_description(self.test_transcription)
        
        # Should return None on failure
        self.assertIsNone(parsed_data)
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('transcription.requests.post')
    @patch('processing.requests.post')
    @patch('transcription.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake audio data")
    def test_pipeline_with_invalid_json_response(self, mock_file, mock_exists, mock_processing_post, mock_transcription_post):
        """Test pipeline behavior when LLM returns invalid JSON"""
        # Mock transcription success
        mock_exists.return_value = True
        mock_transcription_response = MagicMock()
        mock_transcription_response.status_code = 200
        mock_transcription_response.text = self.test_transcription
        mock_transcription_post.return_value = mock_transcription_response
        
        # Mock processing with invalid JSON response
        mock_processing_response = MagicMock()
        mock_processing_response.status_code = 200
        mock_processing_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'This is not valid JSON'
                }
            }]
        }
        mock_processing_post.return_value = mock_processing_response
        
        transcription_service = TranscriptionService()
        processing_service = FoodProcessor()
        
        # Transcription should work
        transcription = transcription_service.transcribe_audio(self.test_audio_path)
        self.assertEqual(transcription, self.test_transcription)
        
        # Processing should fail gracefully
        parsed_data = processing_service.parse_food_description(transcription)
        self.assertIsNone(parsed_data)
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('transcription.requests.post')
    @patch('processing.requests.post')
    @patch('transcription.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake audio data")
    def test_end_to_end_with_multiple_food_items(self, mock_file, mock_exists, mock_processing_post, mock_transcription_post):
        """Test pipeline with complex food description containing multiple items"""
        complex_transcription = "For breakfast I had two scrambled eggs, one slice of whole wheat toast with butter, and a glass of orange juice"
        complex_parsed_data = {
            "items": [
                {"food": "scrambled eggs", "quantity": "2 pieces"},
                {"food": "whole wheat toast", "quantity": "1 slice"},
                {"food": "butter", "quantity": "not specified"},
                {"food": "orange juice", "quantity": "1 glass"}
            ]
        }
        
        # Mock transcription
        mock_exists.return_value = True
        mock_transcription_response = MagicMock()
        mock_transcription_response.status_code = 200
        mock_transcription_response.text = complex_transcription
        mock_transcription_post.return_value = mock_transcription_response
        
        # Mock processing
        mock_processing_response = MagicMock()
        mock_processing_response.status_code = 200
        mock_processing_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': json.dumps(complex_parsed_data)
                }
            }]
        }
        mock_processing_post.return_value = mock_processing_response
        
        # Run complete pipeline
        transcription_service = TranscriptionService()
        processing_service = FoodProcessor()
        storage_service = FoodStorage(self.temp_dir)
        
        transcription = transcription_service.transcribe_audio(self.test_audio_path)
        parsed_data = processing_service.parse_food_description(transcription)
        storage_success = storage_service.store_food_entry(parsed_data['items'])
        
        # Verify results
        self.assertEqual(transcription, complex_transcription)
        self.assertEqual(parsed_data, complex_parsed_data)
        self.assertTrue(storage_success)
        
        # Verify storage contains all 4 items
        entries = storage_service.get_daily_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(len(entries[0]['items']), 4)
    
    def test_data_validation_through_pipeline(self):
        """Test that invalid data is caught by validation"""
        storage_service = FoodStorage(self.temp_dir)
        
        # Test with invalid food items structure
        invalid_items = [
            {"name": "chicken", "amount": "150g"},  # Wrong keys
        ]
        
        success = storage_service.store_food_entry(invalid_items)
        self.assertFalse(success)
        
        # Verify no data was stored
        entries = storage_service.get_daily_entries()
        self.assertEqual(len(entries), 0)
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('transcription.requests.post')
    @patch('processing.requests.post') 
    @patch('transcription.os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data=b"fake audio data")
    def test_pipeline_data_persistence(self, mock_file, mock_exists, mock_processing_post, mock_transcription_post):
        """Test that data persists correctly across multiple pipeline runs"""
        # Setup mocks for first entry
        mock_exists.return_value = True
        
        # First entry
        mock_transcription_response1 = MagicMock()
        mock_transcription_response1.status_code = 200
        mock_transcription_response1.text = "I ate an apple"
        
        mock_processing_response1 = MagicMock()
        mock_processing_response1.status_code = 200
        mock_processing_response1.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"items": [{"food": "apple", "quantity": "1 piece"}]}'
                }
            }]
        }
        
        # Second entry
        mock_transcription_response2 = MagicMock()
        mock_transcription_response2.status_code = 200
        mock_transcription_response2.text = "I ate a banana"
        
        mock_processing_response2 = MagicMock()
        mock_processing_response2.status_code = 200
        mock_processing_response2.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"items": [{"food": "banana", "quantity": "1 piece"}]}'
                }
            }]
        }
        
        # Set up mock responses in sequence
        mock_transcription_post.side_effect = [mock_transcription_response1, mock_transcription_response2]
        mock_processing_post.side_effect = [mock_processing_response1, mock_processing_response2]
        
        # Initialize services
        transcription_service = TranscriptionService()
        processing_service = FoodProcessor()
        storage_service = FoodStorage(self.temp_dir)
        
        test_date = datetime(2024, 1, 15, 12, 0, 0)
        
        # Process first entry
        transcription1 = transcription_service.transcribe_audio(self.test_audio_path)
        parsed_data1 = processing_service.parse_food_description(transcription1)
        storage_service.store_food_entry(parsed_data1['items'], test_date)
        
        # Process second entry
        transcription2 = transcription_service.transcribe_audio(self.test_audio_path)
        parsed_data2 = processing_service.parse_food_description(transcription2)
        storage_service.store_food_entry(parsed_data2['items'], test_date.replace(hour=14))
        
        # Verify both entries are persisted
        entries = storage_service.get_daily_entries(test_date)
        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0]['items'][0]['food'], 'apple')
        self.assertEqual(entries[1]['items'][0]['food'], 'banana')

if __name__ == '__main__':
    unittest.main()