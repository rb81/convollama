import ollama
import logging

# Configure logging
logger = logging.getLogger(__name__)

class Moderator:
    def __init__(self, model, ollama_host="http://localhost:11434"):
        self.model = model
        self.client = ollama.Client(host=ollama_host)

    def generate_topic(self, keywords):
        prompt = f"Based on these keywords: {', '.join(keywords)}, generate an interesting conversation topic. Respond with just the topic in 1-2 sentences, nothing else."
        return self._generate_content(prompt, "topic", "General Discussion")

    def generate_profile(self, topic, participant_num):
        prompt = f"For a conversation about '{topic}', create an interesting and unique profile or viewpoint for Participant {participant_num}. The profile should be somewhat opinionated to encourage debate. Respond with just the profile description in 1-2 sentences max, nothing else."
        return self._generate_content(prompt, "profile", f"Participant {participant_num} with a general interest in the topic")

    def _generate_content(self, prompt, content_type, default_response):
        try:
            response = self.client.chat(model=self.model, messages=[{"role": "user", "content": prompt}])
            return response['message']['content'].strip()
        except Exception as e:
            logger.error(f"Error generating {content_type}: {e}")
            return default_response