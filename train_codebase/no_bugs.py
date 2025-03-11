
def safe_function(a, b):
    """A function with no bugs."""
    if b == 0:
        return None
    return a / b
    
def safe_list_operation(items, index):
    """A safe list operation with proper checks."""
    if not items or index < 0 or index >= len(items):
        return None
    return items[index]
