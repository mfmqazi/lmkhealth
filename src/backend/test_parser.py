from parser import ChatParser
import os

chat_path = r"c:\Users\Musaddique Qazi\.gemini\antigravity\playground\spinning-quasar\chat_backup.txt"

print(f"Testing parser with: {chat_path}")
try:
    parser = ChatParser(chat_path)
    data = parser.parse()
    if len(data) > 0:
        last_day = data[-1]
        last_msg = last_day['messages'][-1]
        content = last_msg['content']
        print(f"Last message length: {len(content)}")
        print("Contains '12 Point Guidelines'?", "12 Point Guidelines" in content)
        print("Contains 'Video Transcript'?", "[Video Transcript]" in content)
        print("Ends with:", content[-100:])
    else:
        print("No data parsed.")
except Exception as e:
    print(f"FAILED: {e}")
