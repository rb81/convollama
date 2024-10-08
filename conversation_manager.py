from participant import Participant
from moderator import Moderator
from cli import display_conversation, clear_screen
from utils import animate_thinking
import threading
import logging

# Configure logging
logger = logging.getLogger(__name__)

class ConversationManager:
    def __init__(self, config, num_participants, selected_model, topic, profiles, num_rounds):
        self.config = config
        self.num_participants = num_participants
        self.selected_model = selected_model
        self.topic = topic
        self.profiles = profiles
        self.num_rounds = num_rounds
        self.participants = self.create_participants()
        self.conversation_history = self.initialize_conversation_history()
        self.moderator = Moderator(config['moderator_model'], config['ollama_host'])
        self.thinking = False
        self.stop_event = threading.Event()
        self.history_limit = self.parse_history_limit(config.get('history_limit'))
        logger.info(f"Initialized ConversationManager with {num_participants} participants and {num_rounds} rounds")

    def parse_history_limit(self, limit):
        if limit is None:
            return None
        try:
            return int(limit)
        except ValueError:
            logger.warning(f"Invalid history_limit value: {limit}. Using full history.")
            return None

    def create_participants(self):
        participants = [Participant(self.selected_model, self.profiles[i], self.topic, f"Participant {i+1}", self.config['ollama_host']) 
                for i in range(self.num_participants)]
        logger.info(f"Created {len(participants)} participants")
        return participants

    def initialize_conversation_history(self):
        history = [{"role": "system", "content": f"Topic: {self.topic}"}]
        for i, profile in enumerate(self.profiles):
            if profile:
                history.append({"role": "system", "content": f"Participant {i+1} profile: {profile}"})
        logger.debug(f"Initialized conversation history: {history}")
        return history

    def get_limited_history(self):
        if self.history_limit is None:
            return self.conversation_history

        # Separate system messages and participant messages
        system_messages = [msg for msg in self.conversation_history if msg['role'] == 'system']
        participant_messages = [msg for msg in self.conversation_history if msg['role'] != 'system']
        
        # Calculate the number of participant messages to keep
        messages_to_keep = self.history_limit * self.num_participants

        # Get the most recent participant messages
        limited_participant_messages = participant_messages[-messages_to_keep:] if messages_to_keep < len(participant_messages) else participant_messages

        return system_messages + limited_participant_messages

    def run_conversation(self):
        try:
            clear_screen()
            display_conversation(self.conversation_history)
            
            for round_num in range(self.num_rounds):
                logger.info(f"Starting round {round_num + 1}")
                for participant in self.participants:
                    is_final_round = (round_num == self.num_rounds - 1)
                    
                    self.thinking = True
                    animation_thread = threading.Thread(target=animate_thinking, args=(participant.name, self.stop_event))
                    animation_thread.start()
                    
                    logger.debug(f"Generating response for {participant.name}")
                    limited_history = self.get_limited_history()
                    
                    response = participant.generate_response(limited_history, is_final_round)
                    
                    self.thinking = False
                    self.stop_event.set()
                    animation_thread.join()
                    self.stop_event.clear()

                    # Store the response with the participant's name as the role
                    self.conversation_history.append({"role": participant.name, "content": response})
                    logger.info(f"Added response from {participant.name} to conversation history")
                    
                    # Display the conversation with participant names
                    display_conversation(self.conversation_history)

            return self.conversation_history
        except KeyboardInterrupt:
            logger.warning("Conversation interrupted by user.")
            return self.conversation_history
        except Exception as e:
            logger.error(f"An error occurred during the conversation: {e}", exc_info=True)
            return self.conversation_history
        finally:
            self.stop_event.set()

    def format_conversation_for_display(self):
        formatted_history = []
        for i, message in enumerate(self.conversation_history):
            if message['role'] == 'user':
                # Find the preceding system message to get the participant's name
                if i > 0 and self.conversation_history[i-1]['role'] == 'system':
                    participant_name = self.conversation_history[i-1]['content']
                    formatted_history.append({"role": participant_name, "content": message['content']})
            else:
                formatted_history.append(message)
        return formatted_history