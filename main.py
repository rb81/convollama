import argparse
import sys
from rich.console import Console
from config import load_config
from cli import get_user_preferences, print_header
from conversation_manager import ConversationManager
from moderator import Moderator
from utils import save_conversation, check_ollama_connection_with_animation, clear_screen

console = Console()

def main():
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