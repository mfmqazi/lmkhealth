from src.backend.parser import ChatParser
import os
import json
import traceback

CHAT_FILE = r"c:\Users\Musaddique Qazi\.gemini\antigravity\playground\spinning-quasar\chat_backup.txt"
ORIGINAL_CHAT_FILE = r"c:\Users\Musaddique Qazi\.gemini\antigravity\playground\spinning-quasar\whatsapp_export\extracted\_chat.txt"
IMAGES_DIR = r"c:\Users\Musaddique Qazi\.gemini\antigravity\playground\spinning-quasar\whatsapp_export\extracted"

def debug():
    print("Starting debug...", flush=True)
    try:
        if not os.path.exists(CHAT_FILE):
            print(f"Chat file not found: {CHAT_FILE}")
            return

        parser = ChatParser(CHAT_FILE, IMAGES_DIR, ORIGINAL_CHAT_FILE)
        print(f"Parser initialized. File size: {os.path.getsize(CHAT_FILE)} bytes", flush=True)
        
        print("Parsing...", flush=True)
        timeline = parser.parse()
        print(f"Parse complete. Found {len(timeline)} days.", flush=True)
        
        total_messages = 0
        text_count = 0
        image_count = 0
        video_count = 0
        
        for day in timeline:
            print(f"Date: {day['date']}, Messaages: {len(day['messages'])}")
            for msg in day['messages']:
                total_messages += 1
                if msg['type'] == 'text':
                    text_count += 1
                    if msg.get('is_video'):
                        video_count += 1
                elif msg['type'] == 'image':
                    image_count += 1
                    
        print(f"Total: {total_messages}")
        print(f"Text: {text_count}")
        print(f"Images: {image_count}")
        print(f"Videos: {video_count}")
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    debug()
