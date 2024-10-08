import os
import json
from datetime import datetime
import ollama
import sys
import time
import threading
import logging
from colorama import Fore, Style, init

# Configure logging
logger = logging.getLogger(__name__)

init(autoreset=True)  # Initialize colorama

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_ollama_connection_with_animation(host, timeout=10):
    client = ollama.Client(host=host)
    stop_event = threading.Event()
    animation_thread = threading.Thread(target=connection_animation, args=(stop_event,))
    animation_thread.start()

    try:
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                client.list()
                stop_event.set()
                animation_thread.join()
                clear_screen()
                logger.info(f"{Fore.GREEN}Successfully connected to Ollama server at {host}{Style.RESET_ALL}")
                return True
            except Exception:
                time.sleep(0.5)
        
        stop_event.set()
        animation_thread.join()
        clear_screen()
        logger.error(f"{Fore.RED}Failed to connect to Ollama server at {host} within {timeout} seconds{Style.RESET_ALL}")
        return False
    except KeyboardInterrupt:
        stop_event.set()
        animation_thread.join()
        clear_screen()
        logger.warning(f"{Fore.YELLOW}Connection attempt cancelled by user{Style.RESET_ALL}")
        return False

def connection_animation(stop_event):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r{Fore.CYAN}Connecting to Ollama server {frames[i % len(frames)]}{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1

def save_conversation(conversation_history, save_path):
    if not conversation_history:
        logger.warning("No conversation history to save.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename_base = f"convo_{timestamp}"

    # Expand the user's home directory
    expanded_path = os.path.expanduser(save_path)

    # Create the directory if it doesn't exist
    os.makedirs(expanded_path, exist_ok=True)

    json_filename = os.path.join(expanded_path, f"{filename_base}.json")
    with open(json_filename, 'w') as f:
        json.dump(conversation_history, f, indent=2)

    md_filename = os.path.join(expanded_path, f"{filename_base}.md")
    with open(md_filename, 'w') as f:
        f.write(f"# Conversation: {conversation_history[0]['content']}\n\n")
        for entry in conversation_history[1:]:
            f.write(f"## {entry['role']}\n\n{entry['content']}\n\n")

    logger.info(f"Conversation saved to {json_filename} and {md_filename}")

def truncate_context(context, max_length):
    return context[-max_length:] if len(context) > max_length else context

def animate_thinking(name, stop_event):
    frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    i = 0
    start_time = time.time()
    while not stop_event.is_set():
        elapsed_time = time.time() - start_time
        sys.stdout.write(f"\r{Fore.YELLOW}{name} is thinking {frames[i % len(frames)]} {elapsed_time:.1f}s{Style.RESET_ALL}")
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * 80 + "\r")  # Clear the animation
    sys.stdout.flush()