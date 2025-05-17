#!/usr/bin/env python3

import os
import re
import sys

# Files to clean
files_to_clean = [
    "ModelDocumentation/model-doc-agent/claude_direct.py",
    "ModelDocumentation/model-doc-agent/claude_test.py",
    "claude_agent_test.py",
    "claude_test.py",
    "simple_test.py",
    ".env"
]

# Patterns to replace
api_key_pattern = re.compile(r'sk-ant-api\w{4}-[A-Za-z0-9_\-]{64,}')
env_var_pattern = re.compile(r'ANTHROPIC_API_KEY=.*')

def clean_file(file_path):
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Replace API keys in Python files
        content_cleaned = api_key_pattern.sub('sk-ant-api****-************************', content)
        
        # Replace environment variables in .env files
        if file_path.endswith('.env'):
            content_cleaned = env_var_pattern.sub('ANTHROPIC_API_KEY=YOUR_API_KEY_HERE', content_cleaned)
        
        if content_cleaned != content:
            with open(file_path, 'w') as f:
                f.write(content_cleaned)
            print(f"Cleaned sensitive information from {file_path}")
            return True
        else:
            print(f"No sensitive information found in {file_path}")
            return False
    
    except Exception as e:
        print(f"Error cleaning {file_path}: {e}")
        return False

def main():
    cleaned_files = 0
    for file_path in files_to_clean:
        if clean_file(file_path):
            cleaned_files += 1
    
    print(f"\nCleaned {cleaned_files} file(s) of sensitive information.")
    print("Please review the changes before committing.")

if __name__ == "__main__":
    main() 