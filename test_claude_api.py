#!/usr/bin/env python3

import os
import sys
from anthropic import Anthropic

def test_claude_api():
    """Simple function to test if the Claude API key is working."""
    try:
        print("Testing Claude API connection...")
        
        # Get API key from environment variable
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not set.")
            return False
        
        # Initialize the client
        client = Anthropic(api_key=api_key)
        
        # Make a simple API call
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say hello and confirm the API is working"}
            ]
        )
        
        # Print the response
        print("\nAPI Response:")
        print(message.content[0].text)
        print("\nSuccess! Your Claude API key is working correctly.")
        return True
    
    except Exception as e:
        print(f"\nError testing Claude API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_claude_api()
    sys.exit(0 if success else 1) 

import os
import sys
from anthropic import Anthropic

def test_claude_api():
    """Simple function to test if the Claude API key is working."""
    try:
        print("Testing Claude API connection...")
        
        # Get API key from environment variable
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: ANTHROPIC_API_KEY environment variable not set.")
            return False
        
        # Initialize the client
        client = Anthropic(api_key=api_key)
        
        # Make a simple API call
        message = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "Say hello and confirm the API is working"}
            ]
        )
        
        # Print the response
        print("\nAPI Response:")
        print(message.content[0].text)
        print("\nSuccess! Your Claude API key is working correctly.")
        return True
    
    except Exception as e:
        print(f"\nError testing Claude API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_claude_api()
    sys.exit(0 if success else 1) 