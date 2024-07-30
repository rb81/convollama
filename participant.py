import ollama
from utils import truncate_context
import logging

# Set up logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class Participant:
    def __init__(self, model, profile, topic, name, ollama_host):
        self.model = model
        self.profile = profile
        self.topic = topic
        self.name = name
        self.context = self.initialize_context()
        self.client = ollama.Client(host=ollama_host)
        logging.info(f"Initialized {self.name} with model {self.model}")

    def initialize_context(self):
        context = [
            {"role": "system", "content": f"You are {self.name} in a conversation about {self.topic}. Keep your responses concise (2-3 sentences max). Feel free to act naturally, change the topic, argue, debate, or do whatever you want. This is a free-flowing conversation. Only provide your response, nothing else."}
        ]
        if self.profile:
            context.append({"role": "system", "content": f"Your profile: {self.profile}"})
        logging.debug(f"Initialized context for {self.name}: {context}")
        return context

    def generate_response(self, conversation_history, is_final_round):
        # Start with the system message
        messages = [
            {
                "role": "system",
                "content": f"You are Participant {self.name.split()[-1]} in a conversation about {self.topic}. "
                        f"Your profile: {self.profile}. "
                        "Keep your responses concise (2-3 sentences max). "
                        "Act naturally, you can change the topic, argue, or debate as you see fit. "
                        "This is a free-flowing conversation."
            }
        ]

        # Add conversation history
        for entry in conversation_history:
            if entry['role'] == 'system':
                continue  # Skip system messages from the history
            if entry['role'] == self.name:
                role = "assistant"
            else:
                role = "user"
            messages.append({"role": role, "content": entry['content']})

        # Add the final round prompt if necessary
        if is_final_round:
            messages.append({
                "role": "system",
                "content": "This is your final turn in the conversation. Please share your concluding thoughts or final comments."
            })

        # Add a user message to prompt for a response
        messages.append({
            "role": "user",
            "content": "Please provide your next response in the conversation."
        })

        logging.debug(f"Generating response for {self.name}. Messages: {messages}")

        try:
            logging.info(f"Sending request to Ollama for {self.name} using model {self.model}")
            response = self.client.chat(model=self.model, messages=messages)
            logging.info(f"Received response from Ollama for {self.name}: {response}")
            
            if 'message' not in response:
                logging.error(f"Unexpected response structure for {self.name}: {response}")
                return f"{self.name} received an unexpected response structure."
            
            content = response['message'].get('content', '').strip()
            
            if not content:
                logging.warning(f"{self.name} generated an empty response. Full response: {response}")
                return f"{self.name} is pondering silently."
            
            logging.info(f"{self.name} generated response: {content}")
            return content
        except Exception as e:
            logging.error(f"Error generating response for {self.name}: {e}", exc_info=True)
            return f"{self.name} is unable to respond at the moment due to a technical issue: {str(e)}"

    def update_context(self, message):
        self.context.append(message)
        self.context = truncate_context(self.context, 10)
        logging.debug(f"Updated context for {self.name}: {self.context}")