# ConvOllama

![ConvOllama](/header.png)

ConvOllama is a Python application that facilitates AI-driven conversations using the Ollama API. It creates engaging, multi-participant discussions on user-specified topics, with the ability to assign unique profiles to each AI participant.

## Features

- Dynamic topic generation based on user input
- Multi-participant conversations with AI-generated profiles
- Configurable conversation parameters (number of participants, max messages, etc.)
- Real-time conversation display with colorized output
- Automatic saving of conversations in both JSON and Markdown formats
- Graceful handling of program interruption

## Requirements

- Python 3.7+
- Ollama API access

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/rb81/convollama.git
   cd convollama
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Ensure you have Ollama set up and running on your system.

## Configuration

Create a `config.yaml` file in the project root directory with the following structure:

```yaml
moderator_model: "wizardlm2:latest"
participant_model: "llama3.1:latest"
use_profiles: true  # Set to false to disable profiles
num_participants: 2
max_context_length: 8
max_messages: 50  # Set to any number, or omit for infinite messages
ollama_host: "http://localhost:11434"
save_path: "~/Downloads/ConvOllama"
timeout: 60  # in seconds
max_retries: 3
message_delay: 1  # in seconds
```

Adjust the values according to your preferences and setup.

## Usage

Run the application using the following command:

```
python convollama.py
```

or specify a custom configuration file:

```
python convollama.py -c path/to/your/config.yaml
```

You will be prompted with two options:

1. Enter comma-separated keywords and have Moderator generate an appropriate discussion topic,
2. Enter a discussion topic yourself (which is great for setting up brainstorming sessions).

The Moderator will then create profiles for participants (if enabled), and start the conversation.

To end the conversation, press Ctrl+C. The program will save the conversation and exit gracefully.

## Output

Conversations are saved in two formats:

1. JSON file for easy parsing and analysis
2. Markdown file for human-readable documentation

Both files are saved in the directory specified by `save_path` in the configuration.

## Model Recommendations

The Moderator seems to work best with `wizardlm2`. Recommended Participant models include Meta's new `llama3.1`, `gemma2`, and `llama3`.

## Demonstration

![ConvOllama Example Conversation](/demo.png)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Transparency Disclaimer

[ai.collaboratedwith.me](ai.collaboratedwith.me) in creating this project.