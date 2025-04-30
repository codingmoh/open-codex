import contextlib
import os
import time
import logging
from typing import List, cast

from huggingface_hub import hf_hub_download  # type: ignore
from llama_cpp import CreateCompletionResponse, Llama
from open_codex.interfaces.llm_agent import LLMAgent

# Configure logger
logger = logging.getLogger(__name__)

class Phi4MiniAgent(LLMAgent):
    def __init__(self, system_prompt: str):
        model_filename = "Phi-4-mini-instruct-Q3_K_L.gguf"
        repo_id = "lmstudio-community/Phi-4-mini-instruct-GGUF"
        local_dir = os.path.expanduser("~/.cache/open-codex")
        model_path = os.path.join(local_dir, model_filename)

        # check if the model is already downloaded
        if not os.path.exists(model_path):
            # download the model
            model_path = self.download_model(model_filename, repo_id, local_dir)
        else:
            logger.info("Model already downloaded, loading model...")
            print(f"We are locking and loading the model for you...\n")

        # suppress the stderr output from llama_cpp
        # this is a workaround for the llama_cpp library
        # which prints a lot of warnings and errors to stderr
        # when loading the model
        # this is a temporary solution until the library is fixed
        with Phi4MiniAgent.suppress_native_stderr():
            lib_dir = os.path.join(os.path.dirname(__file__), "llama_cpp", "lib")
            logger.debug(f"Loading model from {model_path}")
            self.llm: Llama = Llama(
                lib_path=os.path.join(lib_dir, "libllama.dylib"),
                model_path=model_path)  

        self.system_prompt = system_prompt

    def download_model(self, model_filename: str,
                        repo_id: str, 
                        local_dir: str) -> str:
        logger.info("First run detected, downloading model from Hugging Face")
        print(
            "\n🤖 Thank you for using Open Codex!\n"
            "📦 For the first run, we need to download the model from Hugging Face.\n"
            "⏬ This only happens once – it'll be cached locally for future use.\n"
            "🔄 Sit tight, the download will begin now...\n"
        )
        logger.info(f"Downloading model phi4-mini from {repo_id}")
        print("\n⏬ Downloading model phi4-mini ...")
        
        start = time.time()
        model_path:str = hf_hub_download(
            repo_id=repo_id,
            filename=model_filename,
            local_dir=local_dir,
        )
        end = time.time()
        download_time = end - start
        logger.info(f"Model downloaded in {download_time:.2f}s to {model_path}")
        print(f"✅ Model downloaded in {download_time:.2f}s\n")
        return model_path
    
    def one_shot_mode(self, user_input: str) -> str:
        logger.debug("Preparing chat history with system prompt and user input")
        chat_history = [{"role": "system", "content": self.system_prompt}]
        chat_history.append({"role": "user", "content": user_input})
        full_prompt = self.format_chat(chat_history)
        
        logger.debug("Generating completion with phi-4-mini model")
        with Phi4MiniAgent.suppress_native_stderr():
            output_raw = self.llm(prompt=full_prompt, max_tokens=100, temperature=0.2, stream=False)
        
        # unfortuntely llama_cpp has a union type for the output
        output = cast(CreateCompletionResponse, output_raw)
        
        assistant_reply : str = output["choices"][0]["text"].strip() 
        logger.debug(f"Generated response of length {len(assistant_reply)}")
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
        Redirect C‐level stderr (fd 2) into /dev/null, so llama.cpp logs vanish.
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
