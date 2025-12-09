from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

videos = [
    {"title": "Forks Over Knives", "id": "5B8zyQ0oeGQ"},
    {"title": "Is Milk Good For Our Bones", "id": "rxnBDDqXSjk"}
]

formatter = TextFormatter()

succeeded_text = ""

for video in videos:
    print(f"Attempting to fetch transcript for: {video['title']} ({video['id']})")
    try:
        # Use list_transcripts to find available ones (including auto-generated)
        transcript_list = YouTubeTranscriptApi.list_transcripts(video['id'])
        
        # Try to fetch manually created English, then auto-generated English
        try:
            transcript = transcript_list.find_manually_created_transcript(['en'])
        except:
            try:
                transcript = transcript_list.find_generated_transcript(['en'])
            except:
                # Fallback to any available English translation or just the first one
                print(f"No direct English transcript found for {video['id']}, trying first available...")
                transcript = next(iter(transcript_list))

        formatted_text = formatter.format_transcript(transcript.fetch())
        
        entry = f"\n\n================================================================\n"
        entry += f"[Video Transcript] {video['title']}\n"
        entry += f"URL: https://youtu.be/{video['id']}\n"
        entry += f"================================================================\n"
        entry += f"{formatted_text}\n"
        
        succeeded_text += entry
        print("Success!")
        
    except Exception as e:
        print(f"Failed: {e}")

if succeeded_text:
    # Append to transcripts file
    with open("youtube_transcripts.txt", "a", encoding="utf-8") as f:
        f.write(succeeded_text)
    
    # Append to chat backup
    with open("chat_backup.txt", "a", encoding="utf-8") as f:
        f.write(succeeded_text)
    
    print("Appended successful transcripts to youtube_transcripts.txt and chat_backup.txt")
else:
    print("No transcripts were fetched.")
