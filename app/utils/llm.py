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

class StockAnalysisAgent:
    """
    Agent for executing multi-step stock analysis using Gemini LLM
    This follows the pattern from Session3.ipynb
    """
    def __init__(self, max_iterations=5):
        self.max_iterations = max_iterations
        self.system_prompt = ""
        self.current_query = ""
        self.iteration = 0
        self.iteration_results = []
        self.iteration_responses = []
    
    def set_system_prompt(self, system_prompt: str):
        """Set the system prompt for the agent"""
        self.system_prompt = system_prompt
    
    def set_initial_query(self, query: str):
        """Set the initial query"""
        self.current_query = query
    
    async def execute_iteration(self, function_map=None):
        """
        Execute a single iteration of the agent's workflow
        
        Args:
            function_map: Dictionary mapping function names to callables
        
        Returns:
            Response from the LLM or function result
        """
        if self.iteration >= self.max_iterations:
            return "Maximum iterations reached"
        
        self.iteration += 1
        print(f"\n--- Iteration {self.iteration} ---")
        
        # Construct prompt with history if needed
        if len(self.iteration_responses) > 0:
            prompt_context = self.current_query + "\n\n" + "\n".join(self.iteration_responses)
            prompt_context += "\nWhat should I do next?"
        else:
            prompt_context = self.current_query
        
        # Get model's response
        prompt = f"{self.system_prompt}\n\nQuery: {prompt_context}"
        response = await query_llm(prompt)
        
        print(f"LLM Response: {response}")
        
        # Check if it's a function call or final answer
        if function_map and "FUNCTION_CALL:" in response:
            parts = response.split("FUNCTION_CALL:", 1)[1].strip()
            func_name, params = [x.strip() for x in parts.split("|", 1)]
            
            if func_name in function_map:
                result = function_map[func_name](params)
                print(f"  Result: {result}")
                
                # Store the result
                self.iteration_results.append(result)
                self.iteration_responses.append(
                    f"In iteration {self.iteration} you called {func_name} with {params} parameters, "
                    f"and the function returned {result}."
                )
                return result
            else:
                error = f"Function {func_name} not found"
                self.iteration_responses.append(error)
                return error
        
        # If it's not a function call, just return the response
        self.iteration_responses.append(response)
        return response
    
    async def run_until_completion(self, function_map=None, completion_marker="FINAL"):
        """
        Run the agent until completion is reached
        
        Args:
            function_map: Dictionary mapping function names to callables
            completion_marker: String that marks the completion of the workflow
            
        Returns:
            Final result
        """
        while self.iteration < self.max_iterations:
            result = await self.execute_iteration(function_map)
            
            # Check if we've reached completion
            if completion_marker in str(result):
                print("\n=== Agent Execution Complete ===")
                return result
        
        print("\n=== Maximum iterations reached ===")
        return "Maximum iterations reached without completion" 