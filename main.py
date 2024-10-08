import argparse
import sys
import os
from datetime import datetime
from config import load_config
from log_config import setup_logging
import logging

# Load config and set up logging immediately
config = load_config("config.yaml")  # You might want to handle the config path more flexibly
log_level = getattr(logging, config.get('log_level', 'INFO').upper(), logging.INFO)
setup_logging(log_level)

# Now import the rest of the modules
from rich.console import Console
from cli import get_user_preferences, print_header
from conversation_manager import ConversationManager
from moderator import Moderator
from utils import save_conversation, check_ollama_connection_with_animation, clear_screen

console = Console()

def main(config):
    parser = argparse.ArgumentParser(description="Run a moderated AI conversation")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to the configuration file")
    args = parser.parse_args()

    # Reload the config if a different path was specified
    if args.config != "config.yaml":
        config = load_config(args.config)
        log_level = getattr(logging, config.get('log_level', 'INFO').upper(), logging.INFO)
        logging.getLogger().setLevel(log_level)

    logging.info(f"Configuration loaded from {args.config}")

    # Check Ollama server connection
    if not check_ollama_connection_with_animation(config['ollama_host']):
        logging.error("Failed to connect to the Ollama server.")
        sys.exit(1)

    moderator = Moderator(config['moderator_model'], config['ollama_host'])
    logging.info("Moderator initialized")

    print_header("Welcome to ConvOllama")
    num_participants, model, topic, profiles, num_rounds = get_user_preferences(moderator, config)
    logging.info(f"User preferences: {num_participants} participants, model: {model}, topic: {topic}, {num_rounds} rounds")

    manager = ConversationManager(config, num_participants, model, topic, profiles, num_rounds)
    logging.info("Conversation manager initialized")

    conversation_history = manager.run_conversation()
    logging.info("Conversation completed")

    save_conversation(conversation_history, config['save_path'])
    logging.info(f"Conversation saved to {config['save_path']}")

    console.print("\n[bold green]Conversation completed and saved.[/bold green]")
    console.print("Press Enter to exit...")
    input()

if __name__ == "__main__":
    main(config)