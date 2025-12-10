"""
Script to find all YouTube videos that don't have transcripts
"""
import json
import re

# Load timeline data
with open('src/frontend/public/timeline.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extract all video URLs
all_videos = {}
for day in data:
    for msg in day['messages']:
        video_url = msg.get('video_url')
        if video_url:
            # Extract video ID
            vid_match = re.search(r'(?:v=|youtu\.be/|embed/)([\\w\\-]+)', video_url)
            if vid_match:
                video_id = vid_match.group(1)
                if video_id not in all_videos:
                    all_videos[video_id] = {
                        'url': video_url,
                        'sender': msg.get('sender'),
                        'date': day.get('date'),
                        'has_transcript': False
                    }

# Find which videos have transcripts
for day in data:
    for msg in day['messages']:
        if msg.get('type') == 'transcript':
            video_url = msg.get('video_url')
            if video_url:
                vid_match = re.search(r'(?:v=|youtu\.be/|embed/)([\\w\\-]+)', video_url)
                if vid_match:
                    video_id = vid_match.group(1)
                    if video_id in all_videos:
                        all_videos[video_id]['has_transcript'] = True

# Filter videos without transcripts
videos_without_transcripts = {
    vid: info for vid, info in all_videos.items() 
    if not info['has_transcript']
}

print(f"Total unique videos: {len(all_videos)}")
print(f"Videos with transcripts: {sum(1 for v in all_videos.values() if v['has_transcript'])}")
print(f"Videos WITHOUT transcripts: {len(videos_without_transcripts)}")
print("=" * 80)

if videos_without_transcripts:
    print("\\nVideos missing transcripts:\\n")
    for i, (video_id, info) in enumerate(sorted(videos_without_transcripts.items(), key=lambda x: x[1]['date']), 1):
        print(f"{i}. {info['url']}")
        print(f"   Shared by: {info['sender']} on {info['date']}")
        print(f"   Video ID: {video_id}")
        print()
    
    # Save to file
    with open('videos_without_transcripts.txt', 'w', encoding='utf-8') as f:
        f.write("YouTube Videos Without Transcripts\\n")
        f.write("=" * 80 + "\\n\\n")
        for i, (video_id, info) in enumerate(sorted(videos_without_transcripts.items(), key=lambda x: x[1]['date']), 1):
            f.write(f"{i}. {info['url']}\\n")
            f.write(f"   Shared by: {info['sender']} on {info['date']}\\n")
            f.write(f"   Video ID: {video_id}\\n\\n")
    
    print(f"✓ List saved to videos_without_transcripts.txt")
else:
    print("\\n✓ All videos have transcripts!")
