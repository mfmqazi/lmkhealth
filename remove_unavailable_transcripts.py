"""
Script to remove unavailable transcript entries from timeline.json
"""
import json

# Load timeline data
timeline_file = 'src/frontend/public/timeline.json'
with open(timeline_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Count before
total_before = sum(len(day['messages']) for day in data)
transcripts_before = sum(1 for day in data for m in day['messages'] if m.get('type') == 'transcript')

print(f"Before cleanup:")
print(f"  Total messages: {total_before}")
print(f"  Total transcripts: {transcripts_before}")

# Remove unavailable transcripts
removed_count = 0
for day in data:
    original_count = len(day['messages'])
    day['messages'] = [
        m for m in day['messages']
        if not (
            m.get('type') == 'transcript' and (
                '[Transcript Unavailable]' in m.get('content', '') or
                '[No transcript available]' in m.get('content', '') or
                '[Error' in m.get('content', '') or
                len(m.get('content', '')) < 100  # Remove very short transcripts
            )
        )
    ]
    removed_count += (original_count - len(day['messages']))

# Count after
total_after = sum(len(day['messages']) for day in data)
transcripts_after = sum(1 for day in data for m in day['messages'] if m.get('type') == 'transcript')

print(f"\nAfter cleanup:")
print(f"  Total messages: {total_after}")
print(f"  Total transcripts: {transcripts_after}")
print(f"  Removed: {removed_count} unavailable transcript(s)")

# Save cleaned data
with open(timeline_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n✓ Cleaned timeline saved to {timeline_file}")

# Verify Forks Over Knives transcript
forks_transcripts = [m for day in data for m in day['messages'] 
                     if m.get('type') == 'transcript' and '5B8zyQ0oeGQ' in str(m.get('video_url', ''))]

print(f"\nForks Over Knives verification:")
print(f"  Remaining transcripts: {len(forks_transcripts)}")
for i, t in enumerate(forks_transcripts, 1):
    print(f"  Transcript {i}: {len(t['content'])} characters")
