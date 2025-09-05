import os
import json
import yaml
import requests
import time
from typing import Optional, Dict, List
from dotenv import load_dotenv

load_dotenv()

class FoodProcessor:
    def __init__(self):
        self.api_key = os.getenv('GROQ_API_KEY')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-70b-versatile"
        self.max_retries = 3
        self.retry_delay = 1
        
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        # Load prompt template
        self.prompt_template = self._load_prompt_template()
    
    def _load_prompt_template(self) -> str:
        """Load the food parsing prompt from YAML file"""
        prompt_path = "processing/prompts/parser.yaml"
        try:
            with open(prompt_path, 'r') as file:
                prompts = yaml.safe_load(file)
                return prompts['food_parsing_prompt']
        except FileNotFoundError:
            print(f"Warning: Prompt file not found at {prompt_path}, using default")
            return self._default_prompt()
        except Exception as e:
            print(f"Error loading prompt: {e}, using default")
            return self._default_prompt()
    
    def _default_prompt(self) -> str:
        """Default prompt if YAML file is not available"""
        return """You are a food logging assistant. Parse the following food description into JSON format.

Extract individual food items with their quantities. Use this format:
{
  "items": [
    {"food": "food_name", "quantity": "amount unit"}
  ]
}

Rules:
- Extract each distinct food item
- Include quantity and unit for each item  
- If no quantity specified, use "not specified"
- Use standardized food names
- Return ONLY valid JSON

Parse this food description:"""

    def parse_food_description(self, description: str) -> Optional[Dict]:
        """
        Parse natural language food description into structured data
        
        Args:
            description: Natural language description of food consumed
            
        Returns:
            Dictionary with parsed food items or None if failed
        """
        if not description or not description.strip():
            print("Error: Empty food description provided")
            return None
        
        prompt = f"{self.prompt_template}\n\n{description}"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    
                    # Try to extract JSON from the response
                    parsed_data = self._extract_json(content)
                    if parsed_data:
                        print(f"Parsing successful: {parsed_data}")
                        return parsed_data
                    else:
                        print(f"Failed to extract valid JSON from response: {content}")
                        
                else:
                    print(f"API Error {response.status_code}: {response.text}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error on attempt {attempt + 1}: {e}")
            except Exception as e:
                print(f"Unexpected error on attempt {attempt + 1}: {e}")
            
            if attempt < self.max_retries - 1:
                print(f"Retrying in {self.retry_delay} seconds...")
                time.sleep(self.retry_delay)
                self.retry_delay *= 2
        
        print("All parsing attempts failed")
        return None
    
    def _extract_json(self, text: str) -> Optional[Dict]:
        """Extract JSON from LLM response text"""
        try:
            # Try to parse the entire response as JSON first
            return json.loads(text)
        except json.JSONDecodeError:
            # Look for JSON block within the text
            start_markers = ['{', '```json\n{']
            end_markers = ['}', '}\n```']
            
            for start_marker in start_markers:
                start_idx = text.find(start_marker)
                if start_idx != -1:
                    for end_marker in end_markers:
                        end_idx = text.rfind(end_marker)
                        if end_idx != -1 and end_idx > start_idx:
                            json_str = text[start_idx:end_idx + 1].replace('```json\n', '').replace('\n```', '')
                            try:
                                return json.loads(json_str)
                            except json.JSONDecodeError:
                                continue
            
            print(f"Could not extract valid JSON from: {text}")
            return None
    
    def validate_parsed_data(self, data: Dict) -> bool:
        """Validate that parsed data has the expected structure"""
        if not isinstance(data, dict):
            return False
        
        if 'items' not in data:
            return False
        
        if not isinstance(data['items'], list):
            return False
        
        for item in data['items']:
            if not isinstance(item, dict):
                return False
            if 'food' not in item or 'quantity' not in item:
                return False
            if not isinstance(item['food'], str) or not isinstance(item['quantity'], str):
                return False
        
        return True

def process_food_text(text: str) -> Optional[Dict]:
    """Convenience function to process food description text"""
    processor = FoodProcessor()
    return processor.parse_food_description(text)

if __name__ == "__main__":
    # Test with sample descriptions
    test_descriptions = [
        "I ate 150 grams of chicken and half a cup of rice",
        "Had two eggs and a banana for breakfast",
        "Ate some pasta with tomato sauce"
    ]
    
    for desc in test_descriptions:
        print(f"\nTesting: {desc}")
        result = process_food_text(desc)
        if result:
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print("Processing failed")