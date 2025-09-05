import unittest
from unittest.mock import patch, mock_open, MagicMock
import os
import sys
import json

# Add parent directory to path to import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from processing import FoodProcessor, process_food_text

class TestFoodProcessor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_api_key = "test_api_key_123"
        self.sample_yaml_content = """
food_parsing_prompt: |
  You are a food logging assistant. Parse the following food description into JSON format.
  Return only valid JSON with this structure: {"items": [{"food": "name", "quantity": "amount"}]}
"""
        
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('builtins.open', new_callable=mock_open, read_data='food_parsing_prompt: "Test prompt"')
    @patch('processing.yaml.safe_load')
    def test_init_with_yaml_file(self, mock_yaml, mock_file):
        """Test service initialization with YAML prompt file"""
        mock_yaml.return_value = {'food_parsing_prompt': 'Test prompt from YAML'}
        
        processor = FoodProcessor()
        
        self.assertEqual(processor.api_key, "test_api_key_123")
        self.assertEqual(processor.prompt_template, 'Test prompt from YAML')
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_init_without_yaml_file(self, mock_file):
        """Test service initialization without YAML file falls back to default"""
        processor = FoodProcessor()
        
        self.assertEqual(processor.api_key, "test_api_key_123")
        self.assertIn("You are a food logging assistant", processor.prompt_template)
    
    @patch.dict(os.environ, {}, clear=True)
    def test_init_without_api_key(self):
        """Test service initialization without API key"""
        with self.assertRaises(ValueError):
            FoodProcessor()
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('processing.requests.post')
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_parse_food_description_success(self, mock_file, mock_post):
        """Test successful food description parsing"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"items": [{"food": "chicken breast", "quantity": "150 grams"}]}'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        processor = FoodProcessor()
        result = processor.parse_food_description("I ate 150 grams of chicken")
        
        expected = {"items": [{"food": "chicken breast", "quantity": "150 grams"}]}
        self.assertEqual(result, expected)
        mock_post.assert_called_once()
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_parse_empty_description(self, mock_file):
        """Test parsing empty description"""
        processor = FoodProcessor()
        
        result = processor.parse_food_description("")
        self.assertIsNone(result)
        
        result = processor.parse_food_description("   ")
        self.assertIsNone(result)
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('processing.requests.post')
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_parse_food_description_api_error(self, mock_file, mock_post):
        """Test parsing with API error"""
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.text = "Bad request"
        mock_post.return_value = mock_response
        
        processor = FoodProcessor()
        result = processor.parse_food_description("I ate chicken")
        
        self.assertIsNone(result)
    
    def test_extract_json_simple(self):
        """Test JSON extraction from simple text"""
        processor = FoodProcessor.__new__(FoodProcessor)  # Create without __init__
        
        # Test direct JSON
        text = '{"items": [{"food": "chicken", "quantity": "150g"}]}'
        result = processor._extract_json(text)
        expected = {"items": [{"food": "chicken", "quantity": "150g"}]}
        self.assertEqual(result, expected)
    
    def test_extract_json_with_markdown(self):
        """Test JSON extraction from markdown code block"""
        processor = FoodProcessor.__new__(FoodProcessor)
        
        # Test JSON in markdown code block
        text = '''```json
{"items": [{"food": "chicken", "quantity": "150g"}]}
```'''
        result = processor._extract_json(text)
        expected = {"items": [{"food": "chicken", "quantity": "150g"}]}
        self.assertEqual(result, expected)
    
    def test_extract_json_invalid(self):
        """Test JSON extraction from invalid JSON"""
        processor = FoodProcessor.__new__(FoodProcessor)
        
        text = "This is not JSON at all"
        result = processor._extract_json(text)
        self.assertIsNone(result)
    
    def test_validate_parsed_data_valid(self):
        """Test validation of correctly formatted data"""
        processor = FoodProcessor.__new__(FoodProcessor)
        
        valid_data = {
            "items": [
                {"food": "chicken", "quantity": "150g"},
                {"food": "rice", "quantity": "1 cup"}
            ]
        }
        
        self.assertTrue(processor.validate_parsed_data(valid_data))
    
    def test_validate_parsed_data_invalid(self):
        """Test validation of incorrectly formatted data"""
        processor = FoodProcessor.__new__(FoodProcessor)
        
        # Missing 'items' key
        invalid_data1 = {"foods": [{"food": "chicken", "quantity": "150g"}]}
        self.assertFalse(processor.validate_parsed_data(invalid_data1))
        
        # Items is not a list
        invalid_data2 = {"items": "not a list"}
        self.assertFalse(processor.validate_parsed_data(invalid_data2))
        
        # Missing required keys in item
        invalid_data3 = {"items": [{"food": "chicken"}]}  # Missing quantity
        self.assertFalse(processor.validate_parsed_data(invalid_data3))
        
        # Wrong data types
        invalid_data4 = {"items": [{"food": 123, "quantity": "150g"}]}
        self.assertFalse(processor.validate_parsed_data(invalid_data4))
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('processing.requests.post')
    @patch('builtins.open', side_effect=FileNotFoundError)
    @patch('processing.time.sleep')
    def test_retry_logic(self, mock_sleep, mock_file, mock_post):
        """Test retry logic on request failure"""
        # First two calls fail, third succeeds
        mock_response_fail = MagicMock()
        mock_response_fail.status_code = 500
        mock_response_fail.text = "Server error"
        
        mock_response_success = MagicMock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"items": [{"food": "chicken", "quantity": "150g"}]}'
                }
            }]
        }
        
        mock_post.side_effect = [mock_response_fail, mock_response_fail, mock_response_success]
        
        processor = FoodProcessor()
        result = processor.parse_food_description("I ate chicken")
        
        expected = {"items": [{"food": "chicken", "quantity": "150g"}]}
        self.assertEqual(result, expected)
        self.assertEqual(mock_post.call_count, 3)
        self.assertEqual(mock_sleep.call_count, 2)
    
    @patch.dict(os.environ, {'GROQ_API_KEY': 'test_api_key_123'})
    @patch('processing.FoodProcessor.parse_food_description')
    def test_convenience_function(self, mock_parse):
        """Test the convenience function"""
        mock_parse.return_value = {"items": [{"food": "test", "quantity": "1"}]}
        
        result = process_food_text("test description")
        
        expected = {"items": [{"food": "test", "quantity": "1"}]}
        self.assertEqual(result, expected)
        mock_parse.assert_called_once_with("test description")

if __name__ == '__main__':
    unittest.main()