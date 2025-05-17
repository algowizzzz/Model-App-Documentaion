"""
This is a test file containing various Python structures for parsing tests.
"""

from typing import List, Dict, Optional

def simple_function(param1: str, param2: int = 42) -> str:
    """A simple function with type hints and default parameter.
    
    Args:
        param1: First parameter
        param2: Second parameter with default value
        
    Returns:
        A greeting string
    """
    return f"Hello {param1}, your number is {param2}"

class TestClass:
    """A test class with methods and nested structures."""
    
    def __init__(self, value: int):
        """Initialize with a value."""
        self.value = value
    
    def outer_method(self, x: List[int]) -> Dict[str, int]:
        """A method containing a nested function.
        
        Args:
            x: List of integers
            
        Returns:
            Dictionary with processed values
        """
        def nested_function(items: List[int]) -> int:
            """Nested function example."""
            return sum(items)
        
        return {
            "sum": nested_function(x),
            "original_value": self.value
        }
    
    @property
    def doubled_value(self) -> int:
        """A property decorator example."""
        return self.value * 2

# A global variable
GLOBAL_CONSTANT: str = "test"

if __name__ == "__main__":
    # Some test code
    test = TestClass(10)
    result = test.outer_method([1, 2, 3])
    print(result) 