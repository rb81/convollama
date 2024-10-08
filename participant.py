import ollama

# Configure logging
import logging
logger = logging.getLogger(__name__)

class Participant:
    def __init__(self, model, profile, topic, name, ollama_host):
        self.model = model
        self.profile = profile
        self.topic = topic
        self.name = name
        self.client = ollama.Client(host=ollama_host)
        logger.info(f"Initialized {self.name} with model {self.model}")

    def generate_response(self, conversation_history, is_final_round=False):
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

        # Convert conversation history to API-compatible format
        for msg in conversation_history:
            if msg['role'] == 'system':
                messages.append(msg)
            elif msg['role'] == self.name:
                # This is the participant's own previous message
                messages.append({"role": "assistant", "content": msg['content']})
            else:
                # This is a message from other participants
                messages.append({"role": "user", "content": f"{msg['role']}: {msg['content']}"})

        # Add the final round prompt if necessary
        if is_final_round:
            messages.append({
                "role": "user",
                "content": "This is your final turn in the conversation. Please share your concluding thoughts or final comments."
            })
        else:
            messages.append({
                "role": "user",
                "content": "Please provide your next response in the conversation."
            })

        logger.debug(f"Generating response for {self.name}. Messages: {messages}")

        try:
            logger.info(f"Sending request to Ollama for {self.name} using model {self.model}")
            response = self.client.chat(model=self.model, messages=messages)
            logger.info(f"Received response from Ollama for {self.name}: {response}")
            
            if 'message' not in response:
                logger.error(f"Unexpected response structure for {self.name}: {response}")
                return f"{self.name} received an unexpected response structure."
            
            content = response['message'].get('content', '').strip()
            
            if not content:
                logger.warning(f"{self.name} generated an empty response. Full response: {response}")
                return f"{self.name} is pondering silently."
            
            logger.info(f"{self.name} generated response: {content}")
            return content
        except Exception as e:
            logger.error(f"Error generating response for {self.name}: {e}", exc_info=True)
            return f"{self.name} is unable to respond at the moment due to a technical issue: {str(e)}"