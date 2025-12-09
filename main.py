import os
import sys
import time
from src.scraper import WhatsAppScraper
from src.media_handler import process_messages
from src.rag_engine import RAGSystem
from dotenv import load_dotenv

def main():
    load_dotenv()
    
    print("----------------------------------------------------------------")
    print("WhatsApp Chat RAG System (Auto-Connect + Multimedia)")
    print("----------------------------------------------------------------")
    
    # Check Keys
    google_key = os.getenv("GOOGLE_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    if not google_key or not groq_key:
        print("Error: Please set GOOGLE_API_KEY and GROQ_API_KEY in .env file.")
        return

    # 0. Check for Backup
    full_text = ""
    if os.path.exists("chat_backup.txt"):
        use_backup = input("Found 'chat_backup.txt'. Use it instead of scraping? (y/n): ").lower()
        if use_backup == 'y':
            with open("chat_backup.txt", "r", encoding="utf-8") as f:
                full_text = f.read()
            print("Loaded messages from backup.")

    # 1. Scrape (if not using backup)
    if not full_text:
        print("Starting WhatsApp Scraper...")
        scraper = WhatsAppScraper()
        raw_messages = []
        try:
            scraper.connect() # Opens browser, waits for user
            
            do_scroll = input("Do you want to scroll up to load more history? (y/n): ").lower()
            if do_scroll == 'y':
                scroll_conf = input("How many times to scroll (approx 20 msgs per scroll)? [Default: 20]: ")
                limit = int(scroll_conf) if scroll_conf.isdigit() else 20
                scraper.scroll_to_top(limit_videos=limit)
                
            print("Scraping now...")
            raw_messages = scraper.scrape_current_chat()
            print(f"Scraped {len(raw_messages)} raw messages.")
            
        except Exception as e:
            print(f"Scraping Error: {e}")
            return
        finally:
            keep_open = input("Keep browser open? (y/n): ").lower()
            if keep_open != 'y':
                scraper.close()

        if not raw_messages:
            print("No messages found. Exiting.")
            return

        # 2. Process (Transcripts etc)
        print("Processing messages (fetching YouTube transcripts, etc)...")
        full_text = process_messages(raw_messages)
        
        # Save a backup
        with open("chat_backup.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
        print("Saved enriched chat log to 'chat_backup.txt'.")

    # 3. Initialize RAG
    print("Initializing RAG engine...")
    try:
        rag = RAGSystem(google_api_key=google_key, groq_api_key=groq_key)
        rag.ingest_data(full_text)
        rag.setup_chain()
    except Exception as e:
        print(f"Error initializing RAG: {e}")
        return

    # 4. Chat Loop
    print("\n----------------------------------------------------------------")
    print("System Ready! Ask questions about your chat.")
    print("----------------------------------------------------------------\n")
    
    while True:
        try:
            query = input("You: ")
            if query.lower() in ['exit', 'quit']:
                break
            if not query.strip(): continue
            
            print("Thinking...")
            answer = rag.query(query)
            print(f"\nAI: {answer}\n")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
