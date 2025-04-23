from importlib.resources import files
from typing import Literal, Optional

from open_codex.agents.phi_4_mini import AgentPhi4Mini
from open_codex.agents.qwen_25_coder import AgentQwen25Coder
from open_codex.interfaces.llm_agent import LLMAgent

ModelType = Literal["phi-4-mini", "qwen-2.5-coder"]

class AgentBuilder:
    @staticmethod
    def get_agent(model: ModelType = "phi-4-mini", hf_token: Optional[str] = None) -> LLMAgent:
        system_prompt = files("open_codex.resources").joinpath("prompt.txt").read_text(encoding="utf-8")
        
        if model == "phi-4-mini":
            return AgentPhi4Mini(system_prompt=system_prompt)
        elif model == "qwen-2.5-coder":
            return AgentQwen25Coder(system_prompt=system_prompt, hf_token=hf_token)
        else:
            raise ValueError(f"Unsupported model: {model}")
    
    @staticmethod
    def read_file(file_path: str) -> str:
        with open(file_path, 'r') as file:
            content = file.read()
        return content
