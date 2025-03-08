"""Configuration settings for the command generator."""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# LLM Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_MODEL = "gemini-2.0-flash"

# Application Settings
APP_NAME = "Command Generator"
MAX_RESPONSE_LENGTH = 50  # Maximum word length for non-command responses
MAX_DIR_DEPTH = 2  # Maximum directory depth to scan
MAX_FILES_PER_DIR = 10  # Maximum number of files to include per directory
MAX_FILENAME_LENGTH = 30  # Maximum length of filenames to include

# Security Settings
BLOCKED_KEYWORDS = [
    "rm -rf", ":(){ :|:& };:", "mkfs", "dd if=/dev/zero", 
    "chmod -R 777", "wget", "curl", "> /dev/sda",
    "sudo", "su -", "passwd", "/etc/shadow", "/etc/passwd",
    "format", "del /f", "deltree", "rd /s", "iptables"
]

# Prompt Templates
COMMAND_ANALYSIS_TEMPLATE = """
Here's a summary of the current project directory structure (limited to maintain token count):

{directory_structure}

Based on this structure summary, analyze the following request and determine if it requires user input to generate a proper command.
First, determine if this is a request for a command or just a general question. 
Return a JSON object with the following structure:

{{
  'is_command_request': true/false,
  'command': 'shell command to execute (with placeholders if user input is needed)',
  'description': 'brief description of what the command does (10 words or less)',
  'requires_input': true/false,
  'inputs': [array of input prompts to ask the user] (empty if no input required),
  'input_description': 'A brief explanation of what inputs are needed and why (only if requires_input is true)',
  'is_question': true/false (true if this is a general question, not a command request),
  'answer': 'brief answer to the question (max 50 words)' (only if is_question is true)
}}

IMPORTANT: If the user's request is ambiguous but appears to be asking about information you can give based on the context you have about the directory or files, assume it's a question (is_question=true) rather than a command request.
IMPORTANT: "How" is a good indicator that user is asking for commands most of the time.
IMPORTANT: Take a lot of input (ex: asking for commit message, repo link)
IMPORTANT: If you are not sure about the directory/files/folder the user wants to talk about assume the one you are currently in"

VERY IMPORTANT: Use ONLY double quotes in your JSON, not single quotes. Escape any double quotes inside strings with a backslash (\\").
ONLY return the JSON, nothing else.


Request: {prompt}
"""

COMMAND_FINALIZATION_TEMPLATE = """
Here's a summary of the current project directory structure:

{directory_structure}

Based on this structure, I have a command that requires user input.
Command template: {command_template}
User provided inputs: {user_inputs}

Generate the final command with the user inputs properly inserted.
Return a JSON object with 'command' and 'description' fields.
ONLY return the JSON, nothing else.
"""