import os
import json
import yaml
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def _load_prompt() -> str:
    """Load the food parsing prompt from YAML file"""
    prompt_path = "processing/prompts/parser.yaml"
    with open(prompt_path, 'r') as file:
        prompts = yaml.safe_load(file)
        return prompts['food_parsing_prompt']

def process_food_text(text: str) -> dict:
    """
    Parse natural language food description into structured data
    
    Args:
        text: Natural language description of food consumed
        
    Returns:
        Dictionary with parsed food items
        
    Raises:
        Exception: If processing fails
    """
    if not text or not text.strip():
        raise ValueError("Empty food description provided")
    
    prompt = _load_prompt()
    client = Groq()
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "user",
                "content": f"{prompt}\n\n{text}"
            }
        ],
        temperature=0.1,
        max_tokens=500
    )
    
    response_text = completion.choices[0].message.content.strip()
    
    # Parse JSON from response
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        # Try to extract JSON from response if wrapped in text
        start = response_text.find('{')
        end = response_text.rfind('}') + 1
        if start != -1 and end != 0:
            json_str = response_text[start:end]
            return json.loads(json_str)
        else:
            raise ValueError(f"Could not parse JSON from response: {response_text}")

if __name__ == "__main__":
    test_descriptions = [
        "I ate 150 grams of chicken and half a cup of rice",
        "Had two eggs and a banana for breakfast"
    ]
    
    for desc in test_descriptions:
        try:
            result = process_food_text(desc)
            print(f"Input: {desc}")
            print(f"Output: {json.dumps(result, indent=2)}")
            print()
        except Exception as e:
            print(f"Error processing '{desc}': {e}")
            print()