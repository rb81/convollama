import os
import json
from datetime import datetime
import ollama
import sys
import time
from colorama import Fore, Style

def check_ollama_connection(host):
    client = ollama.Client(host=host)
    try:
        # Try to list models as a simple check
        client.list()
        return True
    except Exception as e:
        print(f"Error connecting to Ollama server at {host}: {e}")
        return False

def save_conversation(conversation_history, save_path):
    if not conversation_history:
        print("No conversation history to save.")
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

    print(f"Conversation saved to {json_filename} and {md_filename}")

def truncate_context(context, max_length):
    if len(context) > max_length:
        return context[-max_length:]
    return context

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