"""Utility functions for the command generator."""

import os
import re
import json
import time
import textwrap
from colorama import init, Fore, Style
from cmd_gen.config import MAX_FILES_PER_DIR, MAX_FILENAME_LENGTH

# Initialize colorama for cross-platform color support
init()

def print_styled(text, color=None, bold=False, end="\n"):
    """Print text with specified styling"""
    styled_text = ""
    if bold:
        styled_text += Style.BRIGHT
    if color:
        styled_text += color
    
    styled_text += text + Style.RESET_ALL
    print(styled_text, end=end)

def print_error(text):
    """Print error message"""
    print_styled(f"Error: {text}", Fore.RED)

def print_success(text):
    """Print success message"""
    print_styled(f"✓ {text}", Fore.GREEN)

def print_info(text):
    """Print info message"""
    print_styled(text, Fore.CYAN)

def print_warning(text):
    """Print warning message"""
    print_styled(text, Fore.YELLOW)

def print_thinking():
    """Show a thinking animation"""
    print_styled("Generating response", Fore.CYAN, end="")
    for _ in range(3):
        time.sleep(0.5)
        print_styled(".", Fore.CYAN, end="")
    print()

def get_directory_structure(root_dir=".", max_depth=None):
    """
    Get a token-efficient summary of the directory structure
    
    Args:
        root_dir: Starting directory
        max_depth: Maximum directory depth to scan
        
    Returns:
        String representation of directory structure
    """
    structure = []
    total_files = 0
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Skip hidden directories
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        
        level = dirpath.replace(root_dir, "").count(os.sep)
        
        # Skip if we've reached max depth
        if max_depth is not None and level > max_depth:
            continue
        
        if level == 0:
            dir_name = os.path.basename(root_dir) or '.'
        else:
            dir_name = os.path.basename(dirpath)
            
        # Skip hidden directories
        if dir_name.startswith('.'):
            continue
            
        indent = " " * 4 * level
        structure.append(f"{indent}{dir_name}/")
        
        # Limit number of files shown per directory
        limited_files = filenames[:MAX_FILES_PER_DIR]
        if len(filenames) > MAX_FILES_PER_DIR:
            more_files = len(filenames) - MAX_FILES_PER_DIR
            limited_files.append(f"... ({more_files} more files)")
            
        # Count total files for debugging
        total_files += len(filenames)
        
        sub_indent = " " * 4 * (level + 1)
        for filename in limited_files:
            # Skip hidden files
            if filename.startswith('.'):
                continue
                
            # Truncate long filenames
            if len(filename) > MAX_FILENAME_LENGTH:
                display_name = filename[:MAX_FILENAME_LENGTH-3] + "..."
            else:
                display_name = filename
                
            structure.append(f"{sub_indent}{display_name}")
    
    # If too many files, provide a summary instead
    if total_files > 100:
        structure.append(f"\nDirectory summary: {total_files} total files across {len(structure)} directories")
        
    return "\n".join(structure)

def clean_json_output(response_text):
    """
    Extract JSON from LLM response
    
    Args:
        response_text: The raw text response from the LLM
        
    Returns:
        Cleaned JSON string or None if no JSON found
    """
    # Try to find JSON between curly braces
    match = re.search(r'\{.*\}', response_text, re.DOTALL)
    if match:
        return match.group(0)
        
    # If no match, check if response is already valid JSON
    try:
        json.loads(response_text)
        return response_text
    except json.JSONDecodeError:
        return None

def display_command(command, description):
    """
    Display the generated command in a professional format
    
    Args:
        command: The shell command to display
        description: Description of what the command does
    """
    print()
    print_styled("COMMAND", Fore.BLUE, bold=True)
    print("─" * 50)
    wrapped_command = textwrap.fill(command, width=80)
    print_styled(wrapped_command, Fore.WHITE, bold=True)
    print("─" * 50)
    
    if description:
        print_styled("DESCRIPTION", Fore.BLUE, bold=True)
        print(description)
        print()

def display_answer(answer):
    """
    Display the answer to a question
    
    Args:
        answer: The answer to display
    """
    print()
    print_styled("ANSWER", Fore.GREEN, bold=True)
    print("─" * 50)
    wrapped_answer = textwrap.fill(answer, width=80)
    print_styled(wrapped_answer, Fore.WHITE)
    print("─" * 50)
    print()