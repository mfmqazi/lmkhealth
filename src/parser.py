import re
import pandas as pd
from datetime import datetime

def parse_whatsapp_chat(file_path):
    """
    Parses a WhatsApp chat export file into a list of documents.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Regex patterns for different WhatsApp formats
    # Format 1: 12/25/23, 8:00 PM - User: Message
    pattern1 = r'^(\d{1,2}/\d{1,2}/\d{2,4}, \s?\d{1,2}:\d{2}\s?[APap]?[Mm]?) - (.*?): (.*)$'
    
    # Format 2: [25/12/23, 20:00:00] User: Message
    pattern2 = r'^\[(\d{1,2}/\d{1,2}/\d{2,4}, \s?\d{1,2}:\d{2}:\d{2})\] (.*?): (.*)$'

    messages = []
    current_message = ""
    current_date = ""
    current_sender = ""
    
    # Detect format based on first few lines
    regex = None
    for line in lines[:20]:
        if re.match(pattern1, line):
            regex = pattern1
            print("Detected Format 1: MM/DD/YY, HH:MM AM/PM - User: Message")
            break
        elif re.match(pattern2, line):
            regex = pattern2
            print("Detected Format 2: [DD/MM/YY, HH:MM:SS] User: Message")
            break
            
    if not regex:
        # Fallback for continuing lines or unknown format (naive handling)
        print("Could not autodect standard format. Assuming simple line-by-line or custom format.")
        regex = pattern1 # Default to try

    for line in lines:
        line = line.strip()
        match = re.match(regex, line)
        if match:
            # Save previous message
            if current_message:
                messages.append({
                    'date': current_date,
                    'sender': current_sender,
                    'message': current_message
                })
            
            # Start new message
            current_date = match.group(1)
            current_sender = match.group(2)
            current_message = match.group(3)
        else:
            # Append to previous message (multiline messages)
            if current_message:
                current_message += "\n" + line

    # Append last message
    if current_message:
        messages.append({
            'date': current_date,
            'sender': current_sender,
            'message': current_message
        })

    return messages

def formatting_for_context(messages):
    """
    Converts list of message dicts into a single string or chunks for LLM.
    """
    formatted_text = ""
    for msg in messages:
        formatted_text += f"[{msg['date']}] {msg['sender']}: {msg['message']}\n"
    return formatted_text

if __name__ == "__main__":
    # Test with a dummy file if run directly
    pass
