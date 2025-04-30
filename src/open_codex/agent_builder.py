from importlib.resources import files

from open_codex.interfaces.llm_agent import LLMAgent

class AgentBuilder:
    
    @staticmethod
    def get_system_prompt() -> str:
        return files("open_codex.resources") \
            .joinpath("prompt.txt") \
            .read_text(encoding="utf-8")

    @staticmethod
    def get_phi_agent() -> LLMAgent:
        from open_codex.agents.phi_4_mini_agent import Phi4MiniAgent
        system_prompt = AgentBuilder.get_system_prompt()
        return Phi4MiniAgent(system_prompt=system_prompt)
    
    @staticmethod
    def get_ollama_agent(model: str, host: str) -> LLMAgent:
        from open_codex.agents.ollama_agent import OllamaAgent
        system_prompt = AgentBuilder.get_system_prompt()
        return OllamaAgent(system_prompt=system_prompt, 
                           model_name=model,
                           host=host)

    @staticmethod
    def read_file(file_path: str) -> str:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
