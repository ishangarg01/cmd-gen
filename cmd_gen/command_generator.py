"""Core functionality for generating commands."""

import json
from cmd_gen.config import COMMAND_ANALYSIS_TEMPLATE, COMMAND_FINALIZATION_TEMPLATE, MAX_DIR_DEPTH
from cmd_gen.llm_client import LLMClient
from cmd_gen.utils import get_directory_structure, print_error
from cmd_gen.security import audit_command, validate_input

class CommandGenerator:
    """Generator for shell commands from natural language"""
    
    def __init__(self):
        """Initialize the command generator"""
        self.llm_client = LLMClient()
        
    def analyze_request(self, prompt):
        """
        Analyze a user request to determine if it's a command request or question
        
        Args:
            prompt: The natural language prompt from the user
            
        Returns:
            Dictionary with analysis results or None on failure
        """
        # Validate input for security issues
        if not validate_input(prompt):
            return None
            
        # Get directory structure for context
        directory_structure = get_directory_structure(".", max_depth=MAX_DIR_DEPTH)
        
        # Format the prompt template
        full_prompt = COMMAND_ANALYSIS_TEMPLATE.format(
            directory_structure=directory_structure,
            prompt=prompt
        )
        
        # Generate the response
        return self.llm_client.generate_response(full_prompt)
    
    def generate_command_with_inputs(self, command_template, user_inputs):
        """
        Generate the final command with user inputs
        
        Args:
            command_template: The command template with placeholders
            user_inputs: Dictionary of user inputs
            
        Returns:
            Tuple of (command, description) or (None, None) on failure
        """
        # Get directory structure for context
        directory_structure = get_directory_structure(".", max_depth=MAX_DIR_DEPTH)
        
        # Format the prompt template
        full_prompt = COMMAND_FINALIZATION_TEMPLATE.format(
            directory_structure=directory_structure,
            command_template=command_template,
            user_inputs=json.dumps(user_inputs)
        )
        
        # Generate the response
        response = self.llm_client.generate_response(full_prompt)
        
        if response:
            command = response.get("command")
            description = response.get("description")
            
            # Audit the command for safety
            is_safe, result = audit_command(command, description)
            if is_safe:
                return command, description
            else:
                print_error(f"Generated command was rejected: {result}")
                return None, None
        
        return None, None