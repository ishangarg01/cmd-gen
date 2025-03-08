"""Command line interface for the command generator."""

import sys
import argparse
import textwrap
import pyperclip
from cmd_gen import __version__
from cmd_gen.command_generator import CommandGenerator
from cmd_gen.utils import (
    print_styled, print_error, print_success, print_info,
    display_command, display_answer
)
from colorama import Fore

def create_parser():
    """
    Create the argument parser for the CLI
    
    Returns:
        ArgumentParser object
    """
    parser = argparse.ArgumentParser(
        description="Generate shell commands or get answers from natural language requests.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          cmd-gen "Create a new Python virtual environment"
          cmd-gen "Push my current directory to GitHub"
          cmd-gen "Find all .jpg files and compress them"
          cmd-gen "What files are in my project?"
        """)
    )
    
    parser.add_argument("prompt", type=str, help="What you want to do in natural language")
    parser.add_argument("-v", "--version", action="version", version=f"Command Generator v{__version__}")
    parser.add_argument("-q", "--quiet", action="store_true", help="Minimal output mode")
    parser.add_argument("-d", "--debug", action="store_true", help="Show debug information")
    
    return parser

def handle_command_request(generator, requirements, quiet=False):
    """
    Handle a command generation request
    
    Args:
        generator: CommandGenerator instance
        requirements: Dictionary of command requirements
        quiet: Whether to minimize output
        
    Returns:
        Boolean indicating success
    """
    # Check if user input is required
    if requirements.get('requires_input', False):
        # Display input description before asking for inputs
        print()
        print_styled("INPUT REQUIRED", Fore.YELLOW, bold=True)
        
        # Get the input description or use a default one
        input_description = requirements.get('input_description', 
                                          "Please provide the following information to complete the command:")
        
        # Print the input description with proper formatting
        wrapped_description = textwrap.fill(input_description, width=80)
        print(wrapped_description)
        print()
        
        # Collect user inputs
        user_inputs = {}
        for input_prompt in requirements.get('inputs', []):
            user_response = input(f"  {input_prompt}: ").strip()
            user_inputs[input_prompt] = user_response
            
        # Generate the final command with user inputs
        command, description = generator.generate_command_with_inputs(
            requirements.get('command'), user_inputs
        )
    else:
        # No user input required, use the command directly
        command = requirements.get('command')
        description = requirements.get('description')
    
    if command:
        display_command(command, description)
        
        copy_choice = input("\nCopy to clipboard? [Y/n]: ").strip().lower()
        if not copy_choice or copy_choice == 'y':
            pyperclip.copy(command)
            print_success("Command copied to clipboard!")
        return True
    else:
        if not quiet:
            print_error("Failed to generate command. Please try again with a clearer request.")
        return False

def handle_question_request(requirements, quiet=False):
    """
    Handle a question request
    
    Args:
        requirements: Dictionary with question response
        quiet: Whether to minimize output
        
    Returns:
        Boolean indicating success
    """
    answer = requirements.get('answer')
    if answer:
        display_answer(answer)
        return True
    else:
        if not quiet:
            print_error("Failed to generate an answer. Please try again with a clearer question.")
        return False

def main():
    """Main CLI entry point"""
    parser = create_parser()
    args = parser.parse_args()
    
    try:
        if not args.quiet:
            print_styled("Command Generator", Fore.BLUE, bold=True)
            print_styled("Analyzing your request...", Fore.CYAN)
        
        # Create command generator
        generator = CommandGenerator()
        
        # Update the CommandGenerator to pass the debug flag
        if hasattr(generator.llm_client, 'generate_response'):
            original_generate_response = generator.llm_client.generate_response
            
            def modified_generate_response(prompt, show_thinking=True):
                return original_generate_response(prompt, show_thinking, args.debug)
                
            generator.llm_client.generate_response = modified_generate_response
        
        # Analyze the request
        requirements = generator.analyze_request(args.prompt)
        
        if requirements:
            if requirements.get('is_command_request', False):
                # Handle command request
                return handle_command_request(generator, requirements, args.quiet)
            elif requirements.get('is_question', False):
                # Handle question request
                return handle_question_request(requirements, args.quiet)
            else:
                if not args.quiet:
                    print_error("Could not determine request type. Please be more specific.")
                return False
        else:
            # Error already displayed by the analysis function
            return False
            
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(130)  # 130 is the standard exit code for SIGINT
    except Exception as e:
        print_error(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(0 if main() else 1)