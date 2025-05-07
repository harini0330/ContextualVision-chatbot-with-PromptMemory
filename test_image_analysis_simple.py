import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
import sys
from PIL import Image
import io

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

def resize_image(image_path, max_size=(800, 800), quality=85):
    """Resize an image to reduce its file size"""
    try:
        img = Image.open(image_path)
        img.thumbnail(max_size)
        
        # Save to a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        
        return buffer.read()
    except Exception as e:
        print(f"Error resizing image: {e}")
        # Return original image if resize fails
        with open(image_path, "rb") as f:
            return f.read()

def test_simple_image_analysis(image_path):
    try:
        # Check if image exists
        if not os.path.exists(image_path):
            print(f"Error: Test image not found at {image_path}")
            return
        
        print(f"Using test image: {image_path}")
        
        # Resize the image to reduce file size
        image_content = resize_image(image_path)
        image_base64 = base64.b64encode(image_content).decode()
        print(f"Successfully converted image to base64 (length: {len(image_base64)})")
        
        # Set up site information for API call
        site_url = os.getenv("SITE_URL", "https://image-analysis-chatbot.com")
        site_name = os.getenv("SITE_NAME", "Image Analysis Chatbot")
        
        print("\nSending image to OpenRouter API for analysis...")
        # Make API call with a very simple prompt
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": site_url,
                "X-Title": site_name,
            },
            model="google/gemini-2.5-pro-exp-03-25:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "What's in this image?"
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
        
        print("\nRaw API Response:")
        print(completion)
        
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            if hasattr(completion.choices[0], 'message') and hasattr(completion.choices[0].message, 'content'):
                description = completion.choices[0].message.content
                print("\nExtracted Image Description:")
                print("-" * 50)
                print(description)
                print("-" * 50)
                return description
            else:
                print("Error: Missing message or content in response")
        else:
            print("Error: Missing choices in response")
        
        return None
        
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
    
    test_simple_image_analysis(image_path) 