import contextlib
import os
import time
import multiprocessing
from typing import List, cast

from huggingface_hub import hf_hub_download  # type: ignore
from llama_cpp import CreateCompletionResponse, Llama
from open_codex.interfaces.llm_agent import LLMAgent

class AgentPhi4Mini(LLMAgent):
    
    def download_model(self, model_filename: str,
                        repo_id: str, 
                        local_dir: str) -> str:
        print(
            "\n🤖 Welcome to Open Codex!\n"
            "📦 First run requires downloading the model.\n"
            "⚡️ This model is optimized for quick responses.\n"
        )
        
        start = time.time()
        model_path:str = hf_hub_download(
            repo_id=repo_id,
            filename=model_filename,
            local_dir=local_dir,
        )
        duration = time.time() - start
        print(f"✅ Model downloaded ({duration:.1f}s)")
        return model_path

    def __init__(self, system_prompt: str):
        model_filename = "Phi-4-mini-instruct-Q3_K_L.gguf"
        repo_id = "lmstudio-community/Phi-4-mini-instruct-GGUF"
        local_dir = os.path.expanduser("~/.cache/open-codex")
        model_path = os.path.join(local_dir, model_filename)

        if not os.path.exists(model_path):
            model_path = self.download_model(model_filename, repo_id, local_dir)
        else:
            print("🚀 Loading Phi-4-mini model...")

        # Get optimal thread count for the system
        n_threads = min(4, multiprocessing.cpu_count())

        with AgentPhi4Mini.suppress_native_stderr():
          lib_path = os.path.join(os.path.dirname(__file__), "llama_cpp", "lib", "libllama.dylib")
          llama_kwargs = {
              "model_path": model_path,
              "n_ctx": 2048,
              "n_threads": n_threads,
              "n_batch": 256,
              "use_mlock": True,
              "use_mmap": True,
          }

          if os.path.exists(lib_path):
              llama_kwargs["lib_path"] = lib_path

          self.llm: Llama = Llama(**llama_kwargs)
          print("✨ Model ready!")


        self.system_prompt = system_prompt

    def one_shot_mode(self, user_input: str) -> str:
        chat_history = [{"role": "system", "content": self.system_prompt}]
        chat_history.append({"role": "user", "content": user_input})
        full_prompt = self.format_chat(chat_history)
        
        with AgentPhi4Mini.suppress_native_stderr():
            output_raw = self.llm(
                prompt=full_prompt,
                max_tokens=100,
                temperature=0.2,
                stream=False,
                top_p=0.1,      # More focused responses
                repeat_penalty=1.1  # Reduce repetition
            )
        
        output = cast(CreateCompletionResponse, output_raw)
        assistant_reply: str = output["choices"][0]["text"].strip()
        return assistant_reply

    def format_chat(self, messages: List[dict[str, str]]) -> str:
        chat_prompt = ""
        for msg in messages:
            role_tag = "user" if msg["role"] == "user" else "assistant"
            chat_prompt += f"<|{role_tag}|>\n{msg['content']}\n"
        chat_prompt += "<|assistant|>\n"
        return chat_prompt
    
    @contextlib.contextmanager
    @staticmethod
    def suppress_native_stderr():
        """
        Redirect C‐level stderr (fd 2) into /dev/null, so llama.cpp logs vanish.
        """
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        saved_stderr_fd = os.dup(2)
        try:
            os.dup2(devnull_fd, 2)
            yield
        finally:
            os.dup2(saved_stderr_fd, 2)
            os.close(devnull_fd)
            os.close(saved_stderr_fd)
