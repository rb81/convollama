import ollama
from utils import truncate_context

class Participant:
    def __init__(self, model, profile, topic, name, ollama_host):
        self.model = model
        self.profile = profile
        self.topic = topic
        self.name = name
        self.context = self.initialize_context()
        self.client = ollama.Client(host=ollama_host)

    def initialize_context(self):
        context = [
            {"role": "system", "content": f"You are {self.name} in a conversation about {self.topic}. Keep your responses concise (2-3 sentences max). Feel free to act naturally, change the topic, argue, debate, or do whatever you want. This is a free-flowing conversation. Only provide your response, nothing else."}
        ]
        if self.profile:
            context.append({"role": "system", "content": f"Your profile: {self.profile}"})
        return context

    def generate_response(self, conversation_history, is_final_round):
        # Combine self.context with conversation_history for the API call
        full_context = self.context + truncate_context(conversation_history, 10)

        if is_final_round:
            full_context.append({
                "role": "system",
                "content": "This is your final turn in the conversation. Please share your concluding thoughts or final comments."
            })

        try:
            response = self.client.chat(model=self.model, messages=full_context)
            return response['message']['content']
        except Exception as e:
            print(f"Error generating response for {self.name}: {e}")
            return f"{self.name} is unable to respond at the moment due to a technical issue."

    def update_context(self, message):
        self.context.append(message)
        self.context = truncate_context(self.context, 10)