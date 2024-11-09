def truncate_message_with_notice(output:str, max_length:int = 1000, suffix:str = "Output was truncated") -> str:
    """Trim a long output string to a specified length and append a suffix message if truncation occurs"""

    total_max_length = max_length - len(suffix)  # Adjust for the suffix length
    
    # If the output is already shorter than the max length, return it as is
    if len(output) <= max_length:
        return output

    # Split the output into lines and add lines until the length exceeds the allowed maximum
    result = ""
    lines = output.splitlines()

    for line in lines:
        if len(result) + len(line) + 1 > total_max_length:  # +1 accounts for the line break
            break
        result += line + "\n"
    
    # Append the suffix message
    result += suffix
    return result