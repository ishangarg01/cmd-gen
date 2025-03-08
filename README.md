# Command Generator (cmd-gen)

Generate shell commands from natural language using AI.

## Features

- Convert natural language to shell commands
- Get short answers to questions about your project
- Context-aware: uses your directory structure to generate relevant commands
- Security-focused: filters out potentially dangerous commands
- Interactive input collection for commands that need customization

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/cmd-gen.git
cd cmd-gen

# Install the package
pip install -e .
```

## Usage

```bash
# Generate a command
cmd-gen "Create a new Python virtual environment"

# Ask a question about your project
cmd-gen "What files are in my project?"

# For help
cmd-gen --help
```

## Configuration

Create a `.env` file in your project directory with your API key:

```
GEMINI_API_KEY=your_api_key_here
```

## Security Features

- Input validation to prevent injection attacks
- Command auditing to block potentially dangerous operations
- Directory traversal protection
- Blocklist for high-risk commands

## License

MIT