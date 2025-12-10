"""
Final verification of Forks Over Knives transcript fix
"""
import json

# Load timeline data
with open('src/frontend/public/timeline.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

video_id = '5B8zyQ0oeGQ'

print("=" * 80)
print("FINAL VERIFICATION: Forks Over Knives Transcript")
print("=" * 80)

# Check each date
dates_with_video = []
for day in data:
    video_msgs = [m for m in day['messages'] if video_id in str(m.get('video_url', '')) and m.get('type') != 'transcript']
    transcript_msgs = [m for m in day['messages'] if video_id in str(m.get('video_url', '')) and m.get('type') == 'transcript']
    
    if video_msgs or transcript_msgs:
        dates_with_video.append({
            'date': day['date'],
            'video_count': len(video_msgs),
            'transcript_count': len(transcript_msgs),
            'transcript_length': len(transcript_msgs[0]['content']) if transcript_msgs else 0
        })

print(f"\nVideo appears on {len(dates_with_video)} different dates:")
print()

all_good = True
for info in dates_with_video:
    status = "✅" if info['video_count'] == 1 and info['transcript_count'] == 1 and info['transcript_length'] > 80000 else "❌"
    print(f"{status} {info['date']}")
    print(f"   Videos: {info['video_count']}, Transcripts: {info['transcript_count']}")
    print(f"   Transcript length: {info['transcript_length']:,} characters")
    
    if info['video_count'] != 1 or info['transcript_count'] != 1 or info['transcript_length'] < 80000:
        all_good = False
    print()

print("=" * 80)
if all_good:
    print("✅ SUCCESS! All video occurrences have proper transcripts!")
    print("   The transcript should now be visible on the live site.")
else:
    print("❌ ISSUE: Some dates are missing proper transcripts")
print("=" * 80)
