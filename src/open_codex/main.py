import sys
import argparse
import subprocess
import pyperclip
import shutil
import os
from datetime import datetime

from open_codex.agent_builder import AgentBuilder, ModelType
from open_codex.interfaces.llm_agent import LLMAgent

# ANSI color codes
GREEN = "\033[92m"
RED = "\033[91m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
BOLD = "\033[1m"
RESET = "\033[0m"

# Get terminal width for better formatting
TERM_WIDTH = shutil.get_terminal_size().columns

def print_banner(text: str, color: str = BLUE, char: str = "=") -> None:
    """Print a centered banner with the given text"""
    padding = char * ((TERM_WIDTH - len(text) - 2) // 2)
    print(f"{color}{padding} {text} {padding}{RESET}")

def print_timestamp(prefix: str = "") -> None:
    """Print current timestamp in a consistent format"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{YELLOW}{prefix}[{timestamp}]{RESET}")

# Capture single keypress (terminal) from the user
# and returns it as a string. It works on both Windows and Unix systems.
# Windows
if sys.platform == "win32":
    import msvcrt

    def get_keypress():
        return msvcrt.getch().decode("utf-8")

# Unix (Linux/macOS)
else:
    import termios
    import tty

    def get_keypress():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

def print_response(command: str):
    print_banner("Command Found")
    print(f"{GREEN}{BOLD}{command}{RESET}")
    print_banner("Options")
    
    print(f"{BLUE}What would you like to do?{RESET}")
    print(f"{BOLD}[e]{RESET} Execute command")
    print(f"{BOLD}[c]{RESET} Copy to clipboard")
    print(f"{BOLD}[a]{RESET} Abort")
    print(f"\n{BLUE}Press key: ", end="", flush=True)
    
    choice = get_keypress().lower()
    print(f"{RESET}")

    if choice == "e":
        print_banner("Executing Command")
        print_timestamp()
        print(f"{BLUE}Running: {command}{RESET}\n")
        
        try:
            # Use Popen for real-time output with better error handling
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=os.getcwd(),  # Ensure we're in the correct directory
                env=os.environ.copy()  # Pass through environment variables
            )
            
            permission_error = False
            # Stream output in real-time
            while True:
                # Read stdout
                stdout_line = process.stdout.readline() if process.stdout else ""
                if stdout_line:
                    print(f"{GREEN}{stdout_line.rstrip()}{RESET}")
                
                # Read stderr
                stderr_line = process.stderr.readline() if process.stderr else ""
                if stderr_line:
                    # Check for permission errors
                    if "Permission denied" in stderr_line:
                        permission_error = True
                    print(f"{RED}{stderr_line.rstrip()}{RESET}")
                
                # Check if process has finished
                if process.poll() is not None and not stdout_line and not stderr_line:
                    break
            
            # Print final status
            if process.returncode == 0:
                print(f"\n{GREEN}✓ Command completed successfully{RESET}")
            else:
                error_msg = "✗ Command failed"
                if permission_error:
                    error_msg += " due to permission issues. Try:\n"
                    error_msg += f"  1. Using sudo (if appropriate)\n"
                    error_msg += f"  2. Checking file/directory permissions\n"
                    error_msg += f"  3. Running from a directory you have access to"
                else:
                    error_msg += f" with exit code {process.returncode}"
                print(f"\n{RED}{error_msg}{RESET}")

        except Exception as e:
            print(f"\n{RED}✗ Error executing command: {str(e)}{RESET}")
        
        print_timestamp("Finished at ")

    elif choice == "c":
        pyperclip.copy(command)
        print(f"{GREEN}✓ Command copied to clipboard!{RESET}")

    elif choice == "a":
        print(f"{BLUE}Operation aborted.{RESET}")
    else:
        print(f"{RED}Unknown choice. Nothing happened.{RESET}")

def one_shot_mode(agent: LLMAgent, prompt: str):
    try:
        response = agent.one_shot_mode(prompt)
        print_response(response)
    except Exception as e:
        print(f"{RED}Error: {e}{RESET}")

def print_help_message():
    """Print help message with usage examples."""
    print_banner("Open Codex - Natural Language to CLI commands")
    print(f"{BLUE}Usage examples:{RESET}")
    print(f"{GREEN}open-codex \"list all files in current directory\"")
    print(f"{GREEN}open-codex --model qwen-2.5-coder --hf-token YOUR_TOKEN \"find python files\"")
    print(f"{GREEN}open-codex \"create a tarball of the src directory\"")
    print()
    print(f"{BLUE}Available models:{RESET}")
    print(f"{GREEN}  - phi-4-mini (default)")
    print(f"{GREEN}  - qwen-2.5-coder (requires Hugging Face authentication)")
    print()
    print(f"{BLUE}Authentication:{RESET}")
    print(f"{GREEN}For Qwen 2.5 Coder, you can provide your Hugging Face token:")
    print(f"{GREEN}1. Via environment variable: export HUGGINGFACE_TOKEN=your_token")
    print(f"{GREEN}2. Via command line: --hf-token your_token")
    print()

def main():
    parser = argparse.ArgumentParser(description="Open Codex - Natural Language to CLI commands")
    parser.add_argument("prompt", nargs="*", help="Optional prompt for one-shot mode")
    parser.add_argument("--model", type=str, choices=["phi-4-mini", "qwen-2.5-coder"],
                      default="phi-4-mini", help="Choose the model to use")
    parser.add_argument("--hf-token", type=str, help="Hugging Face API token for authenticated models")
    args = parser.parse_args()
    prompt = " ".join(args.prompt).strip()
    if not prompt or prompt == "--help":
        print_help_message()
        sys.exit(1)
    
    try:
        agent = AgentBuilder.get_agent(model=args.model, hf_token=args.hf_token)
        print(f"{BLUE}Using model: {args.model}{RESET}")
        one_shot_mode(agent, prompt)
    except ValueError as e:
        print(f"{RED}Error: {str(e)}{RESET}")
        sys.exit(1)

if __name__ == "__main__":
    main()