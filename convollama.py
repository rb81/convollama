import ollama
import json
import random
import os
from datetime import datetime
import sys
import argparse
import yaml
from abc import ABC, abstractmethod
from typing import List
import time
import threading
from colorama import init, Fore, Back, Style

# Initialize colorama
init(autoreset=True)

class Participant(ABC):
    def __init__(self, model: str, profile: str, topic: str, max_context_length: int, ollama_host: str):
        self.model = model
        self.client = ollama.Client(host=ollama_host)
        self.profile = profile
        self.topic = topic
        self.context = []
        self.max_context_length = max_context_length

    @abstractmethod
    def generate_response(self, other_participant_profiles: List[str]):
        pass

    def update_context(self, message):
        self.context.append(message)
        if len(self.context) > self.max_context_length:
            self.context.pop(0)

class ConversationParticipant(Participant):
    def generate_response(self, other_participant_profiles: List[str]):
        try:
            other_profiles = "; ".join(other_participant_profiles) if other_participant_profiles else ""
            profile_info = f"Your profile is: {self.profile}. You are talking to others with these profiles: {other_profiles}. " if self.profile else ""
            messages = [
                {"role": "system", "content": f"You are participating in a conversation about {self.topic}. {profile_info}Keep your responses concise (2-3 sentences max). Feel free to act naturally, change the topic, argue, debate, or do whatever you want. This is a free-flowing conversation."},
                *self.context
            ]
            response = self.client.chat(
                model=self.model,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

class Moderator(Participant):
    def generate_response(self, prompt):
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response['message']['content']
        except Exception as e:
            print(f"Error generating response: {e}")
            return None

    def determine_topic(self, keywords):
        prompt = f"Based on these keywords: {', '.join(keywords)}, determine a conversation topic. Respond with just the topic in 1-2 words, nothing else. Do not include 'Topic:' or any other prefix."
        return self.generate_response(prompt)

    def determine_profile(self, topic, profile_number):
        prompt = f"For a conversation about '{topic}', create a single profile or viewpoint for Participant {profile_number}. Respond with just the profile description in 1-2 sentences, nothing else. Do not include 'Participant:', 'Profile Description:', or any other prefix."
        return self.generate_response(prompt)

class ConversationManager:
    def __init__(self, config):
        self.config = config
        self.moderator = Moderator(
            config['moderator_model'],
            "Moderator",
            "Moderation",
            config['max_context_length'],
            config['ollama_host']
        )
        self.topic = None
        self.participants = []
        self.conversation = []
        self.use_profiles = config.get('use_profiles', True)
        self.thinking = False
        self.response_ready = threading.Event()
        self.save_path = os.path.expanduser(config.get('save_path', '~/Downloads/ConvOllama'))
        self.max_messages = config.get('max_messages', float('inf'))  # New parameter
        self.stop_event = threading.Event()  # New event for stopping the conversation

    def setup_conversation(self):
        self.clear_screen()
        self.print_header("Welcome to ConvOllama")
        keywords = input(f"{Fore.YELLOW}Enter a phrase, or comma-separated keywords, for the conversation topic: {Style.RESET_ALL}").split(',')
        self.topic = self.moderator.determine_topic(keywords)
        if not self.topic:
            raise ValueError("Failed to determine a topic.")

        print(f"\n{Fore.GREEN}Topic: {Style.BRIGHT}{self.topic}{Style.RESET_ALL}\n")

        num_participants = self.config['num_participants']
        for i in range(num_participants):
            profile = self.moderator.determine_profile(self.topic, i+1) if self.use_profiles else ""
            if self.use_profiles and not profile:
                raise ValueError(f"Failed to determine profile for Participant {i+1}.")
            if self.use_profiles:
                print(f"{Fore.CYAN}Profile {i+1}: {Style.RESET_ALL}{profile}")
            self.participants.append(ConversationParticipant(
                self.config['participant_model'], 
                profile, 
                self.topic, 
                self.config['max_context_length'],
                self.config['ollama_host']
            ))

        self.conversation = [
            {"speaker": "Moderator", "content": f"Topic: {self.topic}"}
        ]
        if self.use_profiles:
            self.conversation.append({"speaker": "Moderator", "content": f"Profiles: {'; '.join([p.profile for p in self.participants])}"})
            starter = f"Participant {random.randint(1, num_participants)}"
            self.conversation.append({"speaker": "Moderator", "content": f"{starter} starts"})
            print(f"\n{Fore.MAGENTA}{starter} will start the conversation.{Style.RESET_ALL}")
        else:
            starter = "Participant 1"
            self.conversation.append({"speaker": "Moderator", "content": f"{starter} starts"})
            print(f"\n{Fore.MAGENTA}The conversation will start with {starter}.{Style.RESET_ALL}")

        input("\nPress Enter to start the conversation...")
        return starter

    def run_conversation(self, starter):
        current_participant_index = int(starter.split()[-1]) - 1
        message_count = 0
        
        try:
            while not self.stop_event.is_set() and message_count < self.max_messages:
                self.clear_screen()
                self.print_header(f"Topic of Discussion: {self.topic}")
                self.print_conversation()

                current_participant = self.participants[current_participant_index]
                other_profiles = [p.profile for i, p in enumerate(self.participants) if i != current_participant_index] if self.use_profiles else []
                
                speaker = f"Participant {current_participant_index + 1}"
                
                self.thinking = True
                self.response_ready.clear()
                
                animation_thread = threading.Thread(target=self.animate_thinking, args=(speaker,))
                animation_thread.start()
                
                response = current_participant.generate_response(other_profiles)
                
                self.response_ready.set()
                self.thinking = False
                animation_thread.join()
                
                if not response:
                    print("Failed to generate response. Ending conversation.")
                    break

                self.conversation.append({"speaker": speaker, "content": response})

                for participant in self.participants:
                    if participant == current_participant:
                        participant.update_context({"role": "assistant", "content": response})
                    else:
                        participant.update_context({"role": "user", "content": response})

                current_participant_index = (current_participant_index + 1) % len(self.participants)
                message_count += 1

        except KeyboardInterrupt:
            print("\nConversation ended by user.")
        finally:
            self.stop_event.set()

    def animate_thinking(self, speaker):
        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        i = 0
        start_time = time.time()
        while self.thinking and not self.stop_event.is_set():
            elapsed_time = time.time() - start_time
            sys.stdout.write(f"\r{Fore.YELLOW}{speaker} is thinking {frames[i % len(frames)]} ({elapsed_time:.1f}s){Style.RESET_ALL}")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1
        sys.stdout.write("\r" + " " * 70 + "\r")  # Clear the animation
        sys.stdout.flush()

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, text):
        print(f"{Back.BLUE}{Fore.WHITE}{Style.BRIGHT}{text.center(80)}{Style.RESET_ALL}\n")

    def print_conversation(self):
        for entry in self.conversation[-10:]:  # Show last 10 messages
            speaker_color = Fore.GREEN if entry['speaker'] == "Moderator" else Fore.CYAN
            print(f"{speaker_color}{entry['speaker']}:{Style.RESET_ALL} {entry['content']}\n")

    def save_conversation(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename_base = f"convo_{timestamp}"

        # Create the directory if it doesn't exist
        os.makedirs(self.save_path, exist_ok=True)

        json_filename = os.path.join(self.save_path, f"{filename_base}.json")
        with open(json_filename, 'w') as f:
            json.dump(self.conversation, f, indent=2)

        md_filename = os.path.join(self.save_path, f"{filename_base}.md")
        with open(md_filename, 'w') as f:
            f.write(f"# Conversation: {self.topic}\n\n")
            for entry in self.conversation:
                f.write(f"## {entry['speaker']}\n\n{entry['content']}\n\n")

        print(f"Conversation saved to {json_filename} and {md_filename}")

def load_config(config_file):
    with open(config_file, 'r') as f:
        return yaml.safe_load(f)

def main():
    parser = argparse.ArgumentParser(description="Run a moderated AI conversation")
    parser.add_argument("-c", "--config", default="config.yaml", help="Path to the configuration file")
    args = parser.parse_args()

    config = load_config(args.config)
    manager = ConversationManager(config)

    try:
        starter = manager.setup_conversation()
        manager.run_conversation(starter)
    except KeyboardInterrupt:
        print("\nExiting the program...")
    finally:
        manager.stop_event.set()
        manager.save_conversation()

if __name__ == "__main__":
    main()