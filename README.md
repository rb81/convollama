# ConvOllama

![ConvOllama](/header.png)

ConvOllama is a Python application that facilitates AI-driven conversations using the Ollama API. It creates engaging, multi-participant discussions on user-specified topics, with the ability to assign unique profiles to each AI participant.

## Features

- Dynamic topic generation based on user input or keywords
- Multi-participant conversations with AI-generated or user-defined profiles
- User-selectable LLM models for participants
- Configurable conversation parameters (number of participants, rounds, etc.)
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
ollama_host: "http://localhost:11434"
save_path: "~/Downloads/ConvOllama"
available_models:
  - "llama3.1:latest"
  - "gemma2:latest"
  - "falcon2:latest"
```

Adjust the values according to your preferences and setup.

## Usage

Run the application using the following command:

```
python main.py
```

or specify a custom configuration file:

```
python main.py -c path/to/your/config.yaml
```

You will be guided through the following steps:

1. Choose the number of participants (minimum 2)
2. Select the LLM model for the participants
3. Determine the conversation topic:
   - Enter keywords and have the Moderator generate a topic
   - Enter a discussion topic yourself
4. For each participant:
   - Provide a profile yourself
   - Have the Moderator generate a profile
   - Choose no profile
5. Set the number of conversation rounds

The conversation will then begin. To end the conversation early, press Ctrl+C. The program will save the conversation and exit gracefully.

## Output

Conversations are saved in two formats:

1. JSON file for easy parsing and analysis
2. Markdown file for human-readable documentation

Both files are saved in the directory specified by `save_path` in the configuration.

## Model Recommendations

The Moderator works well with `wizardlm2`. Recommended Participant models include Meta's new `llama3.1`, `gemma2`, and `llama3`. You can customize the list of available models in the configuration file.

## Demonstration

![ConvOllama Example Conversation](/demo.png)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Transparency Disclaimer

[ai.collaboratedwith.me](ai.collaboratedwith.me) in creating this project.
