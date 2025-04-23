import time
import os
import multiprocessing
from typing import cast, Optional, List
from llama_cpp import CreateCompletionResponse, Llama
from open_codex.interfaces.llm_agent import LLMAgent
import contextlib
from huggingface_hub import hf_hub_download, login

class AgentQwen25Coder(LLMAgent):
    def download_model(self, model_filename: str,
                        repo_id: str, 
                        local_dir: str,
                        token: Optional[str] = None) -> str:
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
            token=token,
            force_download=True,  # Force download to ensure the latest version
        )
        duration = time.time() - start
        print(f"✅ Model downloaded ({duration:.1f}s)")
        return model_path

    def __init__(self, system_prompt: str, hf_token: Optional[str] = None):
        model_filename = "Qwen2.5-Coder-1.5B-Instruct-F16.gguf"  # Using correct model filename
        repo_id = "unsloth/Qwen2.5-Coder-1.5B-Instruct-GGUF"      # Using TheBloke's repository
        local_dir = os.path.expanduser("~/.cache/open-codex")
        model_path = os.path.join(local_dir, model_filename)

        if not hf_token:
            hf_token = os.environ.get("HUGGINGFACE_TOKEN")

        if not os.path.exists(model_path):
            model_path = self.download_model(model_filename, repo_id, local_dir, token=hf_token)
        else:
            print("🚀 Loading Qwen model...\n")

        # Get optimal thread count for the system
        n_threads = min(4, multiprocessing.cpu_count())
        
        with AgentQwen25Coder.suppress_native_stderr():
            self.llm: Llama = Llama(
                model_path=model_path,
                n_ctx=2048,     # Smaller context for faster responses
                n_threads=n_threads,  # Use optimal thread count
                n_batch=256,    # Balanced batch size
                use_mlock=True, # Lock memory to prevent swapping
                use_mmap=True,  # Use memory mapping for faster loading
            )
            print("✨ Model ready!")

        self.system_prompt = system_prompt

    def one_shot_mode(self, user_input: str) -> str:
        chat_history = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": "I need a shell command to find all python files"},
            {"role": "assistant", "content": "find . -name \"*.py\""},
            {"role": "user", "content": user_input}
        ]
        full_prompt = self.format_chat(chat_history)
        
        with AgentQwen25Coder.suppress_native_stderr():
            try:
                output_raw = self.llm(
                    prompt=full_prompt,
                    max_tokens=100,    # Limit response length
                    temperature=0.1,   # Lower temperature for more deterministic output
                    top_p=0.1,        # Focus on most likely tokens
                    top_k=10,         # Limit vocabulary for shell commands
                    repeat_penalty=1.1,# Prevent repetition
                    stop=["<|im_end|>", "<|im_start|>", "\n"],  # Stop at appropriate tokens
                    stream=False
                )
                
                output = cast(CreateCompletionResponse, output_raw)
                assistant_reply: str = output["choices"][0]["text"].strip()
                
                # Clean up response
                assistant_reply = assistant_reply.split('\n')[0].strip()
                assistant_reply = assistant_reply.replace("<|im_end|>", "").strip()
                
                # Basic validation of shell commands
                if any(invalid_char in assistant_reply for invalid_char in ['<', '>', '|/']):
                    return "find . -name \"*.py\""  # fallback to safe command
                    
                return assistant_reply

            except Exception as e:
                print(f"⚠️  Model error: {str(e)}")
                return ""

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
