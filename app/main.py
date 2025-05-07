from fastapi import FastAPI, Request, Form, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Dict, List, Optional
import base64
import uuid
import os
from openai import OpenAI
from dotenv import load_dotenv
import json
from pathlib import Path
from PIL import Image
import io

load_dotenv()

# OpenRouter API key - try to load from environment first, then use hardcoded value as fallback
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "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")
YOUR_SITE_URL = os.getenv("YOUR_SITE_URL", "https://your-site-url.com")  # Replace with your actual site URL
YOUR_SITE_NAME = os.getenv("YOUR_SITE_NAME", "Image Analysis Chatbot")  # Replace with your site name

# Print API key status for debugging (don't print the actual key)
if OPENROUTER_API_KEY:
    print("OpenRouter API key is set")
else:
    print("WARNING: OpenRouter API key is not set")

app = FastAPI(root_path="/app")

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Mount static files with the correct path
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# Create a directory for storing chat history
CHAT_HISTORY_DIR = os.path.join(BASE_DIR, "chat_history")
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

# Add this near the top of your file with other directory definitions
IMAGE_STORAGE_DIR = os.path.join(BASE_DIR, "image_storage")
os.makedirs(IMAGE_STORAGE_DIR, exist_ok=True)

# Update the chat sessions initialization to load from disk
chat_sessions = {}

# Temporary in-memory storage for images (will be lost on restart)
image_storage = {}

# Load existing chat sessions from disk
def load_chat_sessions():
    global chat_sessions
    if os.path.exists(CHAT_HISTORY_DIR):
        for chat_file in os.listdir(CHAT_HISTORY_DIR):
            if chat_file.endswith('.json'):
                chat_id = chat_file[:-5]  # Remove .json extension
                file_path = os.path.join(CHAT_HISTORY_DIR, chat_file)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        chat_data = json.load(f)
                        # Ensure all required fields exist
                        if "messages" not in chat_data:
                            chat_data["messages"] = []
                        if "image_uploaded" not in chat_data:
                            chat_data["image_uploaded"] = False
                        if "image_description" not in chat_data:
                            chat_data["image_description"] = None
                        if "image_path" not in chat_data:
                            chat_data["image_path"] = None
                        
                        chat_sessions[chat_id] = chat_data
                        
                        # If this chat has an image, try to preload it into memory
                        if chat_data["image_uploaded"] and chat_data["image_path"]:
                            image_path = os.path.join(IMAGE_STORAGE_DIR, chat_data["image_path"])
                            if os.path.exists(image_path):
                                try:
                                    with open(image_path, "rb") as img_file:
                                        image_content = img_file.read()
                                        image_storage[chat_id] = base64.b64encode(image_content).decode("utf-8")
                                except Exception as img_err:
                                    print(f"Error loading image for chat {chat_id}: {img_err}")
                        
                        print(f"Loaded chat session: {chat_id}")
                except Exception as e:
                    print(f"Error loading chat session {chat_id}: {e}")

# Save a chat session to disk
def save_chat_session(chat_id):
    if chat_id in chat_sessions:
        file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
        try:
            with open(file_path, 'w') as f:
                json.dump(chat_sessions[chat_id], f)
        except Exception as e:
            print(f"Error saving chat session {chat_id}: {e}")

# Add this function to migrate existing chat sessions
def migrate_existing_chat_sessions():
    for chat_id, session in chat_sessions.items():
        # Check if this chat has an image uploaded but no image_path
        if session.get("image_uploaded", False) and (
            "image_path" not in session or session["image_path"] is None
        ):
            # Set the image path to the chat_id.jpg
            session["image_path"] = f"{chat_id}.jpg"
            # Save the updated session
            save_chat_session(chat_id)
            print(f"Migrated chat session {chat_id} to include image_path")

# Call this function after loading chat sessions
load_chat_sessions()
migrate_existing_chat_sessions()
print(f"Loaded {len(chat_sessions)} chat sessions from disk")

@app.get("/", response_class=HTMLResponse)
async def get_root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.post("/create_chat")
async def create_chat():
    chat_id = str(uuid.uuid4())
    
    # Create a new chat session with a default name
    chat_sessions[chat_id] = {
        "messages": [],
        "image_uploaded": False,
        "image_description": None,
        "image_path": None,
        "name": f"Chat {len(chat_sessions) + 1}"
    }
    
    # Save to disk
    save_chat_session(chat_id)
    
    return {"chat_id": chat_id}

@app.post("/upload_image/{chat_id}")
async def upload_image(chat_id: str, file: UploadFile = File(...)):
    try:
        # Check if chat exists
        if chat_id not in chat_sessions:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Check file type
        if not file.content_type.startswith('image/'):
            return {"success": False, "error": "Uploaded file is not an image"}
        
        # Read file content
        contents = await file.read()
        
        # Check file size (limit to 5MB)
        if len(contents) > 5 * 1024 * 1024:
            return {"success": False, "error": "Image size exceeds 5MB limit"}
        
        # Resize the image to reduce file size
        resized_contents = resize_image(contents)
        
        # Save the image to disk
        filename = f"{uuid.uuid4()}.jpg"
        file_path = os.path.join(IMAGE_STORAGE_DIR, filename)
        
        with open(file_path, "wb") as f:
            f.write(resized_contents)
        
        # Update chat session
        chat_sessions[chat_id]["image_uploaded"] = True
        chat_sessions[chat_id]["image_path"] = filename
        
        # Convert image to base64 for frontend
        image_data = base64.b64encode(resized_contents).decode('utf-8')
        
        # Get image description using OpenRouter with Gemini
        try:
            # Use OpenRouter client instead of OpenAI
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=OPENROUTER_API_KEY,
            )
            
            # Ensure API key is available
            if not OPENROUTER_API_KEY:
                initial_message = "Image uploaded successfully, but API key is missing. Please set OPENROUTER_API_KEY in your environment variables."
                chat_sessions[chat_id]["image_description"] = "No description available (API key missing)"
            else:
                # Create a data URL for the image
                data_url = f"data:image/jpeg;base64,{image_data}"
                
                print(f"Sending image to OpenRouter API with model: meta-llama/llama-4-maverick:free")
                
                # Use the working method for image analysis
                response = client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": YOUR_SITE_URL,
                        "X-Title": YOUR_SITE_NAME,
                    },
                    model="meta-llama/llama-4-maverick:free",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Analyze this image in detail. Describe what you see including objects, people, setting, colors, and any notable elements."
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": data_url
                                    }
                                }
                            ]
                        }
                    ]
                )
                
                # Extract description with proper error handling
                if hasattr(response, 'choices') and len(response.choices) > 0:
                    if hasattr(response.choices[0], 'message') and hasattr(response.choices[0].message, 'content'):
                        description = response.choices[0].message.content
                        if description and description.strip():
                            # Store the description for analysis but don't add to chat
                            chat_sessions[chat_id]["image_description"] = description
                            
                            # Set a simple initial message that doesn't include the analysis
                            initial_message = "I've received your image. What would you like to know about it?"
                            
                            # Add to chat history
                            chat_sessions[chat_id]["messages"].append({
                                "role": "assistant",
                                "content": initial_message
                            })
                        else:
                            raise ValueError("Empty description received from API")
                    else:
                        raise ValueError("Invalid response format: missing message or content")
                else:
                    raise ValueError("Invalid response format: missing choices")
        except Exception as e:
            print(f"Error analyzing image: {str(e)}")
            print(f"Error type: {type(e)}")
            import traceback
            traceback.print_exc()
            initial_message = "Image uploaded successfully. What would you like to know about it?"
            chat_sessions[chat_id]["image_description"] = "Error during analysis"
            
            # Add to chat history
            chat_sessions[chat_id]["messages"].append({
                "role": "assistant",
                "content": initial_message
            })
        
        # Save chat session
        save_chat_session(chat_id)
        
        return {
            "success": True, 
            "image_data": image_data,
            "initial_message": initial_message
        }
    
    except Exception as e:
        print(f"Error in upload_image: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

@app.post("/send_message/{chat_id}")
async def send_message(chat_id: str, message: str = Form(...)):
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    if not chat_sessions[chat_id]["image_uploaded"]:
        return {"response": "Please upload an image first before asking questions."}
    
    # Add user message to chat history
    chat_sessions[chat_id]["messages"].append({
        "role": "user",
        "content": message
    })
    
    # Get image description
    image_description = chat_sessions[chat_id]["image_description"]
    
    # Generate response based on the image description and user question
    response = await generate_response(message, image_description, chat_sessions[chat_id]["messages"], chat_id)
    
    # Add assistant response to chat history
    chat_sessions[chat_id]["messages"].append({
        "role": "assistant",
        "content": response
    })
    
    # After adding the response to chat history
    save_chat_session(chat_id)
    
    return {"response": response}

async def generate_response(question: str, image_description: str, chat_history: List[Dict], chat_id: str):
    try:
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=OPENROUTER_API_KEY,
        )
        
        # Implement RAG by using the image description as the knowledge base
        messages = [
            {
                "role": "system",
                "content": f"""You are an AI assistant specialized in answering questions about images. 
                You have been provided with a detailed description of an image, and your task is to answer 
                questions about that image based ONLY on the information in the description.
                
                Here is the detailed description of the image:
                {image_description}
                
                Important rules:
                1. Only answer questions related to the image description provided.
                2. If the question cannot be answered based on the image description, politely explain that 
                   the information is not available in the image description.
                3. Do not make up or infer information that is not explicitly stated in the description.
                4. If the question is completely unrelated to the image, politely redirect the user to ask 
                   questions about the image.
                5. Be extremely concise and direct in your answers - provide only the specific information asked for.
                6. Do not provide additional context or information beyond what was specifically requested.
                7. For counting questions (how many X), just give the number or a very brief answer.
                8. Do not repeat the question in your answer.
                9. Do not list additional details or explanations unless specifically asked.
                10. Keep your answers precise and to the point."""
            }
        ]
        
        # Add relevant chat history
        relevant_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        for msg in relevant_history:
            if msg["role"] != "system":  # Skip system messages
                messages.append({"role": msg["role"], "content": msg["content"]})
        
        # Add the current question
        messages.append({"role": "user", "content": question})
        
        # Generate response based on the retrieved knowledge
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            },
            model="meta-llama/llama-4-maverick:free",
            messages=messages,
            temperature=0.3  # Lower temperature for more focused responses
        )
        
        # Return the generated response
        if completion and hasattr(completion, 'choices') and len(completion.choices) > 0:
            if hasattr(completion.choices[0], 'message') and hasattr(completion.choices[0].message, 'content'):
                return completion.choices[0].message.content
            else:
                raise ValueError("Invalid response format: missing message or content")
        else:
            raise ValueError("Invalid response format: missing choices")
    except Exception as e:
        print(f"Error generating response: {e}")
        import traceback
        traceback.print_exc()
        return "I'm sorry, I couldn't process your question. Please try again."

# Add a new function to analyze an image with a specific question
async def analyze_image_with_question(base64_image: str, question: str):
    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=OPENROUTER_API_KEY,
    )
    
    # Create a data URL for the image
    data_url = f"data:image/jpeg;base64,{base64_image}"
    
    try:
        completion = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": YOUR_SITE_URL,
                "X-Title": YOUR_SITE_NAME,
            },
            model="meta-llama/llama-4-maverick:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Please look at this image and answer the following question: {question}"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": data_url
                            }
                        }
                    ]
                }
            ]
        )
        
        # Extract response with proper error handling
        if hasattr(completion, 'choices') and len(completion.choices) > 0:
            if hasattr(completion.choices[0], 'message') and hasattr(completion.choices[0].message, 'content'):
                return completion.choices[0].message.content
            else:
                raise ValueError("Invalid response format: missing message or content")
        else:
            raise ValueError("Invalid response format: missing choices")
    except Exception as e:
        print(f"Error analyzing image with question: {e}")
        import traceback
        traceback.print_exc()
        return "Failed to analyze the image with your specific question. Please try again."

@app.get("/get_chat_history/{chat_id}")
async def get_chat_history(chat_id: str):
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Filter out system messages for the frontend
    messages = [msg for msg in chat_sessions[chat_id]["messages"] if msg["role"] != "system"]
    
    return {
        "messages": messages,
        "image_uploaded": chat_sessions[chat_id]["image_uploaded"]
    }

@app.get("/get_analysis/{chat_id}")
async def get_analysis(chat_id: str):
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    if not chat_sessions[chat_id]["image_uploaded"]:
        return {"analysis": "No image has been uploaded yet."}
    
    return {"analysis": chat_sessions[chat_id]["image_description"]}

@app.get("/get_all_chats")
async def get_all_chats():
    # Make sure chat sessions are loaded
    if not chat_sessions:
        load_chat_sessions()
    
    chats = []
    for chat_id in chat_sessions:
        chats.append({
            "id": chat_id,
            "has_image": chat_sessions[chat_id]["image_uploaded"],
            "name": chat_sessions[chat_id].get("name", f"Chat {len(chats) + 1}")
        })
    
    return {"chats": chats}

# Update the get_image endpoint to use our temporary storage
@app.get("/get_image/{chat_id}")
async def get_image(chat_id: str):
    # First check in-memory storage (faster)
    if chat_id in image_storage:
        return {"image_data": image_storage[chat_id]}
    
    # Then check if we have it on disk
    if chat_id in chat_sessions and chat_sessions[chat_id]["image_uploaded"]:
        # Get the image path from the chat session
        if "image_path" in chat_sessions[chat_id] and chat_sessions[chat_id]["image_path"] is not None:
            image_path = os.path.join(IMAGE_STORAGE_DIR, chat_sessions[chat_id]["image_path"])
            if os.path.exists(image_path):
                # Read the image and convert to base64
                with open(image_path, "rb") as f:
                    image_content = f.read()
                    base64_image = base64.b64encode(image_content).decode("utf-8")
                    
                    # Store in memory for faster access next time
                    image_storage[chat_id] = base64_image
                    
                    return {"image_data": base64_image}
    
    # If we couldn't find the image
    return {"image_data": None}

@app.get("/images/{image_id}")
async def get_image_file(image_id: str):
    image_path = os.path.join(IMAGE_STORAGE_DIR, f"{image_id}.jpg")
    if os.path.exists(image_path):
        return FileResponse(image_path)
    raise HTTPException(status_code=404, detail="Image not found")

@app.get("/app", response_class=HTMLResponse)
async def get_app(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/rename_chat/{chat_id}")
async def rename_chat(chat_id: str, data: dict):
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    if "name" not in data or not data["name"]:
        raise HTTPException(status_code=400, detail="Name is required")
    
    # Update the chat name in memory
    chat_sessions[chat_id]["name"] = data["name"]
    
    # Save the updated chat to disk
    save_chat_session(chat_id)
    
    return {"success": True}

@app.delete("/delete_chat/{chat_id}")
async def delete_chat(chat_id: str):
    if chat_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Chat session not found")
    
    # Remove from memory
    del chat_sessions[chat_id]
    
    # Remove from disk
    file_path = os.path.join(CHAT_HISTORY_DIR, f"{chat_id}.json")
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove associated image if exists
    if "image_path" in chat_sessions.get(chat_id, {}) and chat_sessions[chat_id]["image_path"]:
        image_path = os.path.join(IMAGE_STORAGE_DIR, chat_sessions[chat_id]["image_path"])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    return {"success": True}

# Add the image resizing function to the main application
def resize_image(image_content, max_size=(800, 800), quality=85):
    """Resize an image to reduce its file size"""
    try:
        # Load image from bytes
        img = Image.open(io.BytesIO(image_content))
        img.thumbnail(max_size)
        
        # Save to a bytes buffer
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality)
        buffer.seek(0)
        
        return buffer.read()
    except Exception as e:
        print(f"Error resizing image: {e}")
        # Return original image if resize fails
        return image_content

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8080) 