from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs

def extract_video_id(url):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None

def get_video_transcript(video_url):
    video_id = extract_video_id(video_url)
    if not video_id:
        return ""
    
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Combine text
        full_text = " ".join([t['text'] for t in transcript_list])
        return f"[Transcribed Video Content]: {full_text}"
    except Exception as e:
        return f"[Could not get transcript for video: {e}]"

def process_messages(messages):
    """
    Takes raw scraped messages and enriches them.
    """
    processed_text = ""
    
    for msg in messages:
        # Metadata usually looks like "[10:00, 1/1/2024] Name: "
        # We clean it slightly
        header = msg.get('metadata', '').strip()
        content = msg.get('text', '').strip()
        links = msg.get('links', [])
        
        # Append base message
        entry = f"{header} {content}\n"
        
        # Check links for YouTube
        for link in links:
            if 'youtube.com' in link or 'youtu.be' in link:
                print(f"Found YouTube link: {link} - Fetching transcript...")
                transcript = get_video_transcript(link)
                entry += f"\n   >>> {transcript}\n"
        
        processed_text += entry + "\n"
        
    return processed_text
