import os
import re
import glob
import webvtt
from yt_dlp import YoutubeDL

def parse_markdown_links(md_file_path):
    """
    Extracts (Title, URL) tuples from a markdown file.
    Expects format: 
    1. **Title**
       - URL
    """
    links = []
    current_title = None
    
    with open(md_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for line in lines:
        line = line.strip()
        # Match title: digit. **Title**
        title_match = re.match(r'^\d+\.\s*\*\*(.+)\*\*$', line)
        if title_match:
            current_title = title_match.group(1)
            continue
            
        # Match URL: - https://...
        if line.startswith('- https://') or line.startswith('- http://'):
            url = line.lstrip('- ').strip()
            if current_title:
                links.append({'title': current_title, 'url': url})
                current_title = None # Reset for next
    
    return links

def download_and_extract_transcript(url, output_dir):
    """
    Downloads subtitles for a video and returns the text content.
    """
    ydl_opts = {
        'skip_download': True,
        'format': 'best', # Explicitly ask for best format even if skipping download 
        'writeautomaticsub': True,
        'writesubtitles': True,
        'subtitleslangs': ['en'],
        'outtmpl': os.path.join(output_dir, '%(id)s'),
        'quiet': True,
        'no_warnings': True,
        'ignoreerrors': True,
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                print(f"Skipping {url}: Could not extract info (likely restricted).")
                return "[Transcript Unavailable]"
                
            video_id = info['id']
            
            # Find the downloaded .vtt file
            # yt-dlp usually names it video_id.en.vtt or video_id.en.srv3 etc
            potential_files = glob.glob(os.path.join(output_dir, f"{video_id}*.vtt"))
            
            if not potential_files:
                return "[No transcript available]"
            
            vtt_file = potential_files[0]
            
            # Extract text from VTT
            transcript_text = ""
            try:
                for caption in webvtt.read(vtt_file):
                    # Simple deduplication (often VTT has scrolling duplicates)
                    text = caption.text.strip()
                    # Remove timestamps and newlines
                    text = text.replace('\n', ' ')
                    transcript_text += text + " "
            except Exception as e:
                print(f"Error parsing VTT for {url}: {e}")
                return "[Error parsing transcript]"
            
            # Cleanup: remove the vtt file
            os.remove(vtt_file)
            
            return transcript_text.strip()
            
    except Exception as e:
        print(f"Error downloading for {url}: {e}")
        return f"[Error fetching: {e}]"

def main():
    links_file = "youtube_links.md"
    output_file = "youtube_transcripts.txt"
    temp_dir = "temp_transcripts"
    
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
        
    print(f"Parsing links from {links_file}...")
    videos = parse_markdown_links(links_file)
    print(f"Found {len(videos)} videos.")
    
    all_content = ""
    
    for i, video in enumerate(videos):
        print(f"[{i+1}/{len(videos)}] Fetching transcript for: {video['title']}")
        transcript = download_and_extract_transcript(video['url'], temp_dir)
        
        # Clean up text slightly (remove multiple spaces)
        transcript = re.sub(r'\s+', ' ', transcript)
        
        entry = f"\n\n================================================================\n"
        entry += f"[Video Transcript] {video['title']}\n"
        entry += f"URL: {video['url']}\n"
        entry += f"================================================================\n"
        entry += f"{transcript}\n"
        
        all_content += entry
        
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(all_content)
        
    print(f"Done. Saved all transcripts to {output_file}")
    
    # Cleanup temp dir
    try:
        os.rmdir(temp_dir)
    except:
        pass

if __name__ == "__main__":
    main()
