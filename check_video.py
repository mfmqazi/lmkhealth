import requests

data = requests.get('http://localhost:8000/api/timeline').json()
items = [(m.get('video_url'), m.get('type'), m.get('sender')) 
         for day in data 
         for m in day['messages'] 
         if '5B8zyQ0oeGQ' in str(m.get('video_url', ''))]

for sender, msg_type, url in items:
    print(f"{sender:20} {msg_type:12} {url}")
