import sys
import argparse
import subprocess

from open_codex.agent_builder import AgentBuilder
from open_codex.interfaces.llm_agent import LLMAgent

GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"

# Capture single keypress (terminal) from the user
# and returns it as a string. It works on both Windows and Unix systems.

# Windows
if sys.platform == "win32":
    import msvcrt
    def get_keypress():
        return msvcrt.getch().decode("utf-8")
# Unix
else:
    import termios, tty
    def get_keypress():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

def get_user_action():
    print(f"{BLUE}What do you want to do with this command?{RESET}")
    print(f"{BLUE}[c] Copy  [e] Execute  [a] Abort{RESET}")
    print(f"{BLUE}Press key: ", end="", flush=True)
    choice = get_keypress().lower()
    return choice

def run_user_action(choice: str, command: str):
    if choice == "c":
        print(f"{GREEN}Copying command to clipboard...{RESET}")
        subprocess.run("pbcopy", universal_newlines=True, input=command)
        print(f"{GREEN}Command copied to clipboard!{RESET}")
    elif choice == "e":
        print(f"{GREEN}Executing command...{RESET}")
        subprocess.run(command, shell=True)
    else: 
        print(f"{RED}Aborting...{RESET}")
        sys.exit(1)  

def print_response(command: str):
    print(f"{BLUE}Command found:\n=====================")
    print(f"{GREEN}{command}{RESET}")
    print(f"{BLUE}====================={RESET}")
    print(f"{RESET}")

def get_agent(args: argparse.Namespace) -> LLMAgent:
    model: str = args.model
    if args.ollama:
        print(f"{BLUE}Using Ollama with model: {model}{RESET}")
        return AgentBuilder.get_ollama_agent(model=model, host=args.ollama_host)        
    else:
        print(f"{BLUE}Using model: phi-4-mini-instruct{RESET}")
        return AgentBuilder.get_phi_agent()

def run_one_shot(agent: LLMAgent, user_prompt: str) -> str:   
    try:
        return agent.one_shot_mode(user_prompt)
    except ConnectionError:
        print(f"{RED}Could not connect to Model.{RESET}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"{RED}Unexpected error: {e}{RESET}", file=sys.stderr)
        print(f"{RED}Exiting...{RESET}", file=sys.stderr)
        sys.exit(1)

def get_help_message():
    return f"""
    {BLUE}Usage examples:{RESET}
    {GREEN}open-codex list all files in current directory
    {GREEN}open-codex --ollama find all python files modified in the last week
    {GREEN}open-codex --ollama --model llama3 "create a tarball of the src directory
    """

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Open Codex is a command line interface for LLMs."
                                     "It can be used to generate shell commands from natural language prompts.",
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=get_help_message())

    parser.add_argument("prompt", nargs="+", 
                        help="Natural language prompt")
    parser.add_argument("--model", type=str, 
                        help="Model name to use (default: phi4-mini)", default="phi4-mini:latest")
    parser.add_argument("--ollama", action="store_true", 
                        help="Use Ollama for LLM inference, use --model to specify the model")
    parser.add_argument("--ollama-host", type=str, default="http://localhost:11434", 
                        help="Configure the host for the Ollama API. " \
                        "If left empty, the default http://localhost:11434 is used.")

    return parser.parse_args()

def main():
    args = parse_args()
    agent = get_agent(args)

    # join the prompt arguments into a single string
    prompt = " ".join(args.prompt).strip() 
    response = run_one_shot(agent, prompt)
    print_response(response)
    action = get_user_action()
    run_user_action(action, response)

if __name__ == "__main__":
    # We call multiprocessing.freeze_support() because we are using PyInstaller to build a frozen binary.
    # When Python spawns helper processes (e.g., for Hugging Face downloads or resource tracking),
    # it uses sys.executable to start the current executable with special multiprocessing arguments.
    # Without freeze_support(), the frozen app would accidentally rerun the main CLI logic 
    # and crash (e.g., with argparse errors).
    # freeze_support() ensures the subprocess is handled correctly without restarting the full app.
    # This is required on macOS and Windows, where "spawn" is the default multiprocessing method.
    # See: https://pyinstaller.org/en/stable/common-issues-and-pitfalls.html#when-to-call-multiprocessing-freeze-support
    from multiprocessing import freeze_support
    freeze_support()
    main()