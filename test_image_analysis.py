import os
import base64
from openai import OpenAI
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenRouter API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL", "https://your-site-url.com")
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME", "Image Analysis Test")

def test_image_analysis(image_path):
    """
    Test image analysis with Google Gemini model through OpenRouter
    
    Args:
        image_path: Path to the image file to analyze
    """
    print(f"Testing image analysis with file: {image_path}")
    
    # Check if file exists
    if not os.path.exists(image_path):
        print(f"Error: File {image_path} does not exist")
        return
    
    # Read image file and convert to base64
    try:
        with open(image_path, "rb") as f:
            image_content = f.read()
            image_data = base64.b64encode(image_content).decode('utf-8')
            print(f"Successfully read image file ({len(image_content)} bytes)")
    except Exception as e:
        print(f"Error reading image file: {e}")
        return
    
    # Create data URL
    data_url = f"data:image/jpeg;base64,{image_data}"
    
    # Initialize OpenRouter client
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        print("Successfully initialized OpenRouter client")
    except Exception as e:
        print(f"Error initializing OpenRouter client: {e}")
        return
    
    # Test different prompts and parameters
    test_cases = [
        {
            "name": "Standard prompt",
            "prompt": "Describe this image in detail.",
            "model": "google/gemini-2.5-pro-exp-03-25:free",
            "max_tokens": 500,
            "temperature": 0.7
        },
        {
            "name": "Simple prompt",
            "prompt": "What's in this image?",
            "model": "google/gemini-2.5-pro-exp-03-25:free",
            "max_tokens": 300,
            "temperature": 0.5
        },
        {
            "name": "Detailed prompt",
            "prompt": "Please describe this image in detail. Include information about people, objects, settings, colors, and any notable elements.",
            "model": "google/gemini-2.5-pro-exp-03-25:free",
            "max_tokens": 500,
            "temperature": 0.7
        }
    ]
    
    # Run test cases
    for i, test_case in enumerate(test_cases):
        print(f"\n--- Test Case {i+1}: {test_case['name']} ---")
        try:
            print(f"Sending request to OpenRouter API with model: {test_case['model']}")
            
            response = client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": YOUR_SITE_URL,
                    "X-Title": YOUR_SITE_NAME,
                },
                model=test_case['model'],
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": test_case['prompt']
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": data_url
                                }
                            }
                        ]
                    }
                ],
                max_tokens=test_case['max_tokens'],
                temperature=test_case['temperature']
            )
            
            print("Response received from OpenRouter API")
            
            # Check if response has the expected structure
            if response and hasattr(response, 'choices') and len(response.choices) > 0:
                if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                    description = response.choices[0].message.content
                    if description and description.strip():
                        print(f"Success! Received description ({len(description)} chars)")
                        print("First 100 chars of description:")
                        print(description[:100] + "..." if len(description) > 100 else description)
                    else:
                        print("Error: Empty description received")
                else:
                    print("Error: Invalid response format - missing message or content")
                    print(f"Response structure: {response}")
            else:
                print("Error: Invalid response format - missing choices")
                print(f"Response structure: {response}")
                
        except Exception as e:
            print(f"Error in test case: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    # Check if image path is provided as command line argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Use a default image path if none provided
        image_path = r"H:\Nithya Santhosh\pics\college\Birthdays\friend birthday\IMG20230223221643.jpg"
    
    test_image_analysis(image_path) 