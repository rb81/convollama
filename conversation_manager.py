from participant import Participant
from moderator import Moderator
from cli import display_conversation, clear_screen
from utils import animate_thinking
import threading

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

    def create_participants(self):
        return [Participant(self.selected_model, self.profiles[i], self.topic, f"Participant {i+1}", self.config['ollama_host']) 
                for i in range(self.num_participants)]

    def create_participants(self):
        return [Participant(self.config['participant_model'], self.profiles[i], self.topic, f"Participant {i+1}", self.config['ollama_host']) 
                for i in range(self.num_participants)]

    def initialize_conversation_history(self):
        history = [{"role": "system", "content": f"Topic: {self.topic}"}]
        for i, profile in enumerate(self.profiles):
            if profile:
                history.append({"role": "system", "content": f"Participant {i+1} profile: {profile}"})
        return history

    def run_conversation(self):
        try:
            clear_screen()  # Clear the screen before starting the conversation
            display_conversation(self.conversation_history)  # Display initial topic and profiles
            
            for round_num in range(self.num_rounds):
                for participant in self.participants:
                    is_final_round = (round_num == self.num_rounds - 1)
                    
                    self.thinking = True
                    animation_thread = threading.Thread(target=animate_thinking, args=(participant.name, self.stop_event))
                    animation_thread.start()
                    
                    response = participant.generate_response(self.conversation_history, is_final_round)
                    
                    self.thinking = False
                    self.stop_event.set()
                    animation_thread.join()
                    self.stop_event.clear()

                    self.conversation_history.append({"role": participant.name, "content": response})
                    
                    # Update other participants' contexts
                    for other in self.participants:
                        if other != participant:
                            other.update_context(self.conversation_history[-1])
                    
                    display_conversation(self.conversation_history)

            return self.conversation_history
        except KeyboardInterrupt:
            print("\nConversation interrupted by user.")
            return self.conversation_history
        finally:
            self.stop_event.set()