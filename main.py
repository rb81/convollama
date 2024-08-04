import argparse
import sys, os
from datetime import datetime
from rich.console import Console
from rich.logging import RichHandler
from config import load_config
from cli import get_user_preferences, print_header
from conversation_manager import ConversationManager
from moderator import Moderator
from utils import save_conversation, check_ollama_connection_with_animation, clear_screen
import logging

console = Console()

def setup_logging(level=logging.ERROR):
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Generate a unique log file name with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"convollama_{timestamp}.log")

    # Configure logging to write to both file and console
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="[%X]",
        handlers=[
            logging.FileHandler(log_file),
            RichHandler(rich_tracebacks=True, markup=True)
        ]
    )

    logging.info(f"Logging initialized. Log file: {log_file}")

def main():
    setup_logging()
    clear_screen()  # Clear the screen when the app starts
    
    parser = argparse.ArgumentParser(description="Run a moderated AI conversation")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to the configuration file")
    args = parser.parse_args()

    config = load_config(args.config)

    if not check_ollama_connection_with_animation(config['ollama_host']):
        console.print("[bold red]Unable to connect to Ollama server. Please check your configuration and ensure the server is running.[/bold red]")
        sys.exit(1)

    moderator = Moderator(config['moderator_model'], config['ollama_host'])

    print_header("Welcome to ConvOllama")
    num_participants, model, topic, profiles, num_rounds = get_user_preferences(moderator, config)

    manager = ConversationManager(config, num_participants, model, topic, profiles, num_rounds)
    conversation_history = manager.run_conversation()

    save_conversation(conversation_history, config['save_path'])
    console.print("\n[bold green]Conversation completed and saved.[/bold green]")
    console.print("Press Enter to exit...")
    input()

if __name__ == "__main__":
    main()