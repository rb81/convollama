import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.text import Text
from rich import print as rprint
from questionary import Choice
import questionary
import logging

# Configure logging
logger = logging.getLogger(__name__)

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    clear_screen()
    header = Text(text, style="bold cyan")
    header_panel = Panel(
        header,
        border_style="blue",
        padding=(1, 1),
        expand=False
    )
    console.print(header_panel)

def get_user_preferences(moderator, config):
    print_header("ConvOllama")
    
    num_participants = get_valid_input(
        IntPrompt.ask,
        "How many participants should be in the conversation? (minimum 2, press Enter for default)",
        default=2,
        validator=lambda x: x >= 2,
        error_message="Please enter a number greater than or equal to 2."
    )
    console.print()

    model = get_model_preference(config['available_models'])
    console.print()

    topic = get_topic_preference(moderator)
    console.print()
    
    profiles = [get_profile_preference(i + 1, moderator, topic) for i in range(num_participants)]
    console.print()
    
    num_rounds = get_valid_input(
        IntPrompt.ask,
        "How many rounds should the conversation last? (minimum 1, press Enter for default)",
        default=3,
        validator=lambda x: x >= 1,
        error_message="Please enter a number greater than or equal to 1."
    )
    console.print()
    
    return num_participants, model, topic, profiles, num_rounds

def get_model_preference(available_models):
    console.print("Choose the LLM model for the conversation:")
    model = questionary.select(
        "",
        choices=available_models,
        style=questionary.Style([('selection', 'cyan')])
    ).ask()
    return model

def get_topic_preference(moderator):
    console.print("How would you like to determine the conversation topic?")
    choice = questionary.select(
        "",
        choices=[
            Choice("I'll provide the topic myself", 'manual'),
            Choice("Have the moderator generate it", 'generated')
        ],
        style=questionary.Style([('selection', 'cyan')])
    ).ask()
    console.print()
    
    if choice == 'manual':
        return Prompt.ask("Please enter the conversation topic")
    else:
        while True:
            keywords = Prompt.ask("Enter keywords for topic generation (comma-separated)")
            keywords = [k.strip() for k in keywords.split(',')]
            with console.status("[bold green]Generating topic...", spinner="dots"):
                topic = moderator.generate_topic(keywords)
            console.print(f"\nGenerated topic: [bold cyan]{topic}[/bold cyan]")
            if Confirm.ask("Do you approve this topic?"):
                return topic
            logger.info("User rejected the generated topic. Generating a new one.")

def get_profile_preference(participant_num, moderator, topic):
    console.print(f"How would you like to determine Participant {participant_num}'s profile?")
    choice = questionary.select(
        "",
        choices=[
            Choice("I'll provide the profile myself", 'manual'),
            Choice("Have the moderator generate it", 'generated'),
            Choice("No profile", 'none')
        ],
        style=questionary.Style([('selection', 'cyan')])
    ).ask()
    console.print()
    
    if choice == 'manual':
        return Prompt.ask(f"Enter profile for Participant {participant_num}")
    elif choice == 'generated':
        while True:
            with console.status(f"[bold green]Generating profile for Participant {participant_num}...", spinner="dots"):
                profile = moderator.generate_profile(topic, participant_num)
            console.print(f"\nGenerated profile: [bold cyan]{profile}[/bold cyan]")
            if Confirm.ask("Do you approve this profile?"):
                return profile
            logger.info(f"User rejected the generated profile for Participant {participant_num}. Generating a new one.")
    else:
        return None

def display_conversation(conversation_history):
    clear_screen()
    for entry in conversation_history:
        if entry['role'] == 'system':
            if entry['content'].startswith("Topic:"):
                console.print(Panel(entry['content'], expand=False, border_style="yellow", padding=(1, 1)))
            else:
                console.print(Panel(entry['content'], expand=False, border_style="yellow", padding=(1, 1)))
        else:
            title = Text(entry['role'], style="bold")
            content = entry['content']
            # Remove any potential "Participant X: " prefix if it exists
            if content.startswith(entry['role'] + ":"):
                content = content[len(entry['role'] + ":"):].strip()
            console.print(Panel(
                content,
                expand=False,
                border_style="cyan",
                padding=(1, 1),
                title=title,
                title_align="left"
            ))
        console.print()

def get_valid_input(prompt_func, prompt, default, validator, error_message):
    while True:
        value = prompt_func(prompt, default=default)
        if validator(value):
            return value
        console.print(f"[bold red]{error_message}[/bold red]")