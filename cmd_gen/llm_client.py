"""LLM client for generating responses."""

import json
import sys
import re
from google import genai
from cmd_gen.config import GEMINI_API_KEY, DEFAULT_MODEL
from cmd_gen.utils import clean_json_output, print_error, print_thinking

class LLMClient:
    """Client for interacting with LLM APIs"""
    
    def __init__(self, api_key=None, model=None):
        """
        Initialize the LLM client
        
        Args:
            api_key: API key for the LLM service
            model: Model name to use for generation
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model = model or DEFAULT_MODEL
        
        if not self.api_key:
            print_error("API key not found. Please set GEMINI_API_KEY in your .env file.")
            sys.exit(1)
            
        try:
            self.client = genai.Client(api_key=self.api_key)
        except Exception as e:
            print_error(f"Failed to initialize LLM client: {str(e)}")
            sys.exit(1)
    
    def fix_json_string(self, json_str):
        """
        Fix common JSON formatting issues in LLM responses
        
        Args:
            json_str: The JSON string to fix
            
        Returns:
            Fixed JSON string
        """
        try:
            # If it's already valid JSON, return it
            json.loads(json_str)
            return json_str
        except:
            pass
            
        # Replace outer single quotes with double quotes for keys
        json_str = re.sub(r"'([^']*)':", r'"\1":', json_str)
        
        # Replace inner single quotes with double quotes for string values
        json_str = re.sub(r': \'([^\']*)\'', r': "\1"', json_str)
        
        # Handle special cases for true, false, null
        json_str = json_str.replace("'true'", "true")
        json_str = json_str.replace("'false'", "false")
        json_str = json_str.replace("'null'", "null")
        json_str = json_str.replace("None", "null")
        
        # Handle single-quoted arrays
        def fix_arrays(match):
            inner = match.group(1)
            # Replace single quotes with double quotes, but only for strings
            inner = re.sub(r"'([^']*)'", r'"\1"', inner)
            return f"[{inner}]"
            
        json_str = re.sub(r'\[(.*?)\]', fix_arrays, json_str)
        
        # Handle escaped inner quotes in command strings
        def fix_commands(match):
            cmd = match.group(1)
            # Escape any double quotes inside the command
            cmd = cmd.replace('"', '\\"')
            return f'"{cmd}"'
        
        # Find command entries and escape their inner quotes
        json_str = re.sub(r'"command": "([^"]*)"', lambda m: f'"command": "{m.group(1).replace("\"", "\\\"")}"', json_str)
        
        return json_str
    
    def generate_response(self, prompt, show_thinking=True, debug=False):
        """
        Generate a response from the LLM
        
        Args:
            prompt: The prompt to send to the LLM
            show_thinking: Whether to show thinking animation
            debug: Whether to show debug information
            
        Returns:
            JSON response object or None on failure
        """
        if show_thinking:
            print_thinking()
            
        try:
            response = self.client.models.generate_content(
                model=self.model, contents=prompt
            )
            
            cleaned_json = clean_json_output(response.text.strip())
            
            if debug:
                print("DEBUG - Raw LLM response:")
                print(f"```\n{response.text.strip()}\n```")
            
            if cleaned_json:
                try:
                    # Try to fix the JSON
                    fixed_json = self.fix_json_string(cleaned_json)
                    
                    if debug:
                        print("DEBUG - Fixed JSON:")
                        print(f"```\n{fixed_json}\n```")
                    
                    # If all else fails, use ast.literal_eval as a more forgiving parser
                    try:
                        result = json.loads(fixed_json)
                    except:
                        import ast
                        result = ast.literal_eval(cleaned_json)
                        # Convert to proper Python types
                        result = json.loads(json.dumps(result))
                    
                    return result
                except Exception as e:
                    if debug:
                        print(f"DEBUG - JSON decode error: {str(e)}")
                        print(f"DEBUG - Attempted to parse: {fixed_json}")
                    print_error("Could not parse the LLM response as JSON. Please try again.")
                    return None
            else:
                print_error("Could not generate a valid response. Please try rephrasing your request.")
                return None
                
        except Exception as e:
            print_error(f"LLM connection error: {str(e)}")
            return None