import google.generativeai as genai
from app.utils.config import GOOGLE_API_KEY

# Configure the Gemini API
genai.configure(api_key=GOOGLE_API_KEY)

# Initialize the model
model = genai.GenerativeModel("gemini-pro")

async def query_llm(prompt: str) -> str:
    """
    Send a query to the Gemini LLM and get the response
    
    Args:
        prompt: The prompt to send to the LLM
        
    Returns:
        The LLM's response as a string
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error querying LLM: {e}")
        return f"Error: {str(e)}" 