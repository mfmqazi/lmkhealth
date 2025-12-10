"""
Debug script to check the exact structure of Forks Over Knives messages
"""
import json

# Load timeline data
with open('src/frontend/public/timeline.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Find all messages related to Forks Over Knives
video_id = '5B8zyQ0oeGQ'
print(f"Looking for video ID: {video_id}")
print("=" * 80)

for day_idx, day in enumerate(data):
    day_messages = []
    for msg_idx, msg in enumerate(day['messages']):
        video_url = msg.get('video_url', '')
        if video_id in str(video_url):
            day_messages.append((msg_idx, msg))
    
    if day_messages:
        print(f"\nDate: {day['date']}")
        print(f"Found {len(day_messages)} message(s) with this video")
        print("-" * 80)
        
        for msg_idx, msg in day_messages:
            print(f"\nMessage Index: {msg_idx}")
            print(f"  Type: {msg.get('type')}")
            print(f"  Sender: {msg.get('sender')}")
            print(f"  Time: {msg.get('time')}")
            print(f"  video_url: {msg.get('video_url')}")
            print(f"  Content length: {len(msg.get('content', ''))}")
            print(f"  Content preview: {msg.get('content', '')[:100]}")
            
            # Check if there's a transcript immediately after this message
            if msg.get('type') != 'transcript' and msg_idx + 1 < len(day['messages']):
                next_msg = day['messages'][msg_idx + 1]
                if next_msg.get('type') == 'transcript':
                    print(f"  ✓ Next message IS a transcript")
                else:
                    print(f"  ✗ Next message is NOT a transcript (type: {next_msg.get('type')})")

print("\n" + "=" * 80)
print("\nChecking if transcript and video are in the SAME day:")

# Group by date
for day in data:
    video_msgs = [m for m in day['messages'] if video_id in str(m.get('video_url', '')) and m.get('type') != 'transcript']
    transcript_msgs = [m for m in day['messages'] if video_id in str(m.get('video_url', '')) and m.get('type') == 'transcript']
    
    if video_msgs or transcript_msgs:
        print(f"\nDate: {day['date']}")
        print(f"  Video messages: {len(video_msgs)}")
        print(f"  Transcript messages: {len(transcript_msgs)}")
        
        if video_msgs and not transcript_msgs:
            print(f"  ⚠ WARNING: Video exists but NO transcript in this day!")
        elif transcript_msgs and not video_msgs:
            print(f"  ⚠ WARNING: Transcript exists but NO video in this day!")
