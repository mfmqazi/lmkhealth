import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

class WhatsAppScraper:
    def __init__(self):
        self.driver = None
        
    def setup_driver(self):
        options = webdriver.ChromeOptions()
        # Path to user data to persist session
        # options.add_argument("user-data-dir=./selenium_data_v3") 
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        # options.add_argument("--headless") # CANNOT use headless for QR scan
        
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    def connect(self):
        if not self.driver:
            self.setup_driver()
            
        print("Opening WhatsApp Web...")
        self.driver.get("https://web.whatsapp.com")
        
        print("\n" + "="*50)
        print("ACTION REQUIRED: Please scan the QR code with your phone.")
        print("After scanning, click on the specific Chat/Group you want to scrape.")
        print("Type 'y' in this console when the chat is open and loaded.")
        print("="*50 + "\n")
        
        # Wait for user confirmation
        while True:
            ready = input("Is the chat open? (y/n): ").strip().lower()
            if ready == 'y':
                break

    def scroll_to_top(self, limit_videos=5):
        """
        Scrolls up to load more messages.
        Attempt to scroll until a certain number of messages or user interruption.
        """
        print("Scrolling up to load history... (This can take a while)")
        print("Press Ctrl+C in the terminal if you want to stop scrolling and start scraping.")
        
        # Locate the message container. It usually has role="application" or is the main pane.
        try:
            # Better strategy for general scrolling:
            # Just look for the 'main' element
            main_element = self.driver.find_element(By.CSS_SELECTOR, '#main')
            # The scrollable div is usually a child of main.
            scrollable_div = main_element.find_element(By.CSS_SELECTOR, 'div[class*="copyable-area"] > div[tabindex="0"]')
            
            for i in range(limit_videos): 
                self.driver.execute_script("arguments[0].scrollTop = 0;", scrollable_div)
                time.sleep(1.5) # Wait for load (slightly increased)
                print(f"Scrolled {i+1} times...", end='\r')
        except Exception as e:
            print(f"Auto-scroll error (might just be done or selector changed): {e}")

    def expand_read_more_buttons(self):
        print("Looking for 'Read more' buttons...")
        try:
            # WhatsApp "Read more" is usually a span or div with that text.
            # Strategy: Find by XPath text content
            read_more_buttons = self.driver.find_elements(By.XPATH, "//span[text()='Read more']")
            
            if not read_more_buttons:
                # Try case insensitive or partial generic
                read_more_buttons = self.driver.find_elements(By.XPATH, "//div[@role='button'][contains(., 'Read more')]")
            
            count = 0
            for btn in read_more_buttons:
                try:
                    if btn.is_displayed():
                        self.driver.execute_script("arguments[0].click();", btn)
                        count += 1
                        time.sleep(0.5) # small wait for expansion
                except Exception:
                    pass
            
            if count > 0:
                print(f"Clicked {count} 'Read more' buttons.")
                time.sleep(2) # Wait for DOM to settle
            else:
                print("No 'Read more' buttons found.")
                
        except Exception as e:
            print(f"Error expanding messages: {e}")

    def scrape_current_chat(self):
        self.expand_read_more_buttons()
        
        print("\nScraping visible messages...")
        
        # DEBUG: Save HTML to inspect
        with open("debug_snapshot.html", "w", encoding="utf-8") as f:
            f.write(self.driver.page_source)
        print("Saved debug_snapshot.html for inspection.")
        
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        
        messages = []
        
        # WhatsApp Web generic structures
        # Rows often have role="row"
        rows = soup.find_all("div", role="row")
        
        for row in rows:
            try:
                # Extract Text
                text_container = row.find("div", {"class": "copyable-text"})
                if not text_container:
                    continue
                    
                metadata = text_container.get("data-pre-plain-text", "") # "[10:30, 25/12/2023] Sender: "
                content_text = text_container.find("span", {"class": "_11JPr"}) # The actual message text generic class?
                
                # Fallback text extraction if exact class finding fails
                if not content_text:
                    # just get all text in the readable area
                    content_text = text_container.get_text(separator=" ").replace(metadata, "")
                else:
                    content_text = content_text.get_text()
                
                # Extract Links (YouTube etc)
                links = [a.get('href') for a in row.find_all('a', href=True)]
                
                # Check for images (not easy to get content, but can get alt)
                # img nodes
                imgs = row.find_all('img')
                img_alts = [img.get('alt') or img.get('src') for img in imgs if 'blob:' in img.get('src', '')]
                
                messages.append({
                    "metadata": metadata,
                    "text": content_text.strip(),
                    "links": links,
                    "images": len(img_alts) > 0
                })
            except Exception as e:
                pass # skip malformed rows
                
        print(f"Scraped {len(messages)} messages.")
        return messages

    def close(self):
        if self.driver:
            pass # self.driver.quit()

if __name__ == "__main__":
    scraper = WhatsAppScraper()
    try:
        scraper.connect()
        # scraper.scroll_to_top() # disable auto scroll for first test
        msgs = scraper.scrape_current_chat()
        print(msgs[:5])
    except Exception as e:
        print(e)
    finally:
        scraper.close()
