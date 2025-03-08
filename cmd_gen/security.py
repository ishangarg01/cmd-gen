"""Security features for the command generator."""

import re
from cmd_gen.config import BLOCKED_KEYWORDS
from cmd_gen.utils import print_error, print_warning

def validate_input(text):
    """
    Validate user input for potential security issues
    
    Args:
        text: User input to validate
        
    Returns:
        Boolean indicating if input is safe
    """
    # Check for common injection patterns
    injection_patterns = [
        r'\$\(\s*.*\s*\)',  # Command substitution $(...)
        r'`.*`',            # Backtick command execution
        r'eval\s*\(',       # eval() function
        r'system\s*\(',     # system() function
        r'exec\s*\(',       # exec() function
        r';\s*rm\s',        # Command chaining with rm
        r';\s*dd\s',        # Command chaining with dd
        r'--help',          # SQL injection attempts
        r'--.+',            # SQL comment syntax
        r"'--",             # SQL injection with quotes
        r'<script>',        # XSS attempt
    ]
    
    for pattern in injection_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            print_error(f"Potentially unsafe input detected: {text}")
            return False
            
    return True

def is_safe_command(command):
    """
    Check if a generated command is safe to execute
    
    Args:
        command: The command to check
        
    Returns:
        (boolean, string): Tuple of (is_safe, reason_if_unsafe)
    """
    # Check for blocked keywords
    for keyword in BLOCKED_KEYWORDS:
        if keyword in command.lower():
            return False, f"Command contains blocked keyword: {keyword}"
    
    # Check for potentially dangerous patterns
    dangerous_patterns = [
        # Detect potential file deletion/destruction
        (r'\brm\b.*-[rf]', "Command may delete files/directories"),
        (r'\bformat\b', "Command may format storage device"),
        
        # Detect potential privilege escalation
        (r'\bchmod\b.*777', "Command sets dangerous file permissions"),
        (r'\bsudo\b', "Command requires elevated privileges"),
        
        # Detect potential network exploitation
        (r'\bnc\b.*-e', "Command may open network backdoor"),
        (r'\btelnet\b', "Command uses insecure protocol"),
        
        # Detect destructive redirections 
        (r'>\s*/dev/', "Command writes directly to device files"),
        (r'>>\s*/etc/', "Command modifies system configuration files"),
        
        # Detect potential system modifications
        (r'\bfdisk\b', "Command may modify disk partitions"),
        (r'\bmkfs\b', "Command may format filesystem"),
        
        # Detect fork bombs and resource exhaustion
        (r':\(\){', "Command appears to be a fork bomb"),
        (r'while\s*true', "Command contains infinite loop")
    ]
    
    for pattern, reason in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            return False, reason
            
    return True, ""

def sanitize_filename(filename):
    """
    Sanitize a filename to prevent directory traversal
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove path separators and potentially dangerous characters
    sanitized = re.sub(r'[/\\]', '', filename)
    
    # Remove null bytes
    sanitized = sanitized.replace('\0', '')
    
    # Remove other potentially dangerous characters
    sanitized = re.sub(r'[<>:"|?*]', '', sanitized)
    
    return sanitized

def audit_command(command, description):
    """
    Audit a command before presenting it to the user
    
    Args:
        command: The command to audit
        description: The command description
        
    Returns:
        (boolean, string): Tuple of (is_safe, reason_if_unsafe or command_if_safe)
    """
    # First pass - check if command is obviously dangerous
    is_safe, reason = is_safe_command(command)
    if not is_safe:
        print_error(f"Unsafe command detected: {reason}")
        return False, reason
        
    # Second pass - check for potential data risks
    data_risk_patterns = [
        (r'\bgrep\b.*-r', "Command searches recursively - verify scope"),
        (r'\bfind\b.*-delete', "Command will delete files - verify scope"),
        (r'\bsed\b.*-i', "Command modifies files in-place - verify files"),
        (r'\bchown\b', "Command changes file ownership - verify impact")
    ]
    
    for pattern, warning in data_risk_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            print_warning(warning)
            
    return True, command