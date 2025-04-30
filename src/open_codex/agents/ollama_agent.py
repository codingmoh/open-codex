from typing import List, Dict
import logging
import ollama

from open_codex.interfaces.llm_agent import LLMAgent

# Configure logger
logger = logging.getLogger(__name__)

class OllamaAgent(LLMAgent):
    """
    Agent that connects to Ollama to access local language models 
    using the official Python client.
    """
    
    def __init__(self, 
                 system_prompt: str,
                 model_name: str,
                 host: str,
                 temperature: float = 0.2,
                 max_tokens: int = 500):
        """
        Initialize the Ollama agent.
        
        Args:
            system_prompt: The system prompt to use for generating responses
            model_name: The name of the model to use (default: "llama3")
            host: The host URL of the Ollama API (default: None, uses OLLAMA_HOST env var or http://localhost:11434)
            temperature: The temperature to use for generation (default: 0.2)
            max_tokens: The maximum number of tokens to generate (default: 500)
        """
        self.system_prompt = system_prompt
        self.model_name = model_name
        self.host = host

        self.temperature = temperature
        self.max_tokens = max_tokens
        self._ollama_client = ollama.Client(host=self.host)
    
    def _check_ollama_available(self) -> None:
        """Check if Ollama server is available and the model exists."""
        try:
            # List models to check connection
            models: ollama.ListResponse = self._ollama_client.list()
            
            available_models = [model.model for model in models.models if model.model is not None]
            
            if not available_models:
                logger.error(f"No models found in Ollama. You may need to pull the model with: ollama pull {self.model_name}")
            elif self.model_name not in available_models:
                logger.error(f"Model '{self.model_name}' not found in Ollama. Available models: {', '.join(available_models)}")
                logger.error(f"You can pull the model with: ollama pull {self.model_name}")
                
        except ConnectionError as e:
            logger.error(f"Could not connect to Ollama server.")
            logger.error(
                f"Make sure Ollama is running at {self.host} or install it from https://ollama.com"
            )
            raise ConnectionError(
                f"Could not connect to Ollama server. "
                f"Make sure Ollama is running at {self.host} or install it from https://ollama.com"
            )
    
    def one_shot_mode(self, user_input: str) -> str:
        """
        Generate a one-shot response to the user input.
        
        Args:
            user_input: The user's input prompt
            
        Returns:
            The generated response as a string
        """
        self._check_ollama_available()
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        response = self._generate_completion(messages)
        return response.strip()
    
    def _generate_completion(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a completion using the Ollama API.
        
        Args:
            messages: The conversation history as a list of message dictionaries
            
        Returns:
            The generated text response
        """
        try:
            
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                }
            )
            
            if "message" in response and "content" in response["message"]:
                return response["message"]["content"]
            else:
                raise ValueError(f"Unexpected response format from Ollama API: {response}")
                
        except Exception as e:
            raise ConnectionError(f"Error communicating with Ollama: {str(e)}")