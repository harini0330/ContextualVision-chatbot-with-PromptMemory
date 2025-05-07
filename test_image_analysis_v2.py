import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
import sys

# Load environment variables
load_dotenv()

# Get API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
print(f"API Key: {OPENROUTER_API_KEY[:8]}...")

# Initialize client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Function to convert image to base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Test image extraction
def test_image_analysis(image_path):
    try:
        # Check if image exists
        if not os.path.exists(image_path):
            print(f"Error: Test image not found at {image_path}")
            return
        
        print(f"Using test image: {image_path}")
        
        # Convert image to base64
        image_base64 = image_to_base64(image_path)
        print(f"Successfully converted image to base64 (length: {len(image_base64)})")
        
        # Check if the image is too large (OpenRouter might have limits)
        if len(image_base64) > 1000000:  # 1MB
            print("Warning: Image is quite large, which might cause API issues. Consider using a smaller image.")
        
        # Set up site information for API call
        site_url = os.getenv("SITE_URL", "https://image-analysis-chatbot.com")
        site_name = os.getenv("SITE_NAME", "Image Analysis Chatbot")
        
        print("\nSending image to OpenRouter API for analysis...")
        # Make API call to extract image description
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": site_url,
                "X-Title": site_name,
            },
            extra_body={},
            model="google/gemini-2.5-pro-exp-03-25:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe this image briefly."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        )
        
        # Print the raw response for debugging
        print("\nRaw API Response:")
        print(completion)
        
        # Check if completion is None
        if completion is None:
            print("Error: Received None response from API")
            return None
            
        # Check if choices exists and is not None
        if not hasattr(completion, 'choices') or completion.choices is None:
            print("Error: 'choices' attribute is missing or None in the API response")
            return None
            
        # Check if choices is empty
        if len(completion.choices) == 0:
            print("Error: 'choices' array is empty in the API response")
            return None
            
        # Check if message exists
        if not hasattr(completion.choices[0], 'message'):
            print("Error: 'message' attribute is missing in the API response")
            return None
            
        # Check if content exists
        if not hasattr(completion.choices[0].message, 'content'):
            print("Error: 'content' attribute is missing in the API response")
            return None
        
        # Extract the description
        description = completion.choices[0].message.content
        
        # Check if description is None or empty
        if description is None or description.strip() == "":
            print("Error: Received empty description from API")
            return None
            
        print("\nExtracted Image Description:")
        print("-" * 50)
        print(description[:500] + "..." if len(description) > 500 else description)
        print("-" * 50)
        print(f"Total description length: {len(description)} characters")
        
        return description
        
    except Exception as e:
        print("\nError extracting image description:", str(e))
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # Check if image path is provided as command line argument
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        # Use a default image path if none provided
        image_path = r"H:\Nithya Santhosh\pics\college\Birthdays\friend birthday\IMG20230223221643.jpg"
    
    test_image_analysis(image_path) 